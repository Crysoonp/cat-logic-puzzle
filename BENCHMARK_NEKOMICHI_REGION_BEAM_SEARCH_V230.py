from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
RUNNER=ROOT/'tests/foundation/v230-region-beam-search.js'
JS=r'''const fs=require('fs'),vm=require('vm');global.window=global;global.document={addEventListener(){},querySelector(){return null},querySelectorAll(){return []}};
function load(f){vm.runInThisContext(fs.readFileSync(f,'utf8'),{filename:f})}load('logic-engine.js');load('quality-engine.js');load('stages.js');
function stageLike(x){return x&&Number.isInteger(x.stage)&&Number.isInteger(x.size)&&Array.isArray(x.solution)&&Array.isArray(x.regions)}
function collect(v,seen,out){if(!v||typeof v!=='object'||seen.has(v))return;seen.add(v);if(stageLike(v)){out.push(v);return}if(Array.isArray(v)){for(const x of v)collect(x,seen,out);return}for(const [k,x] of Object.entries(v))if(!['global','window','document','console','process','require','module','exports'].includes(k))collect(x,seen,out)}
let stages=[];for(const n of ['CLPStages','STAGES','stages','stageData','StageData'])if(global[n])collect(global[n],new Set(),stages);if(!stages.length)for(const [k,v] of Object.entries(global))if(/stage/i.test(k))collect(v,new Set(),stages);stages=[...new Map(stages.map(s=>[s.stage,s])).values()];
const source=stages.find(s=>s.stage===302);if(!source)throw new Error('Stage 302 not found');
const clone=x=>JSON.parse(JSON.stringify(x)),near=(r,c,n)=>[[r-1,c],[r+1,c],[r,c-1],[r,c+1]].filter(([a,b])=>a>=0&&b>=0&&a<n&&b<n);
function sizes(s){const a=Array(s.size).fill(0);for(const row of s.regions)for(const g of row)a[g]++;return a}
function metric(s){const z=sizes(s),one=z.filter(x=>x===1).length,two=z.filter(x=>x===2).length;return {one,two,score:one*100+Math.max(0,two-2)*30+two*3+Math.max(...z)-Math.min(...z),sizes:z}}
function connected(s,id){let all=[];for(let r=0;r<s.size;r++)for(let c=0;c<s.size;c++)if(s.regions[r][c]===id)all.push([r,c]);if(!all.length)return false;const seen=new Set([all[0].join(',')]),q=[all[0]];while(q.length){const [r,c]=q.shift();for(const p of near(r,c,s.size))if(s.regions[p[0]][p[1]]===id&&!seen.has(p.join(','))){seen.add(p.join(','));q.push(p)}}return seen.size===all.length}
const cats=new Set(source.solution.map((c,r)=>`${r},${c}`));
function key(s){return s.regions.map(r=>r.join(',')).join(';')}
function moves(s){const z=sizes(s),small=[...z.keys()].filter(i=>z[i]<=4),out=[];for(let r=0;r<s.size;r++)for(let c=0;c<s.size;c++){const donor=s.regions[r][c];if(z[donor]<=2||cats.has(`${r},${c}`))continue;for(const [rr,cc] of near(r,c,s.size)){const target=s.regions[rr][cc];if(target!==donor&&small.includes(target))out.push([r,c,donor,target])}}return out}
function unique(s){return CLPQuality.inspectAll([s])[0].uniqueSolution===true}
let beam=[clone(source)],seen=new Set([key(source)]),best={stage:clone(source),metric:metric(source)},found=null,checks=0,accepted=0,round=0;const start=Date.now(),deadline=start+45000;let next=start+5000;
while(beam.length&&Date.now()<deadline&&!found){round++;const nextStates=[];for(const cur of beam){for(const [r,c,donor,target] of moves(cur)){if(Date.now()>=deadline)break;const n=clone(cur);n.regions[r][c]=target;const k=key(n);if(seen.has(k)||!connected(n,donor)||!connected(n,target))continue;seen.add(k);checks++;if(!unique(n))continue;accepted++;const m=metric(n);if(m.score<best.metric.score)best={stage:clone(n),metric:m};if(m.one<=1&&m.two<=2){found={stage:n,metric:m,logic:CLPLogic.analyze(n)};break}nextStates.push({stage:n,metric:m})}if(found||Date.now()>=deadline)break}
 nextStates.sort((a,b)=>a.metric.score-b.metric.score||a.metric.one-b.metric.one||a.metric.two-b.metric.two);beam=nextStates.slice(0,35).map(x=>x.stage);
 if(Date.now()>=next){console.log(`PROGRESS: ${((Date.now()-start)/1000).toFixed(1)}s round=${round} beam=${beam.length} checks=${checks} accepted=${accepted} best=${best.metric.score} one=${best.metric.one} two=${best.metric.two}`);next+=5000}
}
const logic=found&&found.logic,summary={version:'V230',elapsedSeconds:Number(((Date.now()-start)/1000).toFixed(3)),status:found?'FOUND':'NOT_FOUND',sourceStage:302,rounds:round,statesSeen:seen.size,uniquenessChecks:checks,acceptedStates:accepted,best:{metric:best.metric},candidate:found&&{size:found.stage.size,areaSizes:found.metric.sizes,logicOnly:logic.logicOnly,advancedDifficulty:logic.advancedDifficulty,advancedScore:logic.advancedDifficultyScore,highDifficultyProfile:logic.highDifficultyProfile}};
fs.writeFileSync('NEKOMICHI_REGION_BEAM_SEARCH_V230.json',JSON.stringify(summary,null,2));fs.writeFileSync('NEKOMICHI_REGION_BEAM_CANDIDATES_V230.json',JSON.stringify({candidateOnly:true,notIntegrated:true,candidates:found?[found.stage]:[]},null,2));fs.writeFileSync('NEKOMICHI_REGION_BEAM_SEARCH_V230.txt',['NEKOMICHI REGION BEAM SEARCH V230',`Status: ${summary.status}`,`Elapsed: ${summary.elapsedSeconds}s`,`Rounds: ${round}`,`States seen: ${seen.size}`,`Uniqueness checks: ${checks}`,`Accepted states: ${accepted}`,`Best: ${JSON.stringify(summary.best)}`,`Candidate: ${JSON.stringify(summary.candidate)}`].join('\n')+'\n');
console.log(`RESULT: ${summary.status}`);console.log(`Best: one=${best.metric.one}, two=${best.metric.two}, score=${best.metric.score}`);console.log('WROTE: NEKOMICHI_REGION_BEAM_SEARCH_V230.txt');console.log('WROTE: NEKOMICHI_REGION_BEAM_SEARCH_V230.json');console.log('WROTE: NEKOMICHI_REGION_BEAM_CANDIDATES_V230.json');console.log('SUCCESS: V230 region beam search completed');'''
def main():
 for name in ('logic-engine.js','quality-engine.js','stages.js'):
  if not (ROOT/name).is_file():print(f'ERROR: {name} not found');return 1
 RUNNER.parent.mkdir(parents=True,exist_ok=True);RUNNER.write_text(JS,encoding='utf-8')
 p=subprocess.run(['node',str(RUNNER.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace',timeout=60)
 print(p.stdout,end='');print(p.stderr,end='');return p.returncode
if __name__=='__main__':raise SystemExit(main())
