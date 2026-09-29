window.CLPAssumption=(()=>{
const key=(r,c)=>`${r}-${c}`;
const parse=id=>id.split('-').map(Number);

function cloneState(revealed,marks){
 return {revealed:new Set(revealed),marks:new Map(marks)};
}

function contradiction(stage,revealed,marks){
 const n=stage.size,seenRows=new Set(),seenCols=new Set(),seenRegions=new Set();
 for(const id of revealed){
  const [r,c]=parse(id),region=stage.regions[r][c];
  if(seenRows.has(r))return `行${r+1}に猫が2匹以上`;
  if(seenCols.has(c))return `列${c+1}に猫が2匹以上`;
  if(seenRegions.has(region))return `色エリア${region}に猫が2匹以上`;
  seenRows.add(r);seenCols.add(c);seenRegions.add(region);
 }
 const cats=[...revealed];
 for(let i=0;i<cats.length;i++)for(let j=i+1;j<cats.length;j++){
  const [r1,c1]=parse(cats[i]),[r2,c2]=parse(cats[j]);
  if(Math.abs(r1-r2)<=1&&Math.abs(c1-c2)<=1)return `${cats[i]}と${cats[j]}の猫が隣接`;
 }
 const candidates=window.CLPLogic.candidates(stage,revealed,marks);
 for(let r=0;r<n;r++)if(!seenRows.has(r)&&![...candidates].some(id=>parse(id)[0]===r))return `行${r+1}に猫候補がない`;
 for(let c=0;c<n;c++)if(!seenCols.has(c)&&![...candidates].some(id=>parse(id)[1]===c))return `列${c+1}に猫候補がない`;
 for(const region of new Set(stage.regions.flat()))if(!seenRegions.has(region)&&![...candidates].some(id=>{const [r,c]=parse(id);return stage.regions[r][c]===region}))return `色エリア${region}に猫候補がない`;
 return null;
}

function propagate(stage,revealed,marks,maxSteps=1000){
 const trace=[];let reason=contradiction(stage,revealed,marks);
 if(reason)return {status:'contradiction',reason,steps:0,trace,revealed,marks};
 for(let i=0;i<maxSteps;i++){
  if(revealed.size===stage.size)return {status:'solved',reason:null,steps:trace.length,trace,revealed,marks};
  const step=window.CLPLogic.logicalStep(stage,revealed,marks,3);
  if(!step)return {status:'stalled',reason:null,steps:trace.length,trace,revealed,marks};
  if(step.kind==='only'){
   if(marks.get(step.target)==='x')return {status:'contradiction',reason:`×のマス${step.target}を猫に確定`,steps:trace.length,trace,revealed,marks};
   revealed.add(step.target);
  }else{
   for(const id of step.targets||[step.target]){
    if(revealed.has(id))return {status:'contradiction',reason:`猫のマス${id}を除外`,steps:trace.length,trace,revealed,marks};
    marks.set(id,'x');
   }
  }
  trace.push({ruleLevel:step.ruleLevel,ruleId:step.ruleId,kind:step.kind,target:step.target});
  reason=contradiction(stage,revealed,marks);
  if(reason)return {status:'contradiction',reason,steps:trace.length,trace,revealed,marks};
 }
 return {status:'limit',reason:'伝播上限に到達',steps:trace.length,trace,revealed,marks};
}

function baseState(stage){
 return propagate(stage,new Set(),new Map());
}

function testCandidate(stage,base,id){
 const catState=cloneState(base.revealed,base.marks);catState.revealed.add(id);
 const asCat=propagate(stage,catState.revealed,catState.marks);
 const xState=cloneState(base.revealed,base.marks);xState.marks.set(id,'x');
 const asX=propagate(stage,xState.revealed,xState.marks);
 let conclusion='none',forcedValue=null,assumptionDepth=0;
 if(asCat.status==='contradiction'&&asX.status!=='contradiction'){
  conclusion='cat-assumption-contradicts';forcedValue='x';assumptionDepth=1;
 }else if(asX.status==='contradiction'&&asCat.status!=='contradiction'){
  conclusion='x-assumption-contradicts';forcedValue='cat';assumptionDepth=1;
 }else if(asCat.status==='solved'&&asX.status==='contradiction'){
  conclusion='cat-forced';forcedValue='cat';assumptionDepth=1;
 }else if(asX.status==='solved'&&asCat.status==='contradiction'){
  conclusion='x-forced';forcedValue='x';assumptionDepth=1;
 }
 return {candidate:id,conclusion,forcedValue,assumptionDepth,asCat:{status:asCat.status,steps:asCat.steps,reason:asCat.reason},asX:{status:asX.status,steps:asX.steps,reason:asX.reason}};
}

function testDepth2(stage,base,firstId){
 const first=cloneState(base.revealed,base.marks);first.revealed.add(firstId);
 const afterFirst=propagate(stage,first.revealed,first.marks);
 if(afterFirst.status!=='stalled')return null;
 const candidates=[...window.CLPLogic.candidates(stage,afterFirst.revealed,afterFirst.marks)].slice(0,30);
 for(const secondId of candidates){
  if(secondId===firstId)continue;
  const result=testCandidate(stage,afterFirst,secondId);
  if(result.assumptionDepth===1)return {firstAssumption:firstId,secondCandidate:secondId,result,depth:2};
 }
 return null;
}

function analyzeStage(stage){
 const base=baseState(stage);
 if(base.status==='solved')return {stage:stage.stage,size:`${stage.size}x${stage.size}`,baseStatus:'solved',assumptionDepth:0,classification:'logic-level-1-3',candidateTests:[],depth2Example:null};
 const candidates=[...window.CLPLogic.candidates(stage,base.revealed,base.marks)];
 const tests=candidates.map(id=>testCandidate(stage,base,id));
 const depth1=tests.filter(x=>x.assumptionDepth===1);
 let depth=depth1.length?1:null,depth2Example=null,classification=depth1.length?'level-4-single-assumption':'undetermined';
 if(!depth1.length){
  for(const id of candidates.slice(0,30)){
   depth2Example=testDepth2(stage,base,id);
   if(depth2Example){depth=2;classification='level-5-two-step-assumption';break}
  }
 }
 if(depth===null)classification='requires-deeper-analysis-or-stage-adjustment';
 return {stage:stage.stage,size:`${stage.size}x${stage.size}`,baseStatus:base.status,baseLogicSteps:base.steps,revealedBeforeAssumption:base.revealed.size,remainingCandidates:candidates.length,assumptionDepth:depth,classification,depth1Conclusions:depth1.length,candidateTests:tests,depth2Example};
}

function analyzeUnresolved(stages){
 return stages.map(analyzeStage).filter(x=>x.baseStatus!=='solved');
}

function printReport(stages){
 const report=analyzeUnresolved(stages);window.CLPAssumptionReport=report;
 console.group('猫ロジック Ver.0.4.6 仮定・矛盾深度解析');
 if(!report.length)console.info('全ステージがレベル1～3の論理で解決できます。');
 for(const x of report){
  console.group(`Stage ${x.stage} ${x.size}`);
  console.table([{stage:x.stage,baseLogicSteps:x.baseLogicSteps,revealed:x.revealedBeforeAssumption,remainingCandidates:x.remainingCandidates,assumptionDepth:x.assumptionDepth??'3+',classification:x.classification,depth1Conclusions:x.depth1Conclusions}]);
  const useful=x.candidateTests.filter(t=>t.conclusion!=='none');
  if(useful.length)console.table(useful.map(t=>({candidate:t.candidate,forcedValue:t.forcedValue,conclusion:t.conclusion,catStatus:t.asCat.status,catSteps:t.asCat.steps,catReason:t.asCat.reason||'',xStatus:t.asX.status,xSteps:t.asX.steps,xReason:t.asX.reason||''})));
  else console.info('1段階の仮定では確定できませんでした。');
  if(x.depth2Example)console.info('2段階解析例:',x.depth2Example);
  console.groupEnd();
 }
 console.groupEnd();return report;
}

return {contradiction,propagate,analyzeStage,analyzeUnresolved,printReport};
})();
