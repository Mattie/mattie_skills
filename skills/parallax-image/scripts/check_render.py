"""Check a cached pack's real WebGL renderer using a headless local browser."""
import argparse
import base64
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

from parallax import load_pack, make_view, verify_pack, write_json


def static_reference(source, travel):
    """Independent bilinear crop; catches a shared UV flip in both shader modes."""
    h, w = source.shape[:2]
    zoom = 1 - (travel + 2) / min(w, h)
    x = np.clip((.5 + ((np.arange(w) + .5) / w - .5) * zoom) * w - .5, 0, w - 1)
    y = np.clip((.5 + ((np.arange(h) + .5) / h - .5) * zoom) * h - .5, 0, h - 1)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (x - x0)[None, :, None], (y - y0)[:, None, None]
    top = source[y0[:, None], x0] * (1 - fx) + source[y0[:, None], x1] * fx
    bottom = source[y1[:, None], x0] * (1 - fx) + source[y1[:, None], x1] * fx
    return np.rint(top * (1 - fy) + bottom * fy).astype("uint8")


def temporal_probe(page):
    """Keep pixel comparisons inside the browser; return a small diagnostic crop."""
    return page.evaluate("""() => {
        const canvas=document.getElementById('result'),w=canvas.width,h=canvas.height;
        let previous=null,older=null,best=-1,bestFrames=null,bestIndex=0,bestStep=0,spikes=0,opaque=true;
        for(let step=0;step<41;step++){
            const t=-1+step*.05;parallaxVerifier.position(t,t);
            const frame=canvas.getContext('2d').getImageData(0,0,w,h).data;
            if(older){
                let maximum=0,index=0;
                for(let y=Math.floor(h*.1);y<Math.ceil(h*.9);y++)
                    for(let x=Math.floor(w*.1);x<Math.ceil(w*.9);x++){
                        const pixel=(y*w+x)*4;if(frame[pixel+3]!==255)opaque=false;
                        for(let c=0;c<3;c++){
                            const i=pixel+c,d=Math.abs(frame[i]-2*previous[i]+older[i]);
                            if(d>32)spikes++;if(d>maximum){maximum=d;index=i;}
                        }
                    }
                if(maximum>best){best=maximum;bestFrames=[older,previous,frame];bestIndex=index;bestStep=step-1;}
            }
            older=previous;previous=frame;
        }
        const size=Math.min(96,w,h),px=Math.floor(bestIndex/4)%w,py=Math.floor(bestIndex/4/w);
        const ox=Math.max(0,Math.min(w-size,px-Math.floor(size/2))),oy=Math.max(0,Math.min(h-size,py-Math.floor(size/2)));
        const crops=bestFrames.map(frame=>{
            const big=document.createElement('canvas');big.width=w;big.height=h;
            big.getContext('2d').putImageData(new ImageData(frame,w,h),0,0);
            const small=document.createElement('canvas');small.width=size;small.height=size;
            small.getContext('2d').drawImage(big,ox,oy,size,size,0,0,size,size);return small.toDataURL();
        });
        parallaxVerifier.neutral();
        return {positions:41,compared_frames:39,max_second_difference:best,spike_channels:spikes,
            threshold:32,opaque,peak_pixel:[px,py],peak_position:-1+bestStep*.05,crops,
            note:'Central 80% diagonal sweep; discontinuity proxy, not an aesthetic pass score'};
    }""")


def check(root, browser_path=None):
    root, m = load_pack(root)
    verify_pack(root)
    make_view([root], root / "verifier.html")
    captures = root / "captures"
    captures.mkdir(exist_ok=True)
    results = {"variants": [], "page_errors": [], "visual_approval": "pending",
               "note": "Opacity is measured but does not prove plausible coverage or good infill"}
    panels = []
    with sync_playwright() as p:
        options = {"headless": True}
        if browser_path:
            options["executable_path"] = str(browser_path)
        browser = p.chromium.launch(**options)
        try:
            page = browser.new_page(viewport={"width": 1100, "height": 900}, device_scale_factor=1,
                                    reduced_motion="reduce")
            page.on("pageerror", lambda e: results["page_errors"].append(str(e)))
            page.goto((root / "verifier.html").as_uri())
            page.wait_for_function("window.parallaxVerifier?.ready", timeout=60000)
            assert not page.evaluate("parallaxVerifier.playing"), "Unexpected idle animation"
            assert page.locator("#play").is_disabled(), "Reduced-motion playback enabled"

            def pixels(id):
                # Lossless PNG avoids serializing millions of individual integers.
                uri = page.evaluate("id=>document.getElementById(id).toDataURL('image/png')", id)
                with Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))) as image:
                    return np.asarray(image.convert("RGBA")).reshape(-1).copy()

            for variant in m["variants"]:
                page.evaluate("async id=>await parallaxVerifier.choose(0,id)", variant["id"])
                page.select_option("#view", "motion")
                page.evaluate("parallaxVerifier.neutral()")
                baseline, neutral = pixels("baseline"), pixels("result")
                with Image.open(root / "source.png") as original:
                    expected = static_reference(np.asarray(original.convert("RGB")), m["config"]["travel"])
                actual = baseline.reshape(m["config"]["height"], m["config"]["width"], 4)[..., :3]
                registration_delta = int(np.abs(actual.astype(int) - expected.astype(int)).max())
                assert registration_delta <= 2, f"Static source crop/UV mismatch: {registration_delta}"
                delta = int(np.abs(baseline.astype(int) - neutral.astype(int)).max())
                assert delta == 0, f"Neutral differs: {variant['id']}, delta {delta}"
                im = Image.open(io.BytesIO(page.locator("#result").screenshot()))
                im.save(captures / f"{variant['id']}-neutral.png")
                row = {"id": variant["id"], "neutral_max_delta": delta,
                       "independent_static_crop_max_delta": registration_delta, "extremes": []}
                hashes = set()
                for x, y in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    page.evaluate("([x,y])=>parallaxVerifier.position(x,y)", [x, y])
                    data = pixels("result")
                    assert np.all(data[3::4] == 255), "Transparent output at motion extreme"
                    hashes.add(data.tobytes())
                    name = f"{variant['id']}-{x}-{y}.png"
                    image = Image.open(io.BytesIO(page.locator("#result").screenshot())).convert("RGB")
                    image.save(captures / name)
                    panels.append((f"{variant['id']}  {x},{y}", image))
                    row["extremes"].append({"x": x, "y": y, "opaque": True, "capture": "captures/" + name})
                if not m["static"] and m["config"]["travel"] > 0:
                    assert len(hashes) >= 2, "Motion never changes the image"
                for value in [.25, .5, .75, 0]:
                    page.evaluate("v=>parallaxVerifier.position(v,-v)", value)
                    assert np.all(pixels("result")[3::4] == 255)
                assert np.array_equal(pixels("result"), neutral), "Return-to-neutral differs"
                motion = temporal_probe(page)
                assert motion["opaque"], "Transparent output during dense motion probe"
                crops = motion.pop("crops")
                strip = Image.new("RGB", (288 * 3, 312), "#16171b")
                drawing = ImageDraw.Draw(strip)
                for j, encoded in enumerate(crops):
                    with Image.open(io.BytesIO(base64.b64decode(encoded.split(",", 1)[1]))) as image:
                        strip.paste(image.convert("RGB").resize((288, 288), Image.Resampling.NEAREST), (j * 288, 24))
                    drawing.text((j * 288 + 3, 3), ["before", "event", "after"][j], fill="white")
                name = f"{variant['id']}-temporal-event.png"
                strip.save(captures / name)
                motion["capture"] = "captures/" + name
                row["temporal_probe"] = motion
                assert np.array_equal(pixels("result"), neutral), "Dense motion return-to-neutral differs"
                # Exercise diagnostics and a narrow viewport, then restore motion.
                for mode in ("owner", "surface", "depth", "removal"):
                    page.select_option("#view", mode)
                    page.evaluate("parallaxVerifier.draw()")
                page.select_option("#view", "motion")
                page.set_viewport_size({"width": 300, "height": 700})
                page.evaluate("parallaxVerifier.neutral()")
                assert np.array_equal(pixels("result"), neutral), "Resize changes source pixels"
                page.set_viewport_size({"width": 1100, "height": 900})
                results["variants"].append(row)
            # Revisit a variant to exercise texture disposal/reload.
            page.evaluate("async ()=>await parallaxVerifier.choose(0)")
            page.emulate_media(reduced_motion="no-preference")
            if not m["static"]:
                page.locator("#play").click()
                page.wait_for_function("document.getElementById('x').value!=='0'")
                page.locator("#neutral").click()
                assert not page.evaluate("parallaxVerifier.playing")
            assert not results["page_errors"], results["page_errors"]
            results.update({"render_pass": True, "resize_revisit_return_neutral": True,
                            "reduced_motion_checked": True, "browser_version": browser.version})
        finally:
            browser.close()
    w, h = m["config"]["width"], m["config"]["height"]
    sheet = Image.new("RGB", (w * 4, (h + 24) * ((len(panels) + 3) // 4)), "#16171b")
    draw = ImageDraw.Draw(sheet)
    for i, (label, image) in enumerate(panels):
        x, y = i % 4 * w, i // 4 * (h + 24)
        draw.text((x + 3, y + 3), label, fill="white")
        sheet.paste(image, (x, y + 24))
    sheet.save(root / "contact-sheet.png")
    write_json(root / "render-check.json", results)
    return {"render_pass": True, "variants": len(results["variants"]),
            "contact_sheet": str(root / "contact-sheet.png"), "visual_approval": "pending"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--browser", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.pack, args.browser), indent=2))
