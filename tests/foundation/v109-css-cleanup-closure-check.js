const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const css=fs.readFileSync('style.css','utf8');
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'closure version must remain in the 0.8.x line');
ok(b.cssDeletionGate==='audit-required','CSS gate must remain audit-required');
ok(b.nextCleanupCandidate===null,'no second CSS candidate may be selected');
ok(b.cascadeAuditDecision==='No second CSS cleanup candidate approved','cascade decision mismatch');
ok(Array.isArray(b.cascadeAuditLimitations)&&b.cascadeAuditLimitations.length===4,'cascade limitations missing');
const hash=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');ok(hash==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','style.css changed during closure');
console.log('OK: Nekomichi Ver.0.8.29 CSS cleanup closure passed.');
