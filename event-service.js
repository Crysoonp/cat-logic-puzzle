(function(){
  'use strict';
  const bindings=new Map();
  function element(target){return typeof target==='string'?document.getElementById(target):target;}
  function key(target,type,namespace){const id=typeof target==='string'?target:(target&&target.id)||'anonymous';return `${namespace}:${id}:${type}`;}
  function bind(target,type,handler,namespace='app'){
    const node=element(target);if(!node||typeof handler!=='function')return false;
    const token=key(target,type,namespace);const previous=bindings.get(token);
    if(previous)previous.node.removeEventListener(previous.type,previous.handler);
    node.addEventListener(type,handler);bindings.set(token,{node,type,handler});return true;
  }
  function unbindNamespace(namespace){for(const [token,item] of [...bindings])if(token.startsWith(namespace+':')){item.node.removeEventListener(item.type,item.handler);bindings.delete(token);}}
  function count(){return bindings.size;}
  window.CLPEvents=Object.freeze({bind,unbindNamespace,count});
})();
