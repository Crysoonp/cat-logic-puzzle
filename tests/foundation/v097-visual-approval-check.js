const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'visual approval version must remain in the 0.8.x line');
ok(b.approvedViewCount>=6,'approved visual count must not decrease');
['title-desktop','title-new-session-desktop','board-normal','stage-select','settings-dialog','rules-dialog'].forEach(id=>ok(b.approvedViews.some(v=>v.id===id&&v.status==='approved'),'missing approved view: '+id));
ok(b.remainingRequiredViews.length<=11,'remaining visual count must not increase');
ok(b.firstCleanupCandidate===null||typeof b.firstCleanupCandidate==='object','CSS cleanup candidate format is invalid');
console.log('OK: Nekomichi Ver.0.8.17 visual approvals registered.');
