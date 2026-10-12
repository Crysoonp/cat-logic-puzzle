const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const baseline=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
const css=fs.readFileSync('style.css');const hash=crypto.createHash('sha256').update(css).digest('hex');
ok(/^0\.8\.\d+$/.test(baseline.baselineVersion),'CSS baseline version must remain in the 0.8.x line');
ok([baseline.styleSha256,baseline.currentStyleSha256].filter(Boolean).includes(hash),'style.css hash is outside approved baseline lifecycle');
ok(css.length===baseline.styleBytes||css.length<=baseline.styleBytes,'CSS byte size is outside approved cleanup lifecycle');
ok(baseline.protectedFamilies.includes('mark-x')&&baseline.protectedFamilies.includes('clp-hint-x')&&baseline.protectedFamilies.includes('clp-hint-cat'),'protected mark families missing');
ok(baseline.firstCleanupCandidate===null||typeof baseline.firstCleanupCandidate==='object','cleanup candidate format is invalid');
ok(baseline.requiredViews.length===15,'visual baseline view count mismatch');
console.log('OK: Nekomichi Ver.0.8.16 CSS visual baseline contract passed.');
