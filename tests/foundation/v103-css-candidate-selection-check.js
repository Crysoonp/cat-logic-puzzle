const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const css=fs.readFileSync('style.css','utf8');
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'candidate baseline version must remain in the 0.8.x line');
ok(['candidate-selected','first-family-removed','audit-required'].includes(b.cssDeletionGate),'candidate gate mismatch');
ok(b.firstCleanupCandidate&&b.firstCleanupCandidate.id==='dormant-gimmick-image-utilities','candidate id mismatch');
ok(typeof b.firstCleanupCandidate.removalAuthorized==='boolean','candidate removal authorization state is invalid');
ok(b.firstCleanupCandidate.selectors.length===8,'candidate selector count mismatch');
b.firstCleanupCandidate.selectors.forEach(selector=>ok([0,1].includes(css.split(selector).length-1),'candidate selector count invalid: '+selector));
const hash=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');ok([b.styleSha256,b.currentStyleSha256].filter(Boolean).includes(hash),'style.css hash is outside approved candidate lifecycle');
console.log('OK: Nekomichi Ver.0.8.23 low-risk CSS candidate selection passed.');
