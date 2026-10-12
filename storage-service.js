(function(){
  'use strict';
  const backend=window.localStorage;
  const SCHEMA_VERSION=1;
  const META_KEY='clpStorageMeta';
  const KEYS=Object.freeze({
    hearts:'clpHearts',kibble:'clpKibble',history:'clpHistory',bossPhase:'clpBossPhase',
    heartUpdatedAt:'clpHeartUpdatedAt',currentBoard:'clpCurrentBoard',taijuJoined:'clpTaijuJoined',
    tutorialGift:'clpTutorialGift',storySeen:'clpStorySeen',vibrate:'clpVibrate',
    specialFxWeak:'clpSpecialFxWeak',devUnlockedTo:'clpDevUnlockedTo'
  });
  function getItem(key){return backend.getItem(key);}
  function setItem(key,value){backend.setItem(key,String(value));}
  function removeItem(key){backend.removeItem(key);}
  function clear(){backend.clear();}
  function getJSON(key,fallback=null){
    const raw=getItem(key);if(raw===null)return fallback;
    try{return JSON.parse(raw);}catch(_error){return fallback;}
  }
  function setJSON(key,value){setItem(key,JSON.stringify(value));}
  function ensureSchema(){
    const current=getJSON(META_KEY,null);
    if(current===null){
      setJSON(META_KEY,{schemaVersion:SCHEMA_VERSION,createdBy:window.CLP_APP_VERSION});
      return {schemaVersion:SCHEMA_VERSION,migrated:false};
    }
    if(!Number.isInteger(current.schemaVersion)||current.schemaVersion<1){
      throw new Error('Invalid Nekomichi storage schema metadata');
    }
    if(current.schemaVersion>SCHEMA_VERSION){
      throw new Error('Storage schema is newer than this app supports');
    }
    return {schemaVersion:current.schemaVersion,migrated:false};
  }
  function registeredKeyNames(){return Object.freeze(Object.values(KEYS).slice());}
  window.CLPStorage=Object.freeze({SCHEMA_VERSION,META_KEY,KEYS,getItem,setItem,removeItem,clear,getJSON,setJSON,ensureSchema,registeredKeyNames});
})();
