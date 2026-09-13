/** Bounded adapters for public catalog metadata; none contacts a listed service. */
import { readCatalog, resourceObservation, mcpObservation, isObject } from './discovery-core.mjs';

function queryState(query, searchMethod) {
  return { query, searchMethod, pages: 0, scanned: 0, returned: 0, skipped: 0, truncated: false, errors: [] };
}

function finish(catalog, retrievedAt, queries, observations) {
  const hasErrors = queries.some(query => query.errors.length);
  const incomplete = queries.some(query => query.truncated || query.skipped);
  const pages = queries.reduce((sum, query) => sum + query.pages, 0);
  return {
    catalog, retrievedAt,
    status: hasErrors && !pages ? 'unavailable' : (hasErrors || incomplete ? 'partial' : 'ok'),
    queries, observations,
  };
}

/** Coinbase returns at most 20 resources and advertises partial results without a cursor. */
export async function coinbase(options, context) {
  const retrievedAt = new Date().toISOString();
  const queries = [], observations = [];
  for (const query of options.queries) {
    const state = queryState(query, 'capability-query');
    const selected = new Set();
    queries.push(state);
    try {
      const payload = await readCatalog('coinbase', { query, limit: options.limit }, context);
      if (!Array.isArray(payload.resources) || typeof payload.partialResults !== 'boolean') throw new Error('Invalid Coinbase resources/partialResults');
      state.pages = 1;
      state.scanned = payload.resources.length;
      state.searchMethod = typeof payload.searchMethod === 'string' ? payload.searchMethod : state.searchMethod;
      state.truncated = payload.partialResults || payload.resources.length > options.limit;
      for (const resource of payload.resources) {
        const observation = resourceObservation('coinbase', resource, retrievedAt);
        if (!observation) { state.skipped++; continue; }
        if (selected.has(observation.identity) || selected.size < options.limit) {
          observations.push({ ...observation, query });
          selected.add(observation.identity);
          state.returned = selected.size;
        }
      }
    } catch (error) { state.errors.push(error.message); }
  }
  return finish('coinbase', retrievedAt, queries, observations);
}

/** Retrieve one bounded PayAI inventory for all queries, then match every query token. */
export async function payai(options, context) {
  const retrievedAt = new Date().toISOString();
  const scan = queryState(null, 'local-keywords-in-paginated-inventory');
  const inventory = new Map();
  let offset = 0;
  try {
    for (let page = 0; page < options.maxPages; page++) {
      const payload = await readCatalog('payai', { type: 'http', limit: 100, offset }, context);
      if (!Array.isArray(payload.items) || !isObject(payload.pagination) ||
          !Number.isInteger(payload.pagination.total) || payload.pagination.total < 0) throw new Error('Invalid PayAI items/pagination');
      scan.pages++;
      scan.scanned += payload.items.length;
      scan.total = payload.pagination.total;
      for (const item of payload.items) {
        const observation = resourceObservation('payai', item, retrievedAt);
        if (!observation) { scan.skipped++; continue; }
        // Keep different observations of the same resource if terms change between pages.
        inventory.set(JSON.stringify(observation), observation);
      }
      offset += payload.items.length;
      scan.truncated = offset < scan.total;
      if (!scan.truncated) break;
      if (!payload.items.length) throw new Error('PayAI pagination made no progress');
    }
  } catch (error) { scan.errors.push(error.message); scan.truncated = true; }
  const observations = [];
  const queries = options.queries.map(query => {
    const tokens = query.toLocaleLowerCase('en-US').split(/\s+/u).filter(Boolean);
    const matches = [...inventory.values()].filter(item => {
      const text = [item.name, item.description, item.endpoint, ...(Array.isArray(item.tags) ? item.tags : [])].join(' ').toLocaleLowerCase('en-US');
      return tokens.every(token => text.includes(token));
    });
    // Apply the result limit to identities, keeping conflicting terms for selected identities.
    const identities = [...new Set(matches.map(item => item.identity))];
    const selected = new Set(identities.slice(0, options.limit));
    for (const item of matches) if (selected.has(item.identity)) observations.push({ ...item, query });
    return { ...scan, query, errors: [...scan.errors], returned: selected.size,
      truncated: scan.truncated || identities.length > options.limit };
  });
  const result = finish('payai', retrievedAt, queries, observations);
  result.inventory = { pages: scan.pages, scanned: scan.scanned, total: scan.total ?? null };
  return result;
}

/** MCP search matches server names, not tool capabilities. Preserve that coverage distinction. */
export async function mcp(options, context) {
  const retrievedAt = new Date().toISOString();
  const queries = [], observations = [];
  for (const query of options.queries) {
    const state = queryState(query, 'server-name-substring');
    const selected = new Set();
    queries.push(state);
    let cursor;
    const seenCursors = new Set();
    try {
      for (let page = 0; page < options.maxPages; page++) {
        const payload = await readCatalog('mcp', { search: query, version: 'latest', limit: options.limit - state.returned,
          ...(cursor ? { cursor } : {}) }, context);
        if (!Array.isArray(payload.servers) ||
            (payload.metadata !== undefined && !isObject(payload.metadata))) throw new Error('Invalid MCP servers/metadata');
        state.pages++;
        state.scanned += payload.servers.length;
        for (const entry of payload.servers) {
          const item = mcpObservation(entry, retrievedAt);
          if (!item) { state.skipped++; continue; }
          if (selected.has(item.identity) || selected.size < options.limit) {
            observations.push({ ...item, query });
            selected.add(item.identity);
            state.returned = selected.size;
          }
          else state.truncated = true;
        }
        cursor = payload.metadata?.nextCursor;
        if (cursor !== undefined && cursor !== null && typeof cursor !== 'string') throw new Error('Invalid MCP cursor');
        state.truncated ||= Boolean(cursor);
        if (!cursor) break;
        if (state.returned >= options.limit) break;
        if (seenCursors.has(cursor)) throw new Error('Repeated MCP cursor');
        seenCursors.add(cursor);
        // A cursor may be exhausted on the next page; only the last page determines truncation.
        state.truncated = page + 1 >= options.maxPages;
      }
    } catch (error) {
      state.errors.push(error.message);
      state.truncated ||= Boolean(cursor);
    }
  }
  return finish('mcp', retrievedAt, queries, observations);
}
