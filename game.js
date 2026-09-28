"use strict";
const STAGES=[{"size":4,"solution":[2,0,3,1],"regions":[[0,0,0,2],[1,0,0,2],[3,2,2,2],[3,3,3,2]],"stage":1,"title":"最初の1匹","guide":"青の1マスエリアから始めるんじゃ。練習中はハートは減らんぞい。","tutorial":true,"hard":false,"bonus":false},{"size":4,"solution":[1,3,0,2],"regions":[[2,0,0,0],[2,2,3,1],[2,3,3,3],[3,3,3,3]],"stage":2,"title":"1マスエリアを探そう","guide":"まずはB4の1マスだけの色エリアを開くニャン。そこから周囲、行、列の順に確認するニャン。","tutorial":true,"hard":false,"bonus":false},{"size":4,"solution":[1,3,0,2],"regions":[[0,0,0,1],[2,2,2,1],[3,2,2,2],[2,2,2,2]],"stage":3,"title":"行と色エリアを組み合わせよう","guide":"まずA4へ×。次にB4を開き、D3、C1の順に候補を見つける修行じゃ。","tutorial":true,"hard":false,"bonus":false},{"size":5,"solution":[0,3,1,4,2],"regions":[[0,2,2,1,1],[0,2,1,1,1],[2,2,2,3,3],[2,2,2,3,3],[2,2,4,3,3]],"stage":4,"title":"5×5へ","guide":"ここからは5×5じゃ。少し広くなるが、基本は同じじゃよ。","tutorial":true,"hard":false,"bonus":false},{"size":5,"solution":[2,4,1,3,0],"regions":[[0,0,0,3,1],[0,0,0,3,1],[0,2,0,3,1],[3,3,3,3,3],[4,3,3,3,3]],"stage":5,"title":"1マスエリアから始めよう","guide":"1マスだけの色エリアが二つあるぞい。まず確実な猫から見つけるんじゃ。","tutorial":true,"hard":false,"bonus":false},{"size":5,"solution":[2,4,1,3,0],"regions":[[2,2,0,0,0],[2,2,1,1,1],[2,2,3,3,1],[4,2,2,3,1],[4,2,2,3,1]],"stage":6,"title":"条件を組み合わせる","guide":"行・列・色エリアの条件を組み合わせて考えるんじゃ。","tutorial":true,"hard":false,"bonus":false},{"size":6,"solution":[0,4,1,3,5,2],"regions":[[0,2,2,2,2,1],[2,2,2,1,1,1],[2,2,5,5,1,4],[2,5,5,3,1,4],[5,5,5,5,5,4],[5,5,5,5,4,4]],"stage":7,"title":"6×6へ","guide":"いよいよ6×6じゃ。一か所だけでなく盤面全体を見るんじゃ。","tutorial":true,"hard":false,"bonus":false},{"size":6,"solution":[2,0,3,5,1,4],"regions":[[1,1,0,2,2,2],[1,1,0,2,2,2],[1,2,2,2,2,2],[1,1,1,2,2,3],[4,4,4,2,3,3],[4,4,4,4,5,5]],"stage":8,"title":"候補を残す","guide":"すぐ決められない場所には「？」を置いて、別の場所から進めるんじゃ。","tutorial":true,"hard":false,"bonus":false},{"size":6,"solution":[4,2,0,5,3,1],"regions":[[2,2,1,0,0,3],[2,2,1,0,3,3],[2,4,3,3,3,3],[4,4,4,3,3,3],[4,4,4,4,3,3],[5,5,5,4,4,4]],"stage":9,"title":"仮置き推理","guide":"ここに猫がいると仮に考える「仮置き推理」を試すんじゃ。△は仮置きの印じゃよ。","tutorial":true,"hard":false,"bonus":false},{"size":6,"solution":[2,4,1,3,0,5],"regions":[[2,0,0,0,0,1],[2,2,0,0,1,1],[4,2,3,3,3,3],[4,3,3,3,3,3],[4,4,3,3,3,3],[4,3,3,3,3,5]],"stage":10,"title":"ハードステージ","guide":"ハードステージじゃ。エリートにゃんこを見つけてみるんじゃ！","tutorial":true,"hard":true,"bonus":false},{"size":8,"solution":[4,7,5,1,6,3,0,2],"regions":[[3,3,3,3,0,2,2,2],[3,3,3,3,2,2,2,1],[3,3,3,2,2,2,2,2],[3,3,3,3,2,2,2,2],[3,3,3,3,5,4,4,2],[3,3,7,5,5,4,4,4],[6,7,7,5,5,4,4,4],[6,7,7,7,4,4,4,4]],"stage":11,"title":"本編最初の一歩","guide":"1マスだけの色エリアが二つあるニャン。そこからゆっくり始めるニャン。","tutorial":false,"hard":false,"bonus":false},{"size":8,"solution":[7,2,6,3,1,5,0,4],"regions":[[4,4,1,1,2,2,2,0],[4,4,1,2,2,2,2,2],[4,4,3,3,2,5,2,2],[4,4,3,3,5,5,5,5],[4,4,4,5,5,5,5,5],[4,4,4,7,5,5,5,5],[6,4,4,7,5,5,5,5],[4,4,7,7,7,5,5,5]],"stage":12,"title":"広い盤面を見る","guide":"8×8でも基本は同じ。焦らず広い盤面を見渡そう。","tutorial":false,"hard":false,"bonus":false},{"size":8,"solution":[1,5,3,0,2,7,4,6],"regions":[[0,0,2,2,1,1,1,1],[0,3,2,2,1,1,1,1],[3,3,3,2,2,2,1,1],[3,4,4,4,4,4,5,5],[4,4,4,6,6,4,5,5],[4,4,6,6,6,6,5,5],[4,6,6,6,6,6,6,5],[6,6,6,6,6,6,7,5]],"stage":13,"title":"複数エリア","guide":"複数の行と色エリアを見比べて候補を絞ろう。","tutorial":false,"hard":false,"bonus":false},{"size":8,"solution":[4,6,3,1,5,7,0,2],"regions":[[3,3,3,0,0,0,1,1],[3,3,3,0,1,1,1,1],[3,3,3,2,3,1,1,4],[3,3,3,3,3,3,1,4],[3,3,6,6,3,4,4,4],[6,6,6,4,4,4,5,5],[6,6,4,4,7,4,4,4],[6,6,7,7,7,4,4,4]],"stage":14,"title":"ボーナスステージ","guide":"ボーナスステージ！クリアすると、またたびヒントを1個獲得じゃ。","tutorial":false,"hard":false,"bonus":true},{"size":8,"solution":[3,1,4,2,5,7,0,6],"regions":[[1,1,1,0,0,2,2,2],[3,1,0,0,2,2,2,2],[3,3,3,0,2,2,2,2],[3,3,3,3,2,4,4,4],[3,3,3,3,2,4,4,4],[6,3,3,3,4,4,5,5],[6,3,3,3,3,4,7,5],[6,6,3,3,3,3,7,7]],"stage":15,"title":"本編チャレンジ","guide":"ここまで覚えた基本を使い、ノーミスを目指そう。","tutorial":false,"hard":false,"bonus":false}];
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
function haptic(pattern){try{if(navigator.vibrate)navigator.vibrate(pattern)}catch(e){}}
function travelComment(){const comments=['まずは行と列を見比べるニャン。','同じ色エリアに残ったマスを探すニャン。','焦らず、確定できるところから進めるニャン。','仲間の手掛かりが見つかりそうだニャン。'];return comments[p().stage%comments.length]}
function startIdle(){clearTimeout(state.idle);state.idle=setTimeout(()=>{if(p().tutorial)say('🐱','にゃんこ爺さん','迷ったときは、下のヒントを使ってもよいんじゃぞ。チュートリアル中は無料じゃ。','left');else say('🐱','テコちゃん',travelComment(),'right')},17000)}
function resetBoard(){state.drag.active=false;state.drag.visited=new Set();state.timers.forEach(clearTimeout);state.timers.clear();state.score=100;state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;state.tutorialStep=0;record('START');render();startIdle()}
function say(face,name,text,side='left',enemy=false){$('talkFace').textContent=face;$('talkName').textContent=name;$('talkText').textContent=text;$('talk').className=`talk ${side}${enemy?' enemy':''}`}
function render(){let s=p();$('stageLabel').innerHTML=s.bonus?`STAGE ${s.stage}<br><small>BONUS</small>`:s.hard?`STAGE ${s.stage}<br><small>HARD</small>`:`STAGE ${s.stage}`;$('scoreLabel').textContent=`${state.score}点`;$('panel').className='panel'+(s.hard?' hard':'')+(s.bonus?' bonus':'');$('modeT').classList.toggle('hidden',s.stage<9);$('historyBtn').classList.toggle('hidden',!state.history['10']);if(s.hard)say('😼','エリートにゃんこ','フン！ ここから先へ行きたければ、俺様を見つけてみるんだな！','right',true);else if(s.tutorial)say('🐱','にゃんこ爺さん',tutorialText(),'left');else say('🐱','テコちゃん',s.stage===11?'ここからが本当の旅の始まりニャン。ハートを大切にして、仲間とお母さんの手掛かりを探すニャン！':travelComment(),'right');renderLife();build();updateHint()}
function tutorialText(){let s=p();if(s.stage===1){if(state.revealed.size===0)return 'まずはタイルの開き方じゃ。1マスだけの色エリアを、素早く2回タップして開くんじゃ。';if(state.revealed.size===1&&state.marks.size<3)return 'よくできたのう。次は猫の周囲8マスへ×を付けるんじゃ。斜めにも猫はいないぞい。';if(state.revealed.size===1)return '同じ行と列にも、ほかの猫はいないんじゃ。×で候補を減らしてみるんじゃ。';return '色エリアで残った1マスを探すんじゃ。見つけたら素早く2回タップじゃ。'}if(s.stage===2)return state.revealed.size===0?'B4に1マスだけの色エリアがあるぞい。まずそこを素早く2回タップするんじゃ。':'よいぞ。周囲8マス、その次に同じ行と列を×で確認するんじゃぞ。';if(s.stage===3){if(!state.marks.has('0-3')&&state.revealed.size===0)return 'A1・A2・A3は同じ青エリアじゃ。青の猫はA行のどこかにいるから、A4には猫はいない。まずA4へ×を付けるんじゃ。';if(!state.revealed.has('1-3'))return 'A4へ×を付けたから、黄色エリアで残ったB4に猫がいるぞい。B4を素早く2回タップじゃ。';if(!state.revealed.has('3-2'))return 'B4の猫から行・列・周囲を消すと、3列目で残るD3に猫がいると分かるぞい。D3を開くんじゃ。';if(!state.revealed.has('2-0'))return '次はC1じゃ。ここまでの×と色エリアを見比べて開いてみるんじゃ。';return '残りは頑張るんじゃ。ここまで覚えた基本で解けるぞい。'}if(s.stage===4)return 'ここからは5×5じゃ。まずは1マスだけの色エリアを探すんじゃ。盤面が広くなっても基本は同じじゃよ。';if(s.stage===7)return 'いよいよ6×6じゃ。最初から確定できる場所が二つあるぞい。落ち着いて探すんじゃ。';if(s.stage===9)return 'すぐ決められないときは、△で「ここにいる」と仮に考える方法もあるんじゃ。これを仮置き推理というぞい。';return s.guide}
function renderLife(){let b=$('lifeBox');b.innerHTML='';if(p().tutorial||p().bonus)b.innerHTML='<span class="training">チュートリアル：ハートは減りません</span>';else{b.innerHTML='<label>LIFE</label>';for(let i=0;i<5;i++){let h=document.createElement('span');h.className='life'+(i<state.hearts?'':' empty');h.textContent=i<state.hearts?'♥':'♡';b.appendChild(h)}b.insertAdjacentHTML('beforeend',`<span class="kibble">カリカリ ${state.kibble}</span>`)}}
function build(){let s=p(),n=s.size;board.innerHTML='';board.style.gridTemplateColumns=`repeat(${n},minmax(0,1fr))`;board.style.gridTemplateRows=`repeat(${n},minmax(0,1fr))`;board.style.setProperty('--gap',n<=4?'5px':n<=6?'3px':'2px');board.style.setProperty('--pad',n<=4?'6px':'3px');board.style.setProperty('--radius',n<=4?'11px':n<=6?'6px':'4px');$('coordTop').style.gridTemplateColumns=`repeat(${n},1fr)`;$('coordTop').innerHTML=Array.from({length:n},(_,i)=>`<span>${i+1}</span>`).join('');$('coordSide').style.gridTemplateRows=`repeat(${n},1fr)`;$('coordSide').innerHTML=Array.from({length:n},(_,i)=>`<span>${String.fromCharCode(65+i)}</span>`).join('');let target=firstLogicalTarget();for(let r=0;r<n;r++)for(let c=0;c<n;c++){let id=key(r,c),b=document.createElement('button'),m=state.marks.get(id);b.className=`tile r${s.regions[r][c]}`+(state.revealed.has(id)?' revealed':'')+(state.debugAnswer&&answer(id)?' hinting':'')+(((s.stage===1&&state.revealed.size===0&&id===target)||(s.stage===3&&id===stage3Target()))?' tutorial-target':'');b.dataset.id=id;if(state.revealed.has(id))b.innerHTML='<span>🐱</span>';else if(m)b.innerHTML=`<span class="${m==='x'?'mark-x':m==='q'?'mark-q':'mark-t'}">${m==='x'?'×':m==='q'?'？':'△'}</span>`;b.onpointerdown=e=>pointerStart(e,id);board.appendChild(b)}}
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
function openTile(id){state.marks.delete(id);if(answer(id)){state.revealed.add(id);state.streak++;record('OPEN',id,'OK');haptic([45,35,70]);goodToast(['NICE!','GREAT!','EXCELLENT!','AMAZING!'][Math.min(3,state.streak-1)]);build();if(p().tutorial)say('🐱','にゃんこ爺さん',tutorialText(),'left');if(state.revealed.size===p().size)complete()}else{state.streak=0;state.score=Math.max(0,state.score-10);record('OPEN',id,'MISS');haptic([90,45,90,45,120]);$('scoreLabel').textContent=`${state.score}点`;if(!(p().tutorial||p().bonus)){state.hearts=Math.max(0,state.hearts-1);save();renderLife()}failToast();if(state.hearts===0&&!p().tutorial&&!p().bonus)heartZero()}startIdle()}
function goodToast(t){let x=$('toast');x.className='toast';x.replaceChildren();void x.offsetWidth;x.className='toast good';x.textContent=t;setTimeout(()=>{x.className='toast';x.textContent='';x.replaceChildren()},850)}
function failToast(){
  const x=$("toast");
  x.className="toast try-again-toast";
  x.innerHTML='<div class="try-whole">TRY AGAIN!</div>';
  void x.offsetWidth;
  x.classList.add("show-whole");

  setTimeout(()=>{
    x.className="toast try-again-toast splitting";
    x.innerHTML='<div class="try-piece try-left">TRY AGAIN!</div><div class="try-piece try-right">TRY AGAIN!</div><div class="try-crack"></div>';
  },520);

  setTimeout(()=>{
    x.className="toast";
    x.replaceChildren();
  },1450);
}
function updateHint(){$('hintBtn').textContent=p().tutorial||p().bonus?'ヒントを見る（チュートリアル無料）':`ヒントを見る（カリカリ1～3消費／所持${state.kibble}）`}
function hintMenu(){if(p().tutorial||p().bonus){useHint(3);return}show('ヒントを選ぶ',`<p>所持カリカリ：<b>${state.kibble}</b></p><p>猫じゃらし：注目エリア（1個）<br>またたび：正解位置を光らせる（2個）<br>ネコ缶：猫を1匹開く（3個）</p>`,[['猫じゃらし 1','h1'],['またたび 2','h2'],['ネコ缶 3','h3'],['閉じる','close']])}
function useHint(level){let cost=p().tutorial||p().bonus?0:level;if(state.kibble<cost){show('カリカリが足りません','<p>ボーナスステージなどでカリカリを集められます。</p>',[['閉じる','close']]);return}state.kibble-=cost;state.score=Math.max(0,state.score-cost*5);save();let id=Array.from({length:p().size},(_,r)=>key(r,p().solution[r])).find(x=>!state.revealed.has(x));if(!id)return;if(level===3&&!p().tutorial&&!p().bonus){openTile(id)}else{let t=board.querySelector(`[data-id="${id}"]`);t.classList.add('hinting');setTimeout(()=>t.classList.remove('hinting'),3500)}record('HINT',id,level);updateHint()}
function complete(){state.locked=true;haptic([40,30,60,40,130]);state.history[p().stage]=Math.max(state.history[p().stage]||0,state.score);if(p().bonus)state.kibble+=3;save();let line=p().tutorial?['よくできたのう、テコちゃん。','見事じゃ。仲間をみんな見つけたぞい。','また一つ、修行を終えたのう。'][p().stage%3]:['仲間を見つけたニャン！','無事に再会できたニャン！','みんな見つかったニャン！'][p().stage%3];let speaker=p().tutorial?'にゃんこ爺さん':'テコちゃん';let extra=p().bonus?'<p>カリカリを3個獲得しました！</p>':'';let finish=p().stage===10?'<p>よく覚えたのう、テコちゃん。基本の修行はこれで終わりじゃ。ここから先は、まだ見ぬ仲間たちと、お母さんの手掛かりが待っておるぞい。</p>':'';let result=()=>show(p().hard?'エリートにゃんこを追い払った！':'STAGE CLEAR',`<p><b>${speaker}：</b> ${line}</p><p>スコアは <b>${state.score}点</b> です。${state.score===100?' ノーミスでクリアできました！':' クリアできました！'}</p>${extra}${finish}`,state.i<STAGES.length-1?[['次のステージ','next']]:[['Ver.0.3.2 完了','close']]);if(p().hard)runElite(result);else result()}
function runElite(done){let e=document.createElement('div');e.className='elite-run';e.textContent='😼💨';document.body.appendChild(e);setTimeout(()=>e.remove(),1500);setTimeout(done,1600)}
function heartZero(){state.locked=true;show('ハートがなくなりました',`<p>少し時間を置いて遊んでね。</p><p>将来は時間経過、広告視聴、カリカリ交換で回復できる予定です。</p>`,[['タイトルへ戻る','title'],['DEBUG：全回復','recover']])}
function rules(){show('ルール',`<details open><summary><b>基本ルール</b></summary><ul><li>各行・各列・各色エリアに猫は1匹</li><li>猫同士は周囲8マスで隣り合わない</li></ul></details><details><summary><b>操作</b></summary><p>1回タップで×・？・△、素早い2回タップで開きます。△は仮置き推理用です。</p></details>`,[['閉じる','close']])}
function show(title,body,btns){$('dlgTitle').textContent=title;$('dlgBody').innerHTML=body;$('dlgActions').innerHTML='';btns.forEach(([text,a])=>{let b=document.createElement('button');b.className='primary';b.textContent=text;b.onclick=()=>{if(a.startsWith('h')){dlg.close();useHint(Number(a[1]));return}dlg.close();if(a==='next'){state.i++;resetBoard()}if(a==='recover'){state.hearts=5;state.locked=false;save();render()}if(a==='title'){state.i=0;resetBoard()}};$('dlgActions').appendChild(b)});dlg.showModal()}
function history(){let g=$('historyGrid');g.innerHTML='';let groups=[['チュートリアル 1～9',1,9],['修行の仕上げ・ハード 10',10,10],['第1章 11～15',11,15]];groups.forEach(([title,a,z])=>{let h=document.createElement('h3');h.className='history-heading';h.textContent=title;g.appendChild(h);let wrap=document.createElement('div');wrap.className='history-section';for(let k=a;k<=z;k++){if(!state.history[k])continue;let b=document.createElement('button'),s=STAGES[k-1],score=state.history[k];b.className=(score===100?'gold ':'')+(s.hard||s.bonus?'special':'');b.innerHTML=`<b>${k}</b><br><small>${k<=9?'チュートリアル・':''}${s.bonus?'BONUS・':''}${score}点</small>`;b.onclick=()=>{$('historyDlg').close();state.i=k-1;resetBoard()};wrap.appendChild(b)}if(!wrap.children.length)wrap.innerHTML='<p class="history-empty">まだ記録がありません</p>';g.appendChild(wrap)});$('historyDlg').showModal()}
let storyIndex=0;function showStory(reset=false){if(reset)storyIndex=0;let s=STORY[storyIndex];$('storyArt').textContent=s[1];$('storyPage').textContent=`${storyIndex+1} / ${STORY.length}`;$('storyTitle').textContent=s[0];$('storyText').textContent=s[2];$('storyNext').textContent=storyIndex===STORY.length-1?'修行を始める':'次へ';$('storyDlg').showModal()}$('storyNext').onclick=()=>{if(storyIndex<STORY.length-1){storyIndex++;$('storyDlg').close();showStory()}else{$('storyDlg').close();localStorage.setItem('clpStorySeen','1')}};
function setMode(m){state.mode=m;['X','Q','T'].forEach(x=>$('mode'+x).classList.toggle('active',x.toLowerCase()===m))}
$('modeX').onclick=()=>setMode('x');$('modeQ').onclick=()=>setMode('q');$('modeT').onclick=()=>setMode('t');$('resetBtn').onclick=()=>{state.score=100;state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;record('RESET');render();startIdle()};$('rulesBtn').onclick=rules;$('hintBtn').onclick=hintMenu;$('historyBtn').onclick=history;$('historyClose').onclick=()=>$('historyDlg').close();
$('debugOpen').onclick=()=>$('debugDlg').showModal();$('debugClose').onclick=()=>$('debugDlg').close();$('dbgHeart').onclick=()=>{state.hearts=5;state.locked=false;save();render();goodToast('HEART FULL!')};$('dbgKibble').onclick=()=>{state.kibble+=10;save();render()};$('dbgClear').onclick=complete;$('dbgUnlock').onclick=()=>{for(let i=1;i<=STAGES.length;i++)state.history[i]=state.history[i]||1;save();render()};$('dbgAnswer').onclick=()=>{state.debugAnswer=!state.debugAnswer;build()};$('dbgLog').onclick=()=>$('debugLog').textContent=state.log.join('\n');$('dbgStory').onclick=()=>{storyIndex=0;$('debugDlg').close();showStory()};$('dbgReset').onclick=()=>{localStorage.clear();location.reload()};
resetBoard();if(!localStorage.getItem('clpStorySeen'))showStory();