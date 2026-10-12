const fs=require('fs');const vm=require('vm');
const memory=new Map();
global.window=global;global.localStorage={getItem:k=>memory.has(k)?memory.get(k):null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()};
global.document={title:'ねこみちロジック Ver.0.8.5',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}
function ok(value,message){if(!value)throw new Error(message);}
load('app-config.js');load('storage-service.js');
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'storage startup foundation version must remain in the 0.8.x line');
const game=fs.readFileSync('game.js','utf8');
ok(game.includes('window.CLPStorage.ensureSchema();'),'startup schema check missing');
const registered=Object.values(window.CLPStorage.KEYS);
registered.forEach(key=>{const escaped=key.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');const direct=new RegExp('CLPStorage\\.(getItem|setItem|removeItem)\\([\"\']'+escaped+'[\"\']');ok(!direct.test(game),'direct registered key literal remains: '+key);});
window.CLPStorage.ensureSchema();
const meta=window.CLPStorage.getJSON(window.CLPStorage.META_KEY);
ok(meta.schemaVersion===1&&/^0\.8\.\d+$/.test(meta.createdBy),'startup schema metadata mismatch');
console.log('OK: Nekomichi Ver.0.8.5 storage startup checks passed.');
