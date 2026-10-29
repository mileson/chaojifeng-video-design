import test from 'node:test';
import assert from 'node:assert/strict';
import {createRuntime, captureSamples} from './runtime.mjs';

const bundle = {schema_version:1, bundle_sha256:'fixture', output:{fps:30}, frame_count:90,
  order:['move'], bindings:[{id:'move',target_id:'object',kind:'subject',start_frame:0,end_frame:61,
    peak_frame:30,sample_frames:[0,30,60],channels:{position:{from:[0,0],to:[60,20],easing:'smooth'}}}]};

test('absolute frame evaluation survives reverse/random seeks',()=>{
  const r=createRuntime(bundle), expected=r.at(30);
  r.at(60);r.at(0);r.at(17);
  assert.deepEqual(r.at(30),expected);
  assert.deepEqual(r.at(0).states.move.channels.position,[0,0]);
  assert.deepEqual(r.at(60).states.move.channels.position,[60,20]);
  assert.throws(()=>r.at(90));
  assert.throws(()=>r.at(.5));
});

test('capture awaits readiness and reads applied object, not requested state',async()=>{
  let ready=false, object={x:0};
  const trace=await captureSamples(bundle,{
    name:'fixture-adapter',ready:async()=>{ready=true;},
    render:async s=>{assert.ok(ready);object.x=Math.round(s.states.move.channels.position[0])+1;},
    observe:async()=>({states:{move:{x:object.x}},texts:{}})
  },[0,60,30,0]);
  assert.deepEqual(trace.frames.map(f=>f.states.move.x),[1,61,31,1]);
  assert.equal(trace.observation,'rendered-state');
  assert.notStrictEqual(trace.frames[0].states,trace.frames[3].states);
});
