window.CLPDifficultyManager=(()=>{
function stageBand(stageNo){
 if(stageNo<=10)return {min:1,max:1,logicRequired:true};
 if(stageNo<=20)return {min:1,max:2,logicRequired:true};
 if(stageNo<=30)return {min:1,max:2,logicRequired:true};
 if(stageNo<=50)return {min:2,max:3,logicRequired:true};
 if(stageNo<=100)return {min:2,max:4,logicRequired:true};
 if(stageNo<=300)return {min:3,max:5,logicRequired:false};
 return {min:2,max:5,logicRequired:false};
}
function classify(stage,logic,quality,assumption){
 let difficulty=logic.difficulty,solveType=logic.solveType,assumptionDepth=0,hard=false;
 if(!logic.logicOnly){
  assumptionDepth=assumption?.assumptionDepth??3;
  if(assumptionDepth===1){difficulty=Math.max(4,difficulty);solveType='assumption-logic';}
  else if(assumptionDepth===2){difficulty=5;solveType='assumption-logic';}
  else {difficulty=5;solveType='deeper-analysis-required';}
 }
 hard=difficulty>=3;
 const band=stageBand(stage.stage),reasons=[];
 if(!quality?.uniqueSolution)reasons.push('唯一解ではない');
 if(quality?.decision==='rejected')reasons.push(...quality.reasons);
 if(difficulty<band.min||difficulty>band.max)reasons.push(`ステージ帯の推奨難易度${band.min}～${band.max}外`);
 if(band.logicRequired&&!logic.logicOnly)reasons.push(`ステージ${stage.stage}は完全論理解決必須帯`);
 let decision='accepted';
 if(reasons.some(x=>x.includes('唯一解')||x.includes('複数解')||x.includes('解なし')||x.includes('重複')))decision='rejected';
 else if(reasons.length)decision='hold';
 return {stage:stage.stage,size:`${stage.size}x${stage.size}`,difficulty,hard,difficultyScore:logic.difficultyScore,logicOnly:logic.logicOnly,solveType,assumptionDepth,highestRuleLevel:logic.highestRuleLevel,uniqueSolution:quality?.uniqueSolution??false,qualityDecision:quality?.decision??'unknown',band:`${band.min}-${band.max}`,finalDecision:decision,reasons};
}
function evaluateAll(stages){
 const logic=window.CLPLogic.analyzeAll(stages),quality=window.CLPQuality.inspectAll(stages),assumptions=new Map(window.CLPAssumption.analyzeUnresolved(stages).map(x=>[x.stage,x]));
 return stages.map((stage,i)=>classify(stage,logic[i],quality[i],assumptions.get(stage.stage)));
}
function printReport(stages){
 const report=evaluateAll(stages);window.CLPFinalDifficultyReport=report;
 console.group('猫ロジック Ver.0.4.7 最終難易度・採用判定');
 console.table(report.map(x=>({stage:x.stage,size:x.size,difficulty:x.difficulty,hard:x.hard,score:x.difficultyScore,logicOnly:x.logicOnly,solveType:x.solveType,assumptionDepth:x.assumptionDepth,unique:x.uniqueSolution,band:x.band,decision:x.finalDecision,reasons:x.reasons.join(' / ')})));
 const hold=report.filter(x=>x.finalDecision!=='accepted');
 if(hold.length)console.warn('要確認ステージ:',hold.map(x=>({stage:x.stage,decision:x.finalDecision,reasons:x.reasons})));
 else console.info('全ステージが最終採用条件を通過しました。');
 console.groupEnd();return report;
}
return {stageBand,classify,evaluateAll,printReport};
})();
