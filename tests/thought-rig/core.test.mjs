import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import {createServer} from '../../skills/thought-rig/toolkit/server.mjs';
import {createWorkspace,cutCapture,importLegacyWorkspace,loadWorkspace,readJSON,localPath,workspaceReadback} from '../../skills/thought-rig/toolkit/workspace.mjs';
import {toCanvasDocument,fromCanvasDocument,validateDocument,readback} from '../../skills/thought-rig/toolkit/model.mjs';

function temporary(t){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'thought-rig-test-'));t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));return dir;}

test('custom data, opaque objects, notes, and geometry survive canvas roundtrip',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace'));
  const original=readJSON(path.join(root,'state.json'));
  original.objects.push({id:'meaning',type:'test:meaning',data:{reason:'Keep this even without a renderer'}});
  original.baseline=structuredClone(original.objects);
  original.notes.push({id:'n',targetId:'starter-cue',text:'Hold this longer',source:'typed'});
  const canvas=toCanvasDocument(original),cue=canvas.frames[0].pieces[0];
  cue.extensionData.durationSeconds=7;cue.x+=21;
  const saved=fromCanvasDocument(canvas,original),reopened=toCanvasDocument(saved);
  assert.equal(reopened.frames[0].pieces[0].extensionData.durationSeconds,7);
  assert.equal(reopened.frames[0].pieces[0].x,261);
  assert.deepEqual(saved.objects.find(o=>o.id==='meaning'),original.objects.at(-1));
  assert.deepEqual(saved.notes,original.notes);
  const report=readback(saved,[{summarizeChanges:({before,after})=>after?.type==='demo:cue'&&before.data.durationSeconds!==after.data.durationSeconds?`${before.data.durationSeconds} → ${after.data.durationSeconds} seconds`:null}]);
  const change=report.changes.find(c=>c.targetId==='starter-cue');
  assert.equal(change.delta.x,21);assert.deepEqual(change.semantic,['3 → 7 seconds']);
});

test('an untouched roundtrip and variant caches produce no feedback changes',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace'));
  const doc=readJSON(path.join(root,'state.json'));
  delete doc.objects[0].data.controls;delete doc.objects[0].data.variant;delete doc.objects[0].data.variants;
  doc.baseline=structuredClone(doc.objects);
  const canvas=toCanvasDocument(doc);canvas.frames[0].variants.Explored=structuredClone(canvas.frames[0].pieces);canvas.frames[0].variant='Explored';
  const saved=fromCanvasDocument(canvas,doc);
  assert.deepEqual(readback(saved).changes,[]);
  saved.objects[0].data.description='An actual changed description';
  assert.equal(readback(saved).changes.length,1);
});

test('cutting copies original pixels and refuses to overwrite annotated objects',t=>{
  const dir=temporary(t),root=createWorkspace(path.join(dir,'workspace'),{empty:true});
  const source=path.join(dir,'capture.svg'),spec=path.join(dir,'regions.json');
  fs.writeFileSync(source,'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80"><rect width="100" height="80" fill="navy"/></svg>');
  fs.writeFileSync(spec,JSON.stringify({id:'capture',image:'capture.svg',width:100,height:80,source:{identity:'synthetic-sheet',evidence:'Synthetic illustration; not captured UI',generator:'test fixture',sha256:'incorrect',src:'incorrect',copiedAt:'incorrect',region:[99],method:'incorrect'},regions:[{id:'action',label:'Action',x:10,y:20,w:30,h:25}]}));
  const result=cutCapture(root,spec),doc=readJSON(path.join(root,'state.json'));
  assert.equal(doc.objects.find(o=>o.id==='action').source.method,'rectangular-cutout');
  assert.deepEqual(doc.objects.find(o=>o.id==='action').data.crop,[10,20,30,25]);
  const provenance=doc.objects.find(o=>o.id==='action').source;
  assert.equal(provenance.identity,'synthetic-sheet');assert.equal(provenance.evidence,'Synthetic illustration; not captured UI');assert.equal(provenance.generator,'test fixture');
  assert.match(provenance.sha256,/^[a-f0-9]{64}$/);assert.notEqual(provenance.src,'incorrect');assert.notEqual(provenance.copiedAt,'incorrect');assert.deepEqual(provenance.region,[10,20,30,25]);
  assert.equal(fs.readFileSync(path.join(root,result.source.src),'utf8'),fs.readFileSync(source,'utf8'));
  const before=fs.readFileSync(path.join(root,'state.json'),'utf8');
  assert.throws(()=>cutCapture(root,spec),/already exists/);
  assert.equal(fs.readFileSync(path.join(root,'state.json'),'utf8'),before);
  const backdrop=doc.objects.filter(o=>o.locked);
  assert.ok(backdrop.length>0);
  assert.deepEqual(backdrop[0].source.region,backdrop[0].data.crop);assert.equal(backdrop[0].source.method,'rectangular-background-tile');
  assert.equal(backdrop.reduce((a,o)=>a+o.geometry.w*o.geometry.h,0),100*80-30*25);
});

test('legacy import preserves source file and original geometry',t=>{
  const dir=temporary(t),file=path.join(dir,'legacy.json'),destination=path.join(dir,'imported');
  const legacy={schemaVersion:1,revision:4,title:'Legacy',frames:[{id:'frame',kind:'screen',label:'Frame',x:0,y:0,w:100,h:100,pieces:[{id:'p',kind:'text',label:'Text',text:'Hello',x:20,y:20,w:50,h:30}],baseline:[{id:'p',kind:'text',label:'Text',text:'Hello',x:10,y:20,w:50,h:30}],controls:[],variants:{}}],notes:[{id:'n',targetId:'p',text:'Keep this'}],events:[]};
  fs.writeFileSync(file,JSON.stringify(legacy));const source=fs.readFileSync(file,'utf8');
  importLegacyWorkspace(file,destination);assert.equal(fs.readFileSync(file,'utf8'),source);
  const report=readback(readJSON(path.join(destination,'state.json')));
  assert.equal(report.changes.find(c=>c.targetId==='p').delta.x,10);assert.equal(report.notes[0].text,'Keep this');
  assert.throws(()=>createWorkspace(destination),/already exists/);
});

test('legacy import retains added and removed identities independently of reset snapshots',t=>{
  const dir=temporary(t),file=path.join(dir,'legacy.json'),destination=path.join(dir,'imported');
  const piece=id=>({id,kind:'text',label:id,text:id,x:10,y:10,w:50,h:30});
  const removed=piece('removed'),added=piece('added');
  const legacy={schemaVersion:1,revision:1,frames:[{id:'f',kind:'screen',label:'Frame',x:0,y:0,w:100,h:100,pieces:[added],baseline:[removed]}],originals:{added},notes:[{id:'n',targetId:'removed',text:'Keep the reason'}],events:[]};
  fs.writeFileSync(file,JSON.stringify(legacy));
  importLegacyWorkspace(file,destination);
  const doc=readJSON(path.join(destination,'state.json'));
  for(const saved of [doc,fromCanvasDocument(toCanvasDocument(doc),doc)]){
    const report=readback(saved);
    assert.equal(report.changes.find(c=>c.targetId==='removed').status,'removed');
    assert.equal(report.changes.find(c=>c.targetId==='added').status,'added');
    assert.deepEqual(report.notes,legacy.notes);
  }
  assert.equal(fs.readFileSync(file,'utf8'),JSON.stringify(legacy));
  legacy.frames[0].baseline=[];
  legacy.originals.f={...legacy.frames[0],pieces:[added]};
  legacy.originals.deletedFrame={id:'deletedFrame',kind:'screen',x:0,y:0,w:100,h:100,pieces:[{...removed,id:'deletedChild'}]};
  fs.writeFileSync(file,JSON.stringify(legacy));
  const second=path.join(dir,'empty-baseline');importLegacyWorkspace(file,second);
  const changes=readback(readJSON(path.join(second,'state.json'))).changes;
  assert.equal(changes.find(c=>c.targetId==='added').status,'added');
  assert.equal(changes.find(c=>c.targetId==='deletedFrame').status,'removed');
  assert.equal(changes.find(c=>c.targetId==='deletedChild').status,'removed');
});

test('missing extension preserves data and produces readback warning',async t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace'));
  const manifest=readJSON(path.join(root,'manifest.json'));manifest.extensions=[{id:'missing',module:'extensions/missing.mjs'}];fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest));
  const before=fs.readFileSync(path.join(root,'state.json'),'utf8'),report=await workspaceReadback(root);
  assert.match(report.warnings[0],/Missing extension/);assert.equal(fs.readFileSync(path.join(root,'state.json'),'utf8'),before);
});

test('reject escaping workspace references and invalid containment',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace'));
  assert.throws(()=>localPath(root,'../outside'),/escapes/);
  assert.throws(()=>localPath(root,'https://example.invalid/plugin.mjs'),/relative/);
  const doc=readJSON(loadWorkspace(root).statePath);doc.objects[0].parentId='starter-cue';
  assert.throws(()=>validateDocument(doc),/cycle/);
});

test('root spatial objects roundtrip and removed containers remove opaque descendants',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace')),doc=readJSON(path.join(root,'state.json'));
  doc.objects.push({id:'free',type:'unknown:tile',geometry:{x:5,y:9,w:100,h:80},data:{mystery:42}});
  doc.objects.push({id:'hidden',parentId:'starter-frame',type:'unknown:data',data:{kept:true}});
  doc.baseline=structuredClone(doc.objects);
  const canvas=toCanvasDocument(doc);assert.ok(canvas.frames.some(f=>f._virtual&&f.pieces.some(p=>p.id==='free')));
  assert.deepEqual(readback(fromCanvasDocument(canvas,doc)).changes,[]);
  canvas.frames=canvas.frames.filter(f=>f.id!=='starter-frame');const saved=fromCanvasDocument(canvas,doc);
  assert.ok(!saved.objects.some(o=>o.id==='hidden'));assert.ok(saved.baseline.some(o=>o.id==='hidden'));
  assert.ok(saved.objects.some(o=>o.id==='free'&&!o.parentId));
});

test('new objects remain additions and a broken semantic summary retains structural feedback',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace')),doc=readJSON(path.join(root,'state.json')),canvas=toCanvasDocument(doc);
  canvas.frames[0].pieces.push({id:'new',kind:'text',label:'New',text:'New',x:1,y:2,w:100,h:50});
  canvas.originals.new=structuredClone(canvas.frames[0].pieces.at(-1));
  const saved=fromCanvasDocument(canvas,doc),report=readback(saved,[{summarizeChanges(){throw Error('Unavailable')}}]);
  assert.equal(report.changes.find(c=>c.targetId==='new').status,'added');assert.ok(report.warnings.length);
  assert.equal(toCanvasDocument(saved).originals.new.x,1);
});

test('HTTP saves reject stale revisions and reject unsafe origins, hosts, and traversal',async t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace'));
  const manifest=readJSON(path.join(root,'manifest.json'));manifest.surface='surface/index.html';
  fs.mkdirSync(path.join(root,'surface'));fs.writeFileSync(path.join(root,'surface','index.html'),'<main>Alternate surface</main>');
  fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest));
  const server=createServer(root);
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  try{
    const port=server.address().port,host=`127.0.0.1:${port}`;
    const request=(url,method='GET',body,headers={})=>new Promise((resolve,reject)=>{
      const req=http.request({hostname:'127.0.0.1',port,path:url,method,headers:{Host:host,...headers}},res=>{const chunks=[];res.on('data',chunk=>chunks.push(chunk));res.on('end',()=>resolve({status:res.statusCode,body:Buffer.concat(chunks).toString('utf8')}));});req.on('error',reject);req.end(body?JSON.stringify(body):undefined);
    });
    const doc=JSON.parse((await request('/api/state')).body);doc.objects[1].data.durationSeconds=9;
    assert.equal((await request('/surface/index.html')).status,200);
    const runtime=await request('/toolkit/model.mjs');assert.equal(runtime.status,200);assert.match(runtime.body,/export function validateDocument/);
    assert.equal((await request('/api/state','POST',{expectedRevision:0,document:doc},{Origin:`http://${host}`})).status,200);
    const saved=fs.readFileSync(path.join(root,'state.json'),'utf8');
    assert.equal((await request('/api/state','POST',{expectedRevision:0,document:doc})).status,409);
    assert.equal(fs.readFileSync(path.join(root,'state.json'),'utf8'),saved);
    assert.equal((await request('/api/state','GET',null,{Host:'attacker.invalid'})).status,403);
    assert.equal((await request('/api/state','POST',{expectedRevision:1,document:doc},{Origin:'https://attacker.invalid'})).status,403);
    assert.equal((await request('/toolkit/%2e%2e/%2e%2e/secret.txt')).status,404);
    assert.equal((await request('/toolkit/..%2f..%2fsecret.txt')).status,400);
    assert.equal((await request('/state.json')).status,404);
    assert.equal(fs.readFileSync(path.join(root,'state.json'),'utf8'),saved);
  }finally{await new Promise(resolve=>server.close(resolve));}
});

test('canonical transaction metadata and explicit baseline edits survive the canvas projection',t=>{
  const root=createWorkspace(path.join(temporary(t),'workspace')),base=readJSON(path.join(root,'state.json'));
  const draft=structuredClone(base);
  draft.objects[1].customMetadata={reason:'Imported with a task-local adapter'};
  draft.objects[1].data.durationSeconds=8;
  draft.baseline=structuredClone(draft.objects);
  const saved=fromCanvasDocument(toCanvasDocument(draft),base);
  assert.deepEqual(saved.objects[1].customMetadata,draft.objects[1].customMetadata);
  assert.deepEqual(saved.baseline,draft.baseline);
  assert.deepEqual(readback(saved).changes,[]);
});

test('readback attributes root edits only to explicitly matching event targets',()=>{
  const objects=['a','b'].map(id=>({id,type:'test:root',data:{value:1}}));
  const doc={schemaVersion:2,revision:0,objects,baseline:structuredClone(objects),notes:[],events:[
    {id:'seed',type:'seed',actor:'agent'},
    {id:'edit-a',type:'edit',actor:'user',targetId:'a'},
    {id:'edit-b',type:'edit',actor:'user',targets:['b']},
    {id:'verify-b',type:'check',actor:'verification',changes:[{targetId:'b'}]}
  ]};
  for(const object of doc.objects)object.data.value=2;
  const report=readback(doc);
  assert.deepEqual(report.changes.find(c=>c.targetId==='a').events.map(e=>e.id),['edit-a']);
  assert.deepEqual(report.changes.find(c=>c.targetId==='b').events.map(e=>e.id),['edit-b','verify-b']);
});
