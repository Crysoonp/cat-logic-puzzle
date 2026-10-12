(function(){
  'use strict';
  const SCREEN_IDS=Object.freeze({title:'titleScreen'});
  const DIALOG_IDS=Object.freeze({main:'dlg',story:'storyDlg',history:'historyDlg',debug:'debugDlg',cats:'catsDlg'});
  function element(id){return document.getElementById(id);}
  function showScreen(name){const id=SCREEN_IDS[name];const node=id&&element(id);if(!node)return false;node.classList.remove('hidden');return true;}
  function hideScreen(name){const id=SCREEN_IDS[name];const node=id&&element(id);if(!node)return false;node.classList.add('hidden');return true;}
  function isScreenVisible(name){const id=SCREEN_IDS[name];const node=id&&element(id);return Boolean(node&&!node.classList.contains('hidden'));}
  function openDialog(name){const id=DIALOG_IDS[name];const node=id&&element(id);if(!node||typeof node.showModal!=='function')return false;if(!node.open)node.showModal();return true;}
  function closeDialog(name){const id=DIALOG_IDS[name];const node=id&&element(id);if(!node||typeof node.close!=='function')return false;if(node.open)node.close();return true;}
  function isDialogOpen(name){const id=DIALOG_IDS[name];const node=id&&element(id);return Boolean(node&&node.open);}
  function anyDialogOpen(){return Object.keys(DIALOG_IDS).some(isDialogOpen);}
  window.CLPScreens=Object.freeze({SCREEN_IDS,DIALOG_IDS,showScreen,hideScreen,isScreenVisible,openDialog,closeDialog,isDialogOpen,anyDialogOpen});
})();
