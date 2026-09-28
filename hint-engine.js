window.CLPHints=(()=>{
const COST={toy:1,matatabi:2,can:3,paw:2};
function wrongMarks(stage,marks){const out=[];for(const [id,v] of marks)if(v==='x'){const [r,c]=id.split('-').map(Number);if(stage.solution[r]===c)out.push(id)}return out}
return {COST,wrongMarks};})();