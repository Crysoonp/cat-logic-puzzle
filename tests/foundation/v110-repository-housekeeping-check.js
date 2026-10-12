const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const plan=JSON.parse(fs.readFileSync('repository-housekeeping-plan.json','utf8'));const ignore=fs.readFileSync('.gitignore','utf8');
ok(/^0\.8\.\d+$/.test(plan.version),'housekeeping plan version must remain in the 0.8.x line');
['.nekomichi-backups/','AUDIT_NEKOMICHI_*.py','NEKOMICHI_*_BEFORE_V*.txt','NEKOMICHI_FOUNDATION_AUDIT.txt'].forEach(item=>ok(ignore.includes(item),'missing ignore rule: '+item));
ok(plan.actionsNotPerformed.includes('no deletion'),'housekeeping must not delete files');
ok(plan.actionsNotPerformed.includes('no source or asset change'),'housekeeping must not alter source or assets');
ok(plan.protectedLargeArea.path==='character_reference'&&plan.protectedLargeArea.decision.startsWith('keep'),'character reference protection missing');
console.log('OK: Nekomichi Ver.0.8.30 repository housekeeping plan passed.');
