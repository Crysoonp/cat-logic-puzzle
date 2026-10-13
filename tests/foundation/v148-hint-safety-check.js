const fs=require('fs');function ok(v,m){if(!v)throw new Error(m)}
const game=fs.readFileSync('game.js','utf8');
ok(game.includes("const step=window.CLPLogic.safeXStep(p(),state.revealed,state.marks);"),'logical safe-X source missing');
ok(game.includes("if(!step||!step.target)return null;"),'missing-step guard missing');
ok(game.includes("state.revealed.has(step.target)||state.marks.has(step.target)"),'resolved or marked target guard missing');
ok(game.includes("if(p().solution[r]===c)return null;"),'answer-cell guard missing');
ok(!game.includes("for(let r=0;r<p().size;r++)for(let c=0;c<p().size;c++){const id=`${r}-${c}`;if(isEmpty(id))"),'solution-scan fallback remains');
const noStep=game.indexOf("if(!step){show('猫じゃらし'");
const spend=game.indexOf("if(!spendKibble(window.CLPHints.COST.toy))return;");
ok(noStep>=0&&spend>noStep,'kibble can be spent before validated target handling');
ok(game.includes("setTimeout(clearHintGlow,10000)"),'hint cleanup timer missing');
console.log('OK: Nekomichi Ver.0.8.60 cat-teaser hint safety contract passed.');
