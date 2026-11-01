/** Local workspace I/O. Preparation tools may be copied and adapted per task. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {validateDocument,clone,importLegacy,readback} from './model.mjs';
const toolkit=path.dirname(fileURLToPath(import.meta.url));

export function localPath(root, relative) {
  if(typeof relative!=='string'||!relative||path.isAbsolute(relative)||/^[a-z]+:/i.test(relative))throw Error('Workspace paths must be local relative paths.');
  const absolute=path.resolve(root,relative),base=path.resolve(root);
  if(absolute!==base&&!absolute.startsWith(base+path.sep))throw Error('Path escapes workspace.');
  let existing=absolute;while(!fs.existsSync(existing))existing=path.dirname(existing);
  const actual=fs.realpathSync(existing),realRoot=fs.realpathSync(base);
  if(actual!==realRoot&&!actual.startsWith(realRoot+path.sep))throw Error('Symlink escapes workspace.');
  return absolute;
}
export function readJSON(file){return JSON.parse(fs.readFileSync(file,'utf8'));}
export function writeJSON(file,value){fs.mkdirSync(path.dirname(file),{recursive:true});const temp=`${file}.${crypto.randomUUID()}.tmp`;fs.writeFileSync(temp,JSON.stringify(value,null,2));fs.renameSync(temp,file);}
export function loadWorkspace(root) {
  root=path.resolve(root);const manifest=readJSON(path.join(root,'manifest.json'));
  if(manifest.schemaVersion!==1||!Array.isArray(manifest.extensions))throw Error('Invalid workspace manifest.');
  for(const field of ['surface','state','assets'])localPath(root,manifest[field]);
  const seen=new Set();for(const extension of manifest.extensions){if(!extension.id||seen.has(extension.id))throw Error('Extension IDs must be unique.');seen.add(extension.id);localPath(root,extension.module);}
  return {root,manifest,statePath:localPath(root,manifest.state)};
}
export function createWorkspace(destination,{title='Thought-Rig exploration',empty=false}={}) {
  const root=path.resolve(destination);if(fs.existsSync(root))throw Error('Destination already exists; existing workspaces are never overwritten.');
  if(root.startsWith(toolkit+path.sep))throw Error('Create workspaces outside the shared toolkit.');
  fs.mkdirSync(root,{recursive:true});
  fs.cpSync(toolkit,path.join(root,'toolkit'),{recursive:true,filter:source=>!['node_modules','.DS_Store'].includes(path.basename(source))});
  fs.mkdirSync(path.join(root,'extensions'),{recursive:true});
  if(fs.existsSync(path.join(toolkit,'extensions')))fs.cpSync(path.join(toolkit,'extensions'),path.join(root,'extensions'),{recursive:true});
  fs.mkdirSync(path.join(root,'assets'),{recursive:true});
  const extensions=fs.existsSync(path.join(root,'extensions/duration.mjs'))?[{id:'duration',module:'extensions/duration.mjs'}]:[];
  const manifest={schemaVersion:1,surface:'toolkit/canvas/index.html',state:'state.json',assets:'assets',extensions};
  const stamp=new Date().toISOString();const objects=empty?[]:[
    {id:'starter-frame',type:'core:frame',geometry:{x:0,y:0,w:900,h:500,rotation:0},data:{label:'Explore an idea',description:'Move the cue, change its duration, and attach a note.',variant:'Original',variants:{},controls:[]}},
    {id:'starter-cue',type:'demo:cue',parentId:'starter-frame',geometry:{x:240,y:150,w:360,h:160,rotation:0},data:{label:'Opening cue',durationSeconds:3}}
  ];
  const doc={schemaVersion:2,revision:0,title,createdAt:stamp,coordinateUnit:'CSS pixels',objects,baseline:clone(objects),notes:[],events:[{id:crypto.randomUUID(),at:stamp,type:'seed',actor:'agent',revision:0}],source:{status:'Agent-seeded exploration; unchanged defaults are not approval.'}};
  writeJSON(path.join(root,'manifest.json'),manifest);writeJSON(path.join(root,'state.json'),doc);writeJSON(path.join(root,'seed.json'),doc);return root;
}

export async function workspaceReadback(root) {
  const ws=loadWorkspace(root),plugins=[],warnings=[];
  for(const extension of ws.manifest.extensions){const module=localPath(ws.root,extension.module);if(!fs.existsSync(module)){warnings.push(`Missing extension: ${extension.id}; data retained.`);continue;}try{plugins.push(await import(pathToFileURL(module).href));}catch(error){warnings.push(`Extension ${extension.id} unavailable: ${error.message}`);}}
  const result=readback(readJSON(ws.statePath),plugins);return {...result,warnings:[...warnings,...result.warnings]};
}

/** Copy captures as immutable hash-named assets without image processing dependencies. */
function copyCapture(ws,sourcePath) {
  const bytes=fs.readFileSync(sourcePath),sha256=crypto.createHash('sha256').update(bytes).digest('hex');
  const filename=sha256+path.extname(sourcePath).toLowerCase(),relative=path.posix.join(ws.manifest.assets.replaceAll('\\','/'),filename),target=localPath(ws.root,relative);
  fs.mkdirSync(path.dirname(target),{recursive:true});if(!fs.existsSync(target))fs.writeFileSync(target,bytes);
  return {src:relative,sha256,capturedFrom:path.basename(sourcePath),copiedAt:new Date().toISOString(),evidence:'Captured source pixels; rectangular extraction, no reconstruction'};
}

/** Add a fresh cutout frame; refuse collisions rather than overwriting annotated objects. */
export function cutCapture(root,specFile) {
  const ws=loadWorkspace(root),spec=readJSON(specFile),doc=validateDocument(readJSON(ws.statePath));
  if(!Number.isFinite(spec.width)||spec.width<=0||!Number.isFinite(spec.height)||spec.height<=0||!Array.isArray(spec.regions)||!spec.regions.length)throw Error('Capture needs positive width/height and regions.');
  if(spec.source!==undefined&&(!spec.source||typeof spec.source!=='object'||Array.isArray(spec.source)))throw Error('Source metadata must be an object.');
  const frameId=spec.id||`capture-${crypto.randomUUID()}`,existing=new Set(doc.objects.map(o=>o.id));
  const regions=spec.regions.map((r,i)=>({...r,id:r.id||`${frameId}-region-${i}`}));
  const ids=[frameId,...regions.map(r=>r.id)];if(new Set(ids).size!==ids.length||ids.some(id=>existing.has(id)))throw Error('Capture or region ID already exists. Use new IDs; existing feedback is retained.');
  for(const r of regions)if(![r.x,r.y,r.w,r.h].every(Number.isFinite)||r.x<0||r.y<0||r.w<=0||r.h<=0||r.x+r.w>spec.width||r.y+r.h>spec.height)throw Error(`Region outside capture: ${r.id}`);
  const copied=copyCapture(ws,path.resolve(path.dirname(specFile),spec.image));
  const source={...spec.source,...copied,evidence:spec.source?.evidence??copied.evidence,method:'source-copy',region:[0,0,spec.width,spec.height]};
  const frame={id:frameId,type:'core:frame',geometry:{x:spec.x??0,y:spec.y??(doc.objects.length?700:0),w:spec.width,h:spec.height,rotation:0},data:{label:spec.label||'Captured layout',description:spec.description||'Move a piece or attach a note.',controls:[],variants:{},variant:'Original'},source};
  const pieces=regions.map(r=>({id:r.id,type:'core:image',parentId:frameId,geometry:{x:r.x,y:r.y,w:r.w,h:r.h,rotation:0},data:{label:r.label||r.id,src:source.src,crop:[r.x,r.y,r.w,r.h]},source:{...source,region:[r.x,r.y,r.w,r.h],method:'rectangular-cutout'}}));
  // Background strips omit extracted pixels, avoiding duplicate ghosts when pieces move.
  const xs=[...new Set([0,spec.width,...regions.flatMap(r=>[r.x,r.x+r.w])])].sort((a,b)=>a-b),ys=[...new Set([0,spec.height,...regions.flatMap(r=>[r.y,r.y+r.h])])].sort((a,b)=>a-b),tiles=[];
  for(let yi=0;yi<ys.length-1;yi++){let start=null;for(let xi=0;xi<xs.length;xi++){const blocked=xi===xs.length-1||regions.some(r=>xs[xi]>=r.x&&xs[xi]<r.x+r.w&&ys[yi]>=r.y&&ys[yi]<r.y+r.h);if(!blocked&&start===null)start=xs[xi];if(blocked&&start!==null){const crop=[start,ys[yi],xs[xi]-start,ys[yi+1]-ys[yi]];tiles.push({id:`${frameId}-backdrop-${tiles.length}`,type:'core:image',parentId:frameId,geometry:{x:crop[0],y:crop[1],w:crop[2],h:crop[3],rotation:0},locked:true,data:{label:'Captured background',src:source.src,crop},source});start=null;}}}
  for(const tile of tiles)tile.source={...source,method:'rectangular-background-tile',region:[...tile.data.crop]};
  const added=[frame,...tiles,...pieces];if(added.some(o=>existing.has(o.id)))throw Error('Generated background ID collision.');
  doc.objects.push(...added);doc.baseline.push(...clone(added));doc.revision++;doc.events.push({id:crypto.randomUUID(),at:new Date().toISOString(),type:'capture-import',actor:'agent',revision:doc.revision,targets:pieces.map(p=>p.id)});writeJSON(ws.statePath,validateDocument(doc));return {frameId,regions:pieces.map(p=>p.id),source};
}

/** Import JSON and local/data assets into a separate workspace without running source code. */
export function importLegacyWorkspace(sourceFile,destination) {
  const original=readJSON(sourceFile),doc=importLegacy(original),root=createWorkspace(destination,{title:doc.title||'Imported exploration',empty:true}),ws=loadWorkspace(root);
  const assets=new Map();
  function remap(value){if(!value||typeof value!=='object')return;for(const [key,item] of Object.entries(value)){if(key==='src'&&typeof item==='string'&&!/^https?:|^data:/i.test(item)){if(!assets.has(item)){const source=path.resolve(path.dirname(sourceFile),item);if(!fs.existsSync(source))throw Error(`Asset missing: ${item}. Place the document beside its relative assets before importing.`);assets.set(item,copyCapture(ws,source).src);}value[key]=assets.get(item);}else if(item&&typeof item==='object')remap(item);}}
  remap(doc);doc.importedFrom={filename:path.basename(sourceFile),at:new Date().toISOString()};writeJSON(ws.statePath,doc);writeJSON(path.join(root,'seed.json'),doc);return root;
}
