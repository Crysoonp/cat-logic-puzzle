const fs=require('fs');const vm=require('vm');
const memory=new Map();
global.window=global;global.localStorage={getItem:k=>memory.has(k)?memory.get(k):null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()};
global.document={title:'ねこみちロジック Ver.0.8.2',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}
function ok(value,message){if(!value)throw new Error(message);}
load('app-config.js');load('storage-service.js');
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'storage foundation version must remain in the 0.8.x line');
ok(window.CLPStorage&&Object.isFrozen(window.CLPStorage),'storage service missing or mutable');
window.CLPStorage.setItem('sample',12);ok(window.CLPStorage.getItem('sample')==='12','string storage contract failed');
window.CLPStorage.setJSON('json',{a:1});ok(window.CLPStorage.getJSON('json').a===1,'JSON storage contract failed');
window.CLPStorage.removeItem('sample');ok(window.CLPStorage.getItem('sample')===null,'remove contract failed');
const game=fs.readFileSync('game.js','utf8');
ok(!/\blocalStorage\.(getItem|setItem|removeItem|clear)\b/.test(game),'direct localStorage access remains in game.js');
const html=fs.readFileSync('index.html','utf8');
ok(html.indexOf('storage-service.js')<html.indexOf('game.js'),'storage service must load before game.js');
console.log('OK: Nekomichi Ver.0.8.2 storage foundation checks passed.');
