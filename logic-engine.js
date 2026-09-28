window.CLPLogic=(()=>{
function key(r,c){return `${r}-${c}`}
function candidates(stage,revealed,marks){
 const n=stage.size, foundRows=new Set(),foundCols=new Set(),foundRegs=new Set(),out=new Set();
 for(const id of revealed){const [r,c]=id.split('-').map(Number);foundRows.add(r);foundCols.add(c);foundRegs.add(stage.regions[r][c])}
 for(let r=0;r<n;r++)for(let c=0;c<n;c++){
  const id=key(r,c);if(revealed.has(id)||marks.get(id)==='x'||foundRows.has(r)||foundCols.has(c)||foundRegs.has(stage.regions[r][c]))continue;
  let adjacent=false;for(const f of revealed){const [fr,fc]=f.split('-').map(Number);if(Math.abs(fr-r)<=1&&Math.abs(fc-c)<=1){adjacent=true;break}}
  if(!adjacent)out.add(id)
 }return out
}
function units(stage){const n=stage.size,a=[];for(let r=0;r<n;r++)a.push({type:'row',index:r,cells:Array.from({length:n},(_,c)=>key(r,c))});for(let c=0;c<n;c++)a.push({type:'column',index:c,cells:Array.from({length:n},(_,r)=>key(r,c))});for(let g=0;g<n;g++){const cells=[];for(let r=0;r<n;r++)for(let c=0;c<n;c++)if(stage.regions[r][c]===g)cells.push(key(r,c));a.push({type:'region',index:g,cells})}return a}

function safeXStep(stage,revealed,marks){
 const n=stage.size;
 for(const found of revealed){
  const [fr,fc]=found.split('-').map(Number),reg=stage.regions[fr][fc];
  for(let r=0;r<n;r++)for(let c=0;c<n;c++){
   const id=key(r,c);
   if(id===found||revealed.has(id)||marks.get(id)==='x')continue;
   if(Math.abs(fr-r)<=1&&Math.abs(fc-c)<=1){
    return {kind:'safe-x',target:id,focus:[found,id],message:'このマスは、見つけた猫の周囲にあるから猫はいないニャン。光ったマスへ×を付けるニャン。'};
   }
   if(r===fr){
    return {kind:'safe-x',target:id,focus:[found,id],message:'このマスは、見つけた猫と同じ行だから猫はいないニャン。光ったマスへ×を付けるニャン。'};
   }
   if(c===fc){
    return {kind:'safe-x',target:id,focus:[found,id],message:'このマスは、見つけた猫と同じ列だから猫はいないニャン。光ったマスへ×を付けるニャン。'};
   }
   if(stage.regions[r][c]===reg){
    return {kind:'safe-x',target:id,focus:[found,id],message:'このマスは、見つけた猫と同じ色エリアだから猫はいないニャン。光ったマスへ×を付けるニャン。'};
   }
  }
 }
 return null;
}
function nextStep(stage,revealed,marks){const cand=candidates(stage,revealed,marks);for(const u of units(stage)){if(u.cells.some(x=>revealed.has(x)))continue;const left=u.cells.filter(x=>cand.has(x));if(left.length===1){const names={row:'行',column:'列',region:'色エリア'};return {kind:'only',target:left[0],focus:u.cells,message:`この${names[u.type]}で猫を置けるのは残り1マスだけだニャン。`}}}for(const id of revealed){const [r,c]=id.split('-').map(Number),focus=[];for(let rr=0;rr<stage.size;rr++)for(let cc=0;cc<stage.size;cc++)if((rr===r||cc===c||Math.abs(rr-r)<=1&&Math.abs(cc-c)<=1||stage.regions[rr][cc]===stage.regions[r][c])&&key(rr,cc)!==id&&!marks.has(key(rr,cc)))focus.push(key(rr,cc));if(focus.length)return {kind:'exclude',target:focus[0],focus,message:'見つけた猫と同じ行・列・色エリア、周囲8マスには猫はいないニャン。'}}return null}
function analyze(stage){const n=stage.size,sizes=Array(n).fill(0);stage.regions.flat().forEach(x=>sizes[x]++);const singletons=sizes.filter(x=>x===1).length;let score=n+Math.max(0,3-singletons)*2+(stage.logicLevel||1)*3;return {boardSize:n,singletons,logicLevel:stage.logicLevel||1,difficulty:score<=10?'BEGINNER':score<=16?'EASY':score<=22?'NORMAL':score<=28?'HARD':'ELITE'}}
return {candidates,safeXStep,nextStep,analyze};})();