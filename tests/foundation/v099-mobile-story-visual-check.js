const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'visual baseline version must remain in the 0.8.x line');
ok(b.approvedViewCount>=12,'approved visual count must not decrease');
['title-mobile','board-mobile','story-dialog'].forEach(id=>ok(b.approvedViews.some(v=>v.id===id&&v.status==='approved'),'missing approved view: '+id));
ok(!b.remainingRequiredViews.includes('title-mobile'),'mobile title must be approved');
ok(!b.remainingRequiredViews.includes('story-dialog'),'story dialog must be approved');
ok(b.remainingRequiredViews.length<=7,'remaining required view count must not increase');
ok(b.firstCleanupCandidate===null||typeof b.firstCleanupCandidate==='object','CSS cleanup candidate format is invalid');
console.log('OK: Nekomichi Ver.0.8.19 mobile and story visual approvals registered.');
