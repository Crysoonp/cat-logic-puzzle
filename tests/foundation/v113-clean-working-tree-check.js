const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const i=fs.readFileSync('.gitignore','utf8');const m=JSON.parse(fs.readFileSync('foundation-manifest.json','utf8'));
ok(m.foundationVersion==='0.8.33','version mismatch');
['COLLECT_NEKOMICHI_FOUNDATION_AUDIT.py','NEKOMICHI_V088_TEST_EXACT.txt'].forEach(x=>ok(i.includes(x),'missing ignore rule: '+x));
console.log('OK: Nekomichi Ver.0.8.33 clean working-tree contract passed.');
