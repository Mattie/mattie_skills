/** Shared read-only transport and evidence normalization for service discovery. */
export const ROUTES = Object.freeze({
  coinbase: 'https://api.cdp.coinbase.com/platform/v2/x402/discovery/search',
  payai: 'https://facilitator.payai.network/discovery/resources',
  mcp: 'https://registry.modelcontextprotocol.io/v0.1/servers',
});

export const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const valueOrNull = value => value ?? null;

/** Fetch only a fixed discovery route. Enforce a deadline through body consumption. */
export async function readCatalog(catalog, params, context) {
  const url = new URL(ROUTES[catalog]);
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, String(value));
  const remaining = Math.min(context.requestTimeoutMs, context.deadline - Date.now());
  if (remaining <= 0) throw new Error('Overall discovery deadline reached');
  const controller = new AbortController();
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => {
      controller.abort();
      reject(new Error('Discovery request timed out'));
    }, remaining);
  });
  const request = (async () => {
    const response = await context.fetchImpl(url, {
      method: 'GET', redirect: 'error', credentials: 'omit',
      headers: { accept: 'application/json' }, signal: controller.signal,
    });
    if (!response.ok) {
      await response.body?.cancel();
      throw new Error(`Discovery HTTP ${response.status}`);
    }
    const reader = response.body?.getReader();
    if (!reader) throw new Error('Discovery response has no body');
    const cancelBody = () => { void reader.cancel().catch(() => {}); };
    controller.signal.addEventListener('abort', cancelBody, { once: true });
    const chunks = [];
    let bytes = 0;
    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        bytes += value.byteLength;
        if (bytes > 8 * 1024 * 1024) throw new Error('Discovery response exceeds 8 MiB');
        chunks.push(value);
      }
    } catch (error) {
      await reader.cancel().catch(() => {});
      throw error;
    } finally {
      controller.signal.removeEventListener('abort', cancelBody);
      reader.releaseLock();
    }
    const payload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!isObject(payload)) throw new Error('Invalid discovery response object');
    return payload;
  })();
  try {
    return await Promise.race([request, timeout]);
  } finally {
    clearTimeout(timer);
  }
}

/** Normalize one seller listing without interpreting prices or executing metadata. */
export function resourceObservation(catalog, resource, retrievedAt) {
  if (!isObject(resource) || typeof resource.resource !== 'string') return null;
  const resourceId = resource.resource.trim();
  if (!resourceId) return null;
  const bazaar = resource.extensions?.bazaar;
  return {
    identity: `resource:${resourceId}`,
    catalog, sourceId: resourceId, retrievedAt,
    name: resource.serviceName ?? resourceId,
    kind: 'service', endpoint: resourceId,
    description: resource.description ?? resource.metadata?.description ?? null,
    tags: resource.tags ?? null,
    input: resource.inputSchema ?? bazaar?.info?.input ?? null,
    output: resource.outputSchema ?? bazaar?.info?.output ?? null,
    schema: bazaar?.schema ?? null,
    method: resource.method ?? bazaar?.info?.input?.method ?? null,
    paymentOptions: Array.isArray(resource.accepts) ? resource.accepts : null,
    activity: isObject(resource.quality) ? resource.quality : null,
    updatedAt: valueOrNull(resource.lastUpdated),
    packages: null, remotes: null, version: null,
  };
}

/** Preserve registry package and remote identities; a registry listing is not fulfillment proof. */
export function mcpObservation(entry, retrievedAt) {
  const server = entry?.server;
  if (!isObject(server) || typeof server.name !== 'string' || typeof server.version !== 'string') return null;
  const name = server.name.trim();
  const version = server.version.trim();
  if (!name || !version) return null;
  const remotes = Array.isArray(server.remotes) ? server.remotes : null;
  const packages = Array.isArray(server.packages) ? server.packages : null;
  return {
    identity: `mcp:${name}@${version}`,
    catalog: 'mcp', sourceId: name, retrievedAt,
    name: server.title ?? name,
    kind: remotes?.length ? (packages?.length ? 'remote-and-package' : 'remote-service') : (packages?.length ? 'package' : 'unknown'),
    endpoint: null, description: server.description ?? null,
    website: server.websiteUrl ?? null, repository: server.repository ?? null,
    version, packages, remotes,
    input: null, output: null, schema: null, method: null, paymentOptions: null,
    activity: null, updatedAt: entry._meta?.['io.modelcontextprotocol.registry/official']?.updatedAt ?? null,
    registryMetadata: entry._meta ?? null,
  };
}

/** Merge exact identities only, retaining independent and conflicting observations. */
export function deduplicate(observations) {
  const candidates = new Map();
  const observationKeys = new Map();
  for (const observation of observations) {
    let candidate = candidates.get(observation.identity);
    if (!candidate) {
      candidate = { identity: observation.identity, matchedQueries: [], observations: [] };
      candidates.set(observation.identity, candidate);
      observationKeys.set(observation.identity, new Set());
    }
    if (!candidate.matchedQueries.includes(observation.query)) candidate.matchedQueries.push(observation.query);
    const { query, ...evidence } = observation;
    const evidenceKey = JSON.stringify(evidence);
    if (!observationKeys.get(observation.identity).has(evidenceKey)) {
      observationKeys.get(observation.identity).add(evidenceKey);
      candidate.observations.push(evidence);
    }
  }
  return [...candidates.values()];
}
