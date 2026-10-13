const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8'),b=JSON.parse(fs.readFileSync('css-visual-baseline.json','utf8'));const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d'&&b.currentStyleSha256===h,'CSS snapshot mismatch');
ok(css.includes('.tile > .mark-symbol.mark-q .mark-outline{stroke-width:11!important}'),'question outline correction missing');
ok(css.includes('.tile > .mark-symbol.mark-q .mark-core{stroke-width:7.5!important}'),'question core correction missing');
ok(css.includes('.tile > .mark-symbol.mark-x .mark-core{stroke-width:13!important}'),'X weight changed unexpectedly');
console.log('OK: Nekomichi Ver.0.8.41 question dot separation contract passed.');
