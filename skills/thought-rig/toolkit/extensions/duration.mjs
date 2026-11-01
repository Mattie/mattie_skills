/** A small extension demonstrating domain data beyond spatial transforms. */
export function summarizeChanges({ before, after }) {
  if (after?.type !== 'demo:cue' && before?.type !== 'demo:cue') return [];
  const oldDuration = before?.data?.durationSeconds, newDuration = after?.data?.durationSeconds;
  if (oldDuration === newDuration) return [];
  return [{ field: 'data.durationSeconds', before: oldDuration ?? null, after: newDuration ?? null,
    text: !after ? 'Cue removed' : !before ? `Cue added with ${newDuration}s duration` : `Duration changed from ${oldDuration}s to ${newDuration}s` }];
}

export function register(host) {
  host.registerType('demo:cue', {
    defaults: { geometry: { x: 35, y: 45, w: 240, h: 100, rotation: 0 }, data: { label: 'Timing cue', durationSeconds: 2 } },
    validate(object) { return Number.isFinite(object.data.durationSeconds) && object.data.durationSeconds >= 0 || 'Duration must be a nonnegative number'; },
    render({ ctx, object }) {
      const { w, h } = object.geometry;
      ctx.fillStyle = '#b9a7e2'; ctx.beginPath(); ctx.roundRect(0, 0, w, h, 12); ctx.fill();
      ctx.fillStyle = '#302442'; ctx.textAlign = 'left'; ctx.font = '18px "Segoe UI", sans-serif';
      ctx.fillText(object.data.label || 'Timing cue', 18, 32);
      ctx.font = '26px "Segoe UI", sans-serif'; ctx.fillText(`${object.data.durationSeconds}s`, 18, 72);
    },
    hitTest({ point, object }) { return point.x >= 0 && point.y >= 0 && point.x <= object.geometry.w && point.y <= object.geometry.h; },
    inspector: [{ key: 'durationSeconds', label: 'Duration (seconds)', input: 'number', min: 0, step: 0.1 }],
  });
  host.registerCommand({ id: 'demo:add-cue', label: 'Add timing cue', placement: 'toolbar',
    run({ host, actor }) { host.createObject('demo:cue', {}, { actor }); } });
}
