const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const css=fs.readFileSync('style.css','utf8');
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'cleanup baseline version must remain in the 0.8.x line');
ok(['first-family-removed','audit-required'].includes(b.cssDeletionGate),'cleanup gate mismatch');
ok(b.firstCleanupCandidate.status==='removed'&&b.firstCleanupCandidate.removalAuthorized===true,'candidate removal state mismatch');
b.firstCleanupCandidate.selectors.forEach(selector=>ok(!css.includes(selector),'removed selector remains: '+selector));
ok(b.firstCleanupCandidate.assetsRetained===true,'candidate assets must remain retained');
ok(b.firstCleanupCandidate.sharedKeyframesRemoved===false,'shared keyframes must not be removed');
const hash=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');ok(hash===b.currentStyleSha256,'post-cleanup style hash mismatch');
console.log('OK: Nekomichi Ver.0.8.26 first isolated CSS cleanup passed.');
