const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8'),game=fs.readFileSync('game.js','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');
ok(game.includes('<g class="mark-outline">${paths[type]||paths.x}</g><g class="mark-core">${paths[type]||paths.x}</g>'),'actual markIcon group structure missing');
ok(css.includes('.mark-symbol.mark-q .mark-outline .question-dot{'),'actual outline-child selector missing');
ok(css.includes('.mark-symbol.mark-q .mark-core .question-dot{'),'actual core-child selector missing');
ok(css.includes('r:5.2px!important')&&css.includes('r:3.35px!important'),'question dot radii missing');
ok(!css.includes('.mark-symbol.mark-q.mark-core .question-dot'),'dead same-element core selector remains');
ok(!css.includes('.mark-symbol.mark-q.mark-outline .question-dot'),'dead same-element outline selector remains');
console.log('OK: Nekomichi Ver.0.8.48 actual question-dot render structure passed.');
