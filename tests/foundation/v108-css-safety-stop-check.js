const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const css=fs.readFileSync('style.css','utf8');
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'safety-stop version must remain in the 0.8.x line');
ok(b.cssDeletionGate==='audit-required','CSS gate must require deeper audit');
ok(b.nextCleanupCandidate===null,'a second cleanup candidate must not be selected');
['.r0','.r1','.r2','.r3','.r4','.r5','.r6','.r7','.hint-locked','.gold-sparkle i'].forEach(s=>ok(css.includes(s),'protected dynamic/live selector missing: '+s));
const hash=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');ok(hash==='7615d0a51bc20ddf5e314d3aade781747491ef1576f5f687f4ea821a180ddb2e','style.css changed during safety stop');
console.log('OK: Nekomichi Ver.0.8.28 CSS safety stop passed.');
