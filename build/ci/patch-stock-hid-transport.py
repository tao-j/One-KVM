#!/usr/bin/env python3
"""Patch exactly the qualified stock frontend, without npm/frontend compilation.
All asset filenames are versioned together to avoid mixed cached graphs.
"""
import hashlib
import json
from pathlib import Path
import sys

EXPECTED = '53c8e94e1695ab911e55822bf8ceb0209ac5fd6f7209f4fe0891efaa0839808a'
VERSION = 'hid-reliable-v1'
REPLACEMENTS = [
 ('function yh(n){if(!Is||Is.readyState!=="open")return!1;try{const a=Tv(n);return Is.send(a),!0}catch{return!1}}',
  'function yh(n){if(!Is||Is.readyState!=="open")return!1;try{const a=Tv(n);return Is.send(a),!0}catch{Tr.value=!1;Is?.close();return!1}}'),
 ('function bh(n){if(!Is||Is.readyState!=="open")return!1;try{const a=Ev(n);return Is.send(a),!0}catch{return!1}}',
  'function bh(n){if(!Is||Is.readyState!=="open")return!1;try{const a=Ev(n);return Is.send(a),!0}catch{Tr.value=!1;Is?.close();return!1}}'),
 ('function Df(n){Is=n,n.onopen=()=>{Tr.value=!0},n.onclose=()=>{Tr.value=!1},n.onerror=a=>{Et("WebRTC data channel error",{label:n.label,readyState:n.readyState,event:a,sessionId:Oa})},n.onmessage=()=>{}}',
  'function Df(n){Is=n,n.binaryType="arraybuffer",n.onopen=()=>{if(Is===n)Tr.value=!0},n.onclose=()=>{if(Is===n)Tr.value=!1},n.onerror=a=>{if(Is===n)Tr.value=!1;n.close();Et("WebRTC data channel error",{label:n.label,readyState:n.readyState,event:a,sessionId:Oa})},n.onmessage=a=>{if(a.data instanceof ArrayBuffer&&new Uint8Array(a.data)[0]===1){if(Is===n)Tr.value=!1;n.close()}}}'),
 ('createDataChannel("hid",{ordered:!0,maxRetransmits:3})','createDataChannel("hid",{ordered:!0})'),
 ('function Pi(i,b){}',
  'let fcmLastHidErrorAt=0;function Pi(i,b){const n=Date.now();if(n-fcmLastHidErrorAt<2000)return;fcmLastHidErrorAt=n;vn.error("Input connection unavailable",{description:"Input was not sent. Reconnect the console before continuing."})}'),
 ('function Sl(i,b,O){if(z.value!=="mjpeg"&&_.dataChannelReady.value){const N={type:i==="down"?"keydown":"keyup",key:b,modifier:O};if(_.sendKeyboard(N))return}Gs.keyboard(i,b,O).catch(N=>void 0)}',
  'function Sl(i,b,O){if(z.value!=="mjpeg"){const N={type:i==="down"?"keydown":"keyup",key:b,modifier:O};if(!_.sendKeyboard(N))Pi(null,"keyboard");return}Gs.keyboard(i,b,O).catch(N=>Pi(N,"keyboard"))}'),
 ('function Ea(i){if(z.value!=="mjpeg"&&_.dataChannelReady.value){const b={type:i.type==="move_abs"?"moveabs":i.type,x:i.x,y:i.y,button:i.button==="left"?0:i.button==="middle"?1:i.button==="right"?2:void 0,scroll:i.scroll};if(_.sendMouse(b))return}Gs.mouse(i).catch(b=>(`${i.type}`,void 0))}',
  'function Ea(i){if(z.value!=="mjpeg"){const b={type:i.type==="move_abs"?"moveabs":i.type,x:i.x,y:i.y,button:i.button==="left"?0:i.button==="middle"?1:i.button==="right"?2:void 0,scroll:i.scroll};if(!_.sendMouse(b))Pi(null,"mouse");return}Gs.mouse(i).catch(b=>Pi(b,"mouse"))}'),
]

def sha(data): return hashlib.sha256(data).hexdigest()

def patch(dist, receipt):
    files = {p.relative_to(dist).as_posix(): p.read_bytes() for p in dist.rglob('*') if p.is_file()}
    matches = [name for name,data in files.items() if sha(data)==EXPECTED]
    if len(matches)!=1: raise ValueError('Expected exactly one hash-qualified stock ConsoleView asset')
    name=matches[0]; content=files[name].decode()
    for old,new in REPLACEMENTS:
        if content.count(old)!=1: raise ValueError('Expected exactly one occurrence of a qualified transformation')
        content=content.replace(old,new)
    updated=dict(files); updated[name]=content.encode()
    # A version suffix, rather than recursive content hashes, supports cyclic ESM
    # references. Every asset URL changes, including the entry module.
    rename={n:str(Path(n).with_name(Path(n).stem+'-'+VERSION+Path(n).suffix)) for n in files if n.startswith('assets/')}
    output={}
    for old,data in updated.items():
        if Path(old).suffix in ('.js','.css','.html','.json'):
            text=data.decode()
            for src,dst in rename.items():
                text=text.replace(Path(src).name,Path(dst).name)
            data=text.encode()
        output[rename.get(old,old)]=data
    result={'version':VERSION,'original_console':name,'original_console_sha256':EXPECTED,
            'console':rename[name], 'files':[{'before':n,'after':rename.get(n,n),
            'sha256_before':sha(files[n]),'sha256_after':sha(output[rename.get(n,n)])} for n in sorted(files)]}
    # All validation/transformation completed before the first mutation.
    for n in files: (dist/n).unlink()
    for n,data in output.items(): (dist/n).parent.mkdir(parents=True,exist_ok=True);(dist/n).write_bytes(data)
    receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: patch-stock-hid-transport.py WEB_DIST RECEIPT_JSON')
    patch(Path(sys.argv[1]),Path(sys.argv[2]))
