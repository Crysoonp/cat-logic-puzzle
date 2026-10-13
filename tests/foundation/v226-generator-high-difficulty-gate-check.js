const fs=require('fs'),vm=require('vm');
const store=new Map();global.window=global;global.localStorage={getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)};global.STAGES=[];
global.CLPQuality={inspectAll:()=>[{uniqueSolution:true,solutionCount:1}],canonicalSignature:s=>`sig-${s.stage}`};
global.CLPLogic={analyze:s=>s.logic};
vm.runInThisContext(fs.readFileSync('stage-generator.js','utf8'),{filename:'stage-generator.js'});
function ok(v,m){if(!v)throw new Error(m)}
const known=new Set(),normal={stage:40,size:7,logic:{logicOnly:true,difficulty:2}},good={stage:500,size:12,logic:{logicOnly:true,difficulty:3,advancedDifficulty:4,highDifficultyProfile:{smallAreaWithinTarget:true,openingWithinTarget:true,highDifficultyCandidate:true}}},bad={stage:501,size:12,logic:{logicOnly:true,difficulty:3,advancedDifficulty:3,highDifficultyProfile:{smallAreaWithinTarget:false,openingWithinTarget:false,highDifficultyCandidate:false}}};
ok(CLPGenerator.evaluate(normal,known,'normal').accepted,'normal generation regression');
ok(CLPGenerator.evaluate(good,known,'high-difficulty').accepted,'valid high difficulty candidate');
const rejected=CLPGenerator.evaluate(bad,known,'high-difficulty');ok(!rejected.accepted,'invalid high difficulty rejected');ok(rejected.reasons.includes('high-difficulty-small-areas'),'small area reason');ok(rejected.reasons.includes('high-difficulty-opening'),'opening reason');ok(rejected.reasons.includes('high-difficulty-inference'),'inference reason');ok(rejected.reasons.includes('high-difficulty-star'),'star reason');
const small={stage:502,size:8,logic:good.logic},smallResult=CLPGenerator.evaluate(small,known,'high-difficulty');ok(smallResult.reasons.includes('high-difficulty-size'),'size reason');
console.log('V226 generator high-difficulty gate check: PASS');