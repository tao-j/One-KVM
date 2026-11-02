import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {stripTypeScriptTypes} from 'node:module';

const [asset, mouseSource] = process.argv.slice(2);
if (!asset || !mouseSource) throw Error('usage: node frontend.test.mjs PATCHED_CONSOLE_ASSET web/src/types/hid.ts');
const text=readFileSync(asset,'utf8');
const between=(a,b)=>text.slice(text.indexOf(a),text.indexOf(b,text.indexOf(a)));
// Execute the actual patched stock functions, with browser dependencies mocked.
let packets=[], options, wsCalls=0, errors=0;
const channel=()=>({readyState:'open',close(){this.readyState='closed';this.onclose?.()},send(data){packets.push([...new Uint8Array(data)])}});
const context={Is:null,Tr:{value:false},Et(){},Oa:null,Date:{now:()=>10000},vn:{error(){errors++}},
 z:{value:'webrtc'},Gs:{mouse(){wsCalls++;return Promise.resolve()},keyboard(){wsCalls++;return Promise.resolve()}},
 ArrayBuffer,Uint8Array,DataView};
vm.createContext(context);
// Mouse framing is compiled directly from the actual source, not a reimplementation.
let types=readFileSync(mouseSource,'utf8').replace(/^import.*\n/gm,'').replace(/^export /gm,'');
types=stripTypeScriptTypes(types,{mode:'strip'});
vm.runInContext(types+'\nthis.Ev=encodeMouseEvent;this.Tv=()=>new Uint8Array([1,0,4,0]).buffer;',context);
vm.runInContext(between('function Df(','function Pf(')+between('function yh(','function wh(')+between('let fcmLastHidErrorAt=','function Cl('),context);
context._={sendMouse:context.bh,sendKeyboard:context.yh,dataChannelReady:context.Tr};
context.vh({createDataChannel(label,o){assert.equal(label,'hid'); options=o;return channel()}});
assert.equal(options.ordered,true);assert.equal(options.maxRetransmits,undefined);assert.equal(options.maxPacketLifeTime,undefined);
context.Is.onopen();
context.Ea({type:'move_abs',x:18022,y:16384});context.Ea({type:'down',button:'right'});context.Ea({type:'up',button:'right'});
assert.deepEqual(packets,[[2,1,102,70,0,64,0],[2,2,0,0,0,0,2],[2,3,0,0,0,0,2]]);
assert.equal(wsCalls,0);
context.Is.send=()=>{throw Error('buffer full')};context.Ea({type:'down',button:'left'});
assert.equal(context.Is.readyState,'closed');assert.equal(context.Tr.value,false);assert.equal(wsCalls,0);assert.equal(errors,1);
context.Ea({type:'up',button:'left'});assert.equal(wsCalls,0); // no cross-transport release replay
const old=context.Is;context.Df(channel());context.Is.onopen();old.onclose();assert.equal(context.Tr.value,true);
context.Is.onerror({});assert.equal(context.Tr.value,false);
context.Df(channel());context.Is.onopen();context.Is.onmessage({data:new Uint8Array([1]).buffer});assert.equal(context.Tr.value,false);assert.equal(context.Is.readyState,'closed');
context.z.value='mjpeg';context.Ea({type:'down',button:'left'});assert.equal(wsCalls,1);
console.log('PASS: reliable ordered options; actual mouse packet order; send failure closes/reports; no transport fallback; stale close isolation; MJPEG WS preserved');
