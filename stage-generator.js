window.CLPGenerator=(()=>{
const STORAGE_KEY='clpGeneratedStagesV0481';
const PROGRESS_KEY='clpGeneratorProgressV0482';
const BATCH_ATTEMPTS=5000;
const YIELD_EVERY=100;
let stopRequested=false;
let running=false;

const rnd=(a,b)=>Math.floor(Math.random()*(b-a+1))+a;
function shuffled(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=rnd(0,i);[a[i],a[j]]=[a[j],a[i]]}return a}
function validSolution(sol){return sol.every((c,r)=>r===0||Math.abs(c-sol[r-1])>1)}
function makeSolution(n){for(let k=0;k<3000;k++){const p=shuffled([...Array(n).keys()]);if(validSolution(p))return p}return null}
function orthogonal(r,c,n){return [[1,0],[-1,0],[0,1],[0,-1]].map(([dr,dc])=>[r+dr,c+dc]).filter(([rr,cc])=>rr>=0&&rr<n&&cc>=0&&cc<n)}
function makeRegions(n,solution){
 const grid=Array.from({length:n},()=>Array(n).fill(-1)),cells=Array.from({length:n},()=>[]);
 for(let r=0;r<n;r++){grid[r][solution[r]]=r;cells[r].push([r,solution[r]])}
 let left=n*n-n,guard=n*n*300;
 while(left&&guard--){
  const expandable=[];
  for(let g=0;g<n;g++)if(cells[g].some(([r,c])=>orthogonal(r,c,n).some(([rr,cc])=>grid[rr][cc]===-1)))expandable.push(g);
  if(!expandable.length)break;
  const min=Math.min(...expandable.map(g=>cells[g].length));
  const pool=expandable.filter(g=>cells[g].length<=min+1),g=pool[rnd(0,pool.length-1)],frontier=[];
  for(const [r,c] of cells[g])for(const [rr,cc] of orthogonal(r,c,n))if(grid[rr][cc]===-1)frontier.push([rr,cc]);
  const [rr,cc]=frontier[rnd(0,frontier.length-1)];grid[rr][cc]=g;cells[g].push([rr,cc]);left--;
 }
 return left?null:grid;
}
function sizeFor(no){if(no<=20)return 5;if(no<=30)return 6;if(no<=40)return 7;return 8}
function targetRange(no){if(no<=30)return [1,2];return [2,3]}
function loadSaved(){try{return JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]')}catch{return []}}
function saveStages(stages){localStorage.setItem(STORAGE_KEY,JSON.stringify(stages));window.CLPGeneratedStages=stages}
function loadProgress(){try{return JSON.parse(localStorage.getItem(PROGRESS_KEY)||'{}')}catch{return {}}}
function saveProgress(progress){localStorage.setItem(PROGRESS_KEY,JSON.stringify(progress));window.CLPGenerationProgress=progress}
function signatures(stages){return new Set(stages.map(s=>window.CLPQuality.canonicalSignature(s)))}
function evaluate(stage,known){
 const quality=window.CLPQuality.inspectAll([stage])[0],logic=window.CLPLogic.analyze(stage),sig=window.CLPQuality.canonicalSignature(stage),[min,max]=targetRange(stage.stage),reasons=[];
 if(!quality.uniqueSolution)reasons.push(quality.solutionCount==='2+'?'multiple':'no-solution');
 if(known.has(sig))reasons.push('duplicate');
 if(!logic.logicOnly)reasons.push('not-logic-only');
 if(logic.difficulty<min||logic.difficulty>max)reasons.push('difficulty-outside');
 return {accepted:reasons.length===0,reasons,logic,signature:sig};
}
function addStats(stats,reasons){
 stats.attempts++;
 if(reasons.includes('no-solution'))stats.noSolution++;
 if(reasons.includes('multiple'))stats.multiple++;
 if(reasons.includes('not-logic-only'))stats.notLogicOnly++;
 if(reasons.includes('difficulty-outside'))stats.difficulty++;
 if(reasons.includes('duplicate'))stats.duplicate++;
}
function nextStage(start,end,generated){const done=new Set(generated.map(s=>s.stage));for(let n=start;n<=end;n++)if(!done.has(n))return n;return null}
async function generateNext(start=16,end=50,batchAttempts=BATCH_ATTEMPTS){
 if(running)return {status:'already-running',message:'生成処理はすでに実行中です。'};
 running=true;stopRequested=false;
 try{
  const generated=loadSaved().filter(s=>s.stage>=start&&s.stage<=end),no=nextStage(start,end,generated);
  if(no===null){const complete={status:'complete',stage:null,generated:generated.length,total:end-start+1};console.info('ステージ16～50はすべて生成済みです。',complete);return complete}
  const known=signatures([...STAGES,...generated]),progressAll=loadProgress(),previous=progressAll[no]||{totalAttempts:0,batches:0,stats:{attempts:0,noSolution:0,multiple:0,notLogicOnly:0,difficulty:0,duplicate:0}},batchStats={attempts:0,noSolution:0,multiple:0,notLogicOnly:0,difficulty:0,duplicate:0};
  console.group(`Stage ${no} 生成バッチ開始`);console.info(`今回の上限: ${batchAttempts}回 / 累計: ${previous.totalAttempts}回`);
  for(let attempt=1;attempt<=batchAttempts;attempt++){
   if(stopRequested){console.warn(`Stage ${no}: 停止要求を受け付けました。`);break}
   const n=sizeFor(no),solution=makeSolution(n),regions=solution&&makeRegions(n,solution);if(!regions){batchStats.attempts++;continue}
   const stage={stage:no,size:n,name:`ステージ${no}`,difficulty:'自動判定',logicLevel:0,regions,solution},result=evaluate(stage,known);addStats(batchStats,result.reasons);
   if(result.accepted){generated.push(stage);saveStages(generated);delete progressAll[no];saveProgress(progressAll);const out={status:'generated',stage:no,batchAttempt:attempt,totalAttempts:previous.totalAttempts+attempt,generated:generated.length,logic:result.logic};console.info(`Stage ${no} generated`,out);console.groupEnd();return out}
   if(attempt%500===0)console.info(`Stage ${no}: ${attempt}/${batchAttempts}回`,{累計:previous.totalAttempts+attempt,失敗内訳:batchStats});
   if(attempt%YIELD_EVERY===0)await new Promise(resolve=>setTimeout(resolve,0));
  }
  const used=batchStats.attempts,progress={totalAttempts:previous.totalAttempts+used,batches:previous.batches+1,stats:{attempts:previous.stats.attempts+batchStats.attempts,noSolution:previous.stats.noSolution+batchStats.noSolution,multiple:previous.stats.multiple+batchStats.multiple,notLogicOnly:previous.stats.notLogicOnly+batchStats.notLogicOnly,difficulty:previous.stats.difficulty+batchStats.difficulty,duplicate:previous.stats.duplicate+batchStats.duplicate}};
  progressAll[no]=progress;saveProgress(progressAll);const out={status:stopRequested?'stopped':'batch-ended',stage:no,generated:generated.length,batchStats,progress};console.info('バッチ終了',out);console.groupEnd();return out;
 }finally{running=false}
}
async function generateSeveral(maxStages=1,start=16,end=50){const results=[];for(let i=0;i<maxStages;i++){const r=await generateNext(start,end);results.push(r);if(r.status!=='generated')break}return results}
function requestStop(){stopRequested=true;console.info('停止要求を設定しました。次の安全な区切りで停止します。')}
function status(start=16,end=50){const generated=loadSaved().filter(s=>s.stage>=start&&s.stage<=end),next=nextStage(start,end,generated),out={running,stopRequested,generatedStages:generated.map(s=>s.stage),generatedCount:generated.length,total:end-start+1,nextStage:next,nextProgress:next===null?null:(loadProgress()[next]||null)};console.table([out]);return out}
function exportText(stages=loadSaved()){const text=`// Generated by CLPGenerator Ver.0.4.8.2\nconst GENERATED_STAGES = ${JSON.stringify(stages,null,2)};\n`,blob=new Blob([text],{type:'text/javascript'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='generated-stages-16-50.js';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);return text}
function clearAll(){localStorage.removeItem(STORAGE_KEY);localStorage.removeItem(PROGRESS_KEY);window.CLPGeneratedStages=[];window.CLPGenerationProgress={};console.info('生成済みステージと進捗を削除しました。')}
window.CLPGeneratedStages=loadSaved();window.CLPGenerationProgress=loadProgress();
return {generateNext,generateSeveral,requestStop,status,exportText,clearAll,loadSaved,loadProgress};})();
