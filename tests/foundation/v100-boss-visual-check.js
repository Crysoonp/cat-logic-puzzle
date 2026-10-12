const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
ok(/^0\.8\.\d+$/.test(b.baselineVersion),'visual baseline version must remain in the 0.8.x line');
ok(b.approvedViewCount>=15,'approved visual count must not decrease');
['boss-7x7','boss-8x8-phase2','boss-8x8-phase3'].forEach(id=>ok(b.approvedViews.some(v=>v.id===id&&v.status==='approved'),'missing approved boss view: '+id));
['boss-7x7','boss-8x8-phase2','boss-8x8-phase3'].forEach(id=>ok(!b.remainingRequiredViews.includes(id),'approved boss view remains pending: '+id));
ok(b.remainingRequiredViews.length<=4,'remaining required view count must not increase');
ok(b.firstCleanupCandidate===null||typeof b.firstCleanupCandidate==='object','CSS cleanup candidate format is invalid');
console.log('OK: Nekomichi Ver.0.8.20 boss visual approvals registered.');
