const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8');const b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));
const hash=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(hash==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','approved marker CSS hash mismatch');
ok(b.currentStyleSha256===hash&&b.styleBytes===Buffer.byteLength(css),'CSS baseline snapshot mismatch');
['stroke-width:16!important','stroke-width:11.5!important','stroke-width:18!important','stroke-width:13!important'].forEach(v=>ok(css.includes(v),'marker weight missing: '+v));
ok(css.includes('.tile > .mark-symbol.mark-q{width:82%!important;height:82%!important}'),'question size missing');
ok(css.includes('.tile > .mark-symbol.mark-t{width:86%!important;height:86%!important}'),'triangle size missing');
console.log('OK: Nekomichi Ver.0.8.39 marker visibility lifecycle passed.');
