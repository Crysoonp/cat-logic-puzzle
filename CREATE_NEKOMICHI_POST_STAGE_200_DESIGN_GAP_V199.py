from pathlib import Path
import json, re, subprocess, sys, time

ROOT=Path.cwd()
OUT=ROOT/'NEKOMICHI_POST_STAGE_200_DESIGN_GAP_V199.txt'

def fail(message): raise RuntimeError(message)
def read(name):
    p=ROOT/name
    if not p.is_file(): fail('Missing required file: '+name)
    return p.read_text(encoding='utf-8',errors='replace')
def check_js(name):
    r=subprocess.run(['node','--check',name],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
    if r.returncode: fail('JavaScript syntax failed: '+name+'\n'+r.stdout+r.stderr)
def has(text,token): return token in text

def main():
    if not (ROOT/'.git').exists(): fail('Run from the cat-logic-puzzle project root')
    audit=read('NEKOMICHI_NEXT_GROWTH_AFTER_STAGE_200_BEFORE_V199.txt')
    files={name:read(name) for name in ['index.html','game.js','style.css','stories.js','stages.js','app-config.js','foundation-manifest.json','STORY_BIBLE.md']}
    for name in ['game.js','stories.js','stages.js','app-config.js']: check_js(name)
    manifest=json.loads(files['foundation-manifest.json'])
    checks={
      'version087': manifest.get('foundationVersion')=='0.8.87' and "const VERSION='0.8.87';" in files['app-config.js'],
      'stageCount200': manifest.get('stageCount')==200,
      'noStage201Data': not has(files['stages.js'],'stage:201') and not has(files['stages.js'],'"stage":201'),
      'noStage250Data': not has(files['stages.js'],'stage:250') and not has(files['stages.js'],'"stage":250'),
      'noStage300Data': not has(files['stages.js'],'stage:300') and not has(files['stages.js'],'"stage":300'),
      'stage200Frozen': manifest.get('forestPlazaStage200MilestoneFoundationV0887',{}).get('status')=='frozen',
      'stage200ActualClearGate': manifest.get('forestPlazaStage200MilestoneFoundationV0887',{}).get('authoritativeUnlockCondition')=='isStageCleared(200)',
      'stage100Frozen': manifest.get('forestPlazaStage100RestSpotFoundationV0883',{}).get('status')=='frozen',
      'map101To200Frozen': manifest.get('stage101To200MapRouteFoundationV0885',{}).get('status')=='frozen',
      'profileFoundationFrozen': manifest.get('catProfileProgressionFoundationV0877',{}).get('status')=='frozen',
      'saveSchema1': manifest.get('saveSchemaVersion')==1,
      'boardSave1': manifest.get('boardSaveVersion')==1,
      'auditBaselinePassed': all(token in audit for token in ['"displayVersion087": true','"stage200MilestoneFrozen": true','"saveSchemaUnchanged": true']),
    }
    failures=[k for k,v in checks.items() if not v]
    if failures: fail('Design-gap prerequisites failed: '+', '.join(failures))

    report=f'''NEKOMICHI POST-STAGE-200 DESIGN GAP V199
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Project: {ROOT}

RESULT
Implementation is intentionally blocked. The current repository does not contain enough confirmed data to safely implement Stage 201, Stage 250, Stage 300, a fourth companion, a Stage-200 Nekokan unlock, or a new Forest Plaza growth element.

CONFIRMED AND FROZEN
- Current foundation version: 0.8.87.
- Existing stage data ends at Stage 200.
- Stage 200 Forest Plaza milestone is frozen.
- Its production condition is actual Stage 200 clear through isStageCleared(200).
- Stage 100 rest spot is frozen.
- Stage 1-200 Journey Map routes are frozen.
- Cat-profile progression foundation is frozen.
- Save schema remains 1 and board-save schema remains 1.

DESIGN-BIBLE DIRECTION THAT IS NOT YET IMPLEMENTATION-READY
- Stage 200 includes a provisional fourth-companion slot and a proposed Nekokan/basic-hint completion point.
- Stage 201-400 broadly covers visits to old community bases and gradual information about Miya's rescue activity and disappearance.
- These are direction-level notes only. Exact event timing, character identity, profile text, dialogue, map region, unlock contract and presentation are unresolved.

MISSING DECISIONS BEFORE ANY IMPLEMENTATION
1. Stage range
   - Whether the next production range is 201-250, 201-300, or 201-400.
   - Number and sizes of boards, difficulty policy, boss stages and generation/audit method.
2. Journey Map
   - New region theme and node grouping.
   - Exact production gate after Stage 200.
   - Return routes and whether the Stage 1-200 map remains one continuous view or gains a region selector.
3. Story
   - Exact first post-Stage-200 event stage.
   - Confirmed dialogue and what Teko learns at that point.
   - Information that remains hidden, including Miya's name timing.
4. Fourth companion
   - Formal name, appearance, first encounter, join stage and confirmed role.
   - Whether the companion owns the proposed detection or one-cat reveal ability.
5. Nekokan and hints
   - Whether Nekokan is a new resource, an item, or only a presentation name.
   - Exact unlock condition, cost, inventory behavior, ad relationship and save requirements.
6. Forest Plaza growth
   - The next single visible element after the Stage 200 footprint badge.
   - Exact before/after appearance, click text and confirmed story meaning.

SAFE NEXT STEP
Do not create update_nekomichi_v199.py yet. First fix one narrow design contract. The recommended first contract is Stage 201-250 production scope because stage data and map expansion depend on it. Keep companion identity, Nekokan and new story dialogue separate until formally decided.

PROTECTED ITEMS
- Do not change the frozen Stage 200 milestone.
- Do not add a dedicated Stage 200 save field.
- Do not infer a fourth companion name, design or profile.
- Do not add Stage 201/250/300 placeholder stages to production data.
- Do not alter existing Stage 1-200 map routes.
- Do not combine stage generation, new story, hub redesign and save-schema changes in one version.

CHECKS
{json.dumps(checks,ensure_ascii=False,indent=2)}

FILES MODIFIED
- None. This is a design-gap report only.
'''
    OUT.write_text(report,encoding='utf-8-sig')
    print('OK: Nekomichi post-Stage-200 design gap report created.')
    print('OK: No confirmed Stage 201, 250 or 300 production contract was found.')
    print('OK: Fourth companion, Nekokan unlock and new story facts remain blocked as provisional.')
    print('OK: Frozen Stage 1-200 foundations and save schemas remain unchanged.')
    print('OK: JavaScript syntax checks passed; no game files were modified.')
    print('OUTPUT:',OUT)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('ERROR:',exc); sys.exit(1)
