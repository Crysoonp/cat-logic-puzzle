(function(){
  'use strict';
  const BOUNDARIES=Object.freeze({
    progress:Object.freeze(['hearts','kibble','history','bossPhase']),
    board:Object.freeze(['i','score','mistakes','hintsUsed','totalFound','mode','revealed','marks','streak','locked']),
    runtime:Object.freeze(['timers','idle','log','drag','tutorialStep','debugAnswer','bossIntroShown'])
  });
  function numberFromStorage(key,fallback){
    const value=Number(window.CLPStorage.getItem(key));
    return Number.isFinite(value)?value:fallback;
  }
  function historyFromStorage(){
    const value=window.CLPStorage.getJSON(window.CLPStorage.KEYS.history,{});
    return value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  }
  function createInitialState(){
    return {
      i:0,hearts:numberFromStorage(window.CLPStorage.KEYS.hearts,5),
      kibble:numberFromStorage(window.CLPStorage.KEYS.kibble,0),
      score:0,mistakes:0,hintsUsed:0,totalFound:0,mode:'x',
      revealed:new Set(),marks:new Map(),timers:new Map(),locked:false,streak:0,
      history:historyFromStorage(),log:[],tutorialStep:0,idle:null,debugAnswer:false,
      bossPhase:Math.max(1,Math.min(3,numberFromStorage(window.CLPStorage.KEYS.bossPhase,1))),
      bossIntroShown:false,
      drag:{active:false,moved:false,pointerId:null,startX:0,startY:0,startId:'',action:'add',visited:new Set()}
    };
  }
  function boardSnapshot(state){
    return {version:1,stageIndex:state.i,bossPhase:state.bossPhase,score:state.score,
      mistakes:state.mistakes,hintsUsed:state.hintsUsed,totalFound:state.totalFound,
      mode:state.mode,revealed:[...state.revealed],marks:[...state.marks.entries()],
      streak:state.streak,savedAt:Date.now()};
  }
  function finiteNumber(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function validCellId(value,size){
    if(typeof value!=='string'||!/^\d+-\d+$/.test(value))return false;
    const parts=value.split('-').map(Number);
    return parts.length===2&&parts.every(Number.isInteger)&&parts[0]>=0&&parts[1]>=0&&parts[0]<size&&parts[1]<size;
  }
  function restoreBoardSnapshot(raw,stages){
    if(!raw||typeof raw!=='object'||raw.version!==1||!Array.isArray(stages))return null;
    if(!Number.isInteger(raw.stageIndex)||raw.stageIndex<0||raw.stageIndex>=stages.length)return null;
    const stage=stages[raw.stageIndex];
    if(!stage||!Number.isInteger(stage.size)||stage.size<1)return null;
    const revealed=Array.isArray(raw.revealed)?raw.revealed.filter(id=>validCellId(id,stage.size)):[];
    const marks=[];
    if(Array.isArray(raw.marks))raw.marks.forEach(entry=>{
      if(!Array.isArray(entry)||entry.length!==2)return;
      const id=entry[0],mark=entry[1];
      if(validCellId(id,stage.size)&&['x','q','t'].includes(mark)&&!revealed.includes(id))marks.push([id,mark]);
    });
    return {
      stageIndex:raw.stageIndex,bossPhase:Math.max(1,Math.min(3,finiteNumber(raw.bossPhase,1))),
      score:Math.max(0,finiteNumber(raw.score,0)),mistakes:Math.max(0,finiteNumber(raw.mistakes,0)),
      hintsUsed:Math.max(0,finiteNumber(raw.hintsUsed,0)),totalFound:Math.max(0,finiteNumber(raw.totalFound,0)),
      mode:['x','q','t'].includes(raw.mode)?raw.mode:'x',revealed:new Set(revealed),marks:new Map(marks),
      streak:Math.max(0,finiteNumber(raw.streak,0))
    };
  }
  function applyBoardSnapshot(state,snapshot){
    if(!snapshot)return false;
    state.i=snapshot.stageIndex;state.bossPhase=snapshot.bossPhase;state.score=snapshot.score;
    state.mistakes=snapshot.mistakes;state.hintsUsed=snapshot.hintsUsed;state.totalFound=snapshot.totalFound;
    state.mode=snapshot.mode;state.revealed=snapshot.revealed;state.marks=snapshot.marks;state.streak=snapshot.streak;
    state.locked=false;state.tutorialStep=0;state.bossIntroShown=true;return true;
  }
  function resetBoardState(state,options={}){
    const preserveRun=options.preserveRun===true;
    const preserveBoss=options.preserveBoss===true;
    state.drag.active=false;state.drag.moved=false;state.drag.pointerId=null;state.drag.startId='';state.drag.visited=new Set();
    state.timers.forEach(clearTimeout);state.timers.clear();clearTimeout(state.idle);state.idle=null;
    if(!preserveRun){state.score=0;state.mistakes=0;state.hintsUsed=0;state.totalFound=0;}
    if(!preserveBoss){state.bossPhase=1;state.bossIntroShown=false;}
    state.revealed.clear();state.marks.clear();state.locked=false;state.streak=0;state.tutorialStep=0;
    return state;
  }
  window.CLPGameState=Object.freeze({BOUNDARIES,createInitialState,boardSnapshot,restoreBoardSnapshot,applyBoardSnapshot,resetBoardState});
})();
