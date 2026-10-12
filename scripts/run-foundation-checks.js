const fs=require('fs');const path=require('path');const cp=require('child_process');
const root=path.resolve(__dirname,'..');const dir=path.join(root,'tests','foundation');
const tests=fs.readdirSync(dir).filter(name=>name.endsWith('.js')).sort();
let failed=0;for(const test of tests){const result=cp.spawnSync(process.execPath,[path.join(dir,test)],{cwd:root,encoding:'utf8'});process.stdout.write(`[${test}]\n${result.stdout||''}${result.stderr||''}`);if(result.status!==0)failed++;}
if(failed){console.error(`ERROR: ${failed} foundation test(s) failed.`);process.exit(1);}
console.log(`OK: ${tests.length} Nekomichi foundation tests passed.`);
