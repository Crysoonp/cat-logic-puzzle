from pathlib import Path
from datetime import datetime
import hashlib, json, re, shutil, subprocess, sys

ROOT=Path.cwd(); BACKUP=ROOT/'.nekomichi-backups'/('before-v130-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
BACKED=[]; CREATED=[]
SOURCE_VERSION='0.8.39'; TARGET_VERSION='0.8.41'
OLD_HASH='1e33bd3ee2e99abd3a09b813b7b269a3c2602fce96ec2af059becc23072e53ac'

def fail(m): raise RuntimeError(m)
def run(args,check=True,timeout=300):
 r=subprocess.run(args,cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=timeout)
 if check and r.returncode: fail('command failed: '+' '.join(args)+'\n'+r.stdout+r.stderr)
 return r
def backup(p):
 d=BACKUP/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d);BACKED.append((p,d))
def rollback():
 run(['git','reset'],check=False)
 for p,d in reversed(BACKED):
  if d.exists():p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(d,p)
 for p in reversed(CREATED):
  if p.exists():p.unlink()
def once(text,old,new,label):
 n=text.count(old)
 if n!=1:fail(f'{label}: expected 1 match, found {n}')
 return text.replace(old,new,1)
def version(text):
 m=re.search(r"const\s+VERSION\s*=\s*['\"]([^'\"]+)['\"]",text)
 if not m or m.group(1)!=SOURCE_VERSION:fail('source version must be Ver.'+SOURCE_VERSION)
 return text[:m.start(1)]+TARGET_VERSION+text[m.end(1):]
try:
 names=['style.css','app-config.js','index.html','css-visual-baseline.json','foundation-manifest.json','tests/foundation/v108-css-safety-stop-check.js','tests/foundation/v109-css-cleanup-closure-check.js','tests/foundation/v128-marker-visibility-check.js']
 paths={n:ROOT/n for n in names}
 for n,p in paths.items():
  if not p.is_file():fail('required file missing: '+n)
 if run(['git','diff','--cached','--name-only']).stdout.strip():fail('Git index already contains staged changes')
 for p in paths.values():backup(p)
 raw=paths['style.css'].read_bytes();old_hash=hashlib.sha256(raw).hexdigest()
 if old_hash!=OLD_HASH:fail('style.css source hash mismatch: '+old_hash)
 text=raw.decode('utf-8-sig')
 anchor='/* End Ver.0.8.39 */'
 if anchor not in text:fail('Ver.0.8.39 marker block end not found')
 addition='''\n/* Ver.0.8.41: keep the question mark dot visually separated. */\n.tile > .mark-symbol.mark-q .mark-outline{stroke-width:11!important}\n.tile > .mark-symbol.mark-q .mark-core{stroke-width:7.5!important}\n#modeCycle .mark-symbol.mark-q .mark-outline{stroke-width:11!important}\n#modeCycle .mark-symbol.mark-q .mark-core{stroke-width:7.5!important}\n/* End Ver.0.8.41 */'''
 text=once(text,anchor,anchor+addition,'question separation override')
 paths['style.css'].write_text(text,encoding='utf-8')
 updated=paths['style.css'].read_bytes();new_hash=hashlib.sha256(updated).hexdigest();new_size=len(updated)
 baseline=json.loads(paths['css-visual-baseline.json'].read_text(encoding='utf-8-sig'))
 if baseline.get('currentStyleSha256')!=OLD_HASH:fail('baseline currentStyleSha256 mismatch')
 baseline['baselineVersion']=TARGET_VERSION;baseline['currentStyleSha256']=new_hash;baseline['styleBytes']=new_size
 baseline['questionDotSeparationV0841']={'status':'runtime-review-required','previousStyleSha256':OLD_HASH,'approvedStyleSha256':new_hash,'questionOutlineStrokeWidth':11,'questionCoreStrokeWidth':7.5,'xAndTriangleUnchanged':True,'reason':'Prevent the question-mark stem from visually merging with its dot on small cells.'}
 paths['css-visual-baseline.json'].write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for n in ['tests/foundation/v108-css-safety-stop-check.js','tests/foundation/v109-css-cleanup-closure-check.js']:
  p=paths[n];p.write_text(once(p.read_text(encoding='utf-8-sig'),OLD_HASH,new_hash,n+' hash'),encoding='utf-8')
 marker_test=paths['tests/foundation/v128-marker-visibility-check.js']
 marker_text=marker_test.read_text(encoding='utf-8-sig')
 marker_text=once(marker_text,OLD_HASH,new_hash,'v128 marker approved hash')
 marker_text=marker_text.replace('Ver.0.8.39 CSS hash mismatch','approved marker CSS hash mismatch')
 marker_test.write_text(marker_text,encoding='utf-8')
 paths['app-config.js'].write_text(version(paths['app-config.js'].read_text(encoding='utf-8-sig')),encoding='utf-8')
 index=paths['index.html'].read_text(encoding='utf-8-sig');count=index.count('Ver.0.8.39')
 if count!=3:fail(f'index version: expected 3 matches, found {count}')
 paths['index.html'].write_text(index.replace('Ver.0.8.39','Ver.0.8.41'),encoding='utf-8')
 manifest=json.loads(paths['foundation-manifest.json'].read_text(encoding='utf-8-sig'));manifest['foundationVersion']=TARGET_VERSION
 manifest['markerVisibilityStatus']={'boardMarks':['x','question','triangle'],'approvedStyleSha256':new_hash,'layoutChanged':False,'questionDotSeparated':True,'runtimeReviewRequired':True}
 manifest['nextSafeWork']='Verify the question-mark dot remains separate on 4x4 and 8x8 boards; keep hint fallback work paused until visual approval.'
 paths['foundation-manifest.json'].write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 test=ROOT/'tests/foundation/v130-question-dot-separation-check.js'
 if test.exists():fail('v130 question separation test already exists')
 test.write_text(f"""const fs=require('fs'),crypto=require('crypto');function ok(v,m){{if(!v)throw new Error(m)}}
const css=fs.readFileSync('style.css','utf8'),b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='{new_hash}'&&b.currentStyleSha256===h,'CSS snapshot mismatch');
ok(css.includes('.tile > .mark-symbol.mark-q .mark-outline{{stroke-width:11!important}}'),'question outline correction missing');
ok(css.includes('.tile > .mark-symbol.mark-q .mark-core{{stroke-width:7.5!important}}'),'question core correction missing');
ok(css.includes('.tile > .mark-symbol.mark-x .mark-core{{stroke-width:13!important}}'),'X weight changed unexpectedly');
console.log('OK: Nekomichi Ver.0.8.41 question dot separation contract passed.');
""",encoding='utf-8');CREATED.append(test)
 run(['node','--check','app-config.js']);run(['node','scripts/run-foundation-checks.js'])
 print('OK: Nekomichi Ver.0.8.41 question-mark dot separation passed all foundation checks.')
 print('OK: X and triangle thickness remain unchanged; only the question-mark stroke was rebalanced.')
 print('OK: prior marker snapshot now points to the approved corrected CSS hash.')
 print(f'STYLE_BYTES: {len(raw)} -> {new_size}');print('STYLE_SHA256: '+new_hash)
 print('REVIEW: check the question mark on 4x4 and 8x8 boards; the dot should remain clearly separated from the stem.')
 print('BACKUP: '+str(BACKUP))
except Exception as e:
 rollback();print('ERROR: '+str(e))
 if BACKED:print('ROLLBACK: restored Ver.0.8.39 files and cleared the Git index')
 sys.exit(1)
