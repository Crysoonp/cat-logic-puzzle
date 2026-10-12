const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'baseline version must remain in the 0.8.x line');
ok(b.visualBaselineComplete===true,'visual baseline must be complete');
ok(b.remainingRequiredViews.length===0,'no required views may remain');
const expected=['rain-effect','leaves-effect','cloud-effect','leaf-pile-effect'];
expected.forEach(id=>ok(b.frozenNotApplicableViews.some(v=>v.id===id&&v.status==='frozen-not-applicable'),'missing frozen effect record: '+id));
ok(['candidate-selection-only','candidate-selected','first-family-removed','audit-required'].includes(b.cssDeletionGate),'CSS gate state is invalid');
ok(b.firstCleanupCandidate===null||typeof b.firstCleanupCandidate==='object','CSS cleanup candidate format is invalid');
console.log('OK: Nekomichi Ver.0.8.21 frozen effect baseline closure passed.');
