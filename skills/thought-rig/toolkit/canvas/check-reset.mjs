import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import * as model from '../model.mjs';
import * as registryModule from './registry.mjs';
const {toCanvasDocument,fromCanvasDocument,readback}=model;

// Exercise the actual reset/undo implementation, without a server or saved-state writes.
const drawing=new Proxy({}, {get:(_,key)=>key==='createLinearGradient'?()=>({addColorStop(){}}):()=>{}});
function element(){return {hidden:false,style:{},classList:{add(){},remove(){},toggle(){}},append(child){this.firstChild ||= child},before(){},after(){},remove(){this.removed=true},replaceChildren(){},setAttribute(){},addEventListener(){},removeEventListener(){},getContext:()=>drawing,getBoundingClientRect:()=>({width:1440,height:900,left:0,top:0}),clientWidth:1440,clientHeight:900,querySelector:()=>element(),querySelectorAll:()=>[],focus(){}}}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)};
const frame={id:'frame',type:'core:frame',geometry:{x:0,y:0,w:800,h:500},data:{label:'Test'}};
const cue={id:'cue',type:'demo:cue',parentId:'frame',geometry:{x:30,y:40,w:220,h:100},data:{label:'Original cue',durationSeconds:3}};
const canonical={schemaVersion:2,revision:0,title:'Reset test',objects:[frame,cue],baseline:structuredClone([frame,cue]),notes:[{id:'note',targetId:'cue',text:'Retain my note'}],events:[]};
const sandbox={console,document:{getElementById:get,createElement:element,querySelector:element,body:element()},crypto:webcrypto,devicePixelRatio:1,innerWidth:1440,innerHeight:960,location:{href:'http://127.0.0.1:5320/',origin:'http://127.0.0.1:5320'},fetch:()=>new Promise(()=>{}),URL,Blob,Image:class{},setTimeout:()=>0,clearTimeout(){},addEventListener(){},removeEventListener(){},fixture:toCanvasDocument(canonical)};
sandbox.window=sandbox;vm.createContext(sandbox);
for(const name of ['app.js','enhancements.js'])vm.runInContext(fs.readFileSync(new URL(name,import.meta.url),'utf8'),sandbox);
const opened=JSON.parse(vm.runInContext('doc=fixture;migrateDocument();JSON.stringify(doc)',sandbox));
assert.deepEqual(readback(fromCanvasDocument(opened,canonical)).changes,[],'opening a frame without a description must not manufacture feedback');
const result=JSON.parse(vm.runInContext(`
 doc=fixture;migrateDocument();dirty=false;const initialRevision=doc.revision;pick(['cue']);pick([]);const selectionOnly={dirty,revisionUnchanged:doc.revision===initialRevision,eventCount:doc.events.length};const target=object('cue');target.extensionData.durationSeconds=5;target.extensionData.extra='new';target.x=70;
 resetTarget('cue','position');const positionOnly={x:object('cue').x,duration:object('cue').extensionData.durationSeconds};
 resetTarget('cue','all');const reset=clone(object('cue'));undo();const undone=clone(object('cue'));undo(true);const redone=clone(object('cue'));
 JSON.stringify({selectionOnly,dirtyAfterReset:dirty,positionOnly,reset,undone,redone,document:doc});
`,sandbox));
assert.equal(result.selectionOnly.dirty,false);assert.equal(result.selectionOnly.revisionUnchanged,true);assert.equal(result.selectionOnly.eventCount,2);assert.equal(result.dirtyAfterReset,true);
assert.equal(result.positionOnly.x,30);assert.equal(result.positionOnly.duration,5);
assert.equal(result.reset.extensionData.durationSeconds,3);assert.equal('extra' in result.reset.extensionData,false);
assert.equal(result.undone.extensionData.durationSeconds,5);assert.equal(result.undone.extensionData.extra,'new');
assert.equal(result.redone.extensionData.durationSeconds,3);
const roundTrip=fromCanvasDocument(result.document,canonical);
assert.equal(roundTrip.objects.find(o=>o.id==='cue').data.durationSeconds,3);
assert.deepEqual(roundTrip.notes,canonical.notes);
for(const [type,field,before,after] of [['text','text','Original text','Edited text'],['image','src','original.png','edited.png']]){
 const built={id:'built',type:'core:'+type,parentId:'frame',geometry:{x:10,y:20,w:100,h:50},data:{label:'Original label',[field]:before}};
 const source={...structuredClone(canonical),objects:[frame,built],baseline:structuredClone([frame,built]),notes:[{id:'built-note',targetId:'built',text:'Retain built-in note'}]};
 sandbox.fixture=toCanvasDocument(source);sandbox.contentField=field;sandbox.editedValue=after;
 const actual=JSON.parse(vm.runInContext(`(()=>{
  doc=fixture;past=[];future=[];selected=[];migrateDocument();
  object('built')[contentField]=editedValue;object('built').extra='added';object('built').x=80;
  resetTarget('built','position');const partial=clone(object('built'));
  resetTarget('built','all');const restored=clone(object('built'));undo();const reverted=clone(object('built'));undo(true);
  return JSON.stringify({partial,restored,reverted,document:doc});
 })()`,sandbox));
 assert.equal(actual.partial[field],after);assert.equal(actual.partial.x,10);
 assert.equal(actual.restored[field],before);assert.equal('extra' in actual.restored,false);
 assert.equal(actual.reverted[field],after);assert.equal(actual.reverted.extra,'added');
 const exported=fromCanvasDocument(actual.document,source);
 assert.equal(exported.objects.find(o=>o.id==='built').data[field],before);assert.deepEqual(exported.notes,source.notes);
}
const group={id:'group',type:'core:group',data:{label:'Option A',frameIds:['frame']}};
const grouped={...structuredClone(canonical),objects:[{...structuredClone(frame),geometry:{...frame.geometry,x:250}},group],baseline:structuredClone([frame,group]),notes:[{id:'group-note',targetId:'group',text:'Keep this option'}],resetOriginals:{group:{members:[{id:'frame',x:75,y:25}],capturedAt:'retained'}}};
sandbox.fixture=toCanvasDocument(grouped);
const groupReset=JSON.parse(vm.runInContext(`(()=>{
 doc=fixture;past=[];future=[];selected=[];migrateDocument();resetTarget('group','position');
 const restored=object('frame').x;undo();const undone=object('frame').x;undo(true);
 return JSON.stringify({restored,undone,redone:object('frame').x,document:doc});
})()`,sandbox));
assert.equal(groupReset.restored,0);assert.equal(groupReset.undone,250);assert.equal(groupReset.redone,0);
const groupExport=fromCanvasDocument(groupReset.document,grouped);
assert.deepEqual(groupExport.notes,grouped.notes);
assert.equal(toCanvasDocument(groupExport).originals.group.members[0].x,0);
assert.equal(toCanvasDocument(groupExport).originals.group.capturedAt,'retained');
// Frame content resets use the same path, retaining identity and notes.
const described=structuredClone(canonical);described.objects[0].data.description='Original caption';described.baseline[0].data.description='Original caption';
sandbox.fixture=toCanvasDocument(described);
const frameReset=JSON.parse(vm.runInContext(`(()=>{
 doc=fixture;past=[];future=[];selected=[];migrateDocument();
 setDescription('frame','Edited caption','Edited title');object('frame').x=120;
 resetTarget('frame','position');const partial={label:object('frame').label,description:object('frame').description};
 resetTarget('frame','all');const restored=clone(object('frame'));undo();const undone=clone(object('frame'));undo(true);
 return JSON.stringify({partial,restored,undone,document:doc});
})()`,sandbox));
assert.equal(frameReset.partial.label,'Edited title');assert.equal(frameReset.partial.description,'Edited caption');
assert.equal(frameReset.restored.label,'Test');assert.equal(frameReset.restored.description,'Original caption');
assert.equal(frameReset.undone.label,'Edited title');assert.equal(frameReset.undone.description,'Edited caption');
assert.deepEqual(fromCanvasDocument(frameReset.document,canonical).notes,canonical.notes);
// Start the real host against the same DOM stubs; substitute module loading only.
sandbox.modelModule=model;sandbox.registryModule=registryModule;
sandbox.fixture=toCanvasDocument(canonical);
vm.runInContext('doc=fixture;past=[];future=[];selected=[]',sandbox);
const hostSource=fs.readFileSync(new URL('bootstrap.js',import.meta.url),'utf8')
 .replace("await import('/toolkit/model.mjs')",'modelModule')
 .replace("await import('/toolkit/canvas/registry.mjs')",'registryModule');
vm.runInContext(hostSource,sandbox);
const host=sandbox.thoughtRig;
host.registerType('test:claim',{defaults:{data:{label:'Claim'}}});
const claimId=host.createObject('test:claim',{}, {actor:'verification'});
host.addNote('Explain this claim',claimId,{actor:'verification'});
assert.equal(host.getDocument().notes.find(n=>n.targetId===claimId).text,'Explain this claim');
assert.equal(host.getDocument().events.at(-1).actor,'verification');
vm.runInContext('undo()',sandbox);assert.equal(host.getDocument().notes.some(n=>n.targetId===claimId),false);
vm.runInContext('undo(true)',sandbox);
const reopened=fromCanvasDocument(toCanvasDocument(host.getDocument()),host.getDocument());
assert.equal(readback(reopened).notes.find(n=>n.targetId===claimId).text,'Explain this claim');
assert.equal(reopened.objects.find(o=>o.id===claimId).geometry,undefined);
const webId=host.createObject('core:web',{data:{label:'First',url:'/first'}},{actor:'verification'});
let webElement=vm.runInContext('paneEls.get('+JSON.stringify(webId)+')',sandbox);
const iframe=webElement.firstChild;assert.equal(iframe.src,'http://127.0.0.1:5320/first');
let srcWrites=0,sourceURL=iframe.src;
Object.defineProperty(iframe,'src',{get:()=>sourceURL,set:value=>{srcWrites++;sourceURL=value}});
vm.runInContext('syncPanes();syncPanes()',sandbox);assert.equal(srcWrites,0,'redraw must not reload the page');
host.transaction('update-web',draft=>{const node=draft.objects.find(o=>o.id===webId);node.data.url='/second';node.data.label='Second'},{actor:'verification'});
assert.equal(iframe.src,'http://127.0.0.1:5320/second');assert.equal(iframe.title,'Second');assert.equal(srcWrites,1);
host.transaction('replace-web',draft=>{const node=draft.objects.find(o=>o.id===webId);node.type='core:frame'},{actor:'verification'});
assert.equal(webElement.removed,true);assert.equal(vm.runInContext('paneEls.has('+JSON.stringify(webId)+')',sandbox),false);
vm.runInContext('undo()',sandbox);
webElement=vm.runInContext('paneEls.get('+JSON.stringify(webId)+')',sandbox);
assert.equal(webElement.firstChild.src,'http://127.0.0.1:5320/second');
let mountedDocument=null,registeredAfterPanel=false;
const startup={...sandbox,fetch:async url=>({ok:true,json:async()=>url==='/api/manifest'?{extensions:[{id:'startup-test',module:'extensions/startup-test.mjs'}]}:structuredClone(canonical)}),initialPanelModule:{register(host){
 host.registerPanel({id:'test:startup',label:'Startup',mount({host}){mountedDocument=host.getDocument()}});
 host.registerType('test:after-panel',{defaults:{data:{label:'After panel'}}});registeredAfterPanel=true;
}}};
startup.window=startup;vm.createContext(startup);
for(const name of ['app.js','enhancements.js'])vm.runInContext(fs.readFileSync(new URL(name,import.meta.url),'utf8'),startup);
await vm.runInContext(hostSource.replace('await import(localModuleURL(extension.module,location.href))','initialPanelModule'),startup);
assert.equal(mountedDocument.title,canonical.title);assert.equal(mountedDocument.objects[0].id,'frame');
assert.equal(registeredAfterPanel,true);
console.log('PASS: panel startup can read state; pane synchronization, resets, nonspatial notes, undo/redo, export, and readback.');
