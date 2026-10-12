const fs=require('fs');const vm=require('vm');
const memory=new Map();
global.window=global;global.localStorage={getItem:k=>memory.has(k)?memory.get(k):null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()};
global.document={title:'ねこみちロジック Ver.0.8.4',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}
function ok(value,message){if(!value)throw new Error(message);}
load('app-config.js');load('storage-service.js');
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'storage schema foundation version must remain in the 0.8.x line');
ok(window.CLPStorage.SCHEMA_VERSION===1,'schema version mismatch');
const first=window.CLPStorage.ensureSchema();
ok(first.schemaVersion===1,'schema initialization failed');
const meta=window.CLPStorage.getJSON(window.CLPStorage.META_KEY);
ok(meta.schemaVersion===1&&/^0\.8\.\d+$/.test(meta.createdBy),'schema metadata failed');
const keys=window.CLPStorage.registeredKeyNames();
ok(keys.length===12,'registered game key count changed: '+keys.length);
ok(new Set(keys).size===keys.length,'duplicate storage keys detected');
const before=JSON.stringify(meta);window.CLPStorage.ensureSchema();
ok(JSON.stringify(window.CLPStorage.getJSON(window.CLPStorage.META_KEY))===before,'schema initialization must be idempotent');
window.CLPStorage.setJSON(window.CLPStorage.META_KEY,{schemaVersion:2});
let blocked=false;try{window.CLPStorage.ensureSchema();}catch(_error){blocked=true;}
ok(blocked,'newer storage schema must be rejected');
console.log('OK: Nekomichi Ver.0.8.4 storage schema checks passed.');
