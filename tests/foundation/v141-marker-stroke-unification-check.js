const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');
['mark-t .mark-outline{stroke-width:18!important}','mark-t .mark-core{stroke-width:13!important}','mark-q .mark-outline{stroke-width:18!important}','mark-q .mark-core{stroke-width:13!important}','mark-symbol.mark-t{width:96%!important;height:96%!important}'].forEach(v=>ok(css.includes(v),'stroke unification rule missing: '+v));
ok(css.includes('r:7.8px!important')&&css.includes('r:4.8px!important'),'approved question dot changed');
console.log('OK: Nekomichi Ver.0.8.51 marker stroke unification contract passed.');
