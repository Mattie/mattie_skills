/* Exploration affordances: immutable reset sources, named groups, descriptions and paste. */
function migrateDocument(){
 if(!doc)return;doc.groups ||= [];doc.originals ||= {};
 for(const f of doc.frames){
  f.pieces ||= [];f.controls ||= [];f.variants ||= {};
  if(!doc.originals[f.id])doc.originals[f.id]={...clone(f),pieces:clone(f.baseline||f.pieces),capturedAt:now(),source:f.baseline?'retained baseline; frame placement at migration':'first observed state'};
  for(const p of [...(f.baseline||[]),...f.pieces])if(!doc.originals[p.id])doc.originals[p.id]=clone(p);
 }
 for(const g of doc.groups){g.frameIds=g.frameIds.filter(id=>doc.frames.some(f=>f.id===id));if(!doc.originals[g.id])doc.originals[g.id]={x:g.x,y:g.y,members:g.frameIds.map(id=>({id,x:object(id).x,y:object(id).y}))};}
}
const originalObject=object,originalFrameFor=frameFor;
object=id=>doc.groups?.find(g=>g.id===id)||originalObject(id);
frameFor=id=>doc.groups?.find(g=>g.id===id)||originalFrameFor(id);
const CARD_GEOMETRY=Object.freeze({padding:20,header:140,radius:16});
const GROUP_GEOMETRY=Object.freeze({padding:40,header:100,radius:24});
function cardBounds(f){const p=CARD_GEOMETRY.padding,h=CARD_GEOMETRY.header;return {x:f.x-p,y:f.y-h,w:f.w+p*2,h:f.h+h+p};}
function groupBounds(g){const cards=g.frameIds.map(id=>doc.frames.find(f=>f.id===id)).filter(Boolean).map(cardBounds);if(!cards.length)return null;const pad=GROUP_GEOMETRY.padding,head=GROUP_GEOMETRY.header,x=Math.min(...cards.map(b=>b.x))-pad,y=Math.min(...cards.map(b=>b.y))-head;return {x,y,w:Math.max(...cards.map(b=>b.x+b.w))-x+pad,h:Math.max(...cards.map(b=>b.y+b.h))-y+pad};}
function syncGroups(){for(const g of doc.groups){const b=groupBounds(g);if(b)Object.assign(g,b)}}
// All layout bounds are world-space; only camera navigation uses screen dimensions.
function unionBounds(boxes){return {x:Math.min(...boxes.map(b=>b.x)),y:Math.min(...boxes.map(b=>b.y)),w:Math.max(...boxes.map(b=>b.x+b.w))-Math.min(...boxes.map(b=>b.x)),h:Math.max(...boxes.map(b=>b.y+b.h))-Math.min(...boxes.map(b=>b.y))};}
function fitBounds(bounds,maxZoom=3){const leftMargin=85,rightMargin=$('inspector').hidden?35:310,verticalMargin=30,availableWidth=Math.max(200,surface.clientWidth-leftMargin-rightMargin),availableHeight=Math.max(150,surface.clientHeight-verticalMargin*2);camera.z=Math.max(.12,Math.min(availableWidth/Math.max(1,bounds.w),availableHeight/Math.max(1,bounds.h),maxZoom));camera.x=leftMargin+availableWidth/2-(bounds.x+bounds.w/2)*camera.z;camera.y=verticalMargin+availableHeight/2-(bounds.y+bounds.h/2)*camera.z;draw();}
fit=()=>{if(!doc?.frames.length)return;migrateDocument();syncGroups();fitBounds(unionBounds([...doc.frames.map(cardBounds),...doc.groups.map(groupBounds).filter(Boolean)]),1);};
$('fit').onclick=()=>fit();
const originalHit=hit;
hit=p=>{for(const f of [...doc.frames].reverse()){const b=cardBounds(f);if(p.x>=b.x&&p.x<=b.x+b.w&&p.y>=b.y&&p.y<=f.y)return f.id;for(const o of [...(f.pieces||[])].reverse()){if(o.locked)continue;const q=local(p,f,o);if(typeof hitRegisteredPiece==='function'?hitRegisteredPiece(q,o):(q.x>=0&&q.y>=0&&q.x<=o.w&&q.y<=o.h))return o.id}if(p.x>=b.x&&p.x<=b.x+b.w&&p.y>=f.y&&p.y<=b.y+b.h)return f.id;}for(const g of [...doc.groups].reverse())if(p.x>=g.x&&p.x<=g.x+g.w&&p.y>=g.y&&p.y<=g.y+g.h)return g.id;return null};
const originalDraw=draw;
draw=()=>{migrateDocument();if(!doc)return;syncGroups();originalDraw();};
function paintWorkspaceCards(){
 for(const g of doc.groups){rounded(g.x,g.y,g.w,g.h,GROUP_GEOMETRY.radius);ctx.fillStyle=selected.includes(g.id)?'#ddd5eb':'#e1dce9';ctx.fill();ctx.strokeStyle=selected.includes(g.id)?'#9270c1':'#c3b7d3';ctx.lineWidth=selected.includes(g.id)?3:1.5;ctx.stroke();ctx.save();ctx.beginPath();ctx.rect(g.x,g.y,Math.max(20,g.w-160),GROUP_GEOMETRY.header);ctx.clip();text(g.label,g.x+28,g.y+41,27,'#574467');if(g.description)text(g.description.slice(0,100),g.x+28,g.y+74,18,'#71677a');ctx.restore();}
 for(const f of doc.frames){const b=cardBounds(f);rounded(b.x,b.y,b.w,b.h,CARD_GEOMETRY.radius);ctx.fillStyle='#f8f7f4';ctx.fill();ctx.strokeStyle=selected.includes(f.id)?'#a08ac1':'#d0cccf';ctx.lineWidth=1.5;ctx.stroke();ctx.save();ctx.beginPath();ctx.rect(b.x,b.y,Math.max(20,b.w-160),CARD_GEOMETRY.header);ctx.clip();text(f.label,f.x+8,b.y+40,24,'#49434f');if(f.description){const lines=wrapText(f.description,Math.max(15,Math.floor((f.w-160)/9.9)));lines.slice(0,2).forEach((line,i)=>text(line,f.x+8,b.y+76+i*25,18,'#77707d'));}ctx.restore();}
}
function intersects(a,b,gap=0){return a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;}
function relocateGroupToFreeSpace(g){
 syncGroups();const box=groupBounds(g);if(!box)return;const others=doc.frames.filter(f=>!g.frameIds.includes(f.id)).map(cardBounds);for(const other of doc.groups)if(other.id!==g.id&&!other.frameIds.some(id=>g.frameIds.includes(id))){const b=groupBounds(other);if(b)others.push(b)}const gap=50;
 if(!others.some(o=>intersects(box,o,gap)))return;
 const xs=[0],ys=[0];for(const o of others){xs.push(o.x+o.w+gap-box.x,o.x-gap-box.w-box.x);ys.push(o.y+o.h+gap-box.y,o.y-gap-box.h-box.y)}
 const candidates=[];for(const dx of xs)for(const dy of ys)candidates.push({dx,dy,d:dx*dx+dy*dy});candidates.sort((a,b)=>a.d-b.d);const chosen=candidates.find(v=>!others.some(o=>intersects({...box,x:box.x+v.dx,y:box.y+v.dy},o,gap)));if(chosen)for(const id of g.frameIds){const f=object(id);f.x+=chosen.dx;f.y+=chosen.dy;}syncGroups();
}
function tidyGroup(id=selected[0]){const g=object(id);if(g?.kind!=='group')return;change('tidy-group',()=>relocateGroupToFreeSpace(g),{targetId:id});}
function wrapText(value,width){const lines=[];let current='';for(const word of value.split(/\s+/)){if((current+' '+word).length>width&&current){lines.push(current);current=word}else current+=(current?' ':'')+word}if(current)lines.push(current);return lines;}
const originalChange=change;
change=(type,fn,data={})=>{migrateDocument();originalChange(type,()=>{fn();migrateDocument()},data)};
const originalInspector=renderInspector;
renderInspector=()=>{originalInspector();const o=object(selected[0]);if(!o)return;const isGroup=o.kind==='group',isFrame=doc.frames.some(f=>f.id===o.id);$('descriptionTools').hidden=!(isGroup||isFrame);$('panelDescription').value=o.description||'';$('panelName').value=o.label;$('resetMockup').hidden=!isFrame||o.kind==='web';$('ungroup').hidden=!isGroup;$('tidyGroup').hidden=!isGroup;$('groupSelection').disabled=!selected.some(id=>doc.frames.some(f=>f.id===id));$('duplicate').hidden=isGroup;$('delete').textContent=isGroup?'Ungroup':'Remove';if(isGroup){$('pieceTools').hidden=true;$('proposalControls').replaceChildren();$('selectionScope').textContent=`Group · ${o.frameIds.length} rigs`;}};
const descriptionTools=document.createElement('div');descriptionTools.id='descriptionTools';descriptionTools.innerHTML='<label for="panelName">Panel name</label><input id="panelName"><label for="panelDescription">What is this panel exploring?</label><textarea id="panelDescription" rows="2" placeholder="A short description above the panel"></textarea><button id="updateDescription">Update panel</button>';
$('proposalControls').before(descriptionTools);
const resetButton=document.createElement('button');resetButton.id='resetMockup';resetButton.textContent='Reset whole mockup';resetButton.title='Restore original pieces and geometry, keeping notes';$('proposalControls').after(resetButton);
const groupButton=document.createElement('button');groupButton.id='groupSelection';groupButton.textContent='Group selected rigs';$('proposalControls').after(groupButton);
const ungroupButton=document.createElement('button');ungroupButton.id='ungroup';ungroupButton.textContent='Ungroup rigs';$('proposalControls').after(ungroupButton);
const tidyButton=document.createElement('button');tidyButton.id='tidyGroup';tidyButton.textContent='Tidy group';tidyButton.title='Move this group clear of unrelated panels, keeping its layout';$('proposalControls').after(tidyButton);tidyButton.onclick=()=>tidyGroup();
function setDescription(id,description,label){const o=object(id);if(!o||(!doc.frames.includes(o)&&o.kind!=='group'))return;change('describe-panel',()=>{o.description=String(description).slice(0,1000);if(label?.trim())o.label=label.trim().slice(0,160)},{targetId:id});}
$('updateDescription').onclick=()=>setDescription(selected[0],$('panelDescription').value,$('panelName').value);
function resetTarget(id,part='all'){
 const o=object(id),base=doc.originals[id];if(!o||!base||o.locked)return;
 change('reset-'+part,()=>{
  if(o.kind==='group'){for(const member of base.members||[]){const f=object(member.id);if(f&&o.frameIds.includes(f.id)){f.x=member.x;f.y=member.y;}}return}
  const fields=part==='position'?['x','y']:part==='size'?['w','h']:part==='rotation'?['rotation']:['x','y','w','h','rotation'];
  for(const key of fields)o[key]=base[key]??(key==='rotation'?0:o[key]);
  // All restores content too, including panel captions, built-in text/images and added fields.
  // Notes live separately and retain their stable target IDs.
  if(part==='all'){const restored=clone(base);restored.id=id;if(!('label' in restored))restored.label=o.label;for(const key of Object.keys(o))delete o[key];Object.assign(o,restored);}
  if(doc.frames.includes(o)&&part==='all'&&o.kind!=='web'){o.pieces=clone(base.pieces);o.variant='Original';o.variants={};o.baseline=clone(base.pieces);selected=[o.id]}
  else if(!doc.frames.includes(o)){frameFor(id).variant='Custom';}
 },{targetId:id,baselineCapturedAt:base.capturedAt});
}
$('resetMockup').onclick=()=>resetTarget(selected[0]);
function createGroup(frameIds=selected.filter(id=>doc.frames.some(f=>f.id===id)),label){
 frameIds=[...new Set(frameIds)].filter(id=>doc.frames.some(f=>f.id===id));if(!frameIds.length){toast('Select one or more screen titles first.');return}
 label=label||'Option '+String.fromCharCode(65+doc.groups.length);if(!label.trim())return;
 let created;change('create-group',()=>{for(const g of doc.groups)g.frameIds=g.frameIds.filter(id=>!frameIds.includes(id));doc.groups=doc.groups.filter(g=>g.frameIds.length);created={id:uid(),kind:'group',label:label.trim(),description:'',frameIds};Object.assign(created,groupBounds(created));doc.groups.push(created);relocateGroupToFreeSpace(created);selected=[created.id]});return created.id;
}
function ungroup(id=selected[0]){if(!doc.groups.some(g=>g.id===id))return;change('ungroup',()=>{const g=object(id);selected=[...g.frameIds];doc.groups=doc.groups.filter(g=>g.id!==id)},{targetId:id});}
$('groupSelection').onclick=()=>createGroup();$('ungroup').onclick=()=>ungroup();
const originalRemove=remove;remove=()=>{if(selected.some(id=>object(id)?.kind==='group')){change('ungroup',()=>{const ids=selected.filter(id=>object(id)?.kind==='group');doc.groups=doc.groups.filter(g=>!ids.includes(g.id));selected=selected.filter(id=>!ids.includes(id))});return}originalRemove()};$('delete').onclick=()=>remove();
const originalDuplicate=duplicate;duplicate=()=>{const group=object(selected[0]);if(group?.kind!=='group'){originalDuplicate();return}change('duplicate-group',()=>{const newIds=[];for(const fid of group.frameIds){const original=object(fid);if(!original)continue;const copy=clone(original),ids=new Map();copy.id=uid();copy.x+=group.w+100;for(const p of copy.pieces){const old=p.id;p.id=uid();ids.set(old,p.id)}for(const control of copy.controls){control.id=uid();for(const option of control.options)for(const patch of option.patches)patch.targetId=ids.get(patch.targetId)||patch.targetId;}copy.baseline=clone(copy.pieces);copy.variants={};doc.frames.push(copy);newIds.push(copy.id)}const copy={id:uid(),kind:'group',label:group.label+' copy',description:group.description,frameIds:newIds};Object.assign(copy,groupBounds(copy));doc.groups.push(copy);relocateGroupToFreeSpace(copy);selected=[copy.id]});};$('duplicate').onclick=()=>duplicate();
const menu=document.createElement('div');menu.id='objectMenu';menu.hidden=true;menu.setAttribute('role','menu');document.body.append(menu);
function closeMenu(){menu.hidden=true}
function showMenu(e){e.preventDefault();const id=hit(world(e));if(!id){closeMenu();return}pick(selected.includes(id)?[id,...selected.filter(other=>other!==id)]:[id]);const o=object(id);menu.replaceChildren();const heading=document.createElement('strong');heading.textContent=o.label;menu.append(heading);const add=(label,fn)=>{const b=document.createElement('button');b.type='button';b.setAttribute('role','menuitem');b.textContent=label;b.onclick=()=>{closeMenu();fn()};menu.append(b)};
 const addReset=(entries)=>{const wrap=document.createElement('div');wrap.className='reset-menu';const trigger=document.createElement('button');trigger.type='button';trigger.setAttribute('role','menuitem');trigger.setAttribute('aria-haspopup','menu');trigger.setAttribute('aria-expanded','false');trigger.textContent='Reset  ›';const sub=document.createElement('div');sub.className='reset-submenu';sub.setAttribute('role','menu');sub.hidden=true;const open=()=>{sub.hidden=false;trigger.setAttribute('aria-expanded','true');const r=wrap.getBoundingClientRect();sub.classList.toggle('open-left',r.right+220>innerWidth);sub.style.top='-7px';const bounds=sub.getBoundingClientRect();if(bounds.bottom>innerHeight-8)sub.style.top=(-7-(bounds.bottom-innerHeight+8))+'px';if(sub.getBoundingClientRect().top<8)sub.style.top=(8-r.top)+'px';};const close=()=>{sub.hidden=true;trigger.setAttribute('aria-expanded','false')};trigger.onclick=open;wrap.onpointerenter=open;wrap.onpointerleave=close;trigger.onkeydown=event=>{if(event.key==='ArrowRight'){event.preventDefault();event.stopPropagation();open();sub.querySelector('button')?.focus()}};sub.onkeydown=event=>{if(event.key==='ArrowLeft'||event.key==='Escape'){event.preventDefault();event.stopPropagation();close();trigger.focus()}};for(const [label,part]of entries){const b=document.createElement('button');b.type='button';b.setAttribute('role','menuitem');b.textContent=label;b.onclick=()=>{closeMenu();resetTarget(id,part)};sub.append(b)}wrap.append(trigger,sub);menu.append(wrap);};
 add('Add note',()=>$('noteText').focus());
 if(o.kind==='group'){add('Rename / describe',()=>$('panelName').focus());add('Tidy group',()=>tidyGroup(id));addReset([['Position','position']]);add('Duplicate group',duplicate);add('Ungroup (keep rigs)',()=>ungroup(id))}
 else{addReset([['All changes','all'],['Position','position'],['Size','size'],...(!doc.frames.includes(o)?[['Rotation','rotation']]:[])]);add('Duplicate',duplicate);add('Remove',remove);if(doc.frames.includes(o)){add('Rename / describe',()=>$('panelName').focus());add('Group selected rigs',()=>createGroup())}}
 menu.hidden=false;menu.style.left=Math.min(e.clientX,innerWidth-menu.offsetWidth-12)+'px';menu.style.top=Math.max(8,Math.min(e.clientY,innerHeight-menu.offsetHeight-12))+'px';menu.querySelector('button')?.focus();}
menu.addEventListener('keydown',e=>{e.stopPropagation();if(e.key==='Escape'){e.preventDefault();closeMenu();c.focus();return}if(!['ArrowDown','ArrowUp'].includes(e.key))return;e.preventDefault();const scope=e.target.closest('[role=menu]')||menu;const buttons=[...scope.querySelectorAll('button')].filter(b=>!b.closest('[hidden]')&&b.getBoundingClientRect().height>0);const i=buttons.indexOf(document.activeElement),step=e.key==='ArrowDown'?1:-1;buttons[(i+step+buttons.length)%buttons.length]?.focus()});c.addEventListener('contextmenu',showMenu);window.addEventListener('pointerdown',e=>{if(!menu.contains(e.target))closeMenu()});window.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu()});
function importReference(file){return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onerror=reject;reader.onload=()=>{const im=new Image();im.onerror=reject;im.onload=()=>{let id;change('paste-reference',()=>{const f={id:uid(),kind:'screen',label:file.name||'Pasted reference',description:'Reference image · select it to add a note or lift a cutout',x:(surface.clientWidth/2-camera.x)/camera.z-im.width/2,y:(surface.clientHeight/2-camera.y)/camera.z-im.height/2,w:im.width,h:im.height,pieces:[piece(file.name||'Pasted image',0,0,im.width,im.height,'image',{src:reader.result})],controls:[],variants:{},variant:'Original'};f.baseline=clone(f.pieces);doc.frames.push(f);id=f.id;selected=[f.pieces[0].id]});toast('Reference pasted. Select the image to add a note.');resolve(id)};im.src=reader.result};reader.readAsDataURL(file)});}
window.addEventListener('paste',e=>{if(['INPUT','TEXTAREA'].includes(e.target.tagName)||e.target.isContentEditable)return;const files=[...(e.clipboardData?.items||[])].filter(i=>i.type.startsWith('image/')).map(i=>i.getAsFile()).filter(Boolean);if(!files.length)return;e.preventDefault();files.forEach(file=>importReference(file).catch(()=>toast('Could not read that image.')))});
surface.addEventListener('dragover',e=>{if([...e.dataTransfer.items].some(i=>i.type.startsWith('image/')))e.preventDefault()});surface.addEventListener('drop',e=>{const fs=[...e.dataTransfer.files].filter(f=>f.type.startsWith('image/'));if(fs.length){e.preventDefault();fs.forEach(f=>importReference(f).catch(()=>toast('Could not read that image.')))}});
// File import shares the independent-reference path; adding images never rebases existing mocks.
$('imageFile').onchange=e=>{const file=e.target.files[0];if(file)importReference(file).catch(()=>toast('Could not read that image.'));e.target.value=''};
Object.assign(window.placementRig,{setDescription,createGroup,ungroup,tidyGroup,resetTarget,importReference});

// A focused view is camera navigation, not a layout edit or an approval.
function focusTarget(id=selected[0],select=false){
 const target=object(id);if(!target)return;const group=target.kind==='group'?target:null;
 if(select){selected=[target.id];renderInspector()}
 const bounds=group?groupBounds(group):cardBounds(frameFor(id));if(bounds)fitBounds(bounds);
}
const focusButton=document.createElement('button');focusButton.id='focusRig';focusButton.textContent='Focus rig';focusButton.title='Fit this rig or group in the canvas';$('selectionScope').after(focusButton);focusButton.onclick=()=>focusTarget();
// Header controls live in screen space so their hit targets remain usable while zooming.
const focusHandles=document.createElement('div');focusHandles.id='focusHandles';focusHandles.setAttribute('aria-label','Focus canvas panels');surface.append(focusHandles);
const focusHandleButtons=new Map();
function focusFromHeader(id){
 closeMenu();const target=object(id);if(!target)return;
 const frameIds=target.kind==='group'?target.frameIds:[id];
 if(selected.some(sid=>sid!==id&&!frameIds.includes(frameFor(sid)?.id)))pick([]);
 focusTarget(id);
}
function syncFocusHandles(){
 const targets=[...doc.groups,...doc.frames],ids=new Set(targets.map(t=>t.id));
 for(const [id,button]of focusHandleButtons)if(!ids.has(id)){button.remove();focusHandleButtons.delete(id)}
 for(const target of targets){let button=focusHandleButtons.get(target.id);if(!button){button=document.createElement('button');button.type='button';button.className='pane-focus';button.textContent='⊙ Focus';button.onclick=e=>{e.stopPropagation();focusFromHeader(target.id)};button.onpointerdown=e=>e.stopPropagation();focusHandles.append(button);focusHandleButtons.set(target.id,button)}
  const bounds=target.kind==='group'?target:cardBounds(target);
  const compact=camera.z<.5,width=compact?28:70,header=(target.kind==='group'?GROUP_GEOMETRY.header:CARD_GEOMETRY.header)*camera.z;button.classList.toggle('compact',compact);button.textContent=compact?'⊙':'⊙ Focus';const x=camera.x+(bounds.x+bounds.w)*camera.z-width-8,y=camera.y+bounds.y*camera.z+9;
  button.style.left=x+'px';button.style.top=y+'px';
  button.hidden=header<38||bounds.w*camera.z<90||x+width<0||x>surface.clientWidth||y+28<0||y>surface.clientHeight;
  button.setAttribute('aria-label','Focus '+target.label);button.title='Focus '+target.label+' · F when selected';
 }
}
window.addEventListener('keydown',e=>{
 if(e.defaultPrevented||e.ctrlKey||e.metaKey||e.altKey||e.key.toLowerCase()!=='f'||!menu.hidden)return;
 if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||e.target.isContentEditable)return;
 if(!selected.length)return;e.preventDefault();focusTarget();
});
const navigation=document.createElement('div');navigation.id='focusNavigation';navigation.setAttribute('aria-label','Example views');document.querySelector('header .grow').before(navigation);
let focusNavigationKey='',initialFocusHandled=false;
const drawWithCards=draw;
draw=()=>{if(!doc)return;migrateDocument();const key=JSON.stringify(doc.focusTargets||[]);if(key!==focusNavigationKey){focusNavigationKey=key;navigation.replaceChildren();for(const item of doc.focusTargets||[]){const button=document.createElement('button');button.textContent=item.label;button.onclick=()=>{pick([]);focusTarget(item.targetId)};navigation.append(button)}}if(!initialFocusHandled){initialFocusHandled=true;if(doc.defaultFocus&&!doc.camera&&object(doc.defaultFocus)){focusTarget(doc.defaultFocus);return}}drawWithCards();syncFocusHandles();};

function geometryOf(o){return {x:o.x,y:o.y,w:o.w,h:o.h,rotation:o.rotation||0};}
context=()=>{
 migrateDocument();const changes=[];
 for(const f of doc.frames){const originals=doc.originals[f.id]?.pieces||f.baseline||[],currentIds=new Set(f.pieces.map(p=>p.id));
  for(const p of f.pieces){const original=doc.originals[p.id]||originals.find(o=>o.id===p.id),before=original?geometryOf(original):null,after=geometryOf(p),delta={};
   for(const key of ['x','y','w','h','rotation'])if(before&&Math.abs(after[key]-before[key])>.0001)delta[key]=after[key]-before[key];
   if(!originals.some(o=>o.id===p.id)||!before||Object.keys(delta).length)changes.push({targetId:p.id,frameId:f.id,label:p.label,status:originals.some(o=>o.id===p.id)?'geometry-changed':'added',locked:!!p.locked,before,after,delta,source:p.source||f.source||null,provenance:p.provenance||f.provenance||null,metadata:p.metadata||null,variant:f.variant,evidenceEventIds:doc.events.filter(e=>e.targetId===p.id||(e.frameId===f.id&&e.type==='proposal-preview')||e.changes?.some(c=>c.targetId===p.id)).map(e=>e.id)});
  }
  for(const p of originals)if(!currentIds.has(p.id))changes.push({targetId:p.id,frameId:f.id,label:p.label,status:'removed',before:geometryOf(p),after:null,source:p.source||f.source||null,metadata:p.metadata||null});
 }
 return {workspace:doc.title,revision:doc.revision,at:now(),source:clone(doc.source||null),provenance:clone(doc.provenance||null),metadata:clone(doc.metadata||null),interpretation:'Seed and proposed layouts are reference material, not user approval. Geometry changes describe the current arrangement; notes and events provide intent.',selection:selected.map(id=>({targetId:id,frameId:frameFor(id)?.id,label:object(id)?.label,geometry:geometryOf(object(id))})),changes,notes:clone(doc.notes),recentEvents:clone(doc.events.slice(-30)),voiceConnected:false};
};
Object.assign(window.placementRig,{focusTarget,getContext:context});
window.removeEventListener('resize',originalDraw);
window.addEventListener('resize',draw);
