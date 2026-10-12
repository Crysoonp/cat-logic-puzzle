const fs=require('fs');const vm=require('vm');
const memory=new Map();global.window=global;global.localStorage={getItem:k=>memory.has(k)?memory.get(k):null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()};
global.document={title:'ねこみちロジック Ver.0.8.7',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}function ok(v,m){if(!v)throw new Error(m);}
load('app-config.js');load('storage-service.js');load('game-state.js');
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'board restore foundation version must remain in the 0.8.x line');const stages=[{size:4},{size:5}];
const raw={version:1,stageIndex:0,bossPhase:9,score:'12',mistakes:-2,hintsUsed:'3',totalFound:2,mode:'bad',revealed:['0-1','9-9'],marks:[['1-1','x'],['0-1','q'],['2-2','bad']],streak:'4'};
const restored=window.CLPGameState.restoreBoardSnapshot(raw,stages);ok(restored&&restored.bossPhase===3&&restored.mode==='x','normalized restore failed');
ok(restored.revealed.has('0-1')&&!restored.revealed.has('9-9'),'revealed validation failed');ok(restored.marks.get('1-1')==='x'&&!restored.marks.has('0-1'),'mark validation failed');
ok(window.CLPGameState.restoreBoardSnapshot({...raw,version:2},stages)===null,'unknown board version must be rejected');
ok(window.CLPGameState.restoreBoardSnapshot({...raw,stageIndex:8},stages)===null,'invalid stage index must be rejected');
const state=window.CLPGameState.createInitialState();ok(window.CLPGameState.applyBoardSnapshot(state,restored),'snapshot apply failed');ok(state.i===0&&state.score===12&&state.revealed.has('0-1'),'applied state mismatch');
const game=fs.readFileSync('game.js','utf8');ok(game.includes('restoreBoardSnapshot(raw,STAGES)'),'game restore service is not connected');ok(!game.includes('JSON.parse(window.CLPStorage.getItem(BOARD_SAVE_KEY)'),'legacy direct board parse remains');
console.log('OK: Nekomichi Ver.0.8.7 board restore checks passed.');
