const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8'),game=fs.readFileSync('game.js','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');ok(game.includes('class="question-dot" cx="33" cy="56" r="4.8"'),'question SVG source changed');
['width:94%!important','height:96%!important','r:7.8px!important','r:4.8px!important'].forEach(v=>ok(css.includes(v),'optical alignment rule missing: '+v));
ok(css.includes('.mark-symbol.mark-q .mark-outline .question-dot{'),'actual outline child selector missing');
ok(css.includes('.mark-symbol.mark-q .mark-core .question-dot{'),'actual core child selector missing');
console.log('OK: Nekomichi Ver.0.8.49 question optical alignment contract passed.');
