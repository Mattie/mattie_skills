#!/usr/bin/env node

/**
 * Copy one validated Aiconographer candidate to stable slug-based canonical
 * filenames while preserving the complete candidate run.
 */

import crypto from 'node:crypto';
import { constants } from 'node:fs';
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

const HELP = `
Usage:
  node finalize-winner.mjs --run <run-directory> --candidate <c1..c6> --slug <article-slug>

The command refuses to overwrite canonical files or an existing selection.json.
`;

/** Parse simple `--name value` arguments. */
function parseArgs(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--help') {
      parsed.help = true;
      continue;
    }
    if (!token.startsWith('--')) throw new Error(`Unexpected argument: ${token}`);
    const value = argv[index + 1];
    if (value === undefined || value.startsWith('--')) {
      throw new Error(`Missing value for ${token}`);
    }
    parsed[token.slice(2)] = value;
    index += 1;
  }
  return parsed;
}

/** Return a required trimmed argument. */
function required(args, name) {
  const value = args[name]?.trim();
  if (!value) throw new Error(`--${name} is required.`);
  return value;
}

/** Return a lowercase SHA-256 checksum for a file. */
async function fileSha256(filePath, fsApi = fs) {
  const data = await fsApi.readFile(filePath);
  return crypto.createHash('sha256').update(data).digest('hex');
}

/** Copy a validated file exclusively and remove it if the copied bytes changed. */
export async function copyExclusive(fsApi, source, destination, expectedSha256) {
  await fsApi.copyFile(source, destination, constants.COPYFILE_EXCL);
  try {
    const copied = {
      path: destination,
      bytes: (await fsApi.stat(destination)).size,
      sha256: await fileSha256(destination, fsApi),
    };
    if (expectedSha256 !== undefined && copied.sha256 !== expectedSha256) {
      throw new Error(`Validated source changed while copying: ${source}`);
    }
    return copied;
  } catch (error) {
    await fsApi.unlink(destination).catch(() => {});
    throw error;
  }
}

/** Refuse an existing destination before any canonical copy begins. */
async function requireAbsent(destination) {
  try {
    await fs.access(destination);
    throw new Error(`Destination already exists: ${destination}`);
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
}

/** Verify that a candidate file still matches the compiler's validation record. */
async function verifySource(source, expectedSha256) {
  await fs.access(source, constants.R_OK);
  if (typeof expectedSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(expectedSha256)) {
    throw new Error(`Validation record has no usable SHA-256 for ${source}.`);
  }
  const actualSha256 = await fileSha256(source);
  if (actualSha256 !== expectedSha256) {
    throw new Error(`Validated source changed: ${source}`);
  }
}

/** Write selection metadata exclusively and remove a partial file after write failure. */
export async function writeSelectionExclusive(fsApi, selectionPath, contents) {
  try {
    await fsApi.writeFile(selectionPath, contents, { encoding: 'utf8', flag: 'wx' });
  } catch (error) {
    if (error?.code !== 'EEXIST') await fsApi.unlink(selectionPath).catch(() => {});
    throw error;
  }
}

/** Finalize the selected candidate and write auditable selection metadata. */
async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(HELP);
    return;
  }

  const runRoot = path.resolve(required(args, 'run'));
  const candidate = required(args, 'candidate').toLowerCase();
  const slug = required(args, 'slug').toLowerCase();
  if (!/^c[1-6]$/.test(candidate)) {
    throw new Error('--candidate must be c1, c2, c3, c4, c5, or c6.');
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    throw new Error('--slug must contain lowercase letters, digits, and single hyphens.');
  }

  const validationPath = path.join(runRoot, 'validation.json');
  const validation = JSON.parse(await fs.readFile(validationPath, 'utf8'));
  const candidateValidation = validation.candidates?.[candidate];
  if (!candidateValidation) {
    throw new Error(`${candidate} is missing from validation.json.`);
  }

  const selectionPath = path.join(runRoot, 'selection.json');
  const svgSource = path.join(runRoot, 'svg', `${candidate}.svg`);
  const svgDestination = path.join(runRoot, `${slug}.svg`);
  const previewSizes = validation.previewSizes ?? Object.keys(candidateValidation.previews ?? {});
  const transfers = [{
    kind: 'svg', source: svgSource, destination: svgDestination,
    expectedSha256: candidateValidation.svg?.sha256,
  }];
  for (const size of previewSizes) {
    transfers.push({
      kind: 'preview', size: String(size),
      source: path.join(runRoot, 'previews', String(size), `${candidate}.png`),
      destination: path.join(runRoot, `${slug}-${size}.png`),
      expectedSha256: candidateValidation.previews?.[String(size)]?.sha256,
    });
  }

  await requireAbsent(selectionPath);
  for (const transfer of transfers) {
    await verifySource(transfer.source, transfer.expectedSha256);
    await requireAbsent(transfer.destination);
  }

  const canonical = { svg: null, previews: {} };
  const created = [];
  try {
    for (const transfer of transfers) {
      const copied = await copyExclusive(
        fs,
        transfer.source,
        transfer.destination,
        transfer.expectedSha256,
      );
      created.push(transfer.destination);
      if (transfer.kind === 'svg') canonical.svg = copied;
      else canonical.previews[transfer.size] = copied;
    }

    const selection = { candidate, slug, canonical, candidateValidation };
    await writeSelectionExclusive(fs, selectionPath, `${JSON.stringify(selection, null, 2)}\n`);
  } catch (error) {
    await Promise.allSettled(created.reverse().map((destination) => fs.unlink(destination)));
    throw error;
  }

  process.stdout.write(
    `${JSON.stringify({ ok: true, candidate, slug, selectionPath, canonical }, null, 2)}\n`,
  );
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    process.stderr.write(`aiconographer: ${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
