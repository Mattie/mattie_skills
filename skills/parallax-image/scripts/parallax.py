"""Prepare local depth-mask parallax packs, or verify/view cached textures."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import platform
import re
import sys
import time

import numpy as np
from PIL import Image, ImageCms, ImageOps

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "viewer.html"
RECIPE = "parallax-five-continuous-v1"
DEPTH_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"
DEPTH_REVISION = "5426e4f0f36572d16453bbda7a8389317b1bef99"
LAMA_SHA = "7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c"
K, G = 5, 2


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else sha(f.read())


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def versions():
    result = {"python": platform.python_version()}
    for name in ("numpy", "Pillow", "scipy", "torch", "transformers", "huggingface-hub"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def load_source(path, background):
    with Image.open(path) as raw:
        original_size = list(raw.size)
        orientation = raw.getexif().get(274, 1)
        image = ImageOps.exif_transpose(raw)
        alpha = image.convert("RGBA").getchannel("A")
        icc = image.info.get("icc_profile")
        if icc:
            # Keep native CMYK/LAB channels while applying the embedded profile.
            color = image if image.mode in ("RGB", "CMYK", "LAB", "L") else image.convert("RGB")
            image = ImageCms.profileToProfile(color, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                              ImageCms.createProfile("sRGB"), outputMode="RGB")
        else:
            image = image.convert("RGB")
        backdrop = Image.new("RGB", image.size, background)
        backdrop.paste(image, mask=alpha)
        arr = np.asarray(backdrop).copy()
    return arr, {"name": Path(path).name, "bytes_sha256": file_sha(path),
                 "decoded_rgb_sha256": sha(arr.tobytes()), "original_size": original_size,
                 "size": list(backdrop.size), "exif_orientation": int(orientation),
                 "icc": "converted-to-srgb" if icc else "assumed-srgb",
                 "alpha": {"mode": "flatten", "background": background}}


def supplied_depth(path, size, direction):
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode not in ("I;16", "I;16B", "I;16L", "I") or image.size != size:
            raise ValueError("Depth must be a registered single-channel 16-bit PNG at oriented source size")
        d = np.asarray(image, dtype=np.float32) / 65535
    if not np.isfinite(d).all() or d.min() < 0 or d.max() > 1:
        raise ValueError("Invalid normalized depth values")
    return 1 - d if direction == "far" else d


def sync(torch, device):
    if str(device).startswith("cuda"):
        torch.cuda.synchronize(device)


def estimate_depth(source, args, device, receipt):
    import torch
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation

    start = time.perf_counter()
    opts = {"revision": args.depth_revision, "local_files_only": not args.allow_download,
            "trust_remote_code": False}
    processor = AutoImageProcessor.from_pretrained(args.depth_model, use_fast=False, **opts)
    model = AutoModelForDepthEstimation.from_pretrained(args.depth_model, use_safetensors=True, **opts).to(device).eval()
    sync(torch, device)
    receipt["depth_load_s"] = time.perf_counter() - start
    inputs = processor(images=Image.fromarray(source), return_tensors="pt").to(device)
    sync(torch, device)
    start = time.perf_counter()
    with torch.inference_mode():
        prediction = model(**inputs).predicted_depth
        prediction = torch.nn.functional.interpolate(prediction.unsqueeze(1), size=source.shape[:2],
                                                      mode="bicubic", align_corners=False)[0, 0]
    sync(torch, device)
    receipt["depth_inference_s"] = time.perf_counter() - start
    raw = prediction.float().cpu().numpy()
    if not np.isfinite(raw).all():
        raise ValueError("Nonfinite predicted depth")
    if args.depth_direction == "far":
        raw = -raw
    lo, hi = np.percentile(raw, [1, 99])
    receipt["depth_percentiles"] = [float(lo), float(hi)]
    if hi - lo <= 1e-6:
        return np.full(raw.shape, .5, dtype="float32"), raw
    return np.clip((raw - lo) / max(hi - lo, 1e-6), 0, 1), raw


class Lama:
    """One trusted TorchScript model per process; never imported for cached viewing."""
    def __init__(self, path, device, receipt):
        self.path, self.device, self.receipt = path, device, receipt
        self.model = None

    def fill(self, source, hole):
        import torch
        h, w = hole.shape
        rgb = np.pad(source.astype("float32").transpose(2, 0, 1) / 255,
                     ((0, 0), (0, (-h) % 8), (0, (-w) % 8)), mode="symmetric")
        mask = np.pad(hole.astype("float32")[None],
                      ((0, 0), (0, (-h) % 8), (0, (-w) % 8)), mode="symmetric")
        a, b = torch.from_numpy(rgb)[None].to(self.device), torch.from_numpy(mask)[None].to(self.device)
        if self.model is None:
            if self.path is None:
                raise ValueError("Nonflat surfaces need --lama with a verified local TorchScript artifact")
            start = time.perf_counter()
            self.model = torch.jit.load(str(self.path), map_location=self.device).eval()
            sync(torch, self.device)
            self.receipt["lama_load_s"] = time.perf_counter() - start
        sync(torch, self.device)
        start = time.perf_counter()
        with torch.inference_mode():
            out = self.model(a, b)
        sync(torch, self.device)
        self.receipt.setdefault("lama_inference_s", []).append(time.perf_counter() - start)
        generated = out[0].permute(1, 2, 0).float().cpu().numpy()[:h, :w]
        if generated.shape != source.shape or not np.isfinite(generated).all():
            raise ValueError("LaMa produced invalid RGB")
        generated = np.clip(generated * 255, 0, 255).astype("uint8")
        return np.where(hole[..., None], generated, source)


def gradient_bound(d):
    dx, dy = np.diff(d, axis=1), np.diff(d, axis=0)
    return float(np.hypot(np.maximum(abs(dx[:-1]), abs(dx[1:])),
                          np.maximum(abs(dy[:, :-1]), abs(dy[:, 1:]))).max())


def regularize(field, size, travel):
    from scipy.ndimage import gaussian_filter
    small = np.asarray(Image.fromarray(field.astype("float32")).resize(size, Image.Resampling.BICUBIC))
    for step in range(25):
        sigma = step * .5
        q = np.clip(np.rint((gaussian_filter(small, sigma) if sigma else small) * 255), 0, 255).astype("uint8")
        bound = gradient_bound(q.astype(float) / 255) * travel * math.sqrt(2)
        if bound <= .70:
            return Image.fromarray(q), {"sigma": sigma, "contraction_bound": bound}
    raise ValueError("Quantized depth could not satisfy the motion gradient bound at sigma <= 12")


def paste(atlas, image, index):
    w, h = image.size
    y = index * (h + 2 * G) + G
    atlas.paste(image, (0, y))
    for j in range(G):
        atlas.paste(image.crop((0, 0, w, 1)), (0, y - 1 - j))
        atlas.paste(image.crop((0, h - 1, w, h)), (0, y + h + j))


def build_surfaces(source, d, root, config, filler):
    from scipy.ndimage import distance_transform_edt, maximum_filter
    w, h = config["width"], config["height"]
    size, native = (w, h), (source.shape[1], source.shape[0])
    bins = np.minimum((d * K).astype(int), K - 1)
    radius = config["near_radius_effective"]
    r = math.ceil(radius)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    near = maximum_filter(d, footprint=xx * xx + yy * yy <= radius * radius)
    owner = np.where(near - d > config["near_gain"], near, d)
    own = np.asarray(Image.fromarray(owner.astype("float32")).resize(size, Image.Resampling.BICUBIC))
    Image.fromarray(np.clip(np.rint(own * 255), 0, 255).astype("uint8")).save(root / "owner.png")
    Image.fromarray(source).save(root / "diagnostics" / "source-native.png")
    Image.fromarray(source).resize(size, Image.Resampling.LANCZOS).save(root / "source.png")
    Image.fromarray(np.rint(d * 65535).astype("uint16")).save(root / "diagnostics" / "depth-native.png")
    depth_atlas = Image.new("L", (w, K * (h + 2 * G)))
    # Include source-scaled guard beyond the both-axis displacement envelope.
    reach = math.ceil(config["travel"] * math.sqrt(2) * native[0] / w) + max(4, math.ceil(radius))
    alphas, surfaces = [], []
    for i in range(K):
        visible, nearer = bins == i, bins > i
        if visible.any():
            distance, indices = distance_transform_edt(~visible, return_indices=True)
            field = d[tuple(indices)].copy()
            field[visible] = d[visible]
            alpha = np.where(visible, 1., np.where(nearer, np.clip((reach - distance) / 3, 0, 1), 0.))
        else:
            field, alpha = np.full(d.shape, (i + .5) / K), np.zeros_like(d)
        if i == 0:
            alpha = np.ones_like(d)
        q, stat = regularize(field, size, config["travel"])
        paste(depth_atlas, q, i)
        alphas.append(np.rint(alpha * 255).astype("uint8"))
        surfaces.append({"index": i, "empty": not bool(visible.any()),
                         "visible_share": float(visible.mean()), **stat})
    depth_atlas.save(root / "depth-atlas.png")
    variants = []
    for margin in config["margins"]:
        label = f"margin-{margin:g}"
        folder = root / label
        folder.mkdir()
        atlas, masks = Image.new("RGBA", depth_atlas.size), Image.new("L", depth_atlas.size)
        checks = []
        for i in range(K):
            nearer = bins > i
            hole = distance_transform_edt(~nearer) <= margin * config["radius_scale"] if nearer.any() else np.zeros_like(nearer)
            color = filler.fill(source, hole) if hole.any() and float(np.ptp(d)) >= 1e-6 else source.copy()
            if not np.array_equal(color[~hole], source[~hole]):
                raise ValueError("Fill changed pixels outside the removal mask")
            Image.fromarray(hole.astype("uint8") * 255).save(folder / f"mask-{i}.png")
            Image.fromarray(color).save(folder / f"fill-{i}.png")
            rgba = np.dstack([color, alphas[i]])
            rgba[rgba[:, :, 3] == 0, :3] = 0
            paste(atlas, Image.fromarray(rgba).resize(size, Image.Resampling.LANCZOS), i)
            paste(masks, Image.fromarray(hole.astype("uint8") * 255).resize(size, Image.Resampling.LANCZOS), i)
            checks.append({"surface": i, "outside_removal_unchanged": True, "removed_share": float(hole.mean())})
        atlas.save(folder / "color-atlas.png")
        masks.save(folder / "removal-atlas.png")
        variants.append({"id": label, "margin": margin, "margin_source_px": margin * config["radius_scale"],
                         "color": f"{label}/color-atlas.png", "removal": f"{label}/removal-atlas.png", "fills": checks})
    return surfaces, variants


def asset_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Pack asset path escapes its directory")
    return path


def load_pack(root):
    root = Path(root).resolve()
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if m.get("schema") != 1 or m.get("recipe") != RECIPE:
        raise ValueError("Unsupported pack schema or recipe")
    return root, m


def verify_pack(root):
    root, m = load_pack(root)
    for relative, expected in m["files"].items():
        path = asset_path(root, relative)
        if path.stat().st_size != expected["bytes"] or file_sha(path) != expected["sha256"]:
            raise ValueError(f"Asset checksum mismatch: {relative}")
    w, h = m["config"]["width"], m["config"]["height"]
    if min(w, h) < 2 or m["config"]["surfaces"] != K or m["config"]["gutter"] != G:
        raise ValueError("Invalid geometry")
    for name in ("source.png", "owner.png"):
        with Image.open(root / name) as im:
            if im.size != (w, h):
                raise ValueError(f"Registration mismatch: {name}")
    depth = np.asarray(Image.open(root / "depth-atlas.png"))
    atlases = ["depth-atlas.png"] + [v[k] for v in m["variants"] for k in ("color", "removal")]
    for name in atlases:
        a = np.asarray(Image.open(asset_path(root, name)))
        if a.shape[:2] != (K * (h + 2 * G), w):
            raise ValueError(f"Atlas dimensions: {name}")
        for i in range(K):
            y = i * (h + 2 * G) + G
            if not (np.all(a[y-G:y] == a[y]) and np.all(a[y+h:y+h+G] == a[y+h-1])):
                raise ValueError(f"Atlas gutter mismatch: {name}, surface {i}")
    for i in range(K):
        y = i * (h + 2 * G) + G
        bound = gradient_bound(depth[y:y+h].astype(float) / 255) * m["config"]["travel"] * math.sqrt(2)
        if bound > .70 + 1e-9:
            raise ValueError(f"Quantized depth gradient exceeds envelope: {i}")
    source = np.asarray(Image.open(root / "diagnostics/source-native.png"))
    if sha(source.tobytes()) != m["source"]["decoded_rgb_sha256"]:
        raise ValueError("Native source registration hash mismatch")
    for variant in m["variants"]:
        for i in range(K):
            hole = np.asarray(Image.open(asset_path(root, f'{variant["id"]}/mask-{i}.png'))) > 0
            fill = np.asarray(Image.open(asset_path(root, f'{variant["id"]}/fill-{i}.png')))
            if hole.shape != source.shape[:2] or fill.shape != source.shape or not np.array_equal(fill[~hole], source[~hole]):
                raise ValueError("Native fill changed outside its mask or is unregistered")
    return {"structural_pass": True, "variants": len(m["variants"]), "files_checked": len(m["files"]),
            "visual_approval": "pending", "render_check": "run check_render.py"}


def make_view(roots, output):
    data = []
    for root in roots:
        verify_pack(root)
        root, m = load_pack(root)
        def uri(name):
            return "data:image/png;base64," + base64.b64encode(asset_path(root, name).read_bytes()).decode("ascii")
        data.append({"name": m["source"]["name"], "width": m["config"]["width"], "height": m["config"]["height"],
                     "travel": m["config"]["travel"], "static": m["static"], "selected": m["selected_variant"],
                     "source": uri("source.png"), "depths": uri("depth-atlas.png"), "owner": uri("owner.png"),
                     "variants": [{**{k: v[k] for k in ("id", "margin_source_px")},
                                   "color": uri(v["color"]), "removal": uri(v["removal"])} for v in m["variants"]]})
    # Source names are untrusted strings, including possible HTML closing tags.
    encoded = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(TEMPLATE.read_text(encoding="utf-8").replace("/*PACK_DATA*/[]", encoded), encoding="utf-8")
    return str(output.resolve())


def prepare(args):
    wall = time.perf_counter()
    if not math.isfinite(args.travel) or args.travel < 0 or args.width < 2 or args.near_radius < 0 or not math.isfinite(args.near_radius):
        raise ValueError("Width >= 2 and finite nonnegative travel/radius are required")
    if args.reference_width is not None and (not math.isfinite(args.reference_width) or args.reference_width <= 0):
        raise ValueError("Reference width must be positive")
    margins = sorted(set(args.margins))
    if not margins or any(not math.isfinite(x) or x < 0 for x in margins) or args.selected_margin not in margins:
        raise ValueError("Margins must be finite nonnegative values and include the selected margin")
    if not args.depth and (not re.fullmatch(r"[0-9a-fA-F]{40}", args.depth_revision) or Path(args.depth_model).exists()):
        raise ValueError("Depth estimation requires a Hugging Face model ID and immutable 40-character revision, not a local directory")
    source, registration = load_source(args.image, args.background)
    sh, sw = source.shape[:2]
    h = round(args.width * sh / sw)
    if h < 2 or args.travel + 2 >= min(args.width, h):
        raise ValueError("Image dimensions are too small for the requested crop/travel")
    lama_hash = file_sha(args.lama) if args.lama else None
    if lama_hash is not None and lama_hash != args.lama_sha256:
        raise ValueError("LaMa SHA256 mismatch; use a separately verified trusted artifact")
    scale = sw / args.reference_width if args.reference_width else 1.
    config = {"width": args.width, "height": h, "surfaces": K, "gutter": G, "travel": args.travel,
              "margins": margins, "selected_margin": args.selected_margin,
              "reference_width": args.reference_width, "radius_scale": scale,
              "near_radius": args.near_radius, "near_radius_effective": args.near_radius * scale,
              "near_gain": .25, "background": args.background, "inverse_iterations": 8,
              "renderer_revision": "ownership-overlap-v2", "ownership_blend_depth": .02,
              "alpha": "straight-png-premultiply-once-at-upload", "data_textures": "linear"}
    depth_id = ({"kind": "registered-16bit-png", "sha256": file_sha(args.depth)} if args.depth else
                {"kind": "transformers", "model": args.depth_model, "revision": args.depth_revision})
    depth_id["direction"] = args.depth_direction
    identity = {"recipe": RECIPE, "source": registration, "config": config, "depth": depth_id,
                "lama_sha256": lama_hash, "environment": versions(), "device": args.device,
                "preparer_sha256": file_sha(__file__), "renderer_sha256": file_sha(TEMPLATE)}
    key = sha(json.dumps(identity, sort_keys=True).encode())
    root = Path(args.out).resolve()
    if root.exists() and any(root.iterdir()):
        old = load_pack(root)[1] if (root / "manifest.json").exists() else {}
        if old.get("cache_key") != key:
            raise ValueError("Output is nonempty and does not match this recipe; choose another --out")
        verify_pack(root)
        if not (root / "verifier.html").exists():
            make_view([root], root / "verifier.html")
        return {"cache_hit": True, "out": str(root), "validation": "structural-pass"}
    # Validate supplied depth before creating output files.
    d = supplied_depth(args.depth, (sw, sh), args.depth_direction) if args.depth else None
    device = args.device
    receipt = {"cache_hit": False, "environment": versions(), "command": [sys.executable, *sys.argv],
               "timing_note": "First inference includes warmup; CUDA timings synchronized; tensor memory is not whole-device usage"}
    if d is None or (float(np.ptp(d)) >= 1e-6 and lama_hash is not None):
        import torch
        device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats(device)
    if d is None:
        d, raw = estimate_depth(source, args, device, receipt)
    else:
        raw = None
    static = float(np.ptp(d)) < 1e-6
    if not static and lama_hash is None:
        raise ValueError("Nonflat depth requires --lama; use cached view/verify without models")
    root.mkdir(parents=True, exist_ok=True)
    (root / "diagnostics").mkdir()
    if raw is not None:
        np.save(root / "diagnostics" / "depth-prediction.npy", raw)
    start = time.perf_counter()
    surfaces, variants = build_surfaces(source, d, root, config, Lama(args.lama, device, receipt))
    receipt["surface_fill_pack_write_s"] = time.perf_counter() - start
    receipt["device"] = device
    if str(device).startswith("cuda"):
        import torch
        receipt["cuda_peak_allocated_bytes"] = torch.cuda.max_memory_allocated(device)
        receipt["cuda_peak_reserved_bytes"] = torch.cuda.max_memory_reserved(device)
    selected = f"margin-{args.selected_margin:g}"
    runtime = ["source.png", "depth-atlas.png", "owner.png", f"{selected}/color-atlas.png"]
    inventory = {str(p.relative_to(root)).replace("\\", "/"): {"sha256": file_sha(p), "bytes": p.stat().st_size}
                 for p in sorted(root.rglob("*")) if p.is_file()}
    m = {"schema": 1, "recipe": RECIPE, "cache_key": key, "identity": identity, "source": registration,
         "config": config, "static": static, "surfaces": surfaces, "variants": variants,
         "selected_variant": selected, "runtime_files": runtime, "files": inventory,
         "quality_exceptions": ["Flat depth: static playback"] if static else [], "visual_approval": "pending"}
    write_json(root / "manifest.json", m)
    check = verify_pack(root)
    start = time.perf_counter()
    make_view([root], root / "verifier.html")
    receipt["verifier_write_s"] = time.perf_counter() - start
    receipt["whole_preparation_s"] = time.perf_counter() - wall
    receipt["runtime_asset_bytes"] = sum(inventory[p]["bytes"] for p in runtime)
    receipt["runtime_texture_rgba_bytes"] = 0
    for relative in runtime:
        with Image.open(root / relative) as image:
            receipt["runtime_texture_rgba_bytes"] += image.width * image.height * 4
    write_json(root / "receipt.json", receipt)
    write_json(root / "structural-check.json", check)
    return {"cache_hit": False, "out": str(root), **check}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    a = commands.add_parser("prepare", help="Prepare an image into cached textures and a verifier")
    a.add_argument("--image", type=Path, required=True)
    a.add_argument("--depth", type=Path)
    a.add_argument("--depth-direction", choices=["near", "far"], default="near")
    a.add_argument("--depth-model", default=DEPTH_MODEL)
    a.add_argument("--depth-revision", default=DEPTH_REVISION)
    a.add_argument("--allow-download", action="store_true")
    a.add_argument("--lama", type=Path)
    a.add_argument("--lama-sha256", default=LAMA_SHA)
    a.add_argument("--out", type=Path, required=True)
    a.add_argument("--width", type=int, default=250)
    a.add_argument("--travel", type=float, default=6)
    a.add_argument("--margins", type=float, nargs="+", default=[3, 14])
    a.add_argument("--selected-margin", type=float, default=3)
    a.add_argument("--near-radius", type=float, default=4)
    a.add_argument("--reference-width", type=float)
    a.add_argument("--background", default="#ffffff")
    a.add_argument("--device", default="auto", help="auto, cpu, cuda, or cuda:N")
    a = commands.add_parser("verify", help="Verify cached pack structure, hashes, and native fills")
    a.add_argument("pack", type=Path)
    for name in ("view", "gallery"):
        a = commands.add_parser(name, help="Build standalone HTML using only cached textures")
        a.add_argument("packs", type=Path, nargs="+")
        a.add_argument("--out", type=Path, required=True)
    return p


def main():
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args)
        elif args.command == "verify":
            result = verify_pack(args.pack)
        else:
            result = {"html": make_view(args.packs, args.out)}
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, ImportError, RuntimeError, KeyError) as error:
        print(f"parallax: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
