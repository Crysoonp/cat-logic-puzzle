const fs=require('fs'),vm=require('vm');global.window=global;
function load(n){vm.runInThisContext(fs.readFileSync(n,'utf8'),{filename:n});}load('stages.js');load('logic-engine.js');
function ok(v,m){if(!v)throw new Error(m)}
for(const id of [37,38,39]){const s=CLP_STAGES.find(x=>x.stage===id);ok(s&&s.size===8,'missing Stage '+id);const a=CLPLogic.analyze(s);ok(a.solved,'Stage '+id+' must solve');ok(a.highestRuleLevel<=2,'Stage '+id+' must stay within Level 2');ok(s.quality&&s.quality.regeneratedForBeginnerFlow===true,'Stage '+id+' quality marker missing');}
const gaps=CLP_STAGES.filter(s=>!CLPLogic.analyze(s).solved).map(s=>s.stage);ok(gaps.length===0,'Stage 1-50 production gaps remain: '+gaps.join(','));
console.log('OK: Nekomichi Ver.0.8.35 Stage 37-39 beginner replacements passed.');
