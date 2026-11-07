# Parallax image checks

Install the skill's core dependencies and pytest in a Python 3.12 environment:

```text
python -m pip install -r skills/parallax-image/scripts/requirements.txt pytest
python -m pytest -q tests/parallax-image
```

Six model-free behavioral tests cover image registration, the repair halo and atlas gutters, depth validation, static preparation, cache invalidation, asset tampering, HTML escaping, and path containment. The browser regression is opt-in and skipped by default.

For the browser regression, install `skills/parallax-image/scripts/requirements-check.txt`, run `python -m playwright install chromium`, and set `PARALLAX_RENDER_TESTS` to `1` before running the same pytest command. Optionally set `PARALLAX_TEST_BROWSER` to an installed Chromium or Edge executable instead of downloading Chromium. No depth model, LaMa weights, GPU, source artwork, or network access is needed while the tests run.

The regression generates an asymmetric synthetic coin scene with a known background fill and continuous depth bands. It checks UV orientation, exact neutral and return-to-neutral output, opaque coverage, and absence of large frame-to-frame flashes during a shallow diagonal move. The old hard-ownership renderer fails this test; the overlapping-ownership renderer passes. Its threshold is specific to this controlled fixture and motion range, not an aesthetic approval rule for arbitrary photographs.

The path-scoped GitHub Actions workflow runs all seven checks with software Chromium.
