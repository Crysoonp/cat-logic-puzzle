(function(){
  'use strict';
  const VERSION='0.8.90';
  const LABEL='Ver.'+VERSION;
  window.CLP_APP_VERSION=VERSION;
  window.CLP_APP_VERSION_LABEL=LABEL;
  window.CLPApplyVersion=function(root=document){
    document.title=document.title.replace(/Ver\.\d+\.\d+\.\d+/g,LABEL);
    root.querySelectorAll('[data-app-version]').forEach(function(el){
      el.textContent=LABEL+(el.dataset.versionSuffix||'');
    });
  };
})();
