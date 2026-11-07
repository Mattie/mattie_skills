"""Model-free browser regression for depth-band ownership popping."""
import os
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

from test_pipeline import p


class BackgroundFill:
    def fill(self, source, hole):
        return np.where(hole[..., None], np.array([26, 31, 39], dtype=np.uint8), source)


def make_fixture(root):
    w, h = 256, 192
    y, x = np.mgrid[:h, :w]
    mask = ((x - 130) / 87) ** 2 + ((y - 102) / 63) ** 2 < 1
    image = Image.new("RGB", (w, h), (26, 31, 39))
    draw = ImageDraw.Draw(image)
    draw.ellipse((43, 39, 217, 165), fill=(239, 214, 146), outline=(255, 245, 215), width=3)
    draw.rectangle((92, 64, 104, 137), fill=(24, 27, 35))
    draw.rectangle((104, 126, 169, 138), fill=(24, 27, 35))
    draw.rectangle((8, 7, 21, 15), fill=(220, 45, 110))  # asymmetric UV marker
    source = np.asarray(image).copy()
    depth = np.where(mask, .32 + .50 * np.clip((x - 43) / 174, 0, 1), .05 + .30 * y / h)
    config = {"width": w, "height": h, "surfaces": 5, "gutter": 2, "travel": 3,
              "near_radius_effective": 4, "near_gain": .25, "margins": [3], "radius_scale": 1}
    (root / "diagnostics").mkdir()
    surfaces, variants = p.build_surfaces(source, depth, root, config, BackgroundFill())
    files = {str(path.relative_to(root)).replace("\\", "/"):
             {"sha256": p.file_sha(path), "bytes": path.stat().st_size}
             for path in root.rglob("*") if path.is_file()}
    manifest = {"schema": 1, "recipe": p.RECIPE, "source": {"name": "Synthetic coin",
                "decoded_rgb_sha256": p.sha(source.tobytes())}, "config": config,
                "static": False, "surfaces": surfaces, "variants": variants,
                "selected_variant": "margin-3", "files": files}
    p.write_json(root / "manifest.json", manifest)
    p.make_view([root], root / "verifier.html")


@unittest.skipUnless(os.environ.get("PARALLAX_RENDER_TESTS") == "1", "Set PARALLAX_RENDER_TESTS=1 for the browser regression")
class RenderOwnershipTests(unittest.TestCase):
    def test_opaque_surface_does_not_flash_during_small_motion_steps(self):
        from playwright.sync_api import sync_playwright

        with tempfile.TemporaryDirectory(dir="D:/Temp" if Path("D:/Temp").is_dir() else None) as temp:
            root = Path(temp)
            make_fixture(root)
            with sync_playwright() as playwright:
                options = {"headless": True}
                if os.environ.get("PARALLAX_TEST_BROWSER"):
                    options["executable_path"] = os.environ["PARALLAX_TEST_BROWSER"]
                browser = playwright.chromium.launch(**options)
                try:
                    page = browser.new_page(reduced_motion="reduce")
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto((root / "verifier.html").as_uri())
                    page.wait_for_function("window.parallaxVerifier?.ready")
                    result = page.evaluate("""() => {
                        const c=document.getElementById('result'),s=document.getElementById('baseline'),w=c.width,h=c.height;
                        const baseline=s.getContext('2d').getImageData(0,0,w,h).data;
                        const neutral=c.getContext('2d').getImageData(0,0,w,h).data;
                        let neutralDelta=0,maximum=0,opaque=true,previous=null,older=null;
                        for(let i=0;i<baseline.length;i++)neutralDelta=Math.max(neutralDelta,Math.abs(baseline[i]-neutral[i]));
                        for(let step=0;step<81;step++){
                            const t=-1+step*.025;parallaxVerifier.position(t,t);
                            const frame=c.getContext('2d').getImageData(0,0,w,h).data;
                            for(let i=0;i<frame.length;i++){
                                if(i%4===3){if(frame[i]!==255)opaque=false;continue;}
                                if(older)maximum=Math.max(maximum,Math.abs(frame[i]-2*previous[i]+older[i]));
                            }
                            older=previous;previous=frame;
                        }
                        parallaxVerifier.neutral();
                        const returned=c.getContext('2d').getImageData(0,0,w,h).data;
                        let returnDelta=0;for(let i=0;i<baseline.length;i++)returnDelta=Math.max(returnDelta,Math.abs(baseline[i]-returned[i]));
                        const marker=Array.from(baseline.slice((7*w+12)*4,(7*w+12)*4+3));
                        return {neutralDelta,returnDelta,opaque,marker,maxSecondDifference:maximum};
                    }""")
                    self.assertFalse(errors)
                    self.assertEqual(result["neutralDelta"], 0)
                    self.assertEqual(result["returnDelta"], 0)
                    self.assertTrue(result["opaque"])
                    self.assertEqual(result["marker"], [220, 45, 110])
                    self.assertLess(result["maxSecondDifference"], 100, result)
                finally:
                    browser.close()


if __name__ == "__main__":
    unittest.main()
