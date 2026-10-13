const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8'),game=fs.readFileSync('game.js','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');
ok(game.includes('cy="56" r="4.8"'),'question dot radius missing');ok(game.includes('L33 43'),'question gap geometry missing');
['mark-t .mark-outline{stroke-width:18!important}','mark-t .mark-core{stroke-width:13!important}','mark-q .mark-outline{stroke-width:16!important}','mark-q .mark-core{stroke-width:11.5!important}'].forEach(v=>ok(css.includes(v),'marker balance missing: '+v));
console.log('OK: Nekomichi Ver.0.8.43 marker balance contract passed.');
