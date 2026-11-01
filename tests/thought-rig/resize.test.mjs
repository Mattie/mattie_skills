import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';

// Dispatch the actual canvas pointer handlers, without a browser or server.
function harness(){
 const listeners=new Map(),elements=new Map();
 const element=id=>({style:{},classList:{add(){},remove(){}},getContext:()=>({}),getBoundingClientRect:()=>({left:0,top:0}),setPointerCapture(){},addEventListener(name,fn){listeners.set(id+':'+name,fn)}});
 const get=id=>{if(!elements.has(id))elements.set(id,element(id));return elements.get(id)};
 const context={document:{getElementById:get},window:{addEventListener(){}},crypto:webcrypto,console,URL,setTimeout:()=>0,clearTimeout(){}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(new URL('../../skills/thought-rig/toolkit/canvas/app.js',import.meta.url),'utf8'),context);
 vm.runInContext('draw=()=>{};renderInspector=()=>{}',context);
 return {context,run:code=>vm.runInContext(code,context),send:(name,point)=>listeners.get('canvas:'+name)({button:0,pointerId:1,clientX:point.x,clientY:point.y,shiftKey:false})};
}
const corners=[[-1,-1],[1,-1],[-1,1],[1,1]];
function worldCorner(o,[sx,sy],frame){
 const a=o.rotation*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
 return {x:frame.x+o.x+o.w/2+c*sx*o.w/2-s*sy*o.h/2,y:frame.y+o.y+o.h/2+s*sx*o.w/2+c*sy*o.h/2};
}
const near=(a,b,label)=>assert.ok(Math.abs(a-b)<1e-8,`${label}: ${a} != ${b}`);

test('all pointer corners enlarge, shrink and clamp with the opposite corner anchored',()=>{
 const h=harness(),frame={id:'frame',kind:'screen',x:90,y:160,w:900,h:700};
 for(const rotation of [0,37,-110])for(const z of [.25,1,3.5])for(const corner of corners)for(const delta of [[65,23],[-47,-31],[-400,-400]]){
  const before={id:'piece',kind:'image',label:'Cutout',x:150,y:170,w:200,h:140,rotation,src:'capture.png',crop:[10,20,200,140]};
  const camera={x:43,y:-29,z};
  h.context.fixture={frames:[{...frame,pieces:[before]}],notes:[{targetId:'piece',text:'Keep this note'}],events:[],revision:0};h.context.cameraFixture=camera;
  h.run("doc=JSON.parse(JSON.stringify(fixture));selected=['piece'];camera=cameraFixture;past=[];future=[];gesture=null");
  const start=worldCorner(before,corner,frame),anchor=worldCorner(before,corner.map(v=>-v),frame);
  const a=rotation*Math.PI/180,dx=corner[0]*delta[0],dy=corner[1]*delta[1];
  const end={x:start.x+dx*Math.cos(a)-dy*Math.sin(a),y:start.y+dx*Math.sin(a)+dy*Math.cos(a)};
  const screen=p=>({x:camera.x+p.x*z,y:camera.y+p.y*z});
  h.send('pointerdown',screen(start));assert.equal(h.run('gesture.kind'),'resize',JSON.stringify({rotation,z,corner}));
  h.send('pointermove',screen(end));h.send('pointerup',screen(end));
  const after=JSON.parse(h.run("JSON.stringify(object('piece'))")),fixed=worldCorner(after,corner.map(v=>-v),frame);
  near(after.w,Math.max(20,before.w+delta[0]),'width');near(after.h,Math.max(20,before.h+delta[1]),'height');
  near(fixed.x,anchor.x,'anchor x');near(fixed.y,anchor.y,'anchor y');assert.equal(after.rotation,rotation);
  assert.equal(after.src,before.src);assert.deepEqual(after.crop,before.crop);assert.equal(h.run('doc.notes[0].targetId'),'piece');
  assert.equal(h.run('doc.events.at(-1).type'),'resize');
  h.run('undo()');near(h.run("object('piece').w"),before.w,'undo width');
  h.run('undo(true)');near(h.run("object('piece').w"),after.w,'redo width');
 }
});

test('locked and non-resizable objects do not start a resize from any corner',()=>{
 const h=harness(),frame={id:'frame',kind:'screen',x:0,y:0,w:900,h:700};
 for(const restriction of [{locked:true},{resizable:false},{registeredType:'test:fixed',extensionData:{resizable:false}}])for(const corner of corners){
  const o={id:'piece',kind:'image',x:150,y:170,w:200,h:140,rotation:25,...restriction};
  h.context.fixture={frames:[{...frame,pieces:[o]}],notes:[],events:[],revision:0};
  h.run("doc=JSON.parse(JSON.stringify(fixture));selected=['piece'];camera={x:0,y:0,z:1};gesture=null");
  const point=worldCorner(o,corner,frame);h.send('pointerdown',point);
  assert.notEqual(h.run('gesture?.kind'),'resize');
  h.send('pointermove',{x:point.x+60,y:point.y+40});h.send('pointerup',point);
  near(h.run("object('piece').w"),200,'fixed width');near(h.run("object('piece').h"),140,'fixed height');
 }
});
