const fs=require('fs');const vm=require('vm');
const memory=new Map([['clpHearts','3'],['clpKibble','7'],['clpHistory','{\"1\":90}'],['clpBossPhase','2']]);
global.window=global;global.localStorage={getItem:k=>memory.has(k)?memory.get(k):null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()};
global.document={title:'ねこみちロジック Ver.0.8.6',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}
function ok(value,message){if(!value)throw new Error(message);}
load('app-config.js');load('storage-service.js');load('game-state.js');
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'game state foundation version must remain in the 0.8.x line');
const state=window.CLPGameState.createInitialState();
ok(state.hearts===3&&state.kibble===7&&state.history[1]===90&&state.bossPhase===2,'persisted progress initialization failed');
ok(state.revealed instanceof Set&&state.marks instanceof Map&&state.timers instanceof Map,'runtime collection types failed');
ok(Object.isFrozen(window.CLPGameState.BOUNDARIES),'state boundaries must be fixed');
const snap=window.CLPGameState.boardSnapshot(state);
ok(snap.version===1&&snap.stageIndex===0&&Array.isArray(snap.revealed)&&Array.isArray(snap.marks),'board snapshot contract failed');
const game=fs.readFileSync('game.js','utf8');
ok(game.includes('const state=window.CLPGameState.createInitialState();'),'game state factory is not connected');
ok(game.includes('window.CLPGameState.boardSnapshot(state)'),'board snapshot factory is not connected');
const html=fs.readFileSync('index.html','utf8');
ok(html.indexOf('game-state.js')<html.indexOf('game.js'),'game state service must load before game.js');
console.log('OK: Nekomichi Ver.0.8.6 game state foundation checks passed.');
