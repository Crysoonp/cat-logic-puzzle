const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const m=JSON.parse(fs.readFileSync('foundation-manifest.json','utf8'));const p=JSON.parse(fs.readFileSync('repository-housekeeping-plan.json','utf8'));
ok(m.foundationVersion==='0.8.31','checkpoint foundation version mismatch');ok(p.version==='0.8.31','checkpoint plan version mismatch');
ok(p.pushPerformed===false,'checkpoint update must not push');ok(p.checkpointExclusions.includes('.nekomichi-backups'),'backup exclusion missing');
console.log('OK: Nekomichi Ver.0.8.31 Git checkpoint contract passed.');
