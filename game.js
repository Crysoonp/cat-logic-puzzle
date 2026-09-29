"use strict";
const STAGES=window.CLP_STAGES;
const STORY=[
["ある日のこと","🐱🏘️","幼いテコちゃんは、お母さんとはぐれてしまいました。"],
["にゃんこ爺さん","🐱　🐱","ひとりになったテコちゃんを、にゃんこ爺さんが助けました。"],
["大きくなったテコちゃん","🐱🌱","月日が流れ、テコちゃんは旅に出られるほど成長しました。"],
["旅立ちの相談","🐱💬🐱","『お母さんを探しに行きたいニャン』テコちゃんは、にゃんこ爺さんに相談しました。"],
["修行のはじまり","🟦🟨🟩🩷","『旅に出るなら、隠れた仲間を見つける修行が必要じゃ』"],
["色と模様のタイル","❌❓△","行・列・色エリアの手掛かりを使って、仲間の猫を探します。"],
["最初の約束","🐱❤️","修行中はハートが減りません。失敗を恐れず試してみましょう。"],
["ステージ1へ","🐱✨","『わかったニャン！ 最初の仲間を見つけるニャン！』"]];
const state={i:0,hearts:Number(localStorage.getItem('clpHearts')||5),kibble:Number(localStorage.getItem('clpKibble')||0),score:100,mode:'x',revealed:new Set(),marks:new Map(),timers:new Map(),locked:false,streak:0,history:JSON.parse(localStorage.getItem('clpHistory')||'{}'),log:[],tutorialStep:0,idle:null,debugAnswer:false,drag:{active:false,moved:false,pointerId:null,startX:0,startY:0,startId:'',action:'add',visited:new Set()}};
const $=x=>document.getElementById(x),board=$('board'),dlg=$('dlg'),p=()=>STAGES[state.i],key=(r,c)=>`${r}-${c}`;
function save(){localStorage.setItem('clpHearts',state.hearts);localStorage.setItem('clpKibble',state.kibble);localStorage.setItem('clpHistory',JSON.stringify(state.history))}
function record(action,id='',result=''){state.log.push(`${new Date().toLocaleTimeString()} | S${p().stage} | ${action} ${id} ${result}`);if(state.log.length>200)state.log.shift()}
function haptic(pattern){try{if(localStorage.getItem('clpVibrate')!=='0'&&navigator.vibrate)navigator.vibrate(pattern)}catch(e){}}
function travelComment(){const comments=['まずは行と列を見比べるニャン。','同じ色エリアに残ったマスを探すニャン。','焦らず、確定できるところから進めるニャン。','仲間の手掛かりが見つかりそうだニャン。'];return comments[p().stage%comments.length]}
function startIdle(){clearTimeout(state.idle);state.idle=setTimeout(()=>{if(p().tutorial)say('🐱','にゃんこ爺さん','迷ったときは、下のヒントを使ってもよいんじゃぞ。チュートリアル中は無料じゃ。','left');else say('🐱','テコちゃん',travelComment(),'right')},17000)}
function resetBoard(){state.drag.active=false;state.drag.visited=new Set();state.timers.forEach(clearTimeout);state.timers.clear();state.score=100;state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;state.tutorialStep=0;record('START');render();startIdle()}
function say(face,name,text,side='left',enemy=false){$('talkFace').textContent=face;$('talkName').textContent=name;$('talkText').textContent=text;$('talk').className=`talk ${side}${enemy?' enemy':''}`}
function render(){let s=p();$('stageLabel').innerHTML=s.bonus?`STAGE ${s.stage}<br><small>BONUS</small>`:s.hard?`STAGE ${s.stage}<br><small>HARD</small>`:`STAGE ${s.stage}`;$('scoreLabel').textContent=`${state.score}点`;$('panel').className='panel'+(s.hard?' hard':'')+(s.bonus?' bonus':'');$('modeT').classList.toggle('hidden',s.stage<9);$('historyBtn').classList.toggle('hidden',!state.history['10']);if(s.hard)say('😼','エリートにゃんこ','フン！ ここから先へ行きたければ、俺様を見つけてみるんだな！','right',true);else if(s.tutorial)say('🐱','にゃんこ爺さん',tutorialText(),'left');else say('🐱','テコちゃん',s.stage===11?'ここからが本当の旅の始まりニャン。ハートを大切にして、仲間とお母さんの手掛かりを探すニャン！':travelComment(),'right');renderLife();build();updateHint()}
function stage1FoundId(){return Array.from(state.revealed)[0]||''}
function idsAround(id){if(!id)return[];const [r,c]=id.split('-').map(Number),out=[];for(let rr=Math.max(0,r-1);rr<=Math.min(p().size-1,r+1);rr++)for(let cc=Math.max(0,c-1);cc<=Math.min(p().size-1,c+1);cc++)if(rr!==r||cc!==c)out.push(`${rr}-${cc}`);return out}
function stage1AdjacentRemaining(){if(p().stage!==1||state.revealed.size!==1)return[];return idsAround(stage1FoundId()).filter(id=>!state.marks.has(id)&&!state.revealed.has(id))}
function stage1LineRemaining(){if(p().stage!==1||state.revealed.size!==1)return[];const id=stage1FoundId(),[r,c]=id.split('-').map(Number),out=[];for(let i=0;i<p().size;i++){for(const x of [`${r}-${i}`,`${i}-${c}`])if(x!==id&&!state.revealed.has(x)&&!state.marks.has(x)&&!out.includes(x))out.push(x)}return out}
function stage1ExclusionsRemaining(){if(p().stage!==1||state.revealed.size!==2)return[];const latest=Array.from(state.revealed).at(-1),[r,c]=latest.split('-').map(Number),reg=p().regions[r][c],out=[];for(let rr=0;rr<p().size;rr++)for(let cc=0;cc<p().size;cc++){const id=`${rr}-${cc}`;if(id===latest||state.revealed.has(id)||state.marks.has(id))continue;if(rr===r||cc===c||Math.abs(rr-r)<=1&&Math.abs(cc-c)<=1||p().regions[rr][cc]===reg)out.push(id)}return out}
function stage1HighlightIds(){if(p().stage!==1)return[];if(state.revealed.size===1){const around=stage1AdjacentRemaining();if(around.length)return around;const line=stage1LineRemaining();return line.length?line:['0-2']}if(state.revealed.size===2){const x=stage1ExclusionsRemaining();return x.length?x:['3-1']}if(state.revealed.size===3)return['2-3'];return[]}
function tutorialText(){let s=p();if(s.stage===1){
  if(state.revealed.size===0)return 'まずはタイルの開き方じゃ。1マスだけの色エリアを、素早く2回タップして開くんじゃ。';
  if(state.revealed.size===1&&stage1AdjacentRemaining().length)return 'よくできたのう。今の猫は盤面の端にいるから、周囲で確認するのは5マスじゃ。光っている5マスへ×を付けるんじゃ。';
  if(state.revealed.size===1&&stage1LineRemaining().length)return '次は、同じ行と同じ列じゃ。光っている行と列にも、ほかの猫はいない。×で消すんじゃ。';
  if(state.revealed.size===1)return 'A行で残ったA3が、次の確定マスじゃ。光っているA3を開くんじゃ。';
  if(state.revealed.size===2&&stage1ExclusionsRemaining().length)return 'その調子じゃ。新しく見つけた猫の周囲、行、列、色エリアも×で確認するんじゃ。';
  if(state.revealed.size===2)return '次はD2が確定したぞい。光っているD2を開くんじゃ。';
  if(state.revealed.size===3)return '最後はC4じゃ。ここを開けば完成じゃぞい。';
  return 'これで完成じゃ。よくできたのう、テコちゃん。';
}if(s.stage===2){
  if(state.revealed.size===0)return '前の修行と同じじゃ。まずは1マスだけの色エリアを探して、猫を開くんじゃ。';
  if(state.revealed.size===1&&state.marks.size<5)return 'よくできたのう。盤面の端にいる猫の周囲5マスへ×を付けるんじゃ。';
  if(state.revealed.size===1&&state.marks.size<8)return '次は同じ行と同じ列じゃ。そこにも別の猫はいないから、×で候補を減らすんじゃ。';
  if(state.revealed.size===1)return '候補を減らすと、色エリアの中で猫を置けるマスが1つだけになる場所があるぞい。その1マスを開くんじゃ。';
  if(state.revealed.size===2)return 'その調子じゃ。新しい猫の周囲、行、列を確認して、また残り1マスの色エリアを探すんじゃ。';
  if(state.revealed.size===3)return '残りはあと1匹じゃ。行・列・色エリアを見比べて、最後の1マスを見つけるんじゃ。';
  return '見事じゃ。前の修行を自分の力で繰り返せたのう。';
}if(s.stage===3){if(!state.marks.has('0-3')&&state.revealed.size===0)return 'A1・A2・A3は同じ青エリアじゃ。青の猫はA行のどこかにいるから、A4には猫はいない。まずA4へ×を付けるんじゃ。';if(!state.revealed.has('1-3'))return 'A4へ×を付けたから、黄色エリアで残ったB4に猫がいるぞい。B4を素早く2回タップじゃ。';if(!state.revealed.has('3-2'))return 'B4の猫から行・列・周囲を消すと、3列目で残るD3に猫がいると分かるぞい。D3を開くんじゃ。';if(!state.revealed.has('2-0'))return '次はC1じゃ。ここまでの×と色エリアを見比べて開いてみるんじゃ。';return '残りは頑張るんじゃ。ここまで覚えた基本で解けるぞい。'}if(s.stage===4)return 'ここからは5×5じゃ。まずは1マスだけの色エリアを探すんじゃ。盤面が広くなっても基本は同じじゃよ。';if(s.stage===7)return 'いよいよ6×6じゃ。最初から確定できる場所が二つあるぞい。落ち着いて探すんじゃ。';if(s.stage===9)return 'すぐ決められないときは、△で「ここにいる」と仮に考える方法もあるんじゃ。これを仮置き推理というぞい。';return s.guide}
function renderLife(){let b=$('lifeBox');b.innerHTML='';if(p().tutorial||p().bonus)b.innerHTML='<span class="training">チュートリアル：ハートは減りません<br><small>解放済みのヒントは使い放題です</small></span>';else{b.innerHTML='<label>LIFE</label>';for(let i=0;i<5;i++){let h=document.createElement('span');h.className='life'+(i<state.hearts?'':' empty');h.textContent=i<state.hearts?'♥':'♡';b.appendChild(h)}b.insertAdjacentHTML('beforeend',`<span class="kibble">カリカリ ${state.kibble}</span>`)}}
function build(){let s=p(),n=s.size;board.innerHTML='';board.style.gridTemplateColumns=`repeat(${n},minmax(0,1fr))`;board.style.gridTemplateRows=`repeat(${n},minmax(0,1fr))`;board.style.setProperty('--gap',n<=4?'5px':n<=6?'3px':'2px');board.style.setProperty('--pad',n<=4?'6px':'3px');board.style.setProperty('--radius',n<=4?'11px':n<=6?'6px':'4px');$('coordTop').style.gridTemplateColumns=`repeat(${n},1fr)`;$('coordTop').innerHTML=Array.from({length:n},(_,i)=>`<span>${i+1}</span>`).join('');$('coordSide').style.gridTemplateRows=`repeat(${n},1fr)`;$('coordSide').innerHTML=Array.from({length:n},(_,i)=>`<span>${String.fromCharCode(65+i)}</span>`).join('');let target=firstLogicalTarget();for(let r=0;r<n;r++)for(let c=0;c<n;c++){let id=key(r,c),b=document.createElement('button'),m=state.marks.get(id);b.className=`tile r${s.regions[r][c]}`+(state.revealed.has(id)?' revealed':'')+(state.debugAnswer&&answer(id)?' hinting':'')+(((s.stage===1&&state.revealed.size===0&&id===target)||(s.stage===3&&id===stage3Target()))?' tutorial-target':'')+(stage1HighlightIds().includes(id)?' tutorial-focus':'');b.dataset.id=id;if(state.revealed.has(id))b.innerHTML='<span>🐱</span>';else if(m)b.innerHTML=`<span class="${m==='x'?'mark-x':m==='q'?'mark-q':'mark-t'}">${m==='x'?'×':m==='q'?'？':'△'}</span>`;b.onpointerdown=e=>pointerStart(e,id);board.appendChild(b)}}
function stage3Target(){if(p().stage!==3)return '';if(!state.marks.has('0-3')&&state.revealed.size===0)return '0-3';if(!state.revealed.has('1-3'))return '1-3';if(!state.revealed.has('3-2'))return '3-2';if(!state.revealed.has('2-0'))return '2-0';return ''}
function firstLogicalTarget(){let s=p(),counts={};for(let r=0;r<s.size;r++)for(let c=0;c<s.size;c++)counts[s.regions[r][c]]=(counts[s.regions[r][c]]||0)+1;for(let r=0;r<s.size;r++){let c=s.solution[r];if(counts[s.regions[r][c]]===1)return key(r,c)}return key(0,s.solution[0])}
function markForDrag(id, action){
  if(!id||state.revealed.has(id)||state.drag.visited.has(id))return;
  state.drag.visited.add(id);
  if(action==='remove'){
    if(state.marks.get(id)==='x')state.marks.delete(id);
  }else{
    state.marks.set(id,'x');
  }
  record('DRAG_MARK',id,action);
  haptic(12);
  build();
}
function tileIdAtPoint(x,y){
  const el=document.elementFromPoint(x,y);
  const tile=el&&el.closest?el.closest('.tile'):null;
  return tile&&board.contains(tile)?tile.dataset.id:'';
}
function pointerStart(e,id){
  if(state.locked||state.revealed.has(id)||state.mode!=='x'){
    if(state.mode!=='x')tap(id);
    return;
  }
  state.drag.active=true;
  state.drag.moved=false;
  state.drag.pointerId=e.pointerId;
  state.drag.startX=e.clientX;
  state.drag.startY=e.clientY;
  state.drag.startId=id;
  state.drag.action=state.marks.get(id)==='x'?'remove':'add';
  state.drag.visited=new Set();
  try{board.setPointerCapture(e.pointerId)}catch(_e){}
}
function pointerMove(e){
  if(!state.drag.active||e.pointerId!==state.drag.pointerId)return;
  const distance=Math.hypot(e.clientX-state.drag.startX,e.clientY-state.drag.startY);
  if(!state.drag.moved&&distance<10)return;
  if(!state.drag.moved){
    state.drag.moved=true;
    clearTimeout(state.timers.get(state.drag.startId));
    state.timers.delete(state.drag.startId);
    markForDrag(state.drag.startId,state.drag.action);
  }
  e.preventDefault();
  markForDrag(tileIdAtPoint(e.clientX,e.clientY),state.drag.action);
}
function pointerEnd(e){
  if(!state.drag.active||e.pointerId!==state.drag.pointerId)return;
  const startId=state.drag.startId;
  const moved=state.drag.moved;
  state.drag.active=false;
  state.drag.pointerId=null;
  try{board.releasePointerCapture(e.pointerId)}catch(_e){}
  if(!moved)tap(startId);
  else startIdle();
}
board.addEventListener('pointermove',pointerMove,{passive:false});
board.addEventListener('pointerup',pointerEnd);
board.addEventListener('pointercancel',pointerEnd);
function tap(id){clearTimeout(state.idle);if(!p().tutorial&&!p().bonus&&state.hearts<=0){heartZero();return}if(state.locked||state.revealed.has(id))return;if(state.timers.has(id)){clearTimeout(state.timers.get(id));state.timers.delete(id);openTile(id)}else state.timers.set(id,setTimeout(()=>{state.timers.delete(id);state.marks.get(id)===state.mode?state.marks.delete(id):state.marks.set(id,state.mode);record('MARK',id,state.mode);haptic(18);build();if(p().tutorial)say('🐱','にゃんこ爺さん',tutorialText(),'left');startIdle()},270))}
function answer(id){let [r,c]=id.split('-').map(Number);return p().solution[r]===c}
function openTile(id){state.marks.delete(id);if(answer(id)){state.revealed.add(id);state.streak++;record('OPEN',id,'OK');haptic([45,35,70]);goodToast(['いいね！','すごい！','やったニャン！','かんぺき！'][Math.min(3,state.streak-1)]);build();if(p().tutorial)say('🐱','にゃんこ爺さん',tutorialText(),'left');if(state.revealed.size===p().size)complete()}else{state.streak=0;state.score=Math.max(0,state.score-10);record('OPEN',id,'MISS');haptic([90,45,90,45,120]);$('scoreLabel').textContent=`${state.score}点`;if(!(p().tutorial||p().bonus)){state.hearts=Math.max(0,state.hearts-1);save();renderLife()}failToast();if(state.hearts===0&&!p().tutorial&&!p().bonus)heartZero()}startIdle()}
function goodToast(t){let x=$('toast');x.className='toast';x.replaceChildren();void x.offsetWidth;x.className='toast good';x.textContent=t;setTimeout(()=>{x.className='toast';x.textContent='';x.replaceChildren()},850)}
function failToast(){
  const x=$("toast");
  x.className="toast try-again-toast";
  x.innerHTML='<div class="try-whole">そこじゃないニャン</div>';
  void x.offsetWidth;
  x.classList.add("show-whole");

  setTimeout(()=>{
    x.className="toast try-again-toast splitting";
    x.innerHTML='<div class="try-piece try-left">そこじゃないニャン</div><div class="try-piece try-right">そこじゃないニャン</div><div class="try-crack"></div>';
  },520);

  setTimeout(()=>{
    x.className="toast";
    x.replaceChildren();
  },1450);
}
function updateHint(){
  const unlockStage={toy:3,matatabi:6,can:9,paw:10};
  const labels={toy:['🪶','猫じゃらし','安全な×・1個'],matatabi:['🌿','またたび','有効な一手・2個'],can:['🥫','ネコ缶','猫を開く・3個'],paw:['🐾','肉球チェック','誤り訂正・2個']};
  document.querySelectorAll('[data-hint]').forEach(button=>{
    const type=button.dataset.hint;
    const unlocked=p().stage>=unlockStage[type];
    button.disabled=!unlocked;
    button.classList.toggle('hint-locked',!unlocked);
    if(unlocked){
      const item=labels[type];
      button.innerHTML=`<span class="hint-icon">${item[0]}</span><b>${item[1]}</b><small>${p().tutorial?'チュートリアル無料':item[2]}</small>`;
      button.setAttribute('aria-label',item[1]);
    }else{
      button.innerHTML='<span class="hint-icon mystery-icon">●</span><b>？？？</b><small>まだ使えません</small>';
      button.setAttribute('aria-label','未解放のヒント');
    }
  });
}
function hintMenu(){if(p().tutorial||p().bonus){useHint(3);return}show('ヒントを選ぶ',`<p>所持カリカリ：<b>${state.kibble}</b></p><p>猫じゃらし：注目エリア（1個）<br>またたび：正解位置を光らせる（2個）<br>ネコ缶：猫を1匹開く（3個）</p>`,[['猫じゃらし 1','h1'],['またたび 2','h2'],['ネコ缶 3','h3'],['閉じる','close']])}
function useHint(level){let cost=p().tutorial||p().bonus?0:level;if(state.kibble<cost){show('カリカリが足りません','<p>ボーナスステージなどでカリカリを集められます。</p>',[['閉じる','close']]);return}state.kibble-=cost;state.score=Math.max(0,state.score-cost*5);save();let id=Array.from({length:p().size},(_,r)=>key(r,p().solution[r])).find(x=>!state.revealed.has(x));if(!id)return;if(level===3&&!p().tutorial&&!p().bonus){openTile(id)}else{let t=board.querySelector(`[data-id="${id}"]`);t.classList.add('hinting');setTimeout(()=>t.classList.remove('hinting'),3500)}record('HINT',id,level);updateHint()}
function finishResult(){state.history[p().stage]=Math.max(state.history[p().stage]||0,state.score);if(p().bonus)state.kibble+=3;save();let line=p().tutorial?['よくできたのう、テコちゃん。','見事じゃ。仲間をみんな見つけたぞい。','また一つ、修行を終えたのう。'][p().stage%3]:['仲間を見つけたニャン！','無事に再会できたニャン！','みんな見つかったニャン！'][p().stage%3];let speaker=p().tutorial?'にゃんこ爺さん':'テコちゃん';let extra=p().bonus?'<p>カリカリを3個獲得しました！</p>':'';let finish=p().stage===10?'<p>よく覚えたのう、テコちゃん。基本の修行はこれで終わりじゃ。ここから先は、まだ見ぬ仲間たちと、お母さんの手掛かりが待っておるぞい。</p>':'';let result=()=>show(p().hard?'エリートにゃんこを追い払った！':'STAGE CLEAR',`<p><b>${speaker}：</b> ${line}</p><p>スコアは <b>${state.score}点</b> です。${state.score===100?' ノーミスでクリアできました！':' クリアできました！'}</p>${extra}${finish}`,state.i<STAGES.length-1?[['次のステージ','next']]:[['Ver.0.4.10.3 完了','close']]);if(p().hard)runElite(result);else result()}
function celebrateBoard(done){
  board.classList.add('board-complete');
  board.querySelectorAll('.tile.revealed span').forEach((cat,i)=>{cat.style.animationDelay=`${i*70}ms`;cat.classList.add('cat-celebrate')});
  setTimeout(()=>{board.classList.remove('board-complete');board.querySelectorAll('.cat-celebrate').forEach(x=>x.classList.remove('cat-celebrate'));done()},1850)
}
function complete(){state.locked=true;haptic([40,30,60,40,130]);goodToast('やったニャン！');celebrateBoard(finishResult)}
function runElite(done){let e=document.createElement('div');e.className='elite-run';e.textContent='😼💨';document.body.appendChild(e);setTimeout(()=>e.remove(),1500);setTimeout(done,1600)}
function heartZero(){state.locked=true;show('ハートがなくなりました',`<p>少し時間を置いて遊んでね。</p><p>将来は時間経過、広告視聴、カリカリ交換で回復できる予定です。</p>`,[['タイトルへ戻る','title'],['DEBUG：全回復','recover']])}
function rules(){show('ルール',`<details open><summary><b>基本ルール</b></summary><ul><li>各行・各列・各色エリアに猫は1匹</li><li>猫同士は周囲8マスで隣り合わない</li></ul></details><details><summary><b>操作</b></summary><p>1回タップで×・？・△、素早い2回タップで開きます。△は仮置き推理用です。</p></details>`,[['閉じる','close']])}
function show(title,body,btns){$('dlgTitle').textContent=title;$('dlgBody').innerHTML=body;$('dlgActions').innerHTML='';btns.forEach(([text,a])=>{let b=document.createElement('button');b.className='primary';b.textContent=text;b.onclick=()=>{if(a.startsWith('h')){dlg.close();useHint(Number(a[1]));return}dlg.close();if(a==='next'){state.i++;resetBoard()}if(a==='recover'){state.hearts=5;state.locked=false;save();render()}if(a==='title'){state.i=0;resetBoard()}if(a==='resetStage'){state.score=100;state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;render()}};$('dlgActions').appendChild(b)});dlg.showModal()}
function devUnlockedTo(){return Math.max(1,Math.min(STAGES.length,Number(localStorage.getItem('clpDevUnlockedTo')||1)))}
function isStageUnlocked(stageNo){return stageNo===1||Boolean(state.history[stageNo-1])||stageNo<=devUnlockedTo()}
function specialStageLabel(stageNo){if(stageNo===50)return 'BOSS候補';if([20,30,40].includes(stageNo))return 'ELITE候補';return ''}
window.CLPDevUnlockToStage=function(stageNo=STAGES.length){const target=Math.max(1,Math.min(STAGES.length,Number(stageNo)||1));localStorage.setItem('clpDevUnlockedTo',String(target));goodToast(`STAGE ${target}まで開発用解放`);history();return target};
window.CLPDevUnlockAllStages=function(){return window.CLPDevUnlockToStage(STAGES.length)};
window.CLPDevResetStageProgress=function(){localStorage.removeItem('clpDevUnlockedTo');state.history={};save();state.i=0;resetBoard();goodToast('進行データを初期化しました');return true};
function history(){
 let g=$('historyGrid');g.innerHTML='';
 const groups=[
  ['チュートリアル 1～9',1,9],
  ['修行の仕上げ 10',10,10],
  ['第1章 11～20',11,20],
  ['第2章 21～30',21,30],
  ['第3章 31～40',31,40],
  ['まよい森 41～50',41,50]
 ];
 groups.forEach(([title,a,z])=>{
  let h=document.createElement('h3');h.className='history-heading';h.textContent=title;g.appendChild(h);
  let wrap=document.createElement('div');wrap.className='history-section';
  for(let k=a;k<=Math.min(z,STAGES.length);k++){
   if(!isStageUnlocked(k))continue;
   let b=document.createElement('button'),s=STAGES[k-1],score=Number(state.history[k]||0),special=specialStageLabel(k);
   b.className=(score===100?'gold ':'')+((s&& (s.hard||s.bonus))||special?'special ':'')+(score?'cleared':'unplayed');
   b.innerHTML=`<b>${k}</b><br><small>${s.size}×${s.size}${special?'・'+special:''}<br>${score?score+'点':'未クリア'}</small>`;
   b.onclick=()=>{$('historyDlg').close();state.i=k-1;resetBoard()};
   wrap.appendChild(b);
  }
  if(!wrap.children.length)wrap.innerHTML='<p class="history-empty">前のステージをクリアすると解放されます</p>';
  g.appendChild(wrap);
 });
 $('historyDlg').showModal();
}
let storyIndex=0;function showStory(reset=false){if(reset)storyIndex=0;let s=STORY[storyIndex];$('storyArt').textContent=s[1];$('storyPage').textContent=`${storyIndex+1} / ${STORY.length}`;$('storyTitle').textContent=s[0];$('storyText').textContent=s[2];$('storyNext').textContent=storyIndex===STORY.length-1?'修行を始める':'次へ';$('storyDlg').showModal()}$('storyNext').onclick=()=>{if(storyIndex<STORY.length-1){storyIndex++;$('storyDlg').close();showStory()}else{$('storyDlg').close();localStorage.setItem('clpStorySeen','1')}};
function spendKibble(cost){if(p().tutorial||p().bonus)return true;if(state.kibble<cost){show('カリカリが足りません','<p>ボーナスステージでカリカリを集めるニャン。</p>',[['閉じる','close']]);return false}state.kibble-=cost;state.score=Math.max(0,state.score-cost*5);save();renderLife();$('scoreLabel').textContent=`${state.score}点`;return true}
function clearHintGlow(){board.querySelectorAll('.hinting,.hint-focus,.hint-safe-x').forEach(x=>x.classList.remove('hinting','hint-focus'))}
function directHint(type){
  const button=document.querySelector(`[data-hint="${type}"]`);
  if(!button||button.disabled)return;
  clearHintGlow();
  const cost=window.CLPHints.COST[type];

  if(type==='toy'){
    const step=window.CLPLogic.safeXStep(p(),state.revealed,state.marks);
    if(!step){
      show('猫じゃらし','<p>今は、見つけた猫を手掛かりに安全な×を案内できる場所がないニャン。カリカリは消費しないニャン。</p>',[['閉じる','close']]);
      return;
    }
    if(!spendKibble(cost))return;
    const target=board.querySelector(`[data-id="${step.target}"]`);
    if(target)target.classList.add('hint-safe-x');
    say(p().tutorial?'🐱':'🐱',p().tutorial?'にゃんこ爺さん':'テコちゃん',step.message,p().tutorial?'left':'right');
    record('HINT_SAFE_X',step.target,'toy');
    setTimeout(clearHintGlow,5000);
    return;
  }

  if(type==='matatabi'){
    const step=window.CLPLogic.nextStep(p(),state.revealed,state.marks);
    if(!step){
      show('またたび','<p>今は解法エンジンが説明できる有効な一手を見つけられなかったニャン。カリカリは消費しないニャン。</p>',[['閉じる','close']]);
      return;
    }
    if(!spendKibble(cost))return;
    if(step.kind==='only'){
      const target=board.querySelector(`[data-id="${step.target}"]`);
      if(target)target.classList.add('hinting');
    }else{
      const target=board.querySelector(`[data-id="${step.target}"]`);
      if(target)target.classList.add('hint-safe-x');
    }
    (step.focus||[]).forEach(id=>{const tile=board.querySelector(`[data-id="${id}"]`);if(tile)tile.classList.add('hint-focus')});
    say(p().tutorial?'🐱':'🐱',p().tutorial?'にゃんこ爺さん':'テコちゃん',step.message,p().tutorial?'left':'right');
    record('HINT_VALID_MOVE',step.target,'matatabi');
    setTimeout(clearHintGlow,5500);
    return;
  }

  if(type==='can'){
    const answer=Array.from({length:p().size},(_,r)=>`${r}-${p().solution[r]}`).find(id=>!state.revealed.has(id));
    if(!answer)return;
    if(!spendKibble(cost))return;
    record('HINT_OPEN_CAT',answer,'can');
    openTile(answer);
    return;
  }

  if(type==='paw'){
    const wrong=window.CLPHints.wrongMarks(p(),state.marks);
    if(!wrong.length){
      show('肉球チェック','<p>間違った×は見つからなかったニャン。カリカリは消費しないニャン。</p>',[['閉じる','close']]);
      return;
    }
    if(!spendKibble(cost))return;
    state.marks.delete(wrong[0]);
    record('HINT_FIX_X',wrong[0],'paw');
    build();
    show('肉球チェック','<p>間違った×を1つ直したニャン。</p>',[['閉じる','close']]);
  }
}
function openSettings(){show('設定',`<div class="settings-list"><button id="setReset">最初からやり直す</button><button id="setRules">ルールを見る</button><button id="setHistory">過去ステージ</button><button id="setTitle">タイトルへ戻る</button><label><input id="setVibrate" type="checkbox" ${localStorage.getItem('clpVibrate')==='0'?'':'checked'}> 振動を使う</label></div>`,[['閉じる','close']]);setTimeout(()=>{const a=$('setReset'),b=$('setRules'),c=$('setHistory'),d=$('setTitle'),v=$('setVibrate');a&&(a.onclick=()=>{dlg.close();show('確認','<p>このステージを最初からやり直しますか？ ハートは消費しません。現在の盤面だけ最初に戻ります。</p>',[['やり直す','resetStage'],['キャンセル','close']])});b&&(b.onclick=()=>{dlg.close();rules()});c&&(c.onclick=()=>{dlg.close();history()});d&&(d.onclick=()=>{dlg.close();state.i=0;resetBoard()});v&&(v.onchange=()=>localStorage.setItem('clpVibrate',v.checked?'1':'0'))},0)}
function setMode(m){state.mode=m;['X','Q','T'].forEach(x=>$('mode'+x).classList.toggle('active',x.toLowerCase()===m))}
$('modeX').onclick=()=>setMode('x');$('modeQ').onclick=()=>setMode('q');$('modeT').onclick=()=>setMode('t');$('historyBtn').onclick=history;$('historyClose').onclick=()=>$('historyDlg').close();
$('debugOpen').onclick=()=>$('debugDlg').showModal();$('debugClose').onclick=()=>$('debugDlg').close();$('dbgHeart').onclick=()=>{state.hearts=5;state.locked=false;save();render();goodToast('HEART FULL!')};$('dbgKibble').onclick=()=>{state.kibble+=10;save();render()};$('dbgClear').onclick=complete;$('dbgUnlock').onclick=()=>{window.CLPDevUnlockAllStages();$('debugDlg').close()};$('dbgAnswer').onclick=()=>{state.debugAnswer=!state.debugAnswer;build()};$('dbgLog').onclick=()=>$('debugLog').textContent=state.log.join('\n');$('dbgStory').onclick=()=>{storyIndex=0;$('debugDlg').close();showStory()};$('dbgReset').onclick=()=>{localStorage.clear();location.reload()};
function runDifficultyReport(){
  const report=window.CLPLogic.analyzeAll(STAGES);
  window.CLPDifficultyReport=report;
  console.group('猫ロジック Ver.0.4.3 論理ルール判定');
  console.table(report.map(x=>({stage:x.stage,size:`${x.boardSize}x${x.boardSize}`,difficulty:x.difficulty,score:x.difficultyScore,logicOnly:x.logicOnly,steps:x.logicStepCount,maxChain:x.maxChainLength,highestRule:x.highestRuleLevel,solveType:x.solveType})));
  const unresolved=report.filter(x=>!x.logicOnly);
  if(unresolved.length)console.warn('現在の解法エンジンだけでは完全解決できないステージ:',unresolved.map(x=>x.stage));
  console.groupEnd();
  return report;
}
window.CLPRunDifficultyReport=runDifficultyReport;
function runQualityReport(){
  const report=window.CLPQuality.inspectAll(STAGES);
  window.CLPQualityReport=report;
  console.group('猫ロジック Ver.0.4.4 問題品質検査');
  console.table(report.map(x=>({stage:x.stage,size:x.size,valid:x.valid,solutions:x.solutionCount,unique:x.uniqueSolution,duplicate:x.duplicateType,duplicateOf:x.duplicateOf||'',fingerprint:x.fingerprint,decision:x.decision,reasons:x.reasons.join(' / ')})));
  const rejected=report.filter(x=>x.decision==='rejected');
  if(rejected.length)console.warn('不採用判定ステージ:',rejected.map(x=>({stage:x.stage,reasons:x.reasons})));
  else console.info('全ステージが品質検査を通過しました。');
  console.groupEnd();
  return report;
}
window.CLPRunQualityReport=runQualityReport;


function runFinalDifficultyReport(){return window.CLPDifficultyManager.printReport(STAGES);}
window.CLPRunFinalDifficultyReport=runFinalDifficultyReport;
function runAssumptionReport(){return window.CLPAssumption.printReport(STAGES);}
window.CLPRunAssumptionReport=runAssumptionReport;
function runStallReport(){return window.CLPAnalysis.printReport(STAGES);}
window.CLPRunStallReport=runStallReport;
// Ver.0.4.10.4: 起動時の全50ステージ一括解析を停止
// 必要なときだけ開発者コンソールから各レポート関数を実行する。
// runDifficultyReport();
// runQualityReport();
// runStallReport();
// runAssumptionReport();
// runFinalDifficultyReport();
window.CLPGenerateNextStage=async function(){return await window.CLPGenerator.generateNext(16,50);};
window.CLPGenerateStages16to50=async function(){return await window.CLPGenerator.generateSeveral(1,16,50);};
window.CLPGenerateSeveralStages=async function(count=1){return await window.CLPGenerator.generateSeveral(count,16,50);};
window.CLPStopGeneration=function(){return window.CLPGenerator.requestStop();};
window.CLPGenerationStatus=function(){return window.CLPGenerator.status(16,50);};
window.CLPExportGeneratedStages=function(){return window.CLPGenerator.exportText();};
window.CLPClearGeneratedStages=function(){return window.CLPGenerator.clearAll();};

/* Ver.0.4.10.2 semantic hint colors
   blue + X = mark this cell with X
   yellow + cat paw = open the cat cell */
function clpHintMeaningForTile(tile){
  if(!tile||!tile.dataset||!tile.dataset.id)return null;
  const parts=tile.dataset.id.split('-').map(Number);
  if(parts.length!==2||parts.some(Number.isNaN))return null;
  const [r,c]=parts,stage=p();
  return stage&&Array.isArray(stage.solution)&&stage.solution[r]===c?'cat':'x';
}
function clpTileHasVisualHint(tile){
  if(!tile||!tile.classList)return false;
  const semanticNames=/hint|glow|guide|target|tutorial|focus|highlight|pulse/i;
  return [...tile.classList].some(name=>semanticNames.test(name)&&!/^clp-hint-/.test(name));
}
function clpApplySemanticHint(tile){
  if(!tile||!tile.classList||!tile.classList.contains('tile'))return;
  const hasHint=clpTileHasVisualHint(tile);
  if(!hasHint){
    tile.classList.remove('clp-hint-x','clp-hint-cat');
    return;
  }
  const meaning=clpHintMeaningForTile(tile);
  tile.classList.toggle('clp-hint-x',meaning==='x');
  tile.classList.toggle('clp-hint-cat',meaning==='cat');
}
function clpRefreshSemanticHints(root=document){
  if(root&&root.classList&&root.classList.contains('tile'))clpApplySemanticHint(root);
  if(root&&root.querySelectorAll)root.querySelectorAll('.tile').forEach(clpApplySemanticHint);
}
// Ver.0.4.10.5: class変更を監視対象にすると、ヒント用classの更新を
// MutationObserver自身が再検出し続けるため、childList監視だけに限定する。
const clpHintObserver=new MutationObserver(records=>{
  records.forEach(record=>{
    record.addedNodes&&record.addedNodes.forEach(node=>clpRefreshSemanticHints(node));
  });
});
if(board){
  clpHintObserver.observe(board,{subtree:true,childList:true});
  requestAnimationFrame(()=>clpRefreshSemanticHints(board));
  setTimeout(()=>clpRefreshSemanticHints(board),80);
}
window.CLPRefreshHintColors=()=>clpRefreshSemanticHints(board);

/* Ver.0.4.10.5: 250ms周期の全タイル再走査を停止。
   ヒント表示時は既存処理と CLPRefreshHintColors から必要時だけ更新する。 */


resetBoard();if(!localStorage.getItem('clpStorySeen'))showStory();
const settingsButton=$('settingsBtn');if(settingsButton){settingsButton.disabled=false;settingsButton.onclick=openSettings;}document.querySelectorAll('[data-hint]').forEach(b=>b.onclick=()=>directHint(b.dataset.hint));

const hintDescriptions={toy:['猫じゃらし','安全に×を付けられるマスを1つ教えます。光ったマスへプレイヤー自身で×を付けます。'],matatabi:['またたび','盤面を論理的に前進させる有効な一手を、理由付きで教えます。猫を開く手や安全な×など、状況に合う一手を案内します。'],can:['ネコ缶','正解の猫を1匹、その場で自動的に開く強力なヒントです。'],paw:['肉球チェック','間違って付けた×を1つ見つけて直します。間違いがなければ消費しません。']};
document.querySelectorAll('[data-info]').forEach(info=>info.onclick=e=>{e.preventDefault();e.stopPropagation();const d=hintDescriptions[info.dataset.info];show(d[0],`<p>${d[1]}</p>`,[['閉じる','close']])});

$('historyDlg').addEventListener('click',e=>{if(e.target===$('historyDlg'))$('historyDlg').close()});
