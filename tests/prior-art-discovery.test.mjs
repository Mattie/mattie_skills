/** Offline behavioral checks for public discovery and its network boundary. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = process.env.PRIOR_ART_SKILL_ROOT ?? resolve('skills/prior-art');
const { discover, parseArgs, formatText } = await import(pathToFileURL(resolve(root, 'scripts/discover-services.mjs')));
const fixture = JSON.parse(readFileSync(new URL('./fixtures/prior-art/catalogs.json', import.meta.url), 'utf8'));
const response = payload => new Response(JSON.stringify(payload), { headers: { 'content-type': 'application/json' } });
const routes = {
  'https://api.cdp.coinbase.com/platform/v2/x402/discovery/search': 'coinbase',
  'https://facilitator.payai.network/discovery/resources': 'payai',
  'https://registry.modelcontextprotocol.io/v0.1/servers': 'mcp',
};

function transport(handler = name => response(fixture[name])) {
  const calls = [];
  return { calls, fetchImpl: async (url, init) => {
    const name = routes[`${url.origin}${url.pathname}`];
    assert.ok(name, `Unexpected network route: ${url}`);
    assert.equal(init.method, 'GET');
    assert.equal(init.redirect, 'error');
    assert.equal(init.credentials, 'omit');
    assert.deepEqual(init.headers, { accept: 'application/json' });
    assert.ok(init.signal instanceof AbortSignal);
    calls.push({ name, url });
    return handler(name, url, init);
  } };
}

test('CLI requires explicit queries and rejects invalid options before discovery', () => {
  for (const args of [[], [''], ['--limit', '21', 'x'], ['--limit', '0', 'x'], ['--max-pages', '101', 'x'], ['--catalog', 'constructor', 'x'], ['--wallet', 'x']]) {
    assert.throws(() => parseArgs(args));
  }
  assert.equal(parseArgs(['--help']).help, true);
  assert.deepEqual(parseArgs(['--catalog', 'mcp', '--catalog', 'coinbase,mcp', '--', '-query']).catalogs, ['mcp', 'coinbase']);
  assert.deepEqual(parseArgs(['ocr']).catalogs, ['coinbase', 'payai', 'mcp']);
  assert.throws(() => parseArgs(Array.from({ length: 21 }, (_, index) => `query-${index}`)), /at most 20/);
});

test('three catalogs retain claims, unknowns, conflicts, and package identities without invoking listings', async () => {
  const mock = transport();
  const result = await discover(parseArgs(['ocr']), mock);
  assert.equal(mock.calls.length, 3);
  assert.equal(result.schemaVersion, 1);
  const shared = result.candidates.find(candidate => candidate.identity === 'resource:https://seller.example/ocr');
  assert.equal(shared.observations.length, 2);
  assert.deepEqual(shared.observations[0].paymentOptions, fixture.coinbase.resources[0].accepts);
  assert.equal(shared.observations[1].paymentOptions[0].amount, '999');
  assert.equal(shared.observations[0].activity, null);
  assert.equal(shared.observations[0].schema.type, 'object');
  assert.ok(result.candidates.some(candidate => candidate.identity === 'resource:https://different.example/ocr'));
  assert.equal(result.candidates.find(candidate => candidate.identity === 'mcp:example/ocr@1.0.0').observations[0].kind, 'remote-and-package');
  assert.equal(result.candidates.find(candidate => candidate.identity === 'mcp:example/ocr-local@2.0.0').observations[0].kind, 'package');
  assert.equal(result.catalogs[0].queries[0].truncated, true);
  assert.equal(result.catalogs[2].queries[0].searchMethod, 'server-name-substring');
  assert.ok(mock.calls.find(call => call.name === 'mcp').url.searchParams.get('version') === 'latest');
  assert.ok(!formatText(result).includes('$0.01'));
  assert.ok(!JSON.stringify(result).includes('evidenceScore'));
});

test('PayAI inventory is fetched once and query matching requires all tokens', async () => {
  const mock = transport();
  const result = await discover(parseArgs(['--catalog', 'payai', 'OCR extraction', 'audio transcription', 'OCR transcription']), mock);
  assert.equal(mock.calls.length, 1);
  assert.deepEqual(result.catalogs[0].queries.map(query => query.returned), [2, 1, 0]);
  assert.equal(result.catalogs[0].inventory.scanned, 3);
});

test('PayAI bounded empty match never implies a complete inventory scan', async () => {
  const mock = transport(() => response({ items: fixture.payai.items, pagination: { total: 1000 } }));
  const result = await discover(parseArgs(['--catalog', 'payai', '--max-pages', '1', 'absent']), mock);
  assert.equal(result.catalogs[0].status, 'partial');
  assert.equal(result.catalogs[0].queries[0].truncated, true);
  assert.equal(result.catalogs[0].queries[0].returned, 0);
});

test('PayAI paginates with actual item count and preserves earlier pages on failure', async () => {
  const mock = transport((name, url) => url.searchParams.get('offset') === '0'
    ? response({ items: [fixture.payai.items[0]], pagination: { total: 2 } })
    : new Response('', { status: 503 }));
  const result = await discover(parseArgs(['--catalog', 'payai', 'ocr']), mock);
  assert.equal(mock.calls[1].url.searchParams.get('offset'), '1');
  assert.equal(result.candidates.length, 1);
  assert.equal(result.catalogs[0].status, 'partial');
  assert.match(result.catalogs[0].queries[0].errors[0], /503/);
});

test('MCP uses opaque cursors and clears truncation when all matching pages are consumed', async () => {
  const mock = transport((name, url) => response(url.searchParams.has('cursor')
    ? { servers: [fixture.mcp.servers[1]], metadata: {} }
    : { servers: [fixture.mcp.servers[0]], metadata: { nextCursor: 'opaque:/+&' } }));
  const result = await discover(parseArgs(['--catalog', 'mcp', 'ocr']), mock);
  assert.equal(mock.calls[1].url.searchParams.get('cursor'), 'opaque:/+&');
  assert.equal(result.catalogs[0].queries[0].pages, 2);
  assert.equal(result.catalogs[0].queries[0].truncated, false);
  assert.equal(result.catalogs[0].status, 'ok');
});

test('MCP accepts a single-page response without optional metadata', async () => {
  const mock = transport(() => response({ servers: [fixture.mcp.servers[0]] }));
  const result = await discover(parseArgs(['--catalog', 'mcp', 'ocr']), mock);
  assert.equal(mock.calls.length, 1);
  assert.equal(result.catalogs[0].queries[0].pages, 1);
  assert.equal(result.catalogs[0].queries[0].truncated, false);
  assert.equal(result.catalogs[0].status, 'ok');
});

test('MCP result/page limits and repeated cursors remain visible', async () => {
  for (const extra of [['--limit', '1'], ['--max-pages', '1'], []]) {
    const mock = transport(() => response({ servers: [fixture.mcp.servers[0]], metadata: { nextCursor: 'same' } }));
    const result = await discover(parseArgs(['--catalog', 'mcp', ...extra, 'ocr']), mock);
    assert.equal(result.catalogs[0].status, 'partial');
    assert.equal(result.catalogs[0].queries[0].truncated, true);
    assert.ok(mock.calls.length <= 2);
  }
});

test('authentication, payment and server errors are isolated with no retries', async () => {
  for (const status of [401, 403, 402, 429, 500]) {
    const mock = transport(name => name === 'coinbase' ? new Response('', { status }) : response(fixture[name]));
    const result = await discover(parseArgs(['ocr']), mock);
    assert.equal(mock.calls.length, 3);
    assert.equal(result.catalogs[0].status, 'unavailable');
    assert.ok(result.candidates.length > 0);
    assert.match(result.catalogs[0].queries[0].errors[0], new RegExp(String(status)));
  }
});

test('malformed responses and invalid records report coverage loss', async () => {
  for (const payload of [[], {}, { resources: [] }, { resources: 'bad', partialResults: false }]) {
    const mock = transport(() => response(payload));
    const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), mock);
    assert.equal(result.catalogs[0].status, 'unavailable');
  }
  const mock = transport(() => response({ resources: [null, { description: 'missing ID' }, fixture.coinbase.resources[0]], partialResults: false }));
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), mock);
  assert.equal(result.catalogs[0].queries[0].skipped, 2);
  assert.equal(result.catalogs[0].status, 'partial');
  assert.equal(result.candidates.length, 1);
});

test('invalid JSON and redirects fail without fallback routes', async () => {
  for (const handler of [() => new Response('<html>'), () => { throw new TypeError('fetch failed: redirect'); }]) {
    const mock = transport(handler);
    const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), mock);
    assert.equal(result.catalogs[0].status, 'unavailable');
    assert.equal(mock.calls.length, 1);
  }
});

test('timeout bounds hanging requests while preserving another catalog', async () => {
  const mock = transport(name => name === 'coinbase' ? new Promise(() => {}) : response(fixture[name]));
  const result = await discover(parseArgs(['ocr']), { ...mock, requestTimeoutMs: 20, overallTimeoutMs: 100 });
  assert.equal(result.catalogs[0].status, 'unavailable');
  assert.match(result.catalogs[0].queries[0].errors[0], /timed out/);
  assert.ok(result.candidates.length > 0);
});

test('overall deadline stops subsequent queries and body stalls are bounded', async () => {
  const mock = transport(() => new Response(new ReadableStream({ start() {} })));
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'one', 'two', 'three']), { ...mock, requestTimeoutMs: 100, overallTimeoutMs: 20 });
  assert.equal(mock.calls.length, 1);
  assert.ok(result.catalogs[0].queries.every(query => query.errors.length));
});

test('same source repeated across queries is deduplicated while matches survive', async () => {
  const mock = transport();
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr', 'extract']), mock);
  assert.equal(result.candidates.length, 1);
  assert.deepEqual(result.candidates[0].matchedQueries, ['ocr', 'extract']);
  assert.equal(result.candidates[0].observations.length, 1);
});

test('untrusted terminal control characters are quoted in text output', async () => {
  const payload = structuredClone(fixture.coinbase);
  payload.resources[0].description = '\u001b[2J';
  payload.searchMethod = '\u001b]0;untrusted\u0007';
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), transport(() => response(payload)));
  assert.ok(!formatText(result).includes('\u001b'));
});

test('plain-text output visibly escapes C1 and bidirectional controls', async () => {
  const payload = structuredClone(fixture.coinbase);
  payload.resources[0].description = 'safe\u009b[2J\u202eevil';
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), transport(() => response(payload)));
  const text = formatText(result);
  assert.ok(!text.includes('\u009b'));
  assert.ok(!text.includes('\u202e'));
  assert.match(text, /\\u009b\[2J\\u202e/);
});

test('blank MCP names and versions are skipped as invalid registry records', async () => {
  const invalid = structuredClone(fixture.mcp.servers[0]);
  invalid.server.name = '   ';
  const mock = transport(() => response({ servers: [invalid, fixture.mcp.servers[0]], metadata: {} }));
  const result = await discover(parseArgs(['--catalog', 'mcp', 'ocr']), mock);
  assert.equal(result.catalogs[0].queries[0].skipped, 1);
  assert.equal(result.catalogs[0].queries[0].returned, 1);
});

test('MCP pagination failures preserve incomplete coverage', async () => {
  const mock = transport((name, url) => {
    if (url.searchParams.has('cursor')) return new Response('', { status: 503 });
    return response({ servers: [fixture.mcp.servers[0]], metadata: { nextCursor: 'next' } });
  });
  const result = await discover(parseArgs(['--catalog', 'mcp', '--limit', '2', 'ocr']), mock);
  assert.equal(result.catalogs[0].status, 'partial');
  assert.equal(result.catalogs[0].queries[0].truncated, true);
  assert.match(result.catalogs[0].queries[0].errors[0], /503/);
});

test('duplicate MCP observations keep conflicting metadata without consuming candidate slots', async () => {
  const changed = structuredClone(fixture.mcp.servers[0]);
  changed.server.description = 'Changed description';
  const mock = transport((name, url) => response(url.searchParams.has('cursor')
    ? { servers: [changed, fixture.mcp.servers[1]], metadata: {} }
    : { servers: [fixture.mcp.servers[0]], metadata: { nextCursor: 'next' } }));
  const result = await discover(parseArgs(['--catalog', 'mcp', '--limit', '2', 'ocr']), mock);
  assert.equal(result.candidates.length, 2);
  assert.equal(result.candidates[0].observations.length, 2);
  assert.equal(result.catalogs[0].queries[0].returned, 2);
});

test('duplicate Coinbase identities count once while preserving observations', async () => {
  const changed = structuredClone(fixture.coinbase.resources[0]);
  changed.accepts[0].amount = '123';
  const mock = transport(() => response({ resources: [fixture.coinbase.resources[0], changed], partialResults: false }));
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), mock);
  assert.equal(result.candidates.length, 1);
  assert.equal(result.candidates[0].observations.length, 2);
  assert.equal(result.catalogs[0].queries[0].returned, 1);
});

test('PayAI exhausting the inventory clears bounded scan coverage and advances offsets', async () => {
  const mock = transport((name, url) => response({
    items: [fixture.payai.items[Number(url.searchParams.get('offset'))]], pagination: { total: 3 },
  }));
  const result = await discover(parseArgs(['--catalog', 'payai', 'ocr']), mock);
  assert.deepEqual(mock.calls.map(call => call.url.searchParams.get('offset')), ['0', '1', '2']);
  assert.equal(result.catalogs[0].queries[0].truncated, false);
  assert.equal(result.catalogs[0].status, 'ok');
});

test('oversized bodies and malformed pagination are reported without unbounded reads', async () => {
  const tooLarge = transport(() => new Response('x'.repeat(8 * 1024 * 1024 + 1)));
  const result = await discover(parseArgs(['--catalog', 'coinbase', 'ocr']), tooLarge);
  assert.match(result.catalogs[0].queries[0].errors[0], /8 MiB/);
  const noProgress = transport(() => response({ items: [], pagination: { total: 10 } }));
  const stalled = await discover(parseArgs(['--catalog', 'payai', 'ocr']), noProgress);
  assert.equal(noProgress.calls.length, 1);
  assert.match(stalled.catalogs[0].queries[0].errors[0], /no progress/);
});
