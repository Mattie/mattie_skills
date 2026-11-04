#!/usr/bin/env node

/** Check the same per-tile safety band used by the Aiconographer API edition. */

import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);

function usage() {
  console.log(`Usage: node check-sheet-padding.mjs --input <sheet.png> --deps-root <directory>

Checks each cell in a 3-by-2 sheet for foreground pixels inside a four-percent safety band.
Prints a JSON inspection object and exits 1 when the sheet is rejected.`);
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      args.help = true;
      continue;
    }
    if (token === "--input" || token === "--deps-root") {
      const value = argv[index + 1];
      if (!value) throw new Error(`${token} requires a value.`);
      args[token.slice(2)] = value;
      index += 1;
      continue;
    }
    throw new Error(`Unknown argument: ${token}`);
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  usage();
  process.exit(0);
}
if (!args.input || !args["deps-root"]) {
  usage();
  throw new Error("--input and --deps-root are required.");
}

const sharp = require(path.resolve(args["deps-root"], "node_modules", "sharp"));
const { data, info } = await sharp(path.resolve(args.input))
  .flatten({ background: "#FFFFFF" })
  .removeAlpha()
  .toColourspace("srgb")
  .raw()
  .toBuffer({ resolveWithObject: true });

if (info.width % 3 !== 0 || info.height % 2 !== 0 || info.width / 3 !== info.height / 2) {
  throw new Error("Sheet must divide into a 3-by-2 grid of equal square cells.");
}

const findings = [];
for (let row = 0; row < 2; row += 1) {
  for (let col = 0; col < 3; col += 1) {
    const x0 = Math.floor((info.width * col) / 3);
    const x1 = Math.floor((info.width * (col + 1)) / 3);
    const y0 = Math.floor((info.height * row) / 2);
    const y1 = Math.floor((info.height * (row + 1)) / 2);
    const margin = Math.max(2, Math.floor(Math.min(x1 - x0, y1 - y0) * 0.04));
    let foreground = 0;

    for (let y = y0; y < y1; y += 1) {
      for (let x = x0; x < x1; x += 1) {
        const insideSafeArea =
          x >= x0 + margin && x < x1 - margin && y >= y0 + margin && y < y1 - margin;
        if (insideSafeArea) continue;
        const offset = (y * info.width + x) * info.channels;
        if (Math.min(data[offset], data[offset + 1], data[offset + 2]) < 210) {
          foreground += 1;
        }
      }
    }

    // Ignore isolated antialiased specks while rejecting shapes that enter the safety band.
    if (foreground > 25) {
      findings.push({ cell: row * 3 + col + 1, foreground, margin });
    }
  }
}

const issues = findings.map(
  (finding) =>
    `Cell ${finding.cell} enters its ${finding.margin}px safety margin ` +
    `(${finding.foreground} foreground pixels).`,
);
console.log(JSON.stringify({ accepted: findings.length === 0, issues, findings }, null, 2));
if (findings.length > 0) process.exitCode = 1;
