window.CLPLogic=(()=>{
const DIFFICULTY_LIMITS={level1Max:14,level2Max:29,level3Max:49,level4Max:69};
const key=(r,c)=>`${r}-${c}`;
const parse=id=>id.split('-').map(Number);
const catIds=stage=>new Set(stage.solution.map((c,r)=>key(r,c)));
function units(stage){
 const n=stage.size,out=[];
 for(let r=0;r<n;r++)out.push({type:'row',index:r,cells:Array.from({length:n},(_,c)=>key(r,c))});
 for(let c=0;c<n;c++)out.push({type:'column',index:c,cells:Array.from({length:n},(_,r)=>key(r,c))});
 for(let g=0;g<n;g++){const cells=[];for(let r=0;r<n;r++)for(let c=0;c<n;c++)if(stage.regions[r][c]===g)cells.push(key(r,c));out.push({type:'region',index:g,cells})}
 return out;
}
function foundSets(stage,revealed){const rows=new Set(),cols=new Set(),regs=new Set();for(const id of revealed){const [r,c]=parse(id);rows.add(r);cols.add(c);regs.add(stage.regions[r][c])}return {rows,cols,regs}}
function candidates(stage,revealed,marks){
 const n=stage.size,f=foundSets(stage,revealed),out=new Set();
 for(let r=0;r<n;r++)for(let c=0;c<n;c++){
  const id=key(r,c);if(revealed.has(id)||marks.get(id)==='x'||f.rows.has(r)||f.cols.has(c)||f.regs.has(stage.regions[r][c]))continue;
  let adjacent=false;for(const x of revealed){const [rr,cc]=parse(x);if(Math.abs(rr-r)<=1&&Math.abs(cc-c)<=1){adjacent=true;break}}
  if(!adjacent)out.add(id);
 }return out;
}
function unresolvedUnits(stage,revealed,cand){return units(stage).filter(u=>!u.cells.some(id=>revealed.has(id))).map(u=>({...u,candidates:u.cells.filter(id=>cand.has(id))}))}
function exclusionIds(stage,revealed,marks){
 const out=[];for(const found of revealed){const [fr,fc]=parse(found),reg=stage.regions[fr][fc];for(let r=0;r<stage.size;r++)for(let c=0;c<stage.size;c++){
  const id=key(r,c);if(id===found||revealed.has(id)||marks.get(id)==='x')continue;
  if(r===fr||c===fc||stage.regions[r][c]===reg||(Math.abs(fr-r)<=1&&Math.abs(fc-c)<=1))out.push(id);
 }}return [...new Set(out)];
}
function safeXStep(stage,revealed,marks){
 const ids=exclusionIds(stage,revealed,marks);if(!ids.length)return null;const target=ids[0],[r,c]=parse(target);
 for(const found of revealed){const [fr,fc]=parse(found),reg=stage.regions[fr][fc];
  if(Math.abs(fr-r)<=1&&Math.abs(fc-c)<=1)return xStep(target,[found,target],1,'CAT_ADJACENCY','見つけた猫の周囲8マスには別の猫はいないニャン。');
  if(r===fr)return xStep(target,[found,target],1,'ROW_EXCLUSION','見つけた猫と同じ行には別の猫はいないニャン。');
  if(c===fc)return xStep(target,[found,target],1,'COLUMN_EXCLUSION','見つけた猫と同じ列には別の猫はいないニャン。');
  if(stage.regions[r][c]===reg)return xStep(target,[found,target],1,'REGION_EXCLUSION','見つけた猫と同じ色エリアには別の猫はいないニャン。');
 }return null;
}
function xStep(target,focus,ruleLevel,ruleId,message,targets=[target]){return {kind:'exclude',target,targets,focus,ruleLevel,ruleId,message:`${message} 光ったマスへ×を付けるニャン。`}}
function level1(stage,revealed,marks,cand,us){
 const ex=exclusionIds(stage,revealed,marks);if(ex.length)return xStep(ex[0],ex,1,'DIRECT_EXCLUSION','見つけた猫の行・列・色エリア・周囲を除外できるニャン。',ex);
 for(const u of us)if(u.candidates.length===1){const names={row:'行',column:'列',region:'色エリア'};return {kind:'only',target:u.candidates[0],targets:u.candidates,focus:u.cells,ruleLevel:1,ruleId:`ONLY_${u.type.toUpperCase()}`,message:`この${names[u.type]}で猫を置けるのは残り1マスだけだニャン。`}}
 return null;
}
function level2Locked(stage,revealed,marks,cand,us){
 for(const u of us){if(u.candidates.length<2)continue;const rows=new Set(),cols=new Set(),regs=new Set();for(const id of u.candidates){const [r,c]=parse(id);rows.add(r);cols.add(c);regs.add(stage.regions[r][c])}
  const checks=[];
  if(u.type!=='row'&&rows.size===1)checks.push(['row',[...rows][0]]);
  if(u.type!=='column'&&cols.size===1)checks.push(['column',[...cols][0]]);
  if(u.type!=='region'&&regs.size===1)checks.push(['region',[...regs][0]]);
  for(const [type,index] of checks){const other=us.find(v=>v.type===type&&v.index===index);if(!other)continue;const targets=other.candidates.filter(id=>!u.candidates.includes(id));if(targets.length){const labels={row:'行',column:'列',region:'色エリア'};return xStep(targets[0],[...u.candidates,...targets],2,'LOCKED_CANDIDATES',`${labels[u.type]}の猫候補が同じ${labels[type]}内に限定されるため、その外側候補を除外できるニャン。`,targets)}}
 }return null;
}
function level2CommonAdjacency(stage,revealed,marks,cand,us){
 for(const u of us){if(u.candidates.length<2||u.candidates.length>4)continue;for(const id of cand){if(u.candidates.includes(id)||marks.get(id)==='x')continue;const [r,c]=parse(id);if(u.candidates.every(x=>{const [rr,cc]=parse(x);return Math.abs(rr-r)<=1&&Math.abs(cc-c)<=1}))return xStep(id,[...u.candidates,id],2,'COMMON_ADJACENCY','この範囲のどこに猫がいても、そのマスは必ず隣接するため除外できるニャン。')}}return null;
}
function level3NakedPairs(stage,revealed,marks,cand,us){
 for(const type of ['row','column','region']){const group=us.filter(u=>u.type===type&&u.candidates.length===2);for(let i=0;i<group.length;i++)for(let j=i+1;j<group.length;j++){
  const union=new Set([...group[i].candidates,...group[j].candidates]);if(union.size!==2)continue;const pair=[...union],targets=[];
  for(const u of us)if(u.type===type&&u!==group[i]&&u!==group[j])for(const id of u.candidates)if(pair.includes(id)&&!targets.includes(id))targets.push(id);
  if(targets.length)return xStep(targets[0],[...pair,...targets],3,'NAKED_PAIR','2つの単位で猫候補が同じ2マスに限定されるため、ほかの候補から除外できるニャン。',targets);
 }}return null;
}
function logicalStep(stage,revealed,marks,maxLevel=3){const cand=candidates(stage,revealed,marks),us=unresolvedUnits(stage,revealed,cand);return level1(stage,revealed,marks,cand,us)||(maxLevel>=2&&level2Locked(stage,revealed,marks,cand,us))||(maxLevel>=2&&level2CommonAdjacency(stage,revealed,marks,cand,us))||(maxLevel>=3&&level3NakedPairs(stage,revealed,marks,cand,us))||null}
function nextStep(stage,revealed,marks){return logicalStep(stage,revealed,marks,3)}
function scoreToDifficulty(score,highest,depth){let d=score<=14?1:score<=29?2:score<=49?3:score<=69?4:5;d=Math.max(d,highest);if(depth>=2)d=5;return Math.min(5,d)}
function analyze(stage){
 const revealed=new Set(),marks=new Map(),answers=catIds(stage),ruleUsage={level1:0,level2:0,level3:0,level4:0,level5:0};let logicStepCount=0,cellUpdateCount=0,maxChainLength=0,highestRuleLevel=1,guard=stage.size*stage.size*12;
 while(revealed.size<stage.size&&guard-->0){const step=logicalStep(stage,revealed,marks,3);if(!step)break;logicStepCount++;maxChainLength=Math.max(maxChainLength,logicStepCount);highestRuleLevel=Math.max(highestRuleLevel,step.ruleLevel);ruleUsage[`level${step.ruleLevel}`]++;
  if(step.kind==='only'){if(!answers.has(step.target))break;revealed.add(step.target);cellUpdateCount++;}
  else{let changed=0;for(const id of step.targets||[step.target]){if(answers.has(id))continue;if(!marks.has(id)){marks.set(id,'x');changed++;cellUpdateCount++;}}if(!changed)break;}
 }
 const solved=revealed.size===stage.size,stepRate=logicStepCount/(stage.size*stage.size),stepPoints=stepRate<.75?0:stepRate<1.25?3:stepRate<1.75?6:stepRate<2.5?10:15,chainPoints=maxChainLength<=2?0:maxChainLength<=4?3:maxChainLength<=7?6:maxChainLength<=11?10:15,stallPoints=solved?0:15,candidatePoints=stage.size<=4?0:stage.size<=6?3:stage.size<=8?6:10,rulePoints={1:0,2:10,3:25,4:40,5:55}[highestRuleLevel],difficultyScore=Math.min(100,rulePoints+stepPoints+chainPoints+stallPoints+candidatePoints);
 return {stage:stage.stage,boardSize:stage.size,solved,logicOnly:solved,solveType:solved?'direct-logic':'unresolved-by-current-rules',difficulty:scoreToDifficulty(difficultyScore,highestRuleLevel,0),difficultyScore,logicStepCount,cellUpdateCount,maxChainLength,highestRuleLevel,assumptionDepth:0,ruleUsage,manualLogicLevel:stage.logicLevel||null,manualDifficulty:stage.difficulty||null,solverVersion:'1.1'};
}
const analyzeAll=stages=>stages.map(analyze);
return {candidates,safeXStep,nextStep,logicalStep,analyze,analyzeAll,DIFFICULTY_LIMITS};})();
