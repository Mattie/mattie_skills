/** Local extension registry. No browser globals: safe to inspect and test from Node. */
export function createRegistry() {
  const types = new Map(), commands = new Map(), tools = new Map(), panels = new Map();
  const add = (map, id, value) => {
    if (typeof id !== 'string' || !id.trim() || map.has(id)) throw Error(`Invalid or duplicate registration: ${id}`);
    map.set(id, Object.freeze({ ...value }));
    return () => map.delete(id);
  };
  return {
    types, commands, tools, panels,
    registerType(type, definition) {
      if (!type.includes(':')) throw Error('Object types need a namespace, such as demo:cue');
      return add(types, type, definition);
    },
    registerCommand(definition) {
      if (!['toolbar','context'].includes(definition.placement) || typeof definition.run !== 'function') throw Error('Commands need a placement and run function');
      return add(commands, definition.id, definition);
    },
    registerTool(definition) { return add(tools, definition.id, definition); },
    registerPanel(definition) {
      if (typeof definition.mount !== 'function') throw Error('Panels need a mount function');
      return add(panels, definition.id, definition);
    },
    validate(object) {
      const validator = types.get(object.type)?.validate;
      const result = validator?.(object);
      if (result === false || typeof result === 'string' || Array.isArray(result) && result.length) throw Error(typeof result === 'string' ? result : `Invalid ${object.type} object ${object.id}`);
      return object;
    },
    create(type, overrides = {}) {
      const definition = types.get(type);
      if (!definition) throw Error(`Unregistered object type: ${type}`);
      const defaults = typeof definition.defaults === 'function' ? definition.defaults() : definition.defaults || {};
      const value = { ...structuredClone(defaults), ...structuredClone(overrides), type,
        ...((defaults.geometry || overrides.geometry) ? {geometry: { ...(defaults.geometry || {}), ...(overrides.geometry || {}) }} : {}),
        data: { ...(defaults.data || {}), ...(overrides.data || {}) } };
      this.validate(value);
      return value;
    },
  };
}

/** Manifest modules are explicit same-origin workspace paths, never remote code. */
export function localModuleURL(modulePath, baseURL) {
  if (typeof modulePath !== 'string' || !modulePath || /[?#\\]/.test(modulePath) || modulePath.split('/').includes('..') || /^[a-z][a-z\d+.-]*:/i.test(modulePath) || modulePath.startsWith('//')) throw Error('Extension module must be an explicit local .mjs path');
  const base = new URL(baseURL), url = new URL(modulePath, new URL('/', base));
  if (url.origin !== base.origin || !url.pathname.endsWith('.mjs')) throw Error('Extension module must be a same-origin .mjs file');
  return url.href;
}

export function assertActor(actor) {
  if (!['user','agent','verification'].includes(actor)) throw Error('Actor must be user, agent, or verification');
  return actor;
}
