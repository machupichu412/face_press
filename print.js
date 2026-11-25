// The screen is evaluated in final PNG pixels so dot size is independent of viewport size.
const PortraitPrint = (() => {
  const screens = new Map();
  function makeScreen(width, height, pitch) {
    const key = width + 'x' + height + '/' + pitch;
    if (screens.has(key)) return screens.get(key);
    const threshold = new Uint8Array(width * height);
    const angle = (Math.PI * 23) / 180;
    const cosine = Math.cos(angle) / pitch;
    const sine = Math.sin(angle) / pitch;
    // Rank points within the square screen cell by distance to the dot center.
    // The circular dot grows into its neighbors as ink coverage approaches black.
    const area = new Uint8Array(1024);
    for (let i = 0; i < area.length; i++) {
      const r2 = i / 1600,
        r = Math.sqrt(r2);
      const cap =
        r > 0.5 ? r2 * Math.acos(0.5 / r) - 0.5 * Math.sqrt(r2 - 0.25) : 0;
      area[i] = Math.round(255 * Math.min(1, Math.PI * r2 - 4 * cap));
    }
    for (let y = 0, p = 0; y < height; y++) {
      for (let x = 0; x < width; x++, p++) {
        const u = x * cosine + y * sine,
          v = y * cosine - x * sine;
        const col = Math.floor(u),
          row = Math.floor(v);
        const hash = Math.imul(col ^ Math.imul(row, 8831), 0x45d9f3b) >>> 0;
        const dx = u - col - 0.5 + ((hash % 31) / 30 - 0.5) * 0.14;
        const dy = v - row - 0.5 + (((hash >>> 8) % 31) / 30 - 0.5) * 0.14;
        threshold[p] =
          area[Math.min(1023, Math.round((dx * dx + dy * dy) * 1600))];
      }
    }
    if (screens.size >= 6) screens.delete(screens.keys().next().value);
    screens.set(key, threshold);
    return threshold;
  }

  function apply(canvas, state) {
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    const frame = ctx.getImageData(0, 0, width, height);
    const pixels = frame.data;
    const screen = makeScreen(width, height, state.dotSize);
    const density = 0.62 + state.ink * 0.01;
    for (let i = 0, p = 0; i < screen.length; i++, p += 4) {
      const lum = Math.round(
        pixels[p] * 0.299 + pixels[p + 1] * 0.587 + pixels[p + 2] * 0.114,
      );
      const ink = Math.min(255, (255 - lum) * density);
      const coverage =
        ink === 0 ? 0 : Math.max(0, Math.min(1, (ink - screen[i]) / 25 + 0.5));
      const tone = 255 - 244 * coverage;
      pixels[p] = pixels[p + 1] = pixels[p + 2] = tone;
    }
    ctx.putImageData(frame, 0, 0);
  }
  return { apply };
})();

// Preserve photographic credits when a print leaves the studio. PNG iTXt is UTF-8.
function creditPng(blob, sources) {
  const encoder = new TextEncoder();
  const caption =
    'Face Press. Images cut out, resized, composited, and tonally processed.\n' +
    sources
      .map((source) =>
        [
          source.title,
          source.creator || source.credit,
          source.rights,
          source.url,
          source.licenseUrl,
        ]
          .filter(Boolean)
          .join(' · '),
      )
      .join('\n');
  const data = encoder.encode('Description\0\0\0\0\0' + caption);
  const chunk = new Uint8Array(data.length + 12);
  const view = new DataView(chunk.buffer);
  view.setUint32(0, data.length);
  chunk.set(encoder.encode('iTXt'), 4);
  chunk.set(data, 8);
  let crc = 0xffffffff;
  for (const byte of chunk.subarray(4, chunk.length - 4)) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++)
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
  }
  view.setUint32(chunk.length - 4, (crc ^ 0xffffffff) >>> 0);
  return new Blob([blob.slice(0, -12), chunk, blob.slice(-12)], {
    type: 'image/png',
  });
}
