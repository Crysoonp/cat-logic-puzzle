const fs=require('fs'),vm=require('vm');
global.window=global;
global.document={addEventListener(){},querySelector(){return null},querySelectorAll(){return []}};
function load(file){vm.runInThisContext(fs.readFileSync(file,'utf8'),{filename:file})}
load('logic-engine.js');
load('stages.js');
function stageLike(x){return x&&Number.isInteger(x.stage)&&Number.isInteger(x.size)&&Array.isArray(x.solution)&&Array.isArray(x.regions)}
function collect(value,seen,out){
 if(!value||seen.has(value))return; if(typeof value!=='object')return;seen.add(value);
 if(stageLike(value)){out.push(value);return}
 if(Array.isArray(value)){for(const x of value)collect(x,seen,out);return}
 for(const [k,v] of Object.entries(value)){if(!['global','window','document','console','process','require','module','exports'].includes(k))collect(v,seen,out)}
}
let stages=[];const roots=['CLPStages','STAGES','stages','stageData','StageData'];
for(const name of roots)if(global[name])collect(global[name],new Set(),stages);
if(!stages.length){for(const [k,v] of Object.entries(global))if(/stage/i.test(k))collect(v,new Set(),stages)}
stages=[...new Map(stages.map(s=>[s.stage,s])).values()].sort((a,b)=>a.stage-b.stage);
if(!stages.length)throw new Error('No stage data found after loading stages.js');
const rows=stages.map(s=>CLPLogic.analyze(s));
const countBy=(key)=>Object.fromEntries([...new Set(rows.map(r=>String(r[key])))].sort((a,b)=>Number(a)-Number(b)).map(v=>[v,rows.filter(r=>String(r[key])===v).length]));
const avg=(a)=>a.length?Number((a.reduce((x,y)=>x+y,0)/a.length).toFixed(2)):0;
const summary={
 stageCount:rows.length,stageRange:[rows[0].stage,rows.at(-1).stage],solved:rows.filter(r=>r.solved).length,unsolved:rows.filter(r=>!r.solved).length,
 legacyDifficulty:countBy('difficulty'),advancedDifficulty:countBy('advancedDifficulty'),
 advancedScore:{min:Math.min(...rows.map(r=>r.advancedDifficultyScore)),max:Math.max(...rows.map(r=>r.advancedDifficultyScore)),average:avg(rows.map(r=>r.advancedDifficultyScore))},
 singleCellRegions:{average:avg(rows.map(r=>r.regionProfile.singleCellRegions)),max:Math.max(...rows.map(r=>r.regionProfile.singleCellRegions))},
 twoCellRegions:{average:avg(rows.map(r=>r.regionProfile.twoCellRegions)),max:Math.max(...rows.map(r=>r.regionProfile.twoCellRegions))},
 initialCertainCats:{average:avg(rows.map(r=>r.openingProfile.initialCertainCatCount)),max:Math.max(...rows.map(r=>r.openingProfile.initialCertainCatCount))},
 scoreBands:{'0-24':rows.filter(r=>r.advancedDifficultyScore<=24).length,'25-44':rows.filter(r=>r.advancedDifficultyScore>=25&&r.advancedDifficultyScore<=44).length,'45-64':rows.filter(r=>r.advancedDifficultyScore>=45&&r.advancedDifficultyScore<=64).length,'65-82':rows.filter(r=>r.advancedDifficultyScore>=65&&r.advancedDifficultyScore<=82).length,'83-100':rows.filter(r=>r.advancedDifficultyScore>=83).length}
};
const top=[...rows].sort((a,b)=>b.advancedDifficultyScore-a.advancedDifficultyScore||a.stage-b.stage).slice(0,30);
const milestones=rows.filter(r=>r.stage%50===0||r.stage>=295);
const payload={summary,top,milestones,rows};
fs.writeFileSync('NEKOMICHI_V224_CALIBRATION_BEFORE_V225.json',JSON.stringify(payload,null,2));
let txt=['NEKOMICHI V224 CALIBRATION BEFORE V225','',JSON.stringify(summary,null,2),'','TOP 30 ADVANCED SCORES'];
for(const r of top)txt.push(`Stage ${r.stage} | ${r.boardSize}x${r.boardSize} | score ${r.advancedDifficultyScore} | star ${r.advancedDifficulty} | legacy ${r.difficultyScore}/${r.difficulty} | L${r.highestRuleLevel} | steps ${r.logicStepCount} | chain ${r.longestInferenceRun} | single ${r.regionProfile.singleCellRegions} | double ${r.regionProfile.twoCellRegions} | initial cats ${r.openingProfile.initialCertainCatCount} | solved ${r.solved}`);
txt.push('','MILESTONES AND STAGE 295+');for(const r of milestones)txt.push(`Stage ${r.stage} | ${r.boardSize}x${r.boardSize} | score ${r.advancedDifficultyScore} | star ${r.advancedDifficulty} | L${r.highestRuleLevel} | steps ${r.logicStepCount} | chain ${r.longestInferenceRun} | single ${r.regionProfile.singleCellRegions} | double ${r.regionProfile.twoCellRegions} | initial cats ${r.openingProfile.initialCertainCatCount} | solved ${r.solved}`);
fs.writeFileSync('NEKOMICHI_V224_CALIBRATION_BEFORE_V225.txt',txt.join('\n'));
console.log(`Analyzed stages: ${rows.length}`);console.log(`Range: ${rows[0].stage}-${rows.at(-1).stage}`);console.log(`Solved: ${summary.solved}, Unsolved: ${summary.unsolved}`);console.log('Advanced stars:',JSON.stringify(summary.advancedDifficulty));console.log('SUCCESS: V224 calibration audit completed');
