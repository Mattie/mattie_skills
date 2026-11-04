import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

import { normalizeTile, positiveInteger, previewSizes, validatePreview } from './process-sheet.mjs';

const finalizer = fileURLToPath(new URL('./finalize-winner.mjs', import.meta.url));
const processor = fileURLToPath(new URL('./process-sheet.mjs', import.meta.url));
const paddingChecker = fileURLToPath(new URL('./check-sheet-padding.mjs', import.meta.url));
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');

function checkPadding(source) {
  return spawnSync(process.execPath, [
    paddingChecker, '--input', source, '--deps-root', path.dirname(processor),
  ], { encoding: 'utf8' });
}

test('padding checker detects occupied edges with the same speck tolerance', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-padding-'));
  try {
    const pixels = Buffer.alloc(120 * 80 * 3, 255);
    for (let x = 0; x < 26; x += 1) pixels.fill(0, x * 3, x * 3 + 3);
    for (let x = 40; x < 65; x += 1) pixels.fill(0, x * 3, x * 3 + 3);
    const source = path.join(root, 'sheet.png');
    await sharp(pixels, { raw: { width: 120, height: 80, channels: 3 } }).png().toFile(source);
    const result = checkPadding(source);
    assert.equal(result.status, 1);
    const inspection = JSON.parse(result.stdout);
    assert.equal(inspection.accepted, false);
    assert.deepEqual(inspection.findings.map(({ cell, foreground }) => [cell, foreground]), [[1, 26]]);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('padding checker composites transparency, handles grayscale, and rejects malformed grids', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-padding-formats-'));
  try {
    const transparent = path.join(root, 'transparent.png');
    await sharp(Buffer.alloc(120 * 80 * 4), {
      raw: { width: 120, height: 80, channels: 4 },
    }).png().toFile(transparent);
    assert.equal(JSON.parse(checkPadding(transparent).stdout).accepted, true);

    const grayscale = path.join(root, 'grayscale.png');
    await sharp(Buffer.alloc(120 * 80, 255), {
      raw: { width: 120, height: 80, channels: 1 },
    }).png().toFile(grayscale);
    assert.equal(JSON.parse(checkPadding(grayscale).stdout).accepted, true);

    const malformed = path.join(root, 'malformed.png');
    await sharp({ create: { width: 120, height: 81, channels: 3, background: '#fff' } })
      .png().toFile(malformed);
    const result = checkPadding(malformed);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /3-by-2 grid of equal square cells/);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('integer and preview-size parsing rejects partial tokens and keeps judging sizes', () => {
  for (const value of ['1.5', '48px', '0', '-1']) {
    assert.throws(() => positiveInteger(value, null, '--size'), /positive integer/);
  }
  assert.deepEqual(previewSizes(undefined), [192, 48]);
  assert.deepEqual(previewSizes('64'), [192, 48, 64]);
  assert.deepEqual(previewSizes('48,64'), [192, 48, 64]);
  assert.throws(() => previewSizes('64,64'), /duplicates/);
});

test('tile normalization converts grayscale input to three-channel palette output', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-gray-'));
  try {
    const source = path.join(root, 'gray.png');
    await sharp(Buffer.from([0, 85, 170, 255]), {
      raw: { width: 2, height: 2, channels: 1 },
    }).png().toFile(source);
    const normalized = await normalizeTile(sharp, source, { left: 0, top: 0, width: 2, height: 2 });
    const metadata = await sharp(normalized.png).metadata();
    assert.equal(metadata.channels, 3);
    assert.equal(Object.values(normalized.counts).reduce((sum, count) => sum + count, 0), 4);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('preview validation accepts pixel-aligned art without partially transparent pixels', async () => {
  const png = await sharp(Buffer.from([
    44, 44, 43, 255, 0, 0, 0, 0,
    44, 44, 43, 255, 0, 0, 0, 0,
  ]), {
    raw: { width: 2, height: 2, channels: 4 },
  }).png().toBuffer();

  const validation = await validatePreview(sharp, png, 2);
  assert.equal(validation.partial, 0);
  assert.equal(validation.transparent, 2);
  assert.equal(validation.opaque, 2);
});

test('tile normalization does not invent coral from neutral antialias pixels', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-neutral-'));
  try {
    const source = path.join(root, 'antialias.png');
    await sharp(Buffer.from([
      150, 150, 149,
      247, 124, 106,
    ]), {
      raw: { width: 2, height: 1, channels: 3 },
    }).png().toFile(source);
    const normalized = await normalizeTile(sharp, source, { left: 0, top: 0, width: 2, height: 1 });
    assert.equal(normalized.counts['#FFFFFF'], 1);
    assert.equal(normalized.counts['#2C2C2B'], 0);
    assert.equal(normalized.counts['#F45138'], 1);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('normalization centers noticeably displaced art without moving small offsets', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-center-'));
  try {
    for (const [left, top, expectedLeft, expectedTop, shiftX, shiftY] of [
      [70, 40, 40, 40, -30, 0], [44, 40, 44, 40, 0, 0], [40, 10, 40, 40, 0, 30],
    ]) {
      const pixels = Buffer.alloc(100 * 100 * 3, 255);
      for (let y = top; y < top + 20; y += 1) {
        for (let x = left; x < left + 20; x += 1) {
          const i = (y * 100 + x) * 3;
          const rgb = x < left + 10 ? [44, 44, 43] : [244, 81, 56];
          [pixels[i], pixels[i + 1], pixels[i + 2]] = rgb;
        }
      }
      const source = path.join(root, `tile-${left}-${top}.png`);
      await sharp(pixels, { raw: { width: 100, height: 100, channels: 3 } }).png().toFile(source);
      const tile = await normalizeTile(sharp, source, { left: 0, top: 0, width: 100, height: 100 });
      const rendered = await sharp(tile.png).raw().toBuffer();
      assert.deepEqual(tile.centerShift, { x: shiftX, y: shiftY });
      assert.equal(tile.counts['#2C2C2B'], 200);
      assert.equal(tile.counts['#F45138'], 200);
      assert.equal(rendered[(expectedTop * 100 + expectedLeft) * 3], 44);
      assert.equal(rendered[(expectedTop * 100 + expectedLeft + 10) * 3], 244);
      assert.equal(rendered[(expectedTop * 100 + expectedLeft - 1) * 3], 255);
    }
    const white = path.join(root, 'white.png');
    await sharp({ create: { width: 100, height: 100, channels: 3, background: '#fff' } }).png().toFile(white);
    const blank = await normalizeTile(sharp, white, { left: 0, top: 0, width: 100, height: 100 });
    assert.deepEqual(blank.centerShift, { x: 0, y: 0 });

    // A 5.5-pixel offset is outside the 5-pixel tolerance even though the
    // integer shift rounds to five pixels.
    const pixels = Buffer.alloc(100 * 100 * 3, 255);
    for (let y = 40; y < 60; y += 1) {
      for (let x = 46; x < 65; x += 1) pixels.fill(0, (y * 100 + x) * 3, (y * 100 + x + 1) * 3);
    }
    const edge = path.join(root, 'edge.png');
    await sharp(pixels, { raw: { width: 100, height: 100, channels: 3 } }).png().toFile(edge);
    const adjusted = await normalizeTile(sharp, edge, { left: 0, top: 0, width: 100, height: 100 });
    assert.deepEqual(adjusted.centerShift, { x: -5, y: 0 });
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('compilation failure leaves its output directory empty for retry', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-compile-'));
  const source = path.join(root, 'invalid-sheet.png');
  const output = path.join(root, 'output');
  try {
    await sharp({
      create: { width: 10, height: 10, channels: 3, background: '#FFFFFF' },
    }).png().toFile(source);
    const result = spawnSync(process.execPath, [
      processor,
      '--input', source,
      '--output', output,
      '--deps-root', path.dirname(processor),
    ], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /do not divide/);
    assert.deepEqual(await fs.readdir(output), []);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

async function createRun(root, { alteredSvg = false, lateConflict = false } = {}) {
  const svg = Buffer.from('<svg><path fill="#2C2C2B"/></svg>');
  const preview192 = Buffer.from('preview-192');
  const preview48 = Buffer.from('preview-48');
  await fs.mkdir(path.join(root, 'svg'), { recursive: true });
  await fs.mkdir(path.join(root, 'previews', '192'), { recursive: true });
  await fs.mkdir(path.join(root, 'previews', '48'), { recursive: true });
  await fs.writeFile(path.join(root, 'svg', 'c1.svg'), alteredSvg ? Buffer.from('changed') : svg);
  await fs.writeFile(path.join(root, 'previews', '192', 'c1.png'), preview192);
  await fs.writeFile(path.join(root, 'previews', '48', 'c1.png'), preview48);
  await fs.writeFile(path.join(root, 'validation.json'), JSON.stringify({
    previewSizes: [192, 48],
    candidates: { c1: {
      svg: { sha256: sha256(svg) },
      previews: {
        192: { sha256: sha256(preview192) },
        48: { sha256: sha256(preview48) },
      },
    } },
  }));
  if (lateConflict) await fs.writeFile(path.join(root, 'article-48.png'), 'existing');
}

function finalize(root) {
  return spawnSync(process.execPath, [finalizer, '--run', root, '--candidate', 'c1', '--slug', 'article'], {
    encoding: 'utf8',
  });
}

test('finalization copies the selected files without requiring matching recorded hashes', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-finalize-'));
  try {
    await createRun(root, { alteredSvg: true });
    const result = finalize(root);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(await fs.readFile(path.join(root, 'article.svg'), 'utf8'), 'changed');
    assert.equal(JSON.parse(await fs.readFile(path.join(root, 'selection.json'), 'utf8')).candidate, 'c1');
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('finalization preserves existing output and reports how to retry', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-preflight-'));
  try {
    await createRun(root, { lateConflict: true });
    const result = finalize(root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /retry in a fresh run directory/);
    assert.equal(await fs.readFile(path.join(root, 'article-48.png'), 'utf8'), 'existing');
    await assert.rejects(fs.access(path.join(root, 'selection.json')));
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});
