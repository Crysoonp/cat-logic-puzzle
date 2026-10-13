const fs=require('fs'),vm=require('vm');
global.window=global;
vm.runInThisContext(fs.readFileSync('quality-engine.js','utf8'),{filename:'quality-engine.js'});
function ok(value,message){if(!value)throw new Error(message)}
const unique={stage:1,size:4,solution:[2,0,3,1],regions:[[0,0,0,2],[1,0,0,2],[3,2,2,2],[3,3,3,2]]};
const multiple={stage:999,size:4,solution:[1,3,0,2],regions:[[0,0,1,1],[0,0,1,1],[2,2,3,3],[2,2,3,3]]};
const one=CLPQuality.findSolutions(unique,2);
ok(one.count===1,'unique count');
ok(one.solutions.length===1,'unique witness length');
ok(JSON.stringify(one.solutions[0])===JSON.stringify(unique.solution),'unique witness content');
ok(one.limited===false,'unique limited flag');
const many=CLPQuality.findSolutions(multiple,2);
ok(many.count===2,'multiple count');
ok(many.solutions.length===2,'multiple witness length');
ok(JSON.stringify(many.solutions[0])!==JSON.stringify(many.solutions[1]),'witnesses differ');
ok(many.limited===true,'multiple limited flag');
for(const solution of many.solutions){
 ok(solution.length===multiple.size,'solution length');
 ok(new Set(solution).size===multiple.size,'column uniqueness');
 for(let r=1;r<solution.length;r++)ok(Math.abs(solution[r]-solution[r-1])>1,'adjacency rule');
}
const legacy=CLPQuality.countSolutions(multiple,2);
ok(legacy.count===many.count&&legacy.nodes===many.nodes,'legacy compatibility');
console.log('V232 solution witness check: PASS');
