/* Canonical documents and the local extension host surround the retained canvas interaction layer. */
(async function startToolkit(){
 const model=await import('/toolkit/model.mjs');
 const {createRegistry,localModuleURL,assertActor}=await import('/toolkit/canvas/registry.mjs');
 const registry=createRegistry(),modules=[],stateListeners=new Set(),selectionListeners=new Set();
 let canonicalBase=null,operationActor='user',activePointerTool=null;
 const canonical=()=>model.fromCanvasDocument({...doc,camera},canonicalBase||{});
 const withActor=(actor,fn)=>{const previous=operationActor;operationActor=assertActor(actor);try{return fn()}finally{operationActor=previous}};
 function emit(listeners,value){for(const listener of listeners)try{listener(clone(value))}catch(error){console.error('Extension subscription failed',error)}}
 const originalRecord=record;record=(type,data={})=>{originalRecord(type,{...data,actor:operationActor});emit(stateListeners,canonical());if(type==='selection')emit(selectionListeners,selected);};
 const toolbar=document.createElement('div');toolbar.id='extensionToolbar';document.querySelector('header .grow').before(toolbar);
 const inspector=document.createElement('div');inspector.id='extensionInspector';$('notes').before(inspector);
 const canonicalNode=id=>canonical().objects.find(o=>o.id===id);
 function nodeForPiece(p){return {id:p.id,type:p.registeredType||`core:${p.kind}`,parentId:frameFor(p.id)?.id,geometry:geometryOf(p),data:p.registeredType?clone(p.extensionData||{}):clone(p),source:p.source,locked:!!p.locked};}
 function checkDocument(value){model.validateDocument(value);for(const node of value.objects)registry.validate(node);return value;}
 function transaction(label,mutator,{actor='agent'}={}){
  const before=canonical(),draft=clone(before);const result=mutator(draft);if(result&&typeof result.then==='function')throw Error('Transactions must be synchronous');checkDocument(draft);
  const oldById=new Map(before.objects.map(o=>[o.id,o])),newById=new Map(draft.objects.map(o=>[o.id,o]));
  const changes=[...new Set([...oldById.keys(),...newById.keys()])].filter(id=>JSON.stringify(oldById.get(id))!==JSON.stringify(newById.get(id))).map(id=>({targetId:id,before:oldById.get(id)||null,after:newById.get(id)||null}));
  withActor(actor,()=>change(label,()=>{doc=model.toCanvasDocument(draft);selected=selected.filter(id=>object(id)&&!object(id).locked)},{changes}));return result;
 }
 const host={
  registerType:(type,definition)=>registry.registerType(type,definition),
  registerCommand:definition=>{const dispose=registry.registerCommand(definition);refreshExtensionChrome();return dispose},
  registerTool:definition=>{const dispose=registry.registerTool(definition);refreshExtensionChrome();return dispose},
  registerPanel:definition=>{const dispose=registry.registerPanel(definition);refreshExtensionChrome();return dispose},
  getDocument:()=>clone(canonical()),getSelection:()=>[...selected],
  subscribeState(listener){stateListeners.add(listener);return ()=>stateListeners.delete(listener)},
  subscribeSelection(listener){selectionListeners.add(listener);return ()=>selectionListeners.delete(listener)},
  transaction,
  select(ids,{actor='agent'}={}){return withActor(actor,()=>pick(ids))},
  addNote(text,targetId=selected[0],{actor='agent'}={}){
   if(object(targetId))return withActor(actor,()=>addNote(text,targetId,actor));
   if(!text.trim()||!canonicalNode(targetId)){toast('Choose an existing object and enter a note.');return}
   return transaction('note',draft=>{draft.notes.push({id:uid(),targetId,text:text.trim(),at:now(),source:actor})},{actor});
  },
  focus:focusTarget,
  createObject(type,overrides={},options={}){
   let createdId;transaction('create-object',draft=>{
    const node=registry.create(type,{id:uid(),...overrides});createdId=node.id;
    if(node.geometry&&!['core:frame','core:web','core:group'].includes(type)&&!node.parentId){
     let parent=draft.objects.find(o=>o.id===frameFor(selected[0])?.id&&o.type==='core:frame')||draft.objects.find(o=>o.type==='core:frame');
     if(!parent){parent=registry.create('core:frame',{id:uid()});draft.objects.push(parent)}node.parentId=parent.id;
    }
    draft.objects.push(node);
   },options);withActor(options.actor||'agent',()=>pick([createdId]));focusTarget(createdId);return createdId;
  },
  notify:toast,
 };
 window.thoughtRig=host;

 // Images, cutouts, text, containers and embedded pages register through the same boundary.
 function rectangleHit({point,object}){return point.x>=0&&point.y>=0&&point.x<=object.geometry.w&&point.y<=object.geometry.h}
 function imageRender({ctx,object}){
  const data=object.data,{w,h}=object.geometry;if(!data.src)return;
  const url=new URL(data.src,new URL('/',location.href)).href;let image=images.get(url);
  if(!image){image=new Image();image.onload=draw;image.src=url;images.set(url,image)}
  if(image.complete&&image.naturalWidth){if(data.crop)ctx.drawImage(image,...data.crop,0,0,w,h);else ctx.drawImage(image,0,0,w,h)}
 }
 const imageDefinition={defaults:{geometry:{x:30,y:30,w:300,h:200,rotation:0},data:{label:'Image',src:''}},validate:o=>typeof o.data.src==='string'||'Image src must be a string',render:imageRender,hitTest:rectangleHit};
 registry.registerType('core:image',imageDefinition);registry.registerType('core:cutout',imageDefinition);
 registry.registerType('core:text',{defaults:{geometry:{x:30,y:30,w:280,h:55,rotation:0},data:{label:'Text',text:'Add a thought'}},render:({ctx,object})=>{ctx.font='22px "Segoe UI", sans-serif';ctx.fillStyle='#e5e2ee';ctx.textAlign='left';ctx.fillText(object.data.text||object.data.label||'',5,32)},hitTest:rectangleHit,inspector:[{key:'text',label:'Text',input:'text'}]});
 registry.registerType('core:frame',{defaults:{geometry:{x:0,y:0,w:800,h:500,rotation:0},data:{label:'Untitled rig',description:'',background:'#22333f',controls:[],variants:{},variant:'Original'}},render:({ctx,object})=>{ctx.fillStyle=object.data.background||'#22333f';ctx.fillRect(0,0,object.geometry.w,object.geometry.h)}});
 registry.registerType('core:group',{defaults:{geometry:{x:0,y:0,w:800,h:600},data:{label:'Option',description:'',frameIds:[]}},render(){}});
 registry.registerType('core:web',{defaults:{geometry:{x:0,y:0,w:850,h:540},data:{label:'Web rig',description:'',url:'/toolkit/canvas/sample-rig.html',allowedOrigin:location.origin}},validate:o=>{try{return ['http:','https:'].includes(new URL(o.data.url,location.origin).protocol)||'Web pane needs an HTTP URL'}catch{return 'Invalid web pane URL'}},render(){},mountDOM({element,object}){const iframe=document.createElement('iframe');iframe.sandbox='allow-scripts allow-forms allow-same-origin';iframe.referrerPolicy='no-referrer';iframe.src=new URL(object.data.url,location.origin).href;iframe.title=object.data.label||'Embedded rig';element.append(iframe)}});
 host.registerCommand({id:'core:add-frame',label:'Add panel',placement:'toolbar',run:({host,actor})=>host.createObject('core:frame',{geometry:{x:(surface.clientWidth/2-camera.x)/camera.z-400,y:(surface.clientHeight/2-camera.y)/camera.z-250}},{actor})});

 window.paintRegisteredFrame=f=>{const definition=registry.types.get(f.kind==='web'?'core:web':'core:frame');definition?.render?.({ctx,object:{id:f.id,type:f.kind==='web'?'core:web':'core:frame',geometry:geometryOf(f),data:f},selected:selected.includes(f.id),host})};
 paintPiece=(p,f)=>{
  const node=nodeForPiece(p),definition=registry.types.get(node.type),{w,h}=node.geometry;
  ctx.save();ctx.translate(p.x+w/2,p.y+h/2);ctx.rotate((p.rotation||0)*Math.PI/180);ctx.translate(-w/2,-h/2);
  try{if(definition?.render)definition.render({ctx,object:node,selected:selected.includes(p.id),host});else{ctx.fillStyle='#655a73';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#c4b5d5';ctx.setLineDash([7,5]);ctx.strokeRect(0,0,w,h);ctx.setLineDash([]);text(node.data.label||node.type,12,30,16,'#fff');text('Unavailable type · data preserved',12,54,12,'#eee')}}catch(error){ctx.fillStyle='#713c51';ctx.fillRect(0,0,w,h);text('Extension render failed',10,25,14);console.error(error)}
  if(selected.includes(p.id)){ctx.strokeStyle='#ad86ff';ctx.lineWidth=2/camera.z;ctx.strokeRect(0,0,w,h);for(const [x,y]of [[0,0],[w,0],[0,h],[w,h]]){ctx.fillStyle='#fff';ctx.fillRect(x-4/camera.z,y-4/camera.z,8/camera.z,8/camera.z)}ctx.beginPath();ctx.moveTo(w/2,0);ctx.lineTo(w/2,-25/camera.z);ctx.stroke();ctx.beginPath();ctx.arc(w/2,-25/camera.z,5/camera.z,0,7);ctx.fill();ctx.stroke()}ctx.restore();
 };
 window.hitRegisteredPiece=(point,p)=>{const node=nodeForPiece(p),definition=registry.types.get(node.type);return definition?.hitTest?!!definition.hitTest({point,object:node}):rectangleHit({point,object:node})};
 syncPanes=()=>{for(const [id,el]of paneEls)if(!doc.frames.some(f=>f.id===id)){el.remove();paneEls.delete(id)}for(const f of doc.frames.filter(f=>f.kind==='web')){let el=paneEls.get(f.id);if(!el){el=document.createElement('div');el.className='webpane';registry.types.get('core:web').mountDOM({element:el,object:{id:f.id,type:'core:web',data:f,geometry:geometryOf(f)},host});$('panes').append(el);paneEls.set(f.id,el)}el.style.width=f.w+'px';el.style.height=f.h+'px';el.style.transform=`translate(${camera.x+f.x*camera.z}px,${camera.y+f.y*camera.z}px) scale(${camera.z})`;el.classList.toggle('live',interacting===f.id)}};

 const baseInspector=renderInspector;
 renderInspector=()=>{baseInspector();inspector.replaceChildren();if(!selected.length)return;const node=canonicalNode(selected[0]);if(!node)return;const definition=registry.types.get(node.type);
  if(!definition){const note=document.createElement('p');note.className='muted';note.textContent=`${node.type} is unavailable. Its data and notes will be preserved.`;inspector.append(note);return}
  for(const field of definition.inspector||[]){const label=document.createElement('label');label.textContent=field.label;const input=document.createElement('input');input.type=field.input||'text';input.value=node.data[field.key]??'';if(field.min!==undefined)input.min=field.min;if(field.step!==undefined)input.step=field.step;input.disabled=!!node.locked;input.onchange=()=>{try{transaction('edit-domain-field',draft=>{const target=draft.objects.find(o=>o.id===node.id);target.data[field.key]=input.type==='number'?Number(input.value):input.value},{actor:'user'})}catch(error){toast(error.message);renderInspector()}};label.append(input);inspector.append(label)}
 };
 const panelInstances=new Map();
 function refreshExtensionChrome(){
  toolbar.replaceChildren();for(const command of registry.commands.values())if(command.placement==='toolbar'){const button=document.createElement('button');button.textContent=command.label;button.onclick=()=>runCommand(command);toolbar.append(button)}
  for(const pointerTool of registry.tools.values()){const button=document.createElement('button');button.textContent=pointerTool.label;button.onclick=()=>{activePointerTool=pointerTool;setTool('select');activePointerTool=pointerTool;toast(`${pointerTool.label} tool active · Escape to leave`)};toolbar.append(button)}
  for(const panel of registry.panels.values()){if(!panelInstances.has(panel.id)){const element=document.createElement('section');element.className='extension-panel';element.hidden=true;document.body.append(element);panel.mount({element,host});panelInstances.set(panel.id,element)}const button=document.createElement('button');button.textContent=panel.label;button.onclick=()=>{const el=panelInstances.get(panel.id);el.hidden=!el.hidden};toolbar.append(button)}
 }
 function runCommand(command){try{const selection=selected.map(canonicalNode).filter(Boolean);if(command.when&&!command.when({selection}))return;command.run({host,selection,actor:'user'})}catch(error){toast(error.message)}}
 menu.addEventListener('contextmenu',event=>event.preventDefault());
 c.addEventListener('contextmenu',()=>{if(menu.hidden)return;const selection=selected.map(canonicalNode).filter(Boolean);for(const command of registry.commands.values())if(command.placement==='context'&&(!command.when||command.when({selection}))){const button=document.createElement('button');button.textContent=command.label;button.setAttribute('role','menuitem');button.onclick=()=>{closeMenu();runCommand(command)};menu.append(button)}});
 for(const [eventName,method]of [['pointerdown','onPointerDown'],['pointermove','onPointerMove'],['pointerup','onPointerUp']])c.addEventListener(eventName,event=>{if(!activePointerTool)return;event.preventDefault();event.stopImmediatePropagation();if(eventName==='pointerdown')c.setPointerCapture(event.pointerId);try{activePointerTool[method]?.({point:world(event),event,host})}catch(error){toast(error.message)}},{capture:true});
 const baseSetTool=setTool;setTool=t=>{activePointerTool=null;baseSetTool(t)};
 const baseUndo=undo;undo=(redo=false)=>{baseUndo(redo);emit(selectionListeners,selected)};$('undo').onclick=()=>undo();$('redo').onclick=()=>undo(true);

 save=async()=>{if(save.pending)return;save.pending=true;try{const snapshot=canonical();checkDocument(snapshot);const response=await fetch('/api/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expectedRevision:savedRevision,document:snapshot})});if(!response.ok)throw Error(response.status===409?'Workspace changed elsewhere. Export before reloading.':'Save failed');const result=await response.json();savedRevision=result.revision;dirty=doc.revision!==snapshot.revision;doc.revision=Math.max(doc.revision,result.revision);canonicalBase={...snapshot,revision:result.revision};status();toast('Saved feedback locally')}finally{save.pending=false}};
 $('save').onclick=()=>save().catch(error=>toast(error.message));$('export').onclick=()=>download(canonical(),'thought-rig-workspace.json');
 $('jsonFile').onchange=async event=>{try{const incoming=JSON.parse(await event.target.files[0].text());checkDocument(incoming);change('import-document',()=>{canonicalBase=clone(incoming);doc=model.toCanvasDocument(incoming);doc.revision=Math.max(doc.revision,savedRevision||0)+1;selected=[]});fit()}catch(error){toast(`Import failed: ${error.message}`)}event.target.value=''};
 context=()=>({...model.readback(canonical(),modules),selection:[...selected],voiceConnected:false});
 window.placementRig={...window.placementRig,getDocument:host.getDocument,getContext:context,host};
 for(const key of ['addControl','applyOption','addNote','setDescription','createGroup','ungroup','tidyGroup','resetTarget'])if(typeof window.placementRig[key]==='function'){const fn=window.placementRig[key];window.placementRig[key]=(...args)=>withActor('agent',()=>fn(...args))}
 try{
  const response=await fetch('/api/manifest');if(!response.ok)throw Error('Workspace manifest unavailable');const manifest=await response.json();
  for(const extension of manifest.extensions||[]){try{const module=await import(localModuleURL(extension.module,location.href));if(typeof module.register!=='function')throw Error('Extension needs register(host)');module.register(host);modules.push(module)}catch(error){console.error(error);const warning=document.createElement('div');warning.className='extension-warning';warning.textContent=`Extension ${extension.id||extension.module} unavailable: ${error.message}`;document.body.append(warning)}}
  const stateResponse=await fetch('/api/state');if(!stateResponse.ok)throw Error('Workspace document unavailable');const incoming=await stateResponse.json();model.validateDocument(incoming);canonicalBase=clone(incoming);doc=model.toCanvasDocument(incoming);savedRevision=incoming.revision;dirty=false;if(incoming.camera)camera=incoming.camera;else fit();status();draw();refreshExtensionChrome();emit(stateListeners,canonical());
 }catch(error){$('saveStatus').textContent='Could not load workspace';toast(error.message);console.error(error)}
})().catch(error=>{console.error(error);$('saveStatus').textContent='Toolkit failed to start';toast(error.message)});
