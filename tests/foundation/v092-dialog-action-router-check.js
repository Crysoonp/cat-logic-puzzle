const fs=require('fs'),vm=require('vm');
global.window=global;
vm.runInThisContext(fs.readFileSync('dialog-action-router.js','utf8'));
function ok(v,m){if(!v)throw new Error(m)}
let calls=[];
ok(window.CLPDialogActions.register('a',()=>calls.push('a')),'exact registration failed');
ok(!window.CLPDialogActions.register('a',()=>{}),'duplicate action must be rejected');
ok(window.CLPDialogActions.registerPattern(/^h[123]$/,(_c,a)=>calls.push(a)),'pattern registration failed');
ok(window.CLPDialogActions.dispatch('a',{}),'exact dispatch failed');
ok(window.CLPDialogActions.dispatch('h2',{}),'pattern dispatch failed');
ok(!window.CLPDialogActions.dispatch('unknown',{}),'unknown action must remain unhandled');
ok(calls.join(',')==='a,h2','dispatch result mismatch');
const game=fs.readFileSync('game.js','utf8');
ok(game.includes('function installDialogActions()'),'dialog registrations missing');
ok(game.includes('CLPDialogActions.dispatch(a'),'dialog dispatch not connected');
ok(!game.includes("if(a==='hagureStoryNext')"),'legacy action chain remains');
const html=fs.readFileSync('index.html','utf8');
ok(html.indexOf('dialog-action-router.js')<html.indexOf('game.js'),'router must load before game.js');
console.log('OK: Nekomichi Ver.0.8.12 dialog action router checks passed.');
