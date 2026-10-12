(function(){
  'use strict';
  const exact=new Map();
  const patterns=[];
  function register(action,handler){
    if(typeof action!=='string'||!action||typeof handler!=='function'||exact.has(action))return false;
    exact.set(action,handler);return true;
  }
  function registerPattern(pattern,handler){
    if(!(pattern instanceof RegExp)||typeof handler!=='function')return false;
    patterns.push({pattern,handler});return true;
  }
  function dispatch(action,context){
    if(exact.has(action)){exact.get(action)(context,action);return true;}
    for(const item of patterns){item.pattern.lastIndex=0;if(item.pattern.test(action)){item.handler(context,action);return true;}}
    return false;
  }
  function has(action){return exact.has(action)||patterns.some(item=>{item.pattern.lastIndex=0;return item.pattern.test(action);});}
  function registeredActions(){return Object.freeze([...exact.keys()]);}
  window.CLPDialogActions=Object.freeze({register,registerPattern,dispatch,has,registeredActions});
})();
