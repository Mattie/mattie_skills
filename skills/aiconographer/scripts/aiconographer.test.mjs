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
import { writeSelectionExclusive } from './finalize-winner.mjs';

const finalizer = fileURLToPath(new URL('./finalize-winner.mjs', import.meta.url));
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');

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

test('selection write failure removes a partially created selection file', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-selection-'));
  const selectionPath = path.join(root, 'selection.json');
  const failingFs = {
    writeFile: async (destination, contents, options) => {
      await fs.writeFile(destination, contents.slice(0, 8), options);
      const error = new Error('simulated disk full');
      error.code = 'ENOSPC';
      throw error;
    },
    unlink: fs.unlink.bind(fs),
  };
  try {
    await assert.rejects(
      writeSelectionExclusive(failingFs, selectionPath, '{"candidate":"c1"}\n'),
      /simulated disk full/,
    );
    await assert.rejects(fs.access(selectionPath));
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

test('finalization verifies hashes before creating canonical files', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-hash-'));
  try {
    await createRun(root, { alteredSvg: true });
    const result = finalize(root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Validated source changed/);
    await assert.rejects(fs.access(path.join(root, 'article.svg')));
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});

test('finalization preflights every destination before the first copy', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'aiconographer-preflight-'));
  try {
    await createRun(root, { lateConflict: true });
    const result = finalize(root);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Destination already exists/);
    await assert.rejects(fs.access(path.join(root, 'article.svg')));
    await assert.rejects(fs.access(path.join(root, 'article-192.png')));
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
});
