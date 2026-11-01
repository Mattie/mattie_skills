/** Loopback-only workspace server with revision-checked, atomic document saves. */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {loadWorkspace,localPath,readJSON,writeJSON} from './workspace.mjs';
import {validateDocument} from './model.mjs';
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'};

export function createServer(root) {
  const ws=loadWorkspace(root);
  return http.createServer(async(req,res)=>{
    const send=(status,value)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(value));};
    const port=req.socket.localPort,host=req.headers.host;
    if(![`127.0.0.1:${port}`,`localhost:${port}`].includes(host))return send(403,{error:'Loopback host required'});
    if(req.headers.origin&&req.headers.origin!==`http://${host}`)return send(403,{error:'Same-origin requests required'});
    try{
      const url=new URL(req.url,`http://${host}`);
      if(req.method==='GET'&&url.pathname==='/api/manifest')return send(200,ws.manifest);
      if(req.method==='GET'&&url.pathname==='/api/state')return send(200,readJSON(ws.statePath));
      if(req.method==='POST'&&url.pathname==='/api/state'){
        const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>25_000_000)return send(413,{error:'Document too large'});chunks.push(chunk);}
        const payload=JSON.parse(Buffer.concat(chunks).toString('utf8')),doc=validateDocument(payload.document),old=readJSON(ws.statePath);
        if(payload.expectedRevision!==old.revision)return send(409,{error:'Saved workspace changed. Export before reloading.'});
        doc.revision=Math.max(doc.revision,old.revision)+1;writeJSON(ws.statePath,doc);return send(200,{revision:doc.revision});
      }
      if(req.method!=='GET')return send(404,{error:'Not found'});
      if(url.pathname==='/'){res.writeHead(302,{Location:'/'+ws.manifest.surface,'Cache-Control':'no-store'});res.end();return;}
      const name=url.pathname==='/'?ws.manifest.surface:decodeURIComponent(url.pathname.slice(1));
      // Only declared runtime/assets/extensions are served, never arbitrary sibling project files.
      const allowed=['toolkit',path.dirname(ws.manifest.surface).split(/[\\/]/)[0],ws.manifest.assets,...ws.manifest.extensions.map(e=>e.module.split(/[\\/]/)[0])];
      if(!allowed.some(prefix=>name===prefix||name.startsWith(prefix+'/')))return send(404,{error:'Not found'});
      const file=localPath(ws.root,name);if(!fs.existsSync(file)||!fs.statSync(file).isFile())return send(404,{error:'Not found'});
      res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});fs.createReadStream(file).pipe(res);
    }catch(error){send(400,{error:error.message});}
  });
}
