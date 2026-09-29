window.CLPAnalysis=(()=>{
const key=(r,c)=>`${r}-${c}`;
const parse=id=>id.split('-').map(Number);
function allUnits(stage){
 const n=stage.size,out=[];
 for(let r=0;r<n;r++)out.push({type:'row',index:r,label:`${String.fromCharCode(65+r)}行`,cells:Array.from({length:n},(_,c)=>key(r,c))});
 for(let c=0;c<n;c++)out.push({type:'column',index:c,label:`${c+1}列`,cells:Array.from({length:n},(_,r)=>key(r,c))});
 const ids=[...new Set(stage.regions.flat())];
 for(const g of ids){const cells=[];for(let r=0;r<n;r++)for(let c=0;c<n;c++)if(stage.regions[r][c]===g)cells.push(key(r,c));out.push({type:'region',index:g,label:`色エリア${g}`,cells})}
 return out;
}
function applyKnownSafe(stage,revealed,marks,step,answers){
 if(step.kind==='only'){
  if(!answers.has(step.target))return {ok:false,reason:`論理ルールが正解でない猫位置 ${step.target} を確定候補にした`};
  revealed.add(step.target);return {ok:true,changed:1};
 }
 let changed=0;
 for(const id of step.targets||[step.target]){
  if(answers.has(id))return {ok:false,reason:`論理ルールが正解マス ${id} を除外候補にした`};
  if(!marks.has(id)){marks.set(id,'x');changed++}
 }
 return {ok:changed>0,changed,reason:changed?null:'盤面が変化しない手を返した'};
}
function enumerateSolutions(stage,limit=20000,forcedCat=null,forcedX=null){
 const n=stage.size,regions=stage.regions,usedCols=new Set(),usedRegs=new Set(),chosen=Array(n).fill(-1),solutions=[];let nodes=0,truncated=false;
 function dfs(r,prev){
  if(solutions.length>=limit){truncated=true;return}
  if(r===n){solutions.push(chosen.slice());return}
  for(let c=0;c<n;c++){
   nodes++;const id=key(r,c),g=regions[r][c];
   if(usedCols.has(c)||usedRegs.has(g)||(prev!==null&&Math.abs(prev-c)<=1))continue;
   if(forcedX&&forcedX.has(id))continue;
   if(forcedCat&&forcedCat.row===r&&forcedCat.col!==c)continue;
   if(forcedCat&&forcedCat.row!==r&&forcedCat.col===c)continue;
   if(forcedCat&&regions[forcedCat.row][forcedCat.col]===g&&forcedCat.row!==r)continue;
   chosen[r]=c;usedCols.add(c);usedRegs.add(g);dfs(r+1,c);usedCols.delete(c);usedRegs.delete(g);chosen[r]=-1;
   if(truncated)return;
  }
 }
 dfs(0,null);return {solutions,nodes,truncated};
}
function findForcedFacts(stage,revealed,marks){
 const forcedX=new Set([...marks.entries()].filter(([,v])=>v==='x').map(([id])=>id));
 const base=enumerateSolutions(stage,20000,null,forcedX),n=stage.size;
 if(!base.solutions.length)return {remainingSolutionCount:0,forcedCats:[],forcedXs:[],truncated:base.truncated};
 const forcedCats=[],forcedXs=[];
 for(let r=0;r<n;r++)for(let c=0;c<n;c++){
  const id=key(r,c);if(revealed.has(id)||forcedX.has(id))continue;
  const count=base.solutions.filter(sol=>sol[r]===c).length;
  if(count===base.solutions.length)forcedCats.push(id);
  else if(count===0)forcedXs.push(id);
 }
 return {remainingSolutionCount:base.solutions.length,forcedCats,forcedXs,truncated:base.truncated};
}
function analyzeStall(stage){
 const revealed=new Set(),marks=new Map(),answers=new Set(stage.solution.map((c,r)=>key(r,c))),trace=[];let guard=stage.size*stage.size*20,error=null;
 while(revealed.size<stage.size&&guard-->0){
  const step=window.CLPLogic.logicalStep(stage,revealed,marks,3);if(!step)break;
  const applied=applyKnownSafe(stage,revealed,marks,step,answers);
  trace.push({step:trace.length+1,ruleLevel:step.ruleLevel,ruleId:step.ruleId,kind:step.kind,target:step.target,targets:step.targets||[step.target]});
  if(!applied.ok){error=applied.reason;break}
 }
 const cand=window.CLPLogic.candidates(stage,revealed,marks),units=allUnits(stage).filter(u=>!u.cells.some(id=>revealed.has(id))).map(u=>({type:u.type,index:u.index,label:u.label,candidates:u.cells.filter(id=>cand.has(id))}));
 const byCount={};for(const u of units){const k=String(u.candidates.length);(byCount[k]||(byCount[k]=[])).push(u.label)}
 const forced=findForcedFacts(stage,revealed,marks);
 let recommendation='現在のルールで解決済み';
 if(revealed.size<stage.size){
  if(forced.forcedCats.length||forced.forcedXs.length) recommendation='解集合の比較で確定事実があります。共通候補除外または配置パターン比較ルールの追加候補です。';
  else recommendation='現在の候補情報だけでは直接確定がありません。仮定・背理法または問題調整を検討します。';
 }
 return {stage:stage.stage,size:`${stage.size}x${stage.size}`,solved:revealed.size===stage.size,error,logicSteps:trace.length,revealedCats:[...revealed],revealedCount:revealed.size,markedXCount:[...marks.values()].filter(v=>v==='x').length,remainingCandidateCount:cand.size,remainingCandidates:[...cand],units,candidateUnitCounts:byCount,forcedCats:forced.forcedCats,forcedXs:forced.forcedXs,remainingSolutionCount:forced.remainingSolutionCount,solutionSearchTruncated:forced.truncated,lastStep:trace.at(-1)||null,trace,recommendation};
}
function analyzeUnresolved(stages){return stages.map(analyzeStall).filter(x=>!x.solved)}
function printReport(stages){
 const report=analyzeUnresolved(stages);window.CLPStallReport=report;
 console.group('猫ロジック Ver.0.4.5 停止地点解析');
 if(!report.length)console.info('現在の論理ルールで全ステージを解決できます。');
 for(const x of report){
  console.group(`Stage ${x.stage} ${x.size}`);
  console.table([{stage:x.stage,logicSteps:x.logicSteps,revealed:x.revealedCount,markedX:x.markedXCount,remainingCandidates:x.remainingCandidateCount,remainingSolutions:x.remainingSolutionCount,forcedCats:x.forcedCats.join(' '),forcedXs:x.forcedXs.length,recommendation:x.recommendation}]);
  console.table(x.units.map(u=>({unit:u.label,type:u.type,candidateCount:u.candidates.length,candidates:u.candidates.join(' ')})));
  if(x.forcedCats.length)console.info('全解で猫になるマス:',x.forcedCats);
  if(x.forcedXs.length)console.info('全解で×になるマス:',x.forcedXs);
  if(x.error)console.error(x.error);
  console.groupEnd();
 }
 console.groupEnd();return report;
}
return {analyzeStall,analyzeUnresolved,printReport,enumerateSolutions};})();
