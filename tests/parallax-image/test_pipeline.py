"""Behavioral invariants for the parallax-image runtime pack (no model needed)."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import sys

sys.dont_write_bytecode = True

import numpy as np
from PIL import Image

SKILL = Path(os.environ.get("PARALLAX_SKILL_ROOT", Path(__file__).resolve().parents[2] / "skills/parallax-image"))
spec = importlib.util.spec_from_file_location("parallax", SKILL / "scripts/parallax.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class SyntheticFill:
    def fill(self, source, hole):
        # Distinct RGB makes restoring original halo colors detectable.
        return np.where(hole[..., None], np.array([220, 80, 30], dtype=np.uint8), source)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="D:/Temp" if Path("D:/Temp").is_dir() else None)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def inputs(self, flat=False):
        y, x = np.mgrid[:72, :96]
        rgb = np.stack([x * 2, y * 3, np.full_like(x, 120)], axis=2).astype("uint8")
        rgb[5:20, 7:28] = [240, 30, 160]  # asymmetric orientation marker
        Image.fromarray(rgb).save(self.root / "input.png")
        d = np.full(x.shape, .5) if flat else (x // 20) / 4
        Image.fromarray(np.rint(d * 65535).astype("uint16")).save(self.root / "depth.png")
        return rgb, d.astype("float32")

    def args(self, out="pack"):
        return p.parser().parse_args(["prepare", "--image", str(self.root / "input.png"),
                                     "--depth", str(self.root / "depth.png"), "--out", str(self.root / out),
                                     "--width", "96", "--travel", "6"])

    def test_registered_depth_rejects_8bit_and_wrong_size(self):
        self.inputs()
        self.assertEqual(p.supplied_depth(self.root / "depth.png", (96, 72), "near").shape, (72, 96))
        with self.assertRaises(ValueError):
            p.supplied_depth(self.root / "depth.png", (72, 96), "near")
        Image.new("L", (96, 72), 128).save(self.root / "bad.png")
        with self.assertRaises(ValueError):
            p.supplied_depth(self.root / "bad.png", (96, 72), "near")

    def test_exif_and_alpha_registration(self):
        image = Image.new("RGB", (13, 21), "red")
        exif = image.getexif()
        exif[274] = 6
        image.save(self.root / "rotated.jpg", exif=exif)
        arr, registration = p.load_source(self.root / "rotated.jpg", "#ffffff")
        self.assertEqual(arr.shape[:2], (13, 21))
        self.assertEqual(registration["exif_orientation"], 6)
        Image.new("RGBA", (2, 3), (255, 0, 0, 0)).save(self.root / "alpha.png")
        arr, _ = p.load_source(self.root / "alpha.png", "#010203")
        np.testing.assert_array_equal(arr[0, 0], [1, 2, 3])

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "Install parallax-image/scripts/requirements.txt for geometry checks")
    def test_overlap_halo_and_gutters_preserve_repair_rgb(self):
        source, depth = self.inputs()
        out = self.root / "surfaces"
        (out / "diagnostics").mkdir(parents=True)
        config = {"width": 96, "height": 72, "near_radius_effective": 4, "near_gain": .25,
                  "travel": 6, "margins": [3, 14], "radius_scale": 1}
        surfaces, variants = p.build_surfaces(source, depth, out, config, SyntheticFill())
        self.assertTrue(all(s["contraction_bound"] <= .7 for s in surfaces))
        # Band zero ends at x=19; mask's 3px halo extends back to x=17.
        fill = np.asarray(Image.open(out / "margin-3/fill-0.png"))
        np.testing.assert_array_equal(fill[30, 17], [220, 80, 30])
        np.testing.assert_array_equal(fill[30, 10], source[30, 10])
        for name in ["depth-atlas.png", variants[0]["color"]]:
            atlas = np.asarray(Image.open(out / name))
            self.assertEqual(atlas.shape[:2], (5 * 76, 96))
            np.testing.assert_array_equal(atlas[0], atlas[2])
            np.testing.assert_array_equal(atlas[75], atlas[73])

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "Install parallax-image/scripts/requirements.txt for geometry checks")
    def test_model_free_flat_pack_cache_and_tampering(self):
        self.inputs(flat=True)
        args = self.args()
        first = p.prepare(args)
        self.assertFalse(first["cache_hit"])
        self.assertTrue(p.prepare(args)["cache_hit"])
        manifest = p.load_pack(self.root / "pack")[1]
        self.assertTrue(manifest["static"])
        self.assertEqual(len(manifest["runtime_files"]), 4)
        # Different settings cannot silently use the same pack.
        args.travel = 3
        with self.assertRaises(ValueError):
            p.prepare(args)
        with (self.root / "pack/owner.png").open("ab") as f:
            f.write(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum"):
            p.verify_pack(self.root / "pack")

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "Install parallax-image/scripts/requirements.txt for geometry checks")
    def test_script_escape_for_untrusted_source_names(self):
        self.inputs(flat=True)
        p.prepare(self.args())
        path = self.root / "pack/manifest.json"
        m = json.loads(path.read_text())
        m["source"]["name"] = '</script><img src=x onerror="boom">'
        p.write_json(path, m)
        p.make_view([path.parent], self.root / "review.html")
        text = (self.root / "review.html").read_text(encoding="utf-8")
        self.assertNotIn('</script><img src=x', text)
        self.assertIn('\\u003c/script\\u003e', text)

    def test_asset_paths_cannot_leave_pack(self):
        with self.assertRaises(ValueError):
            p.asset_path(self.root, "../private.png")


if __name__ == "__main__":
    unittest.main()
