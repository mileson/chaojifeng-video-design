/** Engine-neutral time sampling. Apply channels to real objects, then observe those objects.
 * This module does not draw, load assets, play audio, or generate a verification trace itself.
 */
export function createRuntime(bundle) {
  if (bundle.schema_version !== 1 || !Array.isArray(bundle.bindings)) throw Error('Invalid execution bundle');
  const byId = new Map(bundle.bindings.map(b => [b.id, b]));
  const mix = (a, b, p) => Array.isArray(a) ? a.map((v, i) => v + (b[i] - v) * p) : a + (b - a) * p;
  function at(frame) {
    if (!Number.isInteger(frame) || frame < 0 || frame >= bundle.frame_count) throw Error('Frame outside film');
    const states = {};
    for (const id of bundle.order) {
      const b = byId.get(id);
      const duration = Math.max(1, b.end_frame - b.start_frame - 1);
      const p = Math.max(0, Math.min(1, (frame - b.start_frame) / duration));
      const channels = Object.fromEntries(Object.entries(b.channels).map(([key, track]) => {
        const q = track.easing === 'smooth' ? p * p * (3 - 2 * p) : track.easing === 'hold' ? (p === 1 ? 1 : 0) : p;
        return [key, mix(track.from, track.to, q)];
      }));
      states[id] = {target_id: b.target_id, kind: b.kind,
        active: frame >= b.start_frame && frame < b.end_frame,
        progress: p, peak_frame: b.peak_frame, channels};
    }
    return {frame, time: frame / bundle.output.fps, states};
  }
  return {at, sampleFrames: [...new Set(bundle.bindings.flatMap(b => b.sample_frames))].sort((a, b) => a - b)};
}

/** Use existing engine readiness + rendering + measurement; never copy requested channels as observations. */
export async function captureSamples(bundle, adapter, frames) {
  if (!adapter?.name || !adapter.ready || !adapter.render || !adapter.observe) throw Error('Incomplete adapter');
  const runtime = createRuntime(bundle);
  await adapter.ready(); // Must wait for actual fonts, textures, audio metadata and scene readiness.
  const samples = [];
  for (const frame of frames ?? runtime.sampleFrames) {
    await adapter.render(runtime.at(frame));
    const measured = await adapter.observe(); // Read camera/object properties and screen-space text boxes after rendering.
    if (!measured?.states) throw Error('Missing observed states');
    samples.push(JSON.parse(JSON.stringify({frame, states: measured.states, texts: measured.texts ?? {}})));
  }
  return {schema_version: 1, bundle_sha256: bundle.bundle_sha256,
    adapter: adapter.name, observation: 'rendered-state', frames: samples};
}
