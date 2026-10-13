const fs=require('fs'),crypto=require('crypto');function ok(v,m){if(!v)throw new Error(m)}
const css=fs.readFileSync('style.css','utf8'),game=fs.readFileSync('game.js','utf8');const h=crypto.createHash('sha256').update(Buffer.from(css)).digest('hex');
ok(h==='8d1aa2e20b3a9cf116877ee930ffffdd9505b619435f2f34da4f77ad125b1d8d','CSS snapshot mismatch');
ok(game.includes('M17 17 L47 47 M47 17 L17 47'),'X SVG path missing');
ok(css.includes('#modeCycle .mark-symbol.mark-x::before'),'mode X pseudo-element scope missing');
ok(css.includes('content:none!important'),'mode X pseudo-elements were not disabled');
ok(css.includes('#modeCycle .mark-symbol.mark-x > svg{'),'mode X SVG display rule missing');
ok(css.includes('#modeCycle .mark-symbol.mark-x .mark-outline{'),'mode X outline rule missing');
ok(css.includes('#modeCycle .mark-symbol.mark-x .mark-core{'),'mode X core rule missing');
ok(css.includes('transform:translate(-50%,-50%)!important'),'mode X centering rule missing');
console.log('OK: Nekomichi Ver.0.8.56 MARK button SVG X contract passed.');
