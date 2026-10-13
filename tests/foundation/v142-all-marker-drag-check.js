const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const game=fs.readFileSync('game.js','utf8');
ok(game.includes("const dragMode=state.drag.mode;"),'drag mode snapshot missing');
ok(game.includes("['x','q','t'].includes(dragMode)"),'all-marker mode guard missing');
ok(game.includes("state.marks.set(id,dragMode)"),'drag add is not registration-driven by selected mark');
ok(game.includes("state.marks.get(id)===dragMode"),'same-selected-mark removal check missing');
ok(game.includes("state.drag.mode=state.mode"),'pointer start does not freeze selected mode');
ok(game.includes("state.drag.action=state.marks.get(id)===state.drag.mode?'remove':'add'"),'drag action does not use selected mode');
ok(!game.includes("state.mode!=='x'"),'X-only pointer restriction remains');
ok(!game.includes("state.marks.set(id,'x')"),'X-only drag assignment remains');
console.log('OK: Nekomichi Ver.0.8.52 X, question, and triangle drag contract passed.');
