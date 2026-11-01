import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { toCanvasDocument, fromCanvasDocument } from '../model.mjs';

// Exercise the actual reset/undo implementation, without a server or saved-state writes.
const drawing=new Proxy({}, {get:(_,key)=>key==='createLinearGradient'?()=>({addColorStop(){}}):()=>{}});
function element(){return {hidden:false,style:{},classList:{add(){},remove(){},toggle(){}},append(){},before(){},after(){},remove(){},replaceChildren(){},setAttribute(){},addEventListener(){},removeEventListener(){},getContext:()=>drawing,getBoundingClientRect:()=>({width:1440,height:900,left:0,top:0}),clientWidth:1440,clientHeight:900,querySelector:()=>element(),querySelectorAll:()=>[],focus(){}}}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)};
const frame={id:'frame',type:'core:frame',geometry:{x:0,y:0,w:800,h:500},data:{label:'Test'}};
const cue={id:'cue',type:'demo:cue',parentId:'frame',geometry:{x:30,y:40,w:220,h:100},data:{label:'Original cue',durationSeconds:3}};
const canonical={schemaVersion:2,revision:0,title:'Reset test',objects:[frame,cue],baseline:structuredClone([frame,cue]),notes:[{id:'note',targetId:'cue',text:'Retain my note'}],events:[]};
const sandbox={console,document:{getElementById:get,createElement:element,querySelector:element,body:element()},crypto:webcrypto,devicePixelRatio:1,innerWidth:1440,innerHeight:960,location:{href:'http://127.0.0.1:5320/',origin:'http://127.0.0.1:5320'},fetch:()=>new Promise(()=>{}),URL,Blob,Image:class{},setTimeout:()=>0,clearTimeout(){},addEventListener(){},removeEventListener(){},fixture:toCanvasDocument(canonical)};
sandbox.window=sandbox;vm.createContext(sandbox);
for(const name of ['app.js','enhancements.js'])vm.runInContext(fs.readFileSync(new URL(name,import.meta.url),'utf8'),sandbox);
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
console.log('PASS: selection stays clean; custom and built-in content reset, geometry-only reset, undo/redo, export, and notes.');
