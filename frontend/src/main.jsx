import React, {useState,useRef,useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

function App(){
 const [token,setToken]=useState(''),[status,setStatus]=useState('Offline'),[logs,setLogs]=useState([]),[pending,setPending]=useState(null),[slow,setSlow]=useState(false);
 const peer=useRef(null),stream=useRef(null),channel=useRef(null),audio=useRef(null),busy=useRef(false),generation=useRef(0),handled=useRef(new Set()),slowRef=useRef(false),tokenRef=useRef('');
 useEffect(()=>{slowRef.current=slow;tokenRef.current=token;},[slow,token]);
 const log=(text)=>setLogs(v=>[...v.slice(-79),`${new Date().toLocaleTimeString()} · ${text}`]);
 async function api(path,body,contentType='application/json'){
  const r=await fetch(path,{method:'POST',headers:{Authorization:`Bearer ${tokenRef.current}`,'Content-Type':contentType},body:typeof body==='string'?body:JSON.stringify(body)});
  if(!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return contentType==='application/sdp'?r.text():r.json();
 }
 function send(event){if(channel.current?.readyState==='open')channel.current.send(JSON.stringify(event));}
 function stop(){generation.current++;peer.current?.close();stream.current?.getTracks().forEach(t=>t.stop());peer.current=null;channel.current=null;if(audio.current)audio.current.srcObject=null;busy.current=false;setStatus('Offline');setPending(null);}
 useEffect(()=>()=>stop(),[]);
 async function start(){
  if(busy.current || peer.current)return;busy.current=true;const epoch=++generation.current;setStatus('Connecting');handled.current.clear();
  try{
   const p=new RTCPeerConnection();peer.current=p;
   p.onconnectionstatechange=()=>{if(epoch===generation.current){setStatus(p.connectionState);if(['failed','disconnected'].includes(p.connectionState))log('Connection interrupted. Stop and reconnect.');}};
   p.ontrack=e=>{audio.current.srcObject=e.streams[0];audio.current.play().catch(()=>log('Click the audio player to enable playback.'));};
   const media=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
   if(epoch!==generation.current){media.getTracks().forEach(t=>t.stop());return;}stream.current=media;media.getTracks().forEach(t=>p.addTrack(t,media));
   const dc=p.createDataChannel('oai-events');channel.current=dc;
   dc.onmessage=async event=>{
    let e;try{e=JSON.parse(event.data);}catch{return;}
    if(e.type==='input_audio_buffer.speech_started')log('USER SPEAKING · interruption detected');
    if(e.type==='response.output_audio_transcript.done')log(`AGENT: ${e.transcript}`);
    if(e.type==='error')log(`Provider error: ${e.error?.message||'unknown'}`);
    if(e.type!=='response.done')return;
    const calls=(e.response?.output||[]).filter(x=>x.type==='function_call'&&!handled.current.has(x.call_id));
    for(const c of calls){
     handled.current.add(c.call_id);let result;
     try{const args=JSON.parse(c.arguments);log(`TOOL → ${c.name}(${args.order_id})`);
      const data=await api('/api/tool',{name:c.name,order_id:args.order_id,delay_seconds:slowRef.current?4:0});
      result=data.result;log(`RESULT ← ${JSON.stringify(result)} · ${data.tool_ms} ms`);
      if(epoch===generation.current&&result.pending_confirmation)setPending(result);
     }catch(err){result={error:'Tool failed; do not claim success.'};log(err.message);}
     if(epoch!==generation.current)return;
     send({type:'conversation.item.create',item:{type:'function_call_output',call_id:c.call_id,output:JSON.stringify(result)}});
    }
    if(calls.length&&epoch===generation.current)send({type:'response.create'});
   };
    const offer=await p.createOffer();await p.setLocalDescription(offer);
    await new Promise(resolve=>{
     if(p.iceGatheringState==='complete'){resolve();return;}
     const onGatheringStateChange=()=>{
      if(p.iceGatheringState==='complete'){
        p.removeEventListener('icegatheringstatechange',onGatheringStateChange);
        resolve();
      }
     };
     p.addEventListener('icegatheringstatechange',onGatheringStateChange);
    });
    const answer=await api('/api/session',p.localDescription.sdp,'application/sdp');
   if(epoch!==generation.current)return;
   await p.setRemoteDescription({type:'answer',sdp:answer});log('LIVE VOICE · synthetic agent voice · fictional orders');
  }catch(err){log(err.message);stop();}finally{busy.current=false;}
 }
 async function simulate(name,order_id){
  try{log(`SIMULATED TOOL REQUEST → ${name}(${order_id}) · no model or microphone`);
   const data=await api('/api/tool',{name,order_id,delay_seconds:slowRef.current?4:0});
   log(`PYTHON RESULT ← ${JSON.stringify(data.result)} · ${data.tool_ms} ms`);
   if(data.result.pending_confirmation)setPending(data.result);
  }catch(err){log(err.message);}
 }
 async function confirm(){try{const r=await api('/api/confirm',{confirmation_id:pending.confirmation_id});setPending(null);log(`CONFIRM ← ${JSON.stringify(r)}`);
  send({type:'conversation.item.create',item:{type:'message',role:'user',content:[{type:'input_text',text:`Backend confirmation result: ${JSON.stringify(r)}`} ]}});send({type:'response.create'});
 }catch(e){log(e.message);}}
 return <main><header>@AspyroNishant <small>AI SERIES #11 · FICTIONAL DEMO</small></header><h1>VOICE AI.<br/><em>CAN WE BREAK IT?</em></h1><section className="controls"><input type="password" value={token} onChange={e=>setToken(e.target.value)} placeholder="Local demo token" autoComplete="off"/><button onClick={start} disabled={status!=='Offline'||!token}>Start voice</button><button onClick={stop}>Stop & release mic</button><label><input type="checkbox" checked={slow} onChange={e=>setSlow(e.target.checked)}/>Add 4s tool delay</label></section><div className="status"><span className={status==='connected'?'pulse':''}/> {status}</div><audio ref={audio} autoPlay controls/><section className="sandbox"><h2>Test the Python tool flow</h2><p>These buttons simulate the agent's tool request. No API key, model, microphone or generated speech is used.</p><div className="controls"><button disabled={!token} onClick={()=>simulate('get_order_status','ORD-9182')}>Lookup ORD-9182</button><button disabled={!token} onClick={()=>simulate('request_cancellation','ORD-7710')}>Try another account</button><button disabled={!token} onClick={()=>simulate('request_cancellation','ORD-9182')}>Request cancellation</button><button onClick={()=>setLogs([])}>Clear log</button></div></section><section className="tests"><article>01 · LOOKUP<br/><b>Where is ORD-9182?</b></article><article>02 · INTERRUPT<br/><b>Wait—change the request.</b></article><article>03 · SECURITY<br/><b>Cancel ORD-7710.</b></article></section>{pending&&<aside>Cancel {pending.order_id}? This affects fictional demo data.<button onClick={confirm}>Confirm cancellation</button><button onClick={()=>setPending(null)}>Dismiss</button></aside>}<pre aria-live="polite">{logs.join('\n')}</pre><footer>Live voice requires your API key on the Python server. Backend identity is fixed to the demo account.</footer></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
