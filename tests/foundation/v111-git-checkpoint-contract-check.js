const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const m=JSON.parse(fs.readFileSync('foundation-manifest.json','utf8'));const p=JSON.parse(fs.readFileSync('repository-housekeeping-plan.json','utf8'));
ok(/^0\.8\.\d+$/.test(m.foundationVersion),'checkpoint foundation version must remain in the 0.8.x line');ok(/^0\.8\.\d+$/.test(p.version),'checkpoint plan version must remain in the 0.8.x line');
ok(p.pushPerformed===false,'checkpoint update must not push');ok(p.checkpointExclusions.includes('.nekomichi-backups'),'backup exclusion missing');
console.log('OK: Nekomichi Ver.0.8.31 Git checkpoint contract passed.');
