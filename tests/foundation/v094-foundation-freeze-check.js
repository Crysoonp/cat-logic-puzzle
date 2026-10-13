const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const manifest=JSON.parse(fs.readFileSync('foundation-manifest.json','utf8'));
ok(/^0\.8\.\d+$/.test(manifest.foundationVersion),'foundation version must remain in the 0.8.x line');
ok(manifest.stageCount===200,'stage count contract mismatch');
ok(JSON.stringify(manifest.knownLogicOnlyGapStages)===JSON.stringify([]),'solver gap baseline mismatch');
ok(JSON.stringify(manifest.bossPhaseSizes)===JSON.stringify([7,8,8]),'boss phase baseline mismatch');
manifest.services.forEach(name=>ok(fs.existsSync(name),'missing foundation service: '+name));
const game=fs.readFileSync('game.js','utf8');
ok(!/\blocalStorage\.(getItem|setItem|removeItem|clear)\b/.test(game),'direct localStorage access returned');
const html=fs.readFileSync('index.html','utf8');
let last=-1;manifest.services.forEach(name=>{const pos=html.indexOf(name);ok(pos>=0,'service not loaded: '+name);ok(pos>last,'service load order invalid: '+name);last=pos;});
ok(html.indexOf('game.js')>last,'game.js must load after foundation services');
console.log('OK: Nekomichi Ver.0.8.14 foundation freeze checks passed.');
