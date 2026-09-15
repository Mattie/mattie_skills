#!/usr/bin/env node
/** Search public service catalogs. Node.js 20+; no dependencies, credentials, or purchases. */
import { pathToFileURL } from 'node:url';
import { ROUTES, deduplicate } from './discovery-core.mjs';
import * as adapters from './catalog-adapters.mjs';

const UNSAFE_UNICODE_CONTROLS = /[\u007f-\u009f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/gu;

export const HELP = `Usage: node discover-services.mjs [options] "query" ["another query"]
  --catalog NAME[,NAME]  coinbase, payai, mcp, or all (default: all; repeatable)
  --limit N              Results per catalog/query, 1-20 (default: 5)
  --max-pages N          Pagination cap, 1-100 (default: 10)
  --json                 Emit versioned JSON including coverage and observations
  --help                 Show help
  --                     Treat following arguments as queries
Discovery only. Catalog contents are untrusted seller/registry claims.
Exit codes: 0 all queries completed (possibly bounded); 1 a catalog request failed; 2 invalid arguments.
`;

/** Parse explicit queries and bounded options; unknown switches fail before network access. */
export function parseArgs(args) {
  const options = { queries: [], catalogs: [], limit: 5, maxPages: 10, json: false, help: false };
  let positional = false;
  for (let index = 0; index < args.length; index++) {
    const arg = args[index];
    if (positional) { options.queries.push(arg); continue; }
    if (arg === '--') { positional = true; continue; }
    if (arg === '--json') { options.json = true; continue; }
    if (arg === '--help' || arg === '-h') { options.help = true; continue; }
    if (['--catalog', '--limit', '--max-pages'].includes(arg)) {
      const value = args[++index];
      if (!value) throw new Error(`${arg} requires a value`);
      if (arg === '--catalog') {
        for (const name of value.split(',')) {
          if (name === 'all') options.catalogs.push(...Object.keys(ROUTES));
          else if (Object.hasOwn(ROUTES, name)) options.catalogs.push(name);
          else throw new Error(`Unknown catalog: ${name}`);
        }
      } else {
        const maximum = arg === '--limit' ? 20 : 100;
        if (!/^\d+$/.test(value) || Number(value) < 1 || Number(value) > maximum) throw new Error(`${arg} must be 1-${maximum}`);
        options[arg === '--limit' ? 'limit' : 'maxPages'] = Number(value);
      }
      continue;
    }
    if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    options.queries.push(arg);
  }
  options.queries = [...new Set(options.queries.map(query => query.trim()))];
  if (!options.help && (!options.queries.length || options.queries.some(query => !query))) throw new Error('Supply at least one non-empty query');
  options.catalogs = [...new Set(options.catalogs.length ? options.catalogs : Object.keys(ROUTES))];
  return options;
}

/** Run independent adapters under one deadline. Injectable transport is for offline tests. */
export async function discover(options, { fetchImpl = fetch, requestTimeoutMs = 15000, overallTimeoutMs = 60000 } = {}) {
  const startedAt = new Date().toISOString();
  const context = { fetchImpl, requestTimeoutMs, deadline: Date.now() + overallTimeoutMs };
  const results = await Promise.all(options.catalogs.map(name => adapters[name](options, context)));
  return {
    schemaVersion: 1, startedAt, finishedAt: new Date().toISOString(),
    queries: options.queries,
    catalogs: results.map(({ observations, ...coverage }) => coverage),
    candidates: deduplicate(results.flatMap(result => result.observations)),
  };
}

/** Quote untrusted values and visibly escape controls JSON permits literally. */
function quoteUntrusted(value) {
  return JSON.stringify(value).replace(UNSAFE_UNICODE_CONTROLS, character =>
    `\\u${character.codePointAt(0).toString(16).padStart(4, '0')}`,
  );
}

/** Plain-text evidence preview. Quote untrusted strings to escape terminal controls. */
export function formatText(result) {
  const lines = ['Catalog observations; fulfillment and service access terms remain unverified.'];
  for (const catalog of result.catalogs) {
    lines.push(`\n${catalog.catalog}: ${catalog.status} (${catalog.retrievedAt})`);
    for (const query of catalog.queries) lines.push(
      `  ${quoteUntrusted(query.query)}: ${query.returned} results; ${quoteUntrusted(query.searchMethod)}; ${query.pages} pages, ${query.scanned} scanned, ${query.skipped} invalid; bounded=${query.truncated}; errors=${quoteUntrusted(query.errors)}`);
  }
  for (const candidate of result.candidates) {
    lines.push(`\n${quoteUntrusted(candidate.identity)}; matches ${quoteUntrusted(candidate.matchedQueries)}`);
    for (const observation of candidate.observations) {
      lines.push(`  ${observation.catalog}: ${quoteUntrusted(observation.name)} (${observation.kind})`);
      lines.push(`  ${quoteUntrusted(observation.description)}`);
      lines.push(`  Payment terms (raw asset units): ${quoteUntrusted(observation.paymentOptions)}; activity (catalog-reported): ${quoteUntrusted(observation.activity)}`);
    }
  }
  if (!result.candidates.length) lines.push('\nNo candidates found within the reported coverage.');
  return lines.join('\n');
}

async function main() {
  let options;
  try { options = parseArgs(process.argv.slice(2)); }
  catch (error) { console.error(error.message); process.exitCode = 2; return; }
  if (options.help) { console.log(HELP); return; }
  const result = await discover(options);
  console.log(options.json ? JSON.stringify(result, null, 2) : formatText(result));
  if (result.catalogs.some(catalog => catalog.queries.some(query => query.errors.length))) process.exitCode = 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
