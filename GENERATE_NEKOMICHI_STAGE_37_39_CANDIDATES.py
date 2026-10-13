from pathlib import Path
from datetime import datetime
import json, subprocess, tempfile, sys

ROOT=Path.cwd()
OUT_JSON=ROOT/'NEKOMICHI_STAGE_37_39_CANDIDATES.json'
OUT_TXT=ROOT/'NEKOMICHI_STAGE_37_39_CANDIDATES.txt'
NODE=r'''
const fs=require('fs'),vm=require('vm');global.window=global;
function load(n){vm.runInThisContext(fs.readFileSync(n,'utf8'),{filename:n});}
load('stages.js');load('logic-engine.js');
const N=8, TARGETS=[37,38,39], CANDIDATES_PER_STAGE=4, MAX_ATTEMPTS=250000;
let seed=0x37583921;
function rnd(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(rnd()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
const key=(r,c)=>`${r}-${c}`;
function randomSolution(){
 for(let tries=0;tries<300;tries++){
  const p=shuffle([...Array(N).keys()]);
  if(p.every((c,r)=>r===0||Math.abs(c-p[r-1])>1))return p;
 }
 return null;
}
function growRegions(solution){
 const g=Array.from({length:N},()=>Array(N).fill(-1));
 const frontier=[];
 for(let r=0;r<N;r++){g[r][solution[r]]=r;frontier.push([r,solution[r]]);}
 let left=N*N-N, guard=10000;
 const dirs=[[1,0],[-1,0],[0,1],[0,-1]];
 while(left>0&&guard-->0){
  const assigned=[];
  for(let r=0;r<N;r++)for(let c=0;c<N;c++)if(g[r][c]>=0)assigned.push([r,c]);
  shuffle(assigned);let changed=false;
  for(const [r,c] of assigned){
   const ds=shuffle([...dirs]);
   for(const [dr,dc] of ds){const rr=r+dr,cc=c+dc;if(rr>=0&&rr<N&&cc>=0&&cc<N&&g[rr][cc]<0){g[rr][cc]=g[r][c];left--;changed=true;break;}}
   if(changed)break;
  }
  if(!changed)return null;
 }
 return left===0?g:null;
}
function countSolutions(stage,limit=2){
 const out=[],cols=new Set(),regs=new Set(),a=Array(N).fill(-1);
 function rec(r,prev){
  if(out.length>=limit)return;if(r===N){out.push([...a]);return;}
  for(let c=0;c<N;c++){
   const rg=stage.regions[r][c];
   if(cols.has(c)||regs.has(rg)||(prev!==null&&Math.abs(prev-c)<=1))continue;
   a[r]=c;cols.add(c);regs.add(rg);rec(r+1,c);cols.delete(c);regs.delete(rg);
  }
 }
 rec(0,null);return out;
}
function productionRun(stage,maxLevel){
 const revealed=new Set(),marks=new Map(),answer=new Set(stage.solution.map((c,r)=>key(r,c))),trace=[];
 let guard=N*N*20;
 while(revealed.size<N&&guard-->0){
  const s=CLPLogic.logicalStep(stage,revealed,marks,maxLevel);if(!s)break;
  const targets=s.targets||[s.target];let changed=0;
  if(s.kind==='only'){
   if(!answer.has(s.target))return {solved:false,unsafe:true,trace};
   if(!revealed.has(s.target)){revealed.add(s.target);changed++;}
  }else{
   if(targets.some(x=>answer.has(x)))return {solved:false,unsafe:true,trace};
   for(const x of targets)if(!marks.has(x)){marks.set(x,'x');changed++;}
  }
  trace.push({kind:s.kind,ruleId:s.ruleId,ruleLevel:s.ruleLevel,target:s.target,targetCount:targets.length,message:s.message});
  if(!changed)return {solved:false,unsafe:true,trace};
 }
 const usage={};for(const x of trace)usage[x.ruleId]=(usage[x.ruleId]||0)+1;
 return {solved:revealed.size===N,unsafe:false,steps:trace.length,highestRule:Math.max(0,...trace.map(x=>x.ruleLevel)),firstRule:trace[0]?.ruleId||null,usage,trace};
}
function signature(stage){return JSON.stringify([stage.size,stage.regions,stage.solution]);}
const existing=new Set(CLP_STAGES.map(signature));
const selected={37:[],38:[],39:[]};let attempts=0;
while(attempts++<MAX_ATTEMPTS&&TARGETS.some(id=>selected[id].length<CANDIDATES_PER_STAGE)){
 const solution=randomSolution();if(!solution)continue;
 const regions=growRegions(solution);if(!regions)continue;
 const base={size:N,regions,solution};if(existing.has(signature(base)))continue;
 const sols=countSolutions(base,2);if(sols.length!==1||!sols[0].every((c,r)=>c===solution[r]))continue;
 const l1=productionRun(base,1),l2=productionRun(base,2),l3=productionRun(base,3);
 if(!l2.solved||l2.unsafe||!l3.solved||l3.unsafe)continue;
 if(!l2.firstRule)continue;
 // Avoid trivial all-Level-1 replacements, but keep the beginner path natural.
 const score=(l1.solved?18:0)+l2.steps+(l2.highestRule*6)+Object.keys(l2.usage).length*2;
 for(const id of TARGETS){
  if(selected[id].length>=CANDIDATES_PER_STAGE)continue;
  const duplicate=Object.values(selected).flat().some(x=>signature(x)===signature(base));if(duplicate)break;
  selected[id].push({...base,audit:{unique:true,level1Solved:l1.solved,level2Solved:l2.solved,level3Solved:l3.solved,steps:l2.steps,highestRule:l2.highestRule,firstRule:l2.firstRule,usage:l2.usage,score},trace:l2.trace});
  break;
 }
}
if(TARGETS.some(id=>selected[id].length<CANDIDATES_PER_STAGE)){
 console.error(JSON.stringify({error:'not enough candidates',attempts,counts:Object.fromEntries(TARGETS.map(id=>[id,selected[id].length]))}));process.exit(2);
}
for(const id of TARGETS)selected[id].sort((a,b)=>a.audit.score-b.audit.score||a.audit.steps-b.audit.steps);
console.log(JSON.stringify({generatedAt:new Date().toISOString(),seed:'0x37583921',attempts,criteria:{size:8,unique:true,noInitialCats:true,productionLevel2Solved:true,productionLevel3Solved:true,noUnsafeRules:true,noExistingDuplicate:true},selected}));
'''
try:
    for name in ('stages.js','logic-engine.js'):
        if not (ROOT/name).is_file(): raise RuntimeError(name+' is missing')
    with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
        f.write(NODE); runner=Path(f.name)
    try:
        p=subprocess.run(['node',str(runner)],cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=300)
    finally:
        runner.unlink(missing_ok=True)
    if p.returncode:
        raise RuntimeError((p.stdout or '')+(p.stderr or ''))
    raw=(p.stdout or '').strip(); a=raw.find('{'); b=raw.rfind('}')
    if a<0 or b<a: raise RuntimeError('Node output did not contain JSON: '+raw[:500])
    data=json.loads(raw[a:b+1])
    OUT_JSON.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['NEKOMICHI STAGE 37-39 REGENERATION CANDIDATES',f"Generated: {datetime.now().isoformat(timespec='seconds')}",f"Attempts: {data['attempts']}",'','=== FIXED ACCEPTANCE CRITERIA ===']
    for k,v in data['criteria'].items(): lines.append(f'{k}={v}')
    for sid in ('37','38','39'):
        lines += ['',f'=== STAGE {sid} CANDIDATES ===']
        for i,c in enumerate(data['selected'][sid],1):
            lines += [f'CANDIDATE {i}',f"solution={c['solution']}",f"audit={json.dumps(c['audit'],ensure_ascii=False)}",'regions=']
            lines += [' '.join(map(str,row)) for row in c['regions']]
            lines += ['trace=']+[json.dumps(x,ensure_ascii=False) for x in c['trace']]
    lines += ['','=== NEXT STEP ===','Candidate 1 for each stage is the current automatic recommendation because candidates are sorted by the lowest Level-2 complexity score.','Do not edit stages.js manually. The next update script will preserve story/theme metadata and replace only regions, solution, and quality fields after one more cross-check.']
    OUT_TXT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('OK: Nekomichi Stage 37-39 replacement candidates generated.')
    print(f"ATTEMPTS: {data['attempts']}")
    for sid in ('37','38','39'):
        best=data['selected'][sid][0]
        print(f"STAGE_{sid}_BEST: steps={best['audit']['steps']} highestRule={best['audit']['highestRule']} firstRule={best['audit']['firstRule']} level1Solved={best['audit']['level1Solved']}")
    print('OUTPUT_JSON: '+OUT_JSON.name)
    print('OUTPUT_TXT: '+OUT_TXT.name)
    print('SEND: Upload NEKOMICHI_STAGE_37_39_CANDIDATES.json to Copilot.')
except Exception as e:
    print('ERROR: '+str(e)); sys.exit(1)
