#!/usr/bin/env node
/** Dependency-free workspace lifecycle and preparation commands. */
import fs from 'node:fs';
import path from 'node:path';
import {createWorkspace,loadWorkspace,readJSON,writeJSON,workspaceReadback,cutCapture,importLegacyWorkspace} from './workspace.mjs';
import {validateDocument} from './model.mjs';
import {createServer} from './server.mjs';
const args=process.argv.slice(2),command=args.shift();
function flag(name,fallback){const i=args.indexOf(name);return i<0?fallback:args[i+1];}
function required(index){if(!args[index]||args[index].startsWith('--'))throw Error('Missing command argument. Run --help.');return args[index];}
try{
  if(!command||['--help','help'].includes(command))console.log(`Thought-Rig toolkit (Node 20+)\n  init <workspace> [--title TEXT] [--empty]\n  serve <workspace> [--port 5347]\n  validate <workspace>\n  readback <workspace> [--output FILE]\n  cut <workspace> <regions.json>\n  import-legacy <legacy.json> <new-workspace>\n\nRun tools from a task-local workspace/toolkit to adapt them independently.`);
  else if(command==='init')console.log(createWorkspace(required(0),{title:flag('--title','Thought-Rig exploration'),empty:args.includes('--empty')}));
  else if(command==='serve'){const root=required(0),port=Number(flag('--port','5347'));if(!Number.isInteger(port)||port<0||port>65535)throw Error('Invalid port');const server=createServer(root);server.on('error',e=>{console.error(e.message);process.exitCode=1;});server.listen(port,'127.0.0.1',()=>console.log(`Thought-Rig: http://127.0.0.1:${server.address().port}/`));}
  else if(command==='validate'){const ws=loadWorkspace(required(0)),doc=validateDocument(readJSON(ws.statePath));console.log(JSON.stringify({valid:true,objects:doc.objects.length,revision:doc.revision}));}
  else if(command==='readback'){const result=await workspaceReadback(required(0)),output=flag('--output');if(output){writeJSON(path.resolve(output),result);console.log(path.resolve(output));}else console.log(JSON.stringify(result,null,2));}
  else if(command==='cut')console.log(JSON.stringify(cutCapture(required(0),path.resolve(required(1))),null,2));
  else if(command==='import-legacy')console.log(importLegacyWorkspace(path.resolve(required(0)),required(1)));
  else throw Error(`Unknown command: ${command}`);
}catch(error){console.error(error.message);process.exitCode=1;}
