"use strict";
const STAGES=window.CLP_STAGES;
const STORY=[
["ある日のこと","🐱🏘️","幼いテコちゃんは、お母さんとはぐれてしまいました。"],
["ニャンじい","🐱　🐱","ひとりになったテコちゃんを、ニャンじいが助けました。"],
["大きくなったテコちゃん","🐱🌱","月日が流れ、テコちゃんは旅に出られるほど成長しました。"],
["旅立ちの相談","🐱💬🐱","『お母さんを探しに行きたいニャン』テコちゃんは、ニャンじいに相談しました。"],
["修行のはじまり","🟦🟨🟩🩷","『旅に出るなら、隠れた仲間を見つける修行が必要じゃ』"],
["色と模様のタイル","❌❓△","行・列・色エリアの手掛かりを使って、仲間の猫を探します。"],
["最初の約束","🐱❤️","修行中はハートが減りません。失敗を恐れず試してみましょう。"],
["ステージ1へ","🐱✨","『わかったニャン！ 最初の仲間を見つけるニャン！』"]];
const state={i:0,hearts:Number(localStorage.getItem('clpHearts')||5),kibble:Number(localStorage.getItem('clpKibble')||0),score:0,mistakes:0,hintsUsed:0,totalFound:0,mode:'x',revealed:new Set(),marks:new Map(),timers:new Map(),locked:false,streak:0,history:JSON.parse(localStorage.getItem('clpHistory')||'{}'),log:[],tutorialStep:0,idle:null,debugAnswer:false,bossPhase:Math.max(1,Math.min(3,Number(localStorage.getItem('clpBossPhase')||1))),bossIntroShown:false,drag:{active:false,moved:false,pointerId:null,startX:0,startY:0,startId:'',action:'add',visited:new Set()}};
const HAGURE_STAGES={
  20:{kind:'cloud',label:'はぐれにゃんこ',intro:'旅の途中で、はぐれにゃんこが道をふさいでいるニャン。いつもより難しい盤面を解いて、先へ進む力を見せるニャン。',clear:'難しい盤面を解ききったニャン。はぐれにゃんこは満足そうに森の奥へ帰っていったニャン。'},
  30:{kind:'rain',label:'はぐれにゃんこ',intro:'また、はぐれにゃんこが現れたニャン。今度は前より難しい問題を用意しているみたいだニャン。',clear:'今回の難しい盤面も解けたニャン。はぐれにゃんこは静かに道を譲ってくれたニャン。'},
  40:{kind:'leaves',label:'はぐれにゃんこ',intro:'山道の先で、はぐれにゃんこが待っているニャン。旅の成果を確かめる特別な問題みたいだニャン。',clear:'旅で身につけた力を見せられたニャン。はぐれにゃんこはうなずいて、別の道へ向かっていったニャン。'}
};
// Ver.0.5.7: Stage 20, 30 and 40 visual gimmicks are frozen.
// Their implementation and assets remain for possible future use.
const ENABLE_SPECIAL_GIMMICKS=false;
const hagureIntroSeen=new Set();
function hagureConfig(){return HAGURE_STAGES[p().stage]||null}
function isHagureStage(){return Boolean(hagureConfig())}
function hagureStory(){return ENABLE_SPECIAL_GIMMICKS&&window.CLPStories&&window.CLPStories.hagure?window.CLPStories.hagure[p().stage]:null}function hagureTalk(){const x=hagureStory();return x?x.intro:(hagureConfig()?hagureConfig().intro:'')}
function hagureClearTitle(){return isHagureStage()?hagureConfig().label:'STAGE CLEAR'}
function randomizeSpecialFx(){
  const fx=board.querySelector('.special-fx');if(!fx)return;
  [...fx.children].forEach((e,i)=>{
    if(fx.classList.contains('fx-rain')){
      e.style.setProperty('--rx',(Math.random()*96).toFixed(1)+'%');
      e.style.setProperty('--delay',(-Math.random()*1.8).toFixed(2)+'s');
      e.style.setProperty('--speed',(0.48+Math.random()*.58).toFixed(2)+'s');
      e.style.setProperty('--drift',(-18+Math.random()*36).toFixed(0)+'px');
    }
    if(fx.classList.contains('fx-leaves')){
      e.style.setProperty('--leaf-start',(Math.random()*96).toFixed(1)+'%');
      e.style.setProperty('--leaf-delay',(-Math.random()*5).toFixed(2)+'s');
      e.style.setProperty('--leaf-speed',(3.5+Math.random()*4).toFixed(2)+'s');
      e.style.setProperty('--leaf-drift',(-50+Math.random()*100).toFixed(0)+'px');
    }
  });
}
function installLeafSwipe(){return}
function installLeafTilt(){
  if(!ENABLE_SPECIAL_GIMMICKS)return;
  if(window.clpLeafTiltInstalled)return;window.clpLeafTiltInstalled=true;
  let last=0;
  window.addEventListener('deviceorientation',e=>{
    const now=performance.now();if(now-last<50)return;last=now;
    if(!isHagureStage()||hagureConfig().kind!=='leaves')return;
    const pile=board.querySelector('.leaf-pile');if(!pile)return;
    const gamma=Math.max(-24,Math.min(24,Number(e.gamma)||0));
    const beta=Math.max(-18,Math.min(18,(Number(e.beta)||0)-45));
    pile.style.setProperty('--tilt-x',(gamma*1.35).toFixed(1)+'px');
    pile.style.setProperty('--tilt-y',(beta*.55).toFixed(1)+'px');
  },{passive:true});
}
function updateSpecialStageFx(){
  if(!ENABLE_SPECIAL_GIMMICKS){
    const oldFx=board.querySelector('.special-fx');
    if(oldFx)oldFx.remove();
    document.body.classList.remove('hagure-stage');
    return;
  }
  const cfg=hagureConfig();
  let fx=board.querySelector('.special-fx');
  if(!cfg){if(fx)fx.remove();document.body.classList.remove('hagure-stage');return}
  document.body.classList.add('hagure-stage');
  if(!fx||!fx.classList.contains('fx-'+cfg.kind)){
    if(fx)fx.remove();fx=document.createElement('div');fx.className='special-fx fx-'+cfg.kind;
    if(cfg.kind==='rain'){const glass=document.createElement('div');glass.className='wet-glass';for(let j=0;j<14;j++){const d=document.createElement('span');d.style.setProperty('--gx',(4+Math.random()*92).toFixed(1)+'%');d.style.setProperty('--gy',(3+Math.random()*72).toFixed(1)+'%');d.style.setProperty('--gs',(12+Math.random()*25).toFixed(0)+'px');d.style.setProperty('--gr',(-12+Math.random()*24).toFixed(1)+'deg');glass.appendChild(d)}fx.appendChild(glass)}
    if(cfg.kind==='leaves'){const pile=document.createElement('div');pile.className='leaf-pile';for(let j=0;j<34;j++){const leaf=document.createElement('span');leaf.style.setProperty('--px',(Math.random()*96).toFixed(1)+'%');leaf.style.setProperty('--pr',(-55+Math.random()*110).toFixed(0)+'deg');leaf.style.setProperty('--ps',(16+Math.random()*20).toFixed(0)+'px');pile.appendChild(leaf)}fx.appendChild(pile)}
    const counts={cloud:10,rain:48,leaves:42};
    for(let i=0;i<counts[cfg.kind];i++){const e=document.createElement('i');e.style.setProperty('--i',i);e.style.setProperty('--x',((i*37+11)%91)+'%');e.style.setProperty('--y',((i*53+7)%86)+'%');e.style.setProperty('--d',(i%5)*.16+'s');if(cfg.kind==='cloud'){e.style.setProperty('--cloud-speed',(42+(i%4)*7)+'s');e.style.setProperty('--cloud-delay',(-i*4.1)+'s');e.style.setProperty('--cloud-y',((i*19+4)%78)+'%')}fx.appendChild(e)}
    board.appendChild(fx);randomizeSpecialFx()
  }
  const progress=Math.min(1,state.revealed.size/Math.max(1,p().size));
  fx.classList.toggle('fx-weak',localStorage.getItem('clpSpecialFxWeak')==='1');
  const particles=[...fx.children].filter(e=>e.tagName==='I');particles.forEach((e,i)=>e.classList.toggle('cleared',i<Math.floor(progress*particles.length)));
  fx.style.setProperty('--progress',progress.toFixed(3));
  const glass=fx.querySelector('.wet-glass');if(glass){glass.style.opacity=String(Math.max(.10,.96-progress*.84));glass.style.setProperty('--wet-progress',progress.toFixed(3));}
  const pile=fx.querySelector('.leaf-pile');if(pile){const pileLeaves=[...pile.querySelectorAll('span')].slice(0,12);const hideCount=Math.min(pileLeaves.length,Math.floor(progress*pileLeaves.length));pile.style.setProperty('--pile-level','1');pileLeaves.forEach((leaf,i)=>leaf.classList.toggle('leaf-gone',i<pileLeaves.length-hideCount?false:true));pile.classList.toggle('swept',progress>=.98)}
}
const $=x=>document.getElementById(x),board=$('board'),dlg=$('dlg'),isBossStage=()=>STAGES[state.i]&&STAGES[state.i].stage===50,p=()=>isBossStage()&&Array.isArray(window.CLP_BOSS_PHASES)?window.CLP_BOSS_PHASES[state.bossPhase-1]:STAGES[state.i],key=(r,c)=>`${r}-${c}`;
function scoreTarget(){return isBossStage()&&Array.isArray(window.CLP_BOSS_PHASES)?window.CLP_BOSS_PHASES.reduce((sum,phase)=>sum+Number(phase.size||0),0):Number(p().size||0)}
function updateRunScore(){const target=Math.max(1,scoreTarget());state.score=Math.min(80,Math.floor(80*state.totalFound/target));const label=$('scoreLabel');if(label)label.textContent=`評価 ${state.score} / 100`}
function finalScore(){return 80+(state.mistakes===0?10:0)+(state.hintsUsed===0?10:0)}
function scoreBreakdown(){const noMiss=state.mistakes===0,hintFree=state.hintsUsed===0,total=finalScore();return `<div class="score-breakdown"><div><span>盤面クリア</span><b>80点</b></div><div><span>ノーミス</span><b>${noMiss?'10点':'今回は未獲得'}</b></div><div><span>ヒントなし</span><b>${hintFree?'10点':'今回は未獲得'}</b></div><hr><div class="score-total"><span>合計</span><strong>${total}点</strong></div>${total===100?'<p class="gold-earned">金枠を獲得しました！</p>':''}</div>`}
/* Ver.0.7.4: heart recovery and interrupted-board resume */
const HEART_MAX=5,HEART_RECOVERY_MS=30*60*1000,HEART_KIBBLE_COST=1,BOARD_SAVE_KEY='clpCurrentBoard';
function syncHeartRecovery(){
  if(state.hearts>=HEART_MAX){state.hearts=HEART_MAX;localStorage.removeItem('clpHeartUpdatedAt');return 0}
  let base=Number(localStorage.getItem('clpHeartUpdatedAt')||Date.now());
  if(!Number.isFinite(base)||base<=0)base=Date.now();
  const recovered=Math.floor((Date.now()-base)/HEART_RECOVERY_MS);
  if(recovered>0){state.hearts=Math.min(HEART_MAX,state.hearts+recovered);base+=recovered*HEART_RECOVERY_MS;}
  if(state.hearts>=HEART_MAX)localStorage.removeItem('clpHeartUpdatedAt');else localStorage.setItem('clpHeartUpdatedAt',String(base));
  return recovered;
}
function startHeartTimerAfterLoss(){if(state.hearts<HEART_MAX&&!localStorage.getItem('clpHeartUpdatedAt'))localStorage.setItem('clpHeartUpdatedAt',String(Date.now()))}
function heartTimeText(){
  if(state.hearts>=HEART_MAX)return 'ハートは満タンです';
  const base=Number(localStorage.getItem('clpHeartUpdatedAt')||Date.now());
  const remain=Math.max(0,HEART_RECOVERY_MS-(Date.now()-base));
  const minutes=Math.max(1,Math.ceil(remain/60000));
  return `次の回復まで約${minutes}分`;
}
function saveBoard(){
  if(!STAGES[state.i]||state.locked)return;
  const data={version:1,stageIndex:state.i,bossPhase:state.bossPhase,score:state.score,mistakes:state.mistakes,hintsUsed:state.hintsUsed,totalFound:state.totalFound,mode:state.mode,revealed:[...state.revealed],marks:[...state.marks.entries()],streak:state.streak,savedAt:Date.now()};
  localStorage.setItem(BOARD_SAVE_KEY,JSON.stringify(data));
}
function clearBoardSave(){localStorage.removeItem(BOARD_SAVE_KEY)}
function restoreBoard(){
  let data=null;try{data=JSON.parse(localStorage.getItem(BOARD_SAVE_KEY)||'null')}catch(_e){clearBoardSave();return false}
  if(!data||!Number.isInteger(data.stageIndex)||data.stageIndex<0||data.stageIndex>=STAGES.length)return false;
  state.i=data.stageIndex;state.bossPhase=Math.max(1,Math.min(3,Number(data.bossPhase)||1));
  state.score=Number(data.score)||0;state.mistakes=Number(data.mistakes)||0;state.hintsUsed=Number(data.hintsUsed)||0;state.totalFound=Number(data.totalFound)||0;
  state.mode=['x','q','t'].includes(data.mode)?data.mode:'x';state.revealed=new Set(Array.isArray(data.revealed)?data.revealed:[]);state.marks=new Map(Array.isArray(data.marks)?data.marks:[]);state.streak=Number(data.streak)||0;
  state.locked=false;state.tutorialStep=0;state.bossIntroShown=true;render();startIdle();return true;
}
function save(){syncHeartRecovery();localStorage.setItem('clpHearts',state.hearts);localStorage.setItem('clpKibble',state.kibble);localStorage.setItem('clpHistory',JSON.stringify(state.history));localStorage.setItem('clpBossPhase',String(state.bossPhase))}
function hasTaiju(){return localStorage.getItem('clpTaijuJoined')==='1'}
function updateProgressiveUI(){
  const dock=$('hintDock');
  if(dock)dock.classList.toggle('hidden',!hasTaiju());
  updateModeCycle();
}
function renderCats(){
  const list=$('catsList');if(!list)return;
  const cards=[`<article class="cat-card"><div class="cat-card-icon">🐱</div><div><h3>ニャンじい</h3><small>テコちゃんの育て親・修行の先生</small><p>幼いころに迷子になったテコちゃんを助け、大きくなるまで育ててくれた恩人。旅とパズルに詳しく、困ったときには優しく道を示してくれる。</p></div></article>`];
  if(hasTaiju())cards.push(`<article class="cat-card unlocked"><div class="cat-card-icon">🐈‍⬛</div><div><h3>タイジュ</h3><small>まよい森の案内役・STAGE 50</small><p>まよい森で出会った大きなにゃんこ。迷子の小さな猫たちを守っていた。森の道に詳しく、仲間になったあとは「猫じゃらし」で安全な×を教えてくれる。</p></div></article>`);
  list.innerHTML=cards.join('');
}
function openCats(){renderCats();$('catsDlg').showModal()}

function renderBossBanner(){const banner=$('bossBanner');if(!banner)return;banner.classList.toggle('hidden',!isBossStage());document.body.classList.toggle('boss-stage',isBossStage());if(isBossStage()){const labels=['足あとを追う','しっぽの向こう側','迷子猫を守る大きなにゃんこ'];$('bossPhaseLabel').textContent=`第${state.bossPhase}フェーズ　${labels[state.bossPhase-1]}`;$('bossPhaseCount').textContent=`${state.bossPhase} / 3`;}}
function showBossIntro(){if(!isBossStage()||state.bossIntroShown)return;state.bossIntroShown=true;setTimeout(()=>show('まよい森の大きなにゃんこ','<div class="boss-dialog-art">🌲🐾🐈🌲</div><p><b>テコちゃん：</b> 森の奥から、大きな足あとが続いているニャン……。</p><p><b>大きなにゃんこ：</b> ここから先へ来るなら、迷子たちを見つける力を見せておくれ。</p><p>3つの盤面を解いて、大きなにゃんこの事情を確かめよう。</p>',[['ボスステージ開始','close']]),180)}
function record(action,id='',result=''){state.log.push(`${new Date().toLocaleTimeString()} | S${p().stage} | ${action} ${id} ${result}`);if(state.log.length>200)state.log.shift()}
function haptic(pattern){try{if(localStorage.getItem('clpVibrate')!=='0'&&navigator.vibrate)navigator.vibrate(pattern)}catch(e){}}
function travelComment(){const comments=['まずは行と列を見比べるニャン。','同じ色エリアに残ったマスを探すニャン。','焦らず、確定できるところから進めるニャン。','仲間の手掛かりが見つかりそうだニャン。'];return comments[p().stage%comments.length]}
function startIdle(){clearTimeout(state.idle);state.idle=setTimeout(()=>{if(p().tutorial)say('🐱','ニャンじい','迷ったときは、わしの光らせるマスをよく見るんじゃ。青は×、黄色は猫を開く合図じゃぞ。','left');else say('🐱','テコちゃん',travelComment(),'right')},17000)}
function resetBoard(preserveRun=false){state.drag.active=false;state.drag.visited=new Set();state.timers.forEach(clearTimeout);state.timers.clear();if(!isBossStage()){state.bossPhase=1;state.bossIntroShown=false;localStorage.setItem('clpBossPhase','1')}if(!preserveRun){state.score=0;state.mistakes=0;state.hintsUsed=0;state.totalFound=0}state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;state.tutorialStep=0;record('START');render();startIdle();showBossIntro()}
function say(face,name,text,side='left',enemy=false){$('talkFace').textContent=face;$('talkName').textContent=name;$('talkText').textContent=text;$('talk').className=`talk ${side}${enemy?' enemy':''}`}
function render(){let s=p();renderBossBanner();const guide=$('operationGuide');if(guide){guide.classList.toggle('hidden',!s.tutorial);guide.classList.toggle('compact',s.tutorial&&s.stage>=4)}$('scoreLabel').textContent=`評価 ${state.score} / 100`;$('stageLabel').innerHTML=isBossStage()?`STAGE 50<br><small>BOSS ${state.bossPhase}/3</small>`:isHagureStage()?`STAGE ${s.stage}<br><small>${hagureConfig().label}</small>`:s.bonus?`STAGE ${s.stage}<br><small>BONUS</small>`:s.hard?`STAGE ${s.stage}<br><small>HARD</small>`:`STAGE ${s.stage}`;$('panel').className='panel'+(s.hard?' hard':'')+(s.bonus?' bonus':'');updateProgressiveUI();$('historyBtn').classList.add('hidden');if(isHagureStage()){const hs=hagureStory();say(hs?hs.introFace:'🐱',hs?hs.introSpeaker:hagureConfig().label,hagureTalk(),hs&&hs.introSpeaker==='テコちゃん'?'right':'left',false);}else if(s.hard&&s.stage!==10)say('😼','はぐれにゃんこ','何か用かニャン？','right',true);else if(s.tutorial)say('🐱','ニャンじい',tutorialText(),'left');else say('🐱','テコちゃん',s.stage===11?'ここからが本当の旅の始まりニャン。ハートを大切にして、仲間とお母さんの手掛かりを探すニャン！':travelComment(),'right');renderLife();build();updateSpecialStageFx();updateHint()}
function stage1FoundId(){return Array.from(state.revealed)[0]||''}
function idsAround(id){if(!id)return[];const [r,c]=id.split('-').map(Number),out=[];for(let rr=Math.max(0,r-1);rr<=Math.min(p().size-1,r+1);rr++)for(let cc=Math.max(0,c-1);cc<=Math.min(p().size-1,c+1);cc++)if(rr!==r||cc!==c)out.push(`${rr}-${cc}`);return out}
function stage1AdjacentRemaining(){if(p().stage!==1||state.revealed.size!==1)return[];return idsAround(stage1FoundId()).filter(id=>!state.marks.has(id)&&!state.revealed.has(id))}
function stage1LineRemaining(){if(p().stage!==1||state.revealed.size!==1)return[];const id=stage1FoundId(),[r,c]=id.split('-').map(Number),out=[];for(let i=0;i<p().size;i++){for(const x of [`${r}-${i}`,`${i}-${c}`])if(x!==id&&!state.revealed.has(x)&&!state.marks.has(x)&&!out.includes(x))out.push(x)}return out}
function stage1ExclusionsRemaining(){if(p().stage!==1||state.revealed.size!==2)return[];const latest=Array.from(state.revealed).at(-1),[r,c]=latest.split('-').map(Number),reg=p().regions[r][c],out=[];for(let rr=0;rr<p().size;rr++)for(let cc=0;cc<p().size;cc++){const id=`${rr}-${cc}`;if(id===latest||state.revealed.has(id)||state.marks.has(id))continue;if(rr===r||cc===c||Math.abs(rr-r)<=1&&Math.abs(cc-c)<=1||p().regions[rr][cc]===reg)out.push(id)}return out}
function stage1HighlightIds(){if(p().stage!==1)return[];if(state.revealed.size===1){const around=stage1AdjacentRemaining();if(around.length)return around;const line=stage1LineRemaining();return line.length?line:['0-2']}if(state.revealed.size===2){const x=stage1ExclusionsRemaining();return x.length?x:['3-1']}if(state.revealed.size===3)return['2-3'];return[]}
function tutorialText(){let s=p();if(s.stage===10)return state.revealed.size===0?'これが最後の修行じゃ。今まで覚えたことを、一つずつ使って解いてみるんじゃ。':'落ち着いて続けるんじゃ。これまでの修行を思い出せば、きっと最後までたどり着けるぞい。';if(s.stage===1){
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
/* Ver.0.7.5: heart popover and Taiju hint flow */
/* Ver.0.7.8: interactive heart recovery panel */
let heartHelpTimer=0;
function heartRemainText(){
  syncHeartRecovery();
  if(state.hearts>=HEART_MAX)return 'ハートは満タンです';
  const base=Number(localStorage.getItem('clpHeartUpdatedAt')||Date.now());
  const remain=Math.max(0,HEART_RECOVERY_MS-(Date.now()-base));
  const mm=Math.floor(remain/60000),ss=Math.floor((remain%60000)/1000);
  return `次の回復まで ${mm}分${String(ss).padStart(2,'0')}秒`;
}
function heartHelpText(){
  const canRecover=state.hearts<HEART_MAX&&state.kibble>=HEART_KIBBLE_COST;
  const buttonLabel=state.hearts>=HEART_MAX?'ハートは満タンです':state.kibble<HEART_KIBBLE_COST?'カリカリが足りません':'カリカリ1個で♥1回復';
  return `<b>ハート ${state.hearts} / ${HEART_MAX}</b><br><span class="heart-countdown">${heartRemainText()}</span><br><span>30分ごとにハートが1個回復します。</span><br><span>カリカリ：${state.kibble}個</span><button type="button" class="heart-kibble-recover" ${canRecover?'':'disabled'}>${buttonLabel}</button>`;
}
function refreshHeartHelp(){const tip=document.querySelector('.heart-help-pop.open');if(!tip)return;const before=state.hearts;syncHeartRecovery();if(state.hearts!==before){save();renderLife();openHeartHelp();return}tip.innerHTML=heartHelpText()}
function openHeartHelp(){const box=$('lifeBox');if(!box)return;let tip=box.querySelector('.heart-help-pop');if(!tip){tip=document.createElement('span');tip.className='heart-help-pop';tip.setAttribute('role','dialog');box.appendChild(tip)}tip.innerHTML=heartHelpText();tip.classList.add('open');clearInterval(heartHelpTimer);heartHelpTimer=setInterval(refreshHeartHelp,1000)}
/* Ver.0.7.9: heart recovery click fix */
function toggleHeartHelp(e){
  if(e){
    e.preventDefault();e.stopPropagation();
    if(e.target.closest('.heart-kibble-recover')){recoverHeartFromPanel();return}
  }
  const tip=document.querySelector('.heart-help-pop');
  if(tip&&tip.classList.contains('open'))closeHeartHelp();else openHeartHelp();
}
function closeHeartHelp(){const tip=document.querySelector('.heart-help-pop.open');if(tip)tip.classList.remove('open');clearInterval(heartHelpTimer);heartHelpTimer=0}
function recoverHeartFromPanel(){
  syncHeartRecovery();
  if(state.hearts>=HEART_MAX||state.kibble<HEART_KIBBLE_COST){refreshHeartHelp();return}
  state.kibble-=HEART_KIBBLE_COST;state.hearts++;
  if(state.hearts>=HEART_MAX)localStorage.removeItem('clpHeartUpdatedAt');else startHeartTimerAfterLoss();
  state.locked=false;save();saveBoard();renderLife();openHeartHelp();haptic(25);
}
function renderLife(){syncHeartRecovery();let b=$('lifeBox');b.innerHTML='';if(p().tutorial||p().bonus)b.innerHTML='<span class="training">ニャンじいのチュートリアル中は、ハートは減りません</span>';else{b.classList.add('life-help-host');b.setAttribute('tabindex','0');b.setAttribute('aria-label','ハート回復の説明を表示');b.innerHTML='<label>LIFE</label>';for(let i=0;i<HEART_MAX;i++){let h=document.createElement('span');h.className='life'+(i<state.hearts?'':' empty');h.textContent=i<state.hearts?'♥':'♡';b.appendChild(h)}b.insertAdjacentHTML('beforeend',`<span class="kibble">カリカリ ${state.kibble}</span><span class="heart-help-pop" role="dialog">${heartHelpText()}</span>`);b.onclick=toggleHeartHelp;b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){toggleHeartHelp(e)}}}}
function markIcon(type,small=false){
  const cls=`mark-symbol mark-${type}${small?' mark-small':''}`;
  const paths={
    x:'<path d="M17 17 L47 47 M47 17 L17 47"/>',
    q:'<path d="M21 24 C22 13 42 10 47 21 C52 33 39 36 33 42 L33 46"/><circle cx="33" cy="54" r="2.8" fill="currentColor" stroke="none"/>',
    t:'<path d="M32 14 Q33 14 34 16 L51 47 Q52 50 48 50 L16 50 Q12 50 14 47 L30 16 Q31 14 32 14 Z"/>'
  };
  return `<span class="${cls}"><svg viewBox="0 0 64 64" aria-hidden="true"><g class="mark-outline">${paths[type]||paths.x}</g><g class="mark-core">${paths[type]||paths.x}</g></svg></span>`;
}
function build(){let s=p(),n=s.size,preservedFx=board.querySelector('.special-fx');if(preservedFx)preservedFx.remove();board.innerHTML='';board.style.gridTemplateColumns=`repeat(${n},minmax(0,1fr))`;board.style.gridTemplateRows=`repeat(${n},minmax(0,1fr))`;board.style.setProperty('--gap',n<=4?'5px':n<=6?'3px':'2px');board.style.setProperty('--pad',n<=4?'6px':'3px');board.style.setProperty('--radius',n<=4?'11px':n<=6?'6px':'4px');$('coordTop').style.gridTemplateColumns=`repeat(${n},1fr)`;$('coordTop').innerHTML=Array.from({length:n},(_,i)=>`<span>${i+1}</span>`).join('');$('coordSide').style.gridTemplateRows=`repeat(${n},1fr)`;$('coordSide').innerHTML=Array.from({length:n},(_,i)=>`<span>${String.fromCharCode(65+i)}</span>`).join('');let target=firstLogicalTarget();for(let r=0;r<n;r++)for(let c=0;c<n;c++){let id=key(r,c),b=document.createElement('button'),m=state.marks.get(id);b.className=`tile r${s.regions[r][c]}`+(state.revealed.has(id)?' revealed':'')+(state.debugAnswer&&answer(id)?' hinting':'')+(((s.stage===1&&state.revealed.size===0&&id===target)||(s.stage===3&&id===stage3Target()))?' tutorial-target':'')+(stage1HighlightIds().includes(id)?' tutorial-focus':'');b.dataset.id=id;if(state.revealed.has(id))b.innerHTML='<span>🐱</span>';else if(m)b.innerHTML=markIcon(m);b.onpointerdown=e=>pointerStart(e,id);board.appendChild(b)}if(preservedFx)board.appendChild(preservedFx)}
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
  saveBoard();
  haptic(12);
  build();updateSpecialStageFx();
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
function tap(id){clearTimeout(state.idle);const hinted=board.querySelector(`[data-id="${id}"].hint-safe-x`);if(hinted&&state.mode==='x')setTimeout(clearHintGlow,0);if(!p().tutorial&&!p().bonus&&state.hearts<=0){heartZero();return}if(state.locked||state.revealed.has(id))return;if(state.timers.has(id)){clearTimeout(state.timers.get(id));state.timers.delete(id);openTile(id)}else state.timers.set(id,setTimeout(()=>{state.timers.delete(id);state.marks.get(id)===state.mode?state.marks.delete(id):state.marks.set(id,state.mode);record('MARK',id,state.mode);saveBoard();haptic(18);build();updateSpecialStageFx();if(p().tutorial)say('🐱','ニャンじい',tutorialText(),'left');startIdle()},270))}
function answer(id){let [r,c]=id.split('-').map(Number);return p().solution[r]===c}
function openTile(id){state.marks.delete(id);if(answer(id)){state.revealed.add(id);state.totalFound++;updateRunScore();saveBoard();state.streak++;record('OPEN',id,'OK');haptic([45,35,70]);goodToast(['いいね！','すごい！','やったニャン！','かんぺき！'][Math.min(3,state.streak-1)]);build();updateSpecialStageFx();if(p().tutorial)say('🐱','ニャンじい',tutorialText(),'left');if(state.revealed.size===p().size)complete()}else{state.streak=0;state.mistakes++;record('OPEN',id,'MISS');haptic([90,45,90,45,120]);if(!(p().tutorial||p().bonus)){state.hearts=Math.max(0,state.hearts-1);startHeartTimerAfterLoss();save();saveBoard();renderLife()}failToast();if(state.hearts===0&&!p().tutorial&&!p().bonus)heartZero()}startIdle()}
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
  const dock=$('hintDock');if(!dock)return;
  const joined=hasTaiju();dock.classList.toggle('hidden',!joined);
  document.querySelectorAll('[data-hint]').forEach(button=>{
    const type=button.dataset.hint;
    const unlocked=joined&&type==='toy';
    button.classList.toggle('hidden',!unlocked);
    button.disabled=!unlocked;
    if(unlocked){button.innerHTML='<span class="hint-info" data-info="toy" role="button" aria-label="タイジュの道しるべの説明">?</span><span class="hint-icon">🪶</span><b>猫じゃらし</b><small>タイジュの道しるべ・1個</small>';button.setAttribute('aria-label','猫じゃらし。タップ後、中央の羽をタップして使う');}
  });
}

function hintMenu(){if(p().tutorial||p().bonus){useHint(3);return}show('ヒントを選ぶ',`<p>所持カリカリ：<b>${state.kibble}</b></p><p>猫じゃらし：注目エリア（1個）<br>またたび：正解位置を光らせる（2個）<br>ネコ缶：猫を1匹開く（3個）</p>`,[['猫じゃらし 1','h1'],['またたび 2','h2'],['ネコ缶 3','h3'],['閉じる','close']])}
function useHint(level){let cost=p().tutorial||p().bonus?0:level;let id=Array.from({length:p().size},(_,r)=>key(r,p().solution[r])).find(x=>!state.revealed.has(x));if(!id)return;if(state.kibble<cost){show('カリカリが足りません','<p>ボーナスステージなどでカリカリを集められます。</p>',[['閉じる','close']]);return}state.kibble-=cost;if(!(p().tutorial||p().bonus))state.hintsUsed++;save();if(level===3&&!p().tutorial&&!p().bonus){openTile(id)}else{let t=board.querySelector(`[data-id="${id}"]`);t.classList.add('hinting');setTimeout(()=>t.classList.remove('hinting'),3500)}record('HINT',id,level);updateHint()}
function bossScene(title,body,buttons,kind='dialogue'){
  show(title,`<div class="boss-story ${kind}">${body}</div>`,buttons);
}
function showBossTruth(){
  bossScene('まよい森の大きなにゃんこ',`
    <div class="speech-row left"><div class="speaker-icon">🐈‍⬛</div><div class="speech-wrap"><b>大きなにゃんこ</b><p>驚かせてすまなかったね。森で迷った小さな猫たちを、ここで守っていたんだ。</p></div></div>
    <div class="speech-row right"><div class="speaker-icon">🐱</div><div class="speech-wrap"><b>テコちゃん</b><p>そうだったんだニャン。小さな猫たちを守ってくれて、ありがとうニャン！</p></div></div>`,[['話を聞く','bossReunion']]);
}
function showBossReunion(){
  bossScene('会えたね、よかったね',`
    <div class="speech-row left"><div class="speaker-icon">🐱🐱</div><div class="speech-wrap"><b>小さな猫たち</b><p>大きなにゃんこが、ずっとそばにいてくれたニャン！</p></div></div>
    <div class="speech-row right"><div class="speaker-icon">🐱</div><div class="speech-wrap"><b>テコちゃん</b><p>みんな無事でよかったニャン。会えたね、よかったね！</p></div></div>
    <div class="speech-row left"><div class="speaker-icon">🐈‍⬛</div><div class="speech-wrap"><b>大きなにゃんこ</b><p>ぼくの名前はタイジュ。よければ、森の道を案内するよ。</p></div></div>
    <div class="speech-row right"><div class="speaker-icon">🐱</div><div class="speech-wrap"><b>テコちゃん</b><p>ありがとうだニャン、タイジュ！ これからよろしくニャン！</p></div></div>`,[['つづきへ','bossResult']]);
}
function showBossResult(){
  bossScene('第1章クリア',`
    <div class="narration-card">誤解が解け、タイジュは迷い森の案内役として、テコちゃんの旅に力を貸してくれることになりました。</div>
    <div class="result-card"><small>STAGE 50　BOSS CLEAR</small>${scoreBreakdown()}<span>${state.score===100?'金枠・完全クリア':'クリア'}</span><p>新しい仲間　<b>タイジュ</b><br><small>「猫じゃらし」が使えるようになりました</small></p></div>`,[['第1章クリア','close']],'result');
}
function showHagureStoryResult(nextButtons){
  const hs=hagureStory();if(!hs){show('STAGE CLEAR',`<p>ステージをクリアしました。</p>${scoreBreakdown()}`,nextButtons);return}
  let page=0;
  const draw=()=>{const row=hs.result[page],last=page===hs.result.length-1;const body=row.speaker==='ナレーション'?`<div class="narration-card">${row.text}</div>`:`<div class="speech-row ${row.speaker==='テコちゃん'?'right':'left'}"><div class="speaker-icon">${row.face}</div><div class="speech-wrap"><b>${row.speaker}</b><p>${row.text}</p></div></div>`;show(hs.resultTitle,body,last?nextButtons:[['次へ','hagureStoryNext']]);window.clpHagureNext=()=>{page++;draw()}}
  draw();
}
function finishResult(){
  if(isBossStage()){
    if(state.bossPhase<3){
      const next=state.bossPhase+1;
      const messages=['足あとが森の奥へ続いている。次は、しっぽに隠された手掛かりを探すニャン。','大きなにゃんこの向こうから、小さな鳴き声が聞こえるニャン。最後の盤面へ進もう。'];
      show(`ボスフェーズ ${state.bossPhase} クリア`,`<p><b>テコちゃん：</b> ${messages[state.bossPhase-1]}</p><p>次はフェーズ ${next} / 3 です。</p>`,[['次のフェーズ','bossNext']]);
      return;
    }
    state.score=finalScore();$('scoreLabel').textContent=`評価 ${state.score} / 100`;
    state.history[50]=Math.max(state.history[50]||0,state.score);
    localStorage.setItem('clpTaijuJoined','1');localStorage.removeItem('clpBossPhase');state.bossPhase=1;save();
    showBossTruth();
    return;
  }
  state.score=finalScore();$('scoreLabel').textContent=`評価 ${state.score} / 100`;state.history[p().stage]=Math.max(state.history[p().stage]||0,state.score);let tutorialGift='';if(p().stage===10&&localStorage.getItem('clpTutorialGift')!=='1'){state.kibble+=10;localStorage.setItem('clpTutorialGift','1');tutorialGift='<p><b>ニャンじい：</b> 旅がつらくなったら、このカリカリを食べるんじゃよ。</p><p><b>テコちゃん：</b> ありがとう、ニャンじい！ カリカリを10個受け取ったニャン！</p>';}if(p().bonus)state.kibble+=3;save();let line=p().tutorial?['よくできたのう、テコちゃん。','見事じゃ。仲間をみんな見つけたぞい。','また一つ、修行を終えたのう。'][p().stage%3]:['仲間を見つけたニャン！','無事に再会できたニャン！','みんな見つかったニャン！'][p().stage%3];let speaker=p().tutorial?'ニャンじい':'テコちゃん';let extra=p().bonus?'<p>カリカリを3個獲得しました！</p>':'';let finish=p().stage===10?'<p>よく覚えたのう、テコちゃん。基本の修行はこれで終わりじゃ。ここから先は、まだ見ぬ仲間たちと、お母さんの手掛かりが待っておるぞい。</p>':'';if(isHagureStage()){speaker=hagureConfig().label;line=hagureConfig().clear;finish='<p class="hagure-note">このはぐれにゃんこは仲間にはならず、旅の途中でまたどこかへ向かっていきました。</p>';}let result=()=>{const buttons=state.i<STAGES.length-1?[['次のステージ','next']]:[['Ver.0.7.9 完了','close']];if(isHagureStage()){showHagureStoryResult(buttons);return}show(hagureClearTitle(),`<p><b>${speaker}：</b> ${line}</p>${scoreBreakdown()}${extra}${tutorialGift}${finish}`,buttons)};if(p().hard&&p().stage!==10&&!isHagureStage())runElite(result);else result()
}
function celebrateBoard(done){
  board.classList.add('board-complete');
  board.querySelectorAll('.tile.revealed span').forEach((cat,i)=>{cat.style.animationDelay=`${i*70}ms`;cat.classList.add('cat-celebrate')});
  setTimeout(()=>{board.classList.remove('board-complete');board.querySelectorAll('.cat-celebrate').forEach(x=>x.classList.remove('cat-celebrate'));done()},1850)
}
function complete(){state.locked=true;clearBoardSave();haptic([40,30,60,40,130]);goodToast('やったニャン！');celebrateBoard(finishResult)}
function runElite(done){let e=document.createElement('div');e.className='elite-run';e.textContent='😼💨';document.body.appendChild(e);setTimeout(()=>e.remove(),1500);setTimeout(done,1600)}
function heartZero(){syncHeartRecovery();if(state.hearts>0){state.locked=false;render();return}state.locked=true;show('ハートがなくなりました',`<p>ハートは30分ごとに1個回復します。</p><p>${heartTimeText()}</p><p>カリカリ1個を使うと、ハートを1個すぐ回復できます。</p>`,[['カリカリ1個で♥1回復','recoverKibble'],['タイトルへ戻る','title'],['DEBUG：全回復','recover']])}
function rules(){show('ルール',`<details open><summary><b>基本ルール</b></summary><ul><li>各行・各列・各色エリアに猫は1匹</li><li>猫同士は周囲8マスで隣り合わない</li></ul></details><details><summary><b>操作</b></summary><p><b>1回タップ：</b>選択中の印を付ける<br><b>素早く2回タップ：</b>猫のマスを開く<br><b>なぞる：</b>連続で×を付ける</p><p>MARKボタンをタップすると、× → ？ → △の順に切り替わります。△は仮置き推理用です。</p></details>`,[['閉じる','close']])}
function show(title,body,btns){$('dlgTitle').textContent=title;$('dlgBody').innerHTML=body;$('dlgActions').innerHTML='';btns.forEach(([text,a])=>{let b=document.createElement('button');b.className='primary';b.textContent=text;b.onclick=()=>{if(a==='hagureStoryNext'){dlg.close();if(window.clpHagureNext)window.clpHagureNext();return}if(a==='useToy'){dlg.close();castToyHint();return}if(/^h[123]$/.test(a)){dlg.close();useHint(Number(a[1]));return}dlg.close();if(a==='next'){state.i++;resetBoard()}if(a==='bossNext'){state.bossPhase=Math.min(3,state.bossPhase+1);save();resetBoard(true)}if(a==='bossTruth'){showBossTruth()}if(a==='bossReunion'){showBossReunion()}if(a==='bossResult'){showBossResult()}if(a==='recover'){state.hearts=HEART_MAX;state.locked=false;localStorage.removeItem('clpHeartUpdatedAt');save();render()}if(a==='recoverKibble'){if(state.kibble>=HEART_KIBBLE_COST&&state.hearts<HEART_MAX){state.kibble-=HEART_KIBBLE_COST;state.hearts++;state.locked=false;if(state.hearts>=HEART_MAX)localStorage.removeItem('clpHeartUpdatedAt');save();saveBoard();render()}else{show('回復できません',state.kibble<HEART_KIBBLE_COST?'<p>カリカリが足りないニャン。</p>':'<p>ハートは満タンです。</p>',[['閉じる','close']])}}if(a==='title'){showTitle()}if(a==='resetStage'){clearBoardSave();state.score=0;state.mistakes=0;state.hintsUsed=0;state.totalFound=0;state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;render();saveBoard()}if(a==='fullReset'){completeReset()}};$('dlgActions').appendChild(b)});dlg.showModal()}
function devUnlockedTo(){return Math.max(1,Math.min(STAGES.length,Number(localStorage.getItem('clpDevUnlockedTo')||1)))}
function isStageUnlocked(stageNo){return stageNo===1||Boolean(state.history[stageNo-1])||stageNo<=devUnlockedTo()}
function specialStageLabel(stageNo){if(stageNo===50)return 'BOSS';if([20,30,40].includes(stageNo))return 'はぐれにゃんこ';return ''}
window.CLPDevUnlockToStage=function(stageNo=STAGES.length){const target=Math.max(1,Math.min(STAGES.length,Number(stageNo)||1));localStorage.setItem('clpDevUnlockedTo',String(target));goodToast(`STAGE ${target}まで開発用解放`);history();return target};
window.CLPDevUnlockAllStages=function(){return window.CLPDevUnlockToStage(STAGES.length)};
window.CLPDevResetStageProgress=function(){localStorage.removeItem('clpDevUnlockedTo');state.history={};save();state.i=0;resetBoard();goodToast('進行データを初期化しました');return true};
function history(){
 let g=$('historyGrid');g.innerHTML='';
 const groups=[
  ['チュートリアル',1,10],
  ['第1章・まよい森',11,50]
 ];
 groups.forEach(([title,a,z])=>{
  let wrap=document.createElement('div');wrap.className='history-section';
  for(let k=a;k<=Math.min(z,STAGES.length);k++){
   if(!isStageUnlocked(k))continue;
   let b=document.createElement('button'),s=STAGES[k-1],score=Number(state.history[k]||0),special=specialStageLabel(k);
   const rank=score===100?'gold':score>=90?'silver':score>=80?'bronze':'';
   b.className=(rank?rank+' ':'')+(score?'cleared':'unplayed');
   b.innerHTML=`<b>${k}</b><small>${s.size}×${s.size}</small><em>${score?score:'－'}</em>${score===100?`<span class="gold-trail" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>`:''}`;b.title=`STAGE ${k}・${s.size}×${s.size}${special?'・'+special:''}・${score?score+'点':'未クリア'}`;
   b.onclick=()=>{$('historyDlg').close();clearBoardSave();state.i=k-1;resetBoard();saveBoard()};wrap.appendChild(b);
  }
  if(!wrap.children.length)return;
  let h=document.createElement('h3');h.className='history-heading';h.textContent=title;g.appendChild(h);g.appendChild(wrap);
 });
 if(!g.children.length)g.innerHTML='<p class="history-empty">ゲームを始めるとステージが表示されます</p>';
 $('historyDlg').showModal();
}

let storyIndex=0;function showStory(reset=false){if(reset)storyIndex=0;let s=STORY[storyIndex];$('storyArt').textContent=s[1];$('storyPage').textContent=`${storyIndex+1} / ${STORY.length}`;$('storyTitle').textContent=s[0];$('storyText').textContent=s[2];$('storyNext').textContent=storyIndex===STORY.length-1?'修行を始める':'次へ';$('storyDlg').showModal()}$('storyNext').onclick=()=>{if(storyIndex<STORY.length-1){storyIndex++;$('storyDlg').close();showStory()}else{$('storyDlg').close();localStorage.setItem('clpStorySeen','1')}};
function spendKibble(cost){if(p().tutorial||p().bonus)return true;if(state.kibble<cost){show('カリカリが足りません','<p>ボーナスステージでカリカリを集めるニャン。</p>',[['閉じる','close']]);return false}state.kibble-=cost;save();renderLife();return true}
function registerHintUse(){if(!(p().tutorial||p().bonus)){state.hintsUsed++;record('HINT_USED','',state.hintsUsed)}}
function clearHintGlow(){board.querySelectorAll('.hinting,.hint-focus,.hint-safe-x,.clp-hint-x,.clp-hint-cat').forEach(x=>x.classList.remove('hinting','hint-focus','hint-safe-x','clp-hint-x','clp-hint-cat'));document.body.classList.remove('hint-casting');if(window.CLPRefreshHintColors)window.CLPRefreshHintColors()}
/* Ver.0.7.6: tactile toy confirmation */
function closeToyReady(){const layer=document.getElementById('toyReadyLayer');if(layer)layer.remove()}
function showToyReady(){
  closeToyReady();
  const layer=document.createElement('div');layer.id='toyReadyLayer';layer.className='toy-ready-layer';
  layer.innerHTML='<button type="button" class="toy-ready-feather" aria-label="猫じゃらしを使う"><span>🪶</span><small>タップして使う</small></button>';
  layer.onclick=e=>{if(e.target===layer)closeToyReady()};
  const feather=layer.querySelector('.toy-ready-feather');
  feather.onclick=e=>{e.preventDefault();e.stopPropagation();closeToyReady();castToyHint()};
  document.body.appendChild(layer);requestAnimationFrame(()=>layer.classList.add('show'));
}
/* Ver.0.7.7: valid toy target and centered mode mark */
function validToyStep(){
  let step=window.CLPLogic.safeXStep(p(),state.revealed,state.marks);
  const isEmpty=id=>{if(!id||state.revealed.has(id))return false;const [r,c]=id.split('-').map(Number);return Number.isInteger(r)&&Number.isInteger(c)&&p().solution[r]!==c&&state.marks.get(id)!=='x'};
  if(step&&isEmpty(step.target))return step;
  for(let r=0;r<p().size;r++)for(let c=0;c<p().size;c++){const id=`${r}-${c}`;if(isEmpty(id))return {target:id,message:'青く光るマスには猫がいないニャン。×印をつけておこう。'}}
  return null;
}
function castToyHint(){
  clearHintGlow();
  const step=validToyStep();
  if(!step){show('猫じゃらし','<p>案内できる未確定の空きマスがないニャン。カリカリは消費しないニャン。</p>',[['閉じる','close']]);return}
  if(!spendKibble(window.CLPHints.COST.toy))return;
  registerHintUse();saveBoard();document.body.classList.add('hint-casting');
  setTimeout(()=>{document.body.classList.remove('hint-casting');const target=board.querySelector(`[data-id="${step.target}"]`);if(target){target.classList.add('hint-safe-x','clp-hint-x')}say('🐈‍⬛','タイジュ','青く光るマスには猫がいないニャン。×印をつけておこう。','left');record('HINT_SAFE_X',step.target,'toy');if(window.CLPRefreshHintColors)window.CLPRefreshHintColors();setTimeout(clearHintGlow,10000)},420);
}
function directHint(type){  
  const button=document.querySelector(`[data-hint="${type}"]`);
  if(!button||button.disabled)return;
  clearHintGlow();
  const cost=window.CLPHints.COST[type];

  if(type==='toy'){showToyReady();return;}

  if(type==='matatabi'){
    const step=window.CLPLogic.nextStep(p(),state.revealed,state.marks);
    if(!step){
      show('またたび','<p>今は解法エンジンが説明できる有効な一手を見つけられなかったニャン。カリカリは消費しないニャン。</p>',[['閉じる','close']]);
      return;
    }
    if(!spendKibble(cost))return;
    registerHintUse();
    if(step.kind==='only'){
      const target=board.querySelector(`[data-id="${step.target}"]`);
      if(target)target.classList.add('hinting');
    }else{
      const target=board.querySelector(`[data-id="${step.target}"]`);
      if(target)target.classList.add('hint-safe-x');
    }
    (step.focus||[]).forEach(id=>{const tile=board.querySelector(`[data-id="${id}"]`);if(tile)tile.classList.add('hint-focus')});
    say(p().tutorial?'🐱':'🐱',p().tutorial?'ニャンじい':'テコちゃん',step.message,p().tutorial?'left':'right');
    record('HINT_VALID_MOVE',step.target,'matatabi');
    saveBoard();setTimeout(clearHintGlow,5500);
    return;
  }

  if(type==='can'){
    const answer=Array.from({length:p().size},(_,r)=>`${r}-${p().solution[r]}`).find(id=>!state.revealed.has(id));
    if(!answer)return;
    if(!spendKibble(cost))return;
    registerHintUse();
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
    registerHintUse();
    state.marks.delete(wrong[0]);saveBoard();
    record('HINT_FIX_X',wrong[0],'paw');
    build();updateSpecialStageFx();
    show('肉球チェック','<p>間違った×を1つ直したニャン。</p>',[['閉じる','close']]);
  }
}
function showTitle(){
  const t=$('titleScreen');if(!t)return;
  t.classList.remove('hidden');
  const played=Boolean(localStorage.getItem('clpStorySeen'))||Object.keys(state.history||{}).length>0;$('titleContinue').textContent=played?'つづきから':'ゲームを始める';$('titleStages').classList.toggle('hidden',!played);$('titleNew').classList.toggle('hidden',!played);
}
function hideTitle(){const t=$('titleScreen');if(t)t.classList.add('hidden')}
function completeReset(){
  const keepVibrate=localStorage.getItem('clpVibrate');
  localStorage.clear();
  if(keepVibrate!==null)localStorage.setItem('clpVibrate',keepVibrate);
  location.reload();
}
function startNatureBreeze(){
  clearInterval(window.clpNatureBreezeTimer);
  window.clpNatureBreezeTimer=setInterval(()=>{
    if(document.hidden||localStorage.getItem('clpSpecialFxWeak')==='1'||document.querySelector('dialog[open]')||!$('titleScreen').classList.contains('hidden')||state.locked)return;
    const tiles=[...board.querySelectorAll('.tile:not(.revealed)')].filter(tile=>!tile.querySelector('.mark-x,.mark-q,.mark-t'));
    tiles.forEach(tile=>{const [r,c]=(tile.dataset.id||'0-0').split('-').map(Number);const diagonal=(r+c)*85;setTimeout(()=>{tile.classList.add('nature-breeze');setTimeout(()=>tile.classList.remove('nature-breeze'),1450)},diagonal)});
  },10000);
}
function openSettings(){show('設定',`<div class="settings-list"><button id="setReset">このステージを最初から</button><button id="setRules">ルールを見る</button><button id="setTitle">タイトルへ戻る</button><button id="setFullReset" class="danger-soft">データを完全初期化</button><label><input id="setVibrate" type="checkbox" ${localStorage.getItem('clpVibrate')==='0'?'':'checked'}> 振動を使う</label></div>`,[['閉じる','close']]);setTimeout(()=>{const a=$('setReset'),b=$('setRules'),d=$('setTitle'),full=$('setFullReset'),v=$('setVibrate');a&&(a.onclick=()=>{dlg.close();show('確認','<p>現在の盤面を最初からやり直しますか？ ハートは消費しません。</p>',[['やり直す','resetStage'],['キャンセル','close']])});b&&(b.onclick=()=>{dlg.close();rules()});d&&(d.onclick=()=>{dlg.close();showTitle()});full&&(full.onclick=()=>{dlg.close();show('完全初期化','<p>ステージ履歴、仲間、ヒント、カリカリ、ハート、物語の既読状態をすべて消してStage 1へ戻します。</p>',[['すべて初期化','fullReset'],['キャンセル','close']])});v&&(v.onchange=()=>localStorage.setItem('clpVibrate',v.checked?'1':'0'))},0)}
function updateModeCycle(){const b=$('modeCycle');if(!b)return;const names={x:'×マーク',q:'？マーク',t:'△マーク'};b.innerHTML=markIcon(state.mode,true);b.dataset.mode=state.mode;b.setAttribute('aria-label',`${names[state.mode]||'×マーク'}。タップで切り替え`)}
function setMode(m){state.mode=m;updateModeCycle();saveBoard()}
function cycleMode(){const order=['x','q','t'],i=Math.max(0,order.indexOf(state.mode));setMode(order[(i+1)%order.length]);haptic(12)}
$('stageSelectBtn').onclick=history;$('titleContinue').onclick=()=>{hideTitle();syncHeartRecovery();save();const resumed=restoreBoard();if(!resumed){resetBoard();saveBoard()}if(!localStorage.getItem('clpStorySeen'))showStory()};$('titleStages').onclick=()=>{hideTitle();history()};$('titleSettings').onclick=openSettings;$('titleNew').onclick=()=>show('最初から始める','<p>すべての進行を消してStage 1から始めますか？</p>',[['最初から','fullReset'],['キャンセル','close']]);$('modeCycle').onclick=cycleMode;$('historyBtn').onclick=history;$('historyClose').onclick=()=>$('historyDlg').close();$('catsBtn').onclick=openCats;$('catsClose').onclick=()=>$('catsDlg').close();$('catsDlg').addEventListener('click',e=>{if(e.target===$('catsDlg'))$('catsDlg').close()});
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


document.title=document.title.replace(/Ver\.0\.7\.[0-9]+/g,'Ver.0.7.9');document.querySelectorAll('body *').forEach(el=>{if(el.children.length===0&&/Ver\.0\.7\.[0-9]+/.test(el.textContent))el.textContent=el.textContent.replace(/Ver\.0\.7\.[0-9]+/g,'Ver.0.7.9')});syncHeartRecovery();save();resetBoard();installLeafSwipe();installLeafTilt();startNatureBreeze();showTitle();setInterval(()=>{const before=state.hearts;if(syncHeartRecovery()>0||state.hearts!==before){save();renderLife()}},60000);
const settingsButton=$('settingsBtn');if(settingsButton){settingsButton.disabled=false;settingsButton.onclick=openSettings;}document.querySelectorAll('[data-hint]').forEach(b=>b.onclick=()=>directHint(b.dataset.hint));

const hintDescriptions={toy:['タイジュの道しるべ','猫じゃらしを使うと、猫がいないと確定できるマスを1か所、青く光らせます。青いマスには×印を付けます。消費はカリカリ1個です。'],matatabi:['またたび','盤面を論理的に前進させる有効な一手を、理由付きで教えます。猫を開く手や安全な×など、状況に合う一手を案内します。'],can:['ネコ缶','正解の猫を1匹、その場で自動的に開く強力なヒントです。'],paw:['肉球チェック','間違って付けた×を1つ見つけて直します。間違いがなければ消費しません。']};
document.addEventListener('click',e=>{const info=e.target.closest('[data-info]');if(!info)return;e.preventDefault();e.stopPropagation();const d=hintDescriptions[info.dataset.info];if(d)show(d[0],`<p>${d[1]}</p>`,[['閉じる','close']])});

$('historyDlg').addEventListener('click',e=>{if(e.target===$('historyDlg'))$('historyDlg').close()});document.addEventListener('click',e=>{const recover=e.target.closest('.heart-kibble-recover');if(recover){e.preventDefault();e.stopPropagation();recoverHeartFromPanel();return}const box=$('lifeBox');if(box&&!box.contains(e.target))closeHeartHelp()});
