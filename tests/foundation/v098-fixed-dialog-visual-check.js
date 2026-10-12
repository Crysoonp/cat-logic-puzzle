const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'visual baseline version must remain in the 0.8.x line');
ok(b.approvedViewCount>=9,'approved visual count must not decrease');
['cats-dialog','debug-dialog','boss-result-dialog'].forEach(id=>ok(b.approvedViews.some(v=>v.id===id&&v.status==='approved'),'missing approved view: '+id));
ok(!b.remainingRequiredViews.includes('cats-dialog'),'cats dialog must be removed from remaining views');
ok(!b.remainingRequiredViews.includes('debug-dialog'),'debug dialog must be removed from remaining views');
ok(b.remainingRequiredViews.length<=9,'remaining required view count must not increase');
ok(b.firstCleanupCandidate===null||typeof b.firstCleanupCandidate==='object','CSS cleanup candidate format is invalid');
console.log('OK: Nekomichi Ver.0.8.18 fixed dialog visual approvals registered.');
