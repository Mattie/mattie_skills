import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../../skills/thought-rig/', import.meta.url));
function files(dir) {
  return fs.readdirSync(dir,{withFileTypes:true}).flatMap(entry => {
    const filename = path.join(dir,entry.name);
    return entry.isDirectory() ? files(filename) : [filename];
  });
}

test('distributed toolkit excludes private project evidence and machine paths', () => {
  for (const filename of files(root)) {
    assert.doesNotMatch(filename,/manasplash|workspace\.json|preview-.*\.png/i);
    const body = fs.readFileSync(filename,'utf8');
    assert.doesNotMatch(body,/manasplash|[CD]:[\\/]Users[\\/]matti|D:[\\/]Dev[\\/]/i,filename);
  }
});

test('skill markdown links resolve within the packaged skill', () => {
  for (const filename of files(root).filter(file=>file.endsWith('.md'))) {
    for (const match of fs.readFileSync(filename,'utf8').matchAll(/\]\(([^)]+)\)/g)) {
      const target=match[1].split('#')[0];
      if (!target || /^(?:https?:|mailto:)/.test(target)) continue;
      assert.ok(fs.existsSync(path.resolve(path.dirname(filename),target)),`${filename}: ${target}`);
    }
  }
});
