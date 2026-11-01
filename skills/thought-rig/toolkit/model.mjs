/** Renderer-independent documents and a compatibility adapter for the canvas starter. */
export const clone = value => JSON.parse(JSON.stringify(value));
const geometryKeys = ['x','y','w','h','rotation'];
const reserved = new Set(['id','type','parentId','geometry','data','source','locked']);
const structural = new Set(['id','x','y','w','h','rotation','source','locked','pieces','baseline','registeredType','extensionData','_virtual']);

/** Reject malformed identity/containment while retaining unknown extension data. */
export function validateDocument(doc) {
  if (!doc || doc.schemaVersion !== 2 || !Array.isArray(doc.objects) || !Array.isArray(doc.baseline) || !Array.isArray(doc.notes) || !Array.isArray(doc.events)) throw Error('Expected a schemaVersion 2 document with objects, baseline, notes and events.');
  if (!Number.isInteger(doc.revision) || doc.revision < 0) throw Error('Revision must be a nonnegative integer.');
  const ids = new Set();
  for (const o of doc.objects) {
    if (!o || typeof o.id !== 'string' || !o.id || ids.has(o.id)) throw Error('Object IDs must be unique nonempty strings.');
    ids.add(o.id);
    if (typeof o.type !== 'string' || !o.type.includes(':') || !o.data || typeof o.data !== 'object' || Array.isArray(o.data)) throw Error(`Invalid type/data for ${o.id}`);
    if (o.geometry) for (const [k,v] of Object.entries(o.geometry)) if (geometryKeys.includes(k) && (!Number.isFinite(v) || (['w','h'].includes(k) && v <= 0))) throw Error(`Invalid geometry ${o.id}.${k}`);
  }
  const byId = new Map(doc.objects.map(o => [o.id,o]));
  for (const o of doc.objects) {
    let current=o, seen=new Set([o.id]);
    while (current.parentId) {
      if (!byId.has(current.parentId)) throw Error(`Missing parent for ${o.id}`);
      if (seen.has(current.parentId)) throw Error(`Containment cycle at ${o.id}`);
      seen.add(current.parentId);current=byId.get(current.parentId);
    }
  }
  return doc;
}

function legacyObject(node) {
  const known=node.type.startsWith('core:');
  return {...clone(node.data),id:node.id,...clone(node.geometry||{}),source:clone(node.source??null),locked:!!node.locked,
    kind:known?node.type.slice(5):'extension',...(!known?{registeredType:node.type,extensionData:clone(node.data)}:{})};
}
function nodeFromLegacy(o,parentId,base) {
  const extras=base?Object.fromEntries(Object.entries(base).filter(([k])=>!reserved.has(k))):{};
  const type=o.registeredType||`core:${o.kind||'text'}`;
  const data=o.registeredType?clone(o.extensionData||{}):Object.fromEntries(Object.entries(o).filter(([k])=>!structural.has(k)));
  delete data.kind;
  const geometry=Object.fromEntries(geometryKeys.filter(k=>Number.isFinite(o[k])).map(k=>[k,o[k]]));
  return {...extras,id:o.id,type,...(parentId?{parentId}:{}),...(Object.keys(geometry).length?{geometry}:{}),data,
    ...(o.source?{source:clone(o.source)}:{}),...(o.locked?{locked:true}:{})};
}

/** Project only supported spatial objects into the starter; opaque objects remain retained. */
export function toCanvasDocument(document) {
  validateDocument(document);
  const doc=clone(document), groups=doc.objects.filter(o=>o.type==='core:group').map(legacyObject);
  const frames=doc.objects.filter(o=>['core:frame','core:web'].includes(o.type)).map(node=>{
    const f=legacyObject(node);f.kind=node.type==='core:web'?'web':'screen';
    f.pieces=doc.objects.filter(o=>o.parentId===node.id&&o.geometry&&!['core:frame','core:web','core:group'].includes(o.type)).map(legacyObject);
    f.baseline=doc.baseline.filter(o=>o.parentId===node.id&&o.geometry).map(legacyObject);
    f.controls ||= [];f.variants ||= {};f.variant ||= 'Original';return f;
  });
  const loose=doc.objects.filter(o=>!o.parentId&&o.geometry&&!['core:frame','core:web','core:group'].includes(o.type));
  if(loose.length){
    let id='__root_spatial__';while(doc.objects.some(o=>o.id===id))id+='_';
    frames.push({id,_virtual:true,locked:true,kind:'screen',label:'Ungrouped objects',description:'Independent spatial objects',x:0,y:0,w:Math.max(600,...loose.map(o=>o.geometry.x+o.geometry.w)),h:Math.max(400,...loose.map(o=>o.geometry.y+o.geometry.h)),pieces:loose.map(legacyObject),baseline:doc.baseline.filter(o=>loose.some(p=>p.id===o.id)).map(legacyObject),controls:[],variants:{},variant:'Original'});
  }
  const represented=new Set([...frames,...groups,...frames.flatMap(f=>f.pieces)].map(o=>o.id));
  const originals=clone(doc.resetOriginals||{});for(const o of doc.baseline)originals[o.id]=legacyObject(o);
  for(const f of frames){if(originals[f.id]){originals[f.id].kind=f.kind; originals[f.id].pieces=clone(f.baseline);}}
  return {...doc,schemaVersion:1,frames,groups,originals,_unrepresentedObjects:doc.objects.filter(o=>!represented.has(o.id))};
}

/** Reconcile the starter view without discarding extensions or geometry-less domain objects. */
export function fromCanvasDocument(canvas, canonicalBase={}) {
  const baseById=new Map((canvas.objects||canonicalBase.objects||[]).map(o=>[o.id,o]));
  const objects=[];
  for(const f of canvas.frames||[]){if(!f._virtual){const node=nodeFromLegacy(f,baseById.get(f.id)?.parentId,baseById.get(f.id));node.type=f.kind==='web'?'core:web':'core:frame';objects.push(node);}for(const p of f.pieces||[])objects.push(nodeFromLegacy(p,f._virtual?undefined:f.id,baseById.get(p.id)));}
  for(const g of canvas.groups||[]){const node=nodeFromLegacy(g,baseById.get(g.id)?.parentId,baseById.get(g.id));node.type='core:group';objects.push(node);}
  const objectIds=new Set(objects.map(o=>o.id));for(const o of canvas._unrepresentedObjects||[])if(!objectIds.has(o.id))objects.push(clone(o));
  // Explicit parent deletion removes its hidden descendants too; baselines and notes remain evidence.
  let removed=true;while(removed){removed=false;const live=new Set(objects.map(o=>o.id));for(let i=objects.length-1;i>=0;i--)if(objects[i].parentId&&!live.has(objects[i].parentId)){objects.splice(i,1);removed=true;}}
  const baselineById=new Map((canvas.baseline||canonicalBase.baseline||[]).map(o=>[o.id,clone(o)]));
  for(const o of objects)if(canonicalBase.schemaVersion!==2&&!baselineById.has(o.id)){
    const original=canvas.originals?.[o.id];baselineById.set(o.id,original?nodeFromLegacy(original,o.parentId,o):clone(o));baselineById.get(o.id).type=o.type;
  }
  const result={...clone(canonicalBase),...Object.fromEntries(Object.entries(canvas).filter(([k])=>!['frames','groups','originals','_unrepresentedObjects','schemaVersion','objects','baseline'].includes(k))),schemaVersion:2,objects,baseline:[...baselineById.values()],resetOriginals:clone(canvas.originals||{})};
  return validateDocument(result);
}

/** Import a legacy document in memory. Files and referenced assets are handled by the CLI. */
export function importLegacy(legacy) {
  if(legacy?.schemaVersion!==1||!Array.isArray(legacy.frames))throw Error('Expected a legacy schemaVersion 1 canvas.');
  const input=clone(legacy);input.notes ||= [];input.events ||= [];input.revision ||= 0;input.originals ||= {};
  // Baseline membership comes from the old proposal, never from surviving edits.
  const baseline=[];
  const addFrame=f=>{
    const original=input.originals[f.id]||f;
    const pieces=f.baseline??original.pieces??f.pieces??[];
    const node=nodeFromLegacy({...f,...original,id:f.id});node.type=f.kind==='web'?'core:web':'core:frame';baseline.push(node);
    for(const p of pieces)baseline.push(nodeFromLegacy(p,f.id));
    input.originals[f.id] ||= {...clone(f),pieces:clone(pieces)};
    for(const p of pieces)input.originals[p.id] ||= clone(p);
  };
  input.frames.forEach(addFrame);
  for(const [id,o] of Object.entries(input.originals))if(Array.isArray(o.pieces)&&!input.frames.some(f=>f.id===id))addFrame({...o,id});
  for(const g of input.groups||[])baseline.push({...nodeFromLegacy({...g,...input.originals[g.id],id:g.id}),type:'core:group'});
  input.baseline=baseline;
  input.events=input.events.map(e=>({...e,actor:e.actor||'unknown'}));
  return fromCanvasDocument(input,{schemaVersion:2});
}

/** Compare final state to baseline; untouched seeds and view-only navigation are not decisions. */
export function readback(doc, plugins=[]) {
  validateDocument(doc);const old=new Map(doc.baseline.map(o=>[o.id,o])), current=new Map(doc.objects.map(o=>[o.id,o]));const changes=[],warnings=[];
  for(const id of new Set([...old.keys(),...current.keys()])){
    const before=old.get(id),after=current.get(id);
    if(equivalentForReadback(before,after))continue;
    const delta={};for(const key of geometryKeys)if(before?.geometry?.[key]!==after?.geometry?.[key]&&Number.isFinite(before?.geometry?.[key])&&Number.isFinite(after?.geometry?.[key]))delta[key]=after.geometry[key]-before.geometry[key];
    const semantic=[];for(const plugin of plugins)if(typeof plugin.summarizeChanges==='function'){try{const value=plugin.summarizeChanges({before:clone(before??null),after:clone(after??null)});if(value)semantic.push(...(Array.isArray(value)?value:[value]));}catch(error){warnings.push(`Semantic summary unavailable for ${id}: ${error.message}`);}}
    const parentId=after?.parentId||before?.parentId;
    changes.push({targetId:id,label:after?.data?.label||before?.data?.label||id,type:after?.type||before?.type,status:!before?'added':!after?'removed':'changed',before:before??null,after:after??null,delta,semantic,events:doc.events.filter(e=>e.targetId===id||e.changes?.some(c=>c.targetId===id)||e.targets?.includes(id)||(e.frameId&&e.frameId===parentId)).map(e=>({id:e.id,type:e.type,actor:e.actor||'unknown'}))});
  }
  return {workspace:doc.title,revision:doc.revision,source:doc.source||null,interpretation:'Seeds and proposals are not approval. Interpret final changes together with targeted notes and actor-labelled events.',changes,notes:clone(doc.notes),recentEvents:clone(doc.events.slice(-30)),warnings};
}

function equivalentForReadback(a,b) {
  const normalize=node=>{
    if(!node)return node;
    const o=clone(node);if(!o.source)delete o.source;if(!o.locked)delete o.locked;
    if(o.geometry?.rotation===0)delete o.geometry.rotation;
    // Variant caches and generated group bounds are view bookkeeping, not independent intent.
    if(['core:frame','core:web'].includes(o.type)){
      delete o.data.variant;delete o.data.variants;
      if(!o.data.controls?.length)delete o.data.controls;
    }
    if(o.type==='core:group')delete o.geometry;
    return o;
  };
  const stable=value=>Array.isArray(value)?value.map(stable):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,stable(value[key])])):value;
  return JSON.stringify(stable(normalize(a)))===JSON.stringify(stable(normalize(b)));
}
