const fs=require('fs');
const vm=require('vm');
global.window=global;
global.document={title:'ねこみちロジック Ver.0.8.0',querySelectorAll:()=>[]};
function load(name){vm.runInThisContext(fs.readFileSync(name,'utf8'),{filename:name});}
load('app-config.js');load('stages.js');load('logic-engine.js');load('quality-engine.js');
function ok(value,message){if(!value)throw new Error(message);}
ok(/^0\.8\.\d+$/.test(window.CLP_APP_VERSION),'foundation version must remain in the 0.8.x line');
ok(Array.isArray(window.CLP_STAGES)&&window.CLP_STAGES.length===200,'stage count must be 200');
ok(window.CLP_STAGES.every((stage,index)=>stage.stage===index+1),'stage numbers must be continuous');
const quality=window.CLPQuality.inspectAll(window.CLP_STAGES);
ok(quality.every(item=>item.decision!=='rejected'),'all stages must pass quality checks');
const stage50=window.CLP_STAGES.find(stage=>stage.stage===50);
ok(stage50&&Array.isArray(stage50.bossPhasePlan),'stage 50 boss plan missing');
ok(Array.isArray(window.CLP_BOSS_PHASES)&&window.CLP_BOSS_PHASES.length===3,'boss phases must be 3');
stage50.bossPhasePlan.forEach((plan,index)=>{ok(plan.size===window.CLP_BOSS_PHASES[index].size,'boss phase size mismatch at phase '+(index+1));});
const expected=[7,8,8];
ok(stage50.bossPhasePlan.every((plan,index)=>plan.size===expected[index]),'boss sizes must be 7,8,8');
const logic=window.CLPLogic.analyzeAll(window.CLP_STAGES);
const knownUnresolved=logic.filter(item=>!item.logicOnly).map(item=>item.stage);
ok(JSON.stringify(knownUnresolved)===JSON.stringify([]),'known unresolved-stage baseline changed: '+JSON.stringify(knownUnresolved));
console.log('OK: Nekomichi Ver.0.8.0 foundation checks passed.');
console.log('OK: Stage quality, boss metadata, central version, and known solver gap baseline are fixed.');
