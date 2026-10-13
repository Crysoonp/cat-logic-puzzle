const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const game=fs.readFileSync('game.js','utf8');
ok(game.includes("function installHintEvents(){"),'hint installer missing');
ok(game.includes("window.CLPEvents.bind('hintDock','click',e=>{"),'persistent dock delegation missing');
ok(game.includes("const button=e.target.closest('[data-hint]');"),'data-hint lookup missing');
ok(game.includes("if(e.target.closest('[data-info]'))return;"),'info control exclusion missing');
ok(game.includes("directHint(button.dataset.hint);"),'delegated hint action missing');
ok(game.includes("if(type==='toy'){showToyReady();return;}"),'toy confirmation flow changed');
ok(!game.includes("document.querySelectorAll('[data-hint]').forEach(b=>window.CLPEvents.bind"),'startup-only hint binding remains');
console.log('OK: Nekomichi Ver.0.8.57 hint-button delegated action contract passed.');
