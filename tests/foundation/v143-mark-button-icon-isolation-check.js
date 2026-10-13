const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');
['#modeCycle{','overflow:hidden!important','width:62%!important','height:62%!important','transform:translate(-50%,-50%)!important','pointer-events:none!important'].forEach(v=>ok(css.includes(v),'MARK button isolation rule missing: '+v));
ok(css.includes('#modeCycle .mark-symbol.mark-q .mark-outline .question-dot{r:7.8px!important}'),'question dot outline rule missing');
ok(css.includes('#modeCycle .mark-symbol.mark-q .mark-core .question-dot{r:4.8px!important}'),'question dot core rule missing');
console.log('OK: Nekomichi Ver.0.8.53 MARK button icon isolation contract passed.');
