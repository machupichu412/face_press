'use strict';

const $ = (id) => document.getElementById(id);
const paths = {
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-11v2"/>',
  shuffle:
    '<path d="M3 6h3c5 0 7 12 12 12h3m-4-4 4 4-4 4M3 18h3c1.8 0 3.4-1.7 5-4.3M14 8c1.4-1.4 2.7-2 4-2h3m-4-4 4 4-4 4"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 15v5h16v-5"/>',
  frame:
    '<path d="M4 9V4h5m6 0h5v5m0 6v5h-5m-6 0H4v-5"/><rect x="8" y="8" width="8" height="8" rx="1"/>',
  grid: '<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M4 12h16M12 4v16"/>',
  expand: '<path d="M3 9V3h6m6 0h6v6m0 6v6h-6m-6 0H3v-6"/>',
  undo: '<path d="m8 4-5 5 5 5M4 9h9a6 6 0 1 1 0 12"/>',
  redo: '<path d="m16 4 5 5-5 5m4-5h-9a6 6 0 1 0 0 12"/>',
  bookmark: '<path d="M6 3h12v18l-6-4-6 4z"/>',
  stack: '<path d="m3 8 9-5 9 5-9 5zm0 5 9 5 9-5M3 17l9 5 9-5"/>',
  left: '<path d="m15 5-7 7 7 7"/>',
  right: '<path d="m9 5 7 7-7 7"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
  close: '<path d="m5 5 14 14m0-14L5 19"/>',
  move: '<path d="M3 12h18M12 3v18M6 9l-3 3 3 3m12-6 3 3-3 3M9 6l3-3 3 3M9 18l3 3 3-3"/>',
  sliders:
    '<path d="M3 7h4m5 0h9M3 17h10m5 0h3"/><circle cx="9.5" cy="7" r="2.5"/><circle cx="15.5" cy="17" r="2.5"/>',
};
document.querySelectorAll('[data-icon]').forEach((el) => {
  el.className = 'ico';
  el.setAttribute('aria-hidden', 'true');
  el.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
    paths[el.dataset.icon] +
    '</svg>';
});

const groups = {
  features: [
    'eyes',
    'eyebrows',
    'nose',
    'mouth',
    'chin',
    'ears',
    'hair',
    'beard',
    'gills',
    'fins',
  ],
  extras: ['glasses', 'tattoo', 'piercing', 'jewelry', 'antlers'],
  textures: ['texture'],
};
const names = {
  eyes: 'Eyes',
  eyebrows: 'Brows',
  nose: 'Nose',
  mouth: 'Mouth',
  chin: 'Jaw',
  ears: 'Ears',
  hair: 'Hair',
  glasses: 'Glasses',
  beard: 'Facial hair',
  tattoo: 'Tattoos',
  piercing: 'Piercings',
  jewelry: 'Jewelry',
  antlers: 'Antlers',
  gills: 'Gills',
  fins: 'Fins',
  texture: 'Textures',
};
const order = [
  'fins',
  'ears',
  'chin',
  'beard',
  'gills',
  'eyes',
  'eyebrows',
  'nose',
  'mouth',
  'hair',
  'antlers',
  'glasses',
  'tattoo',
  'piercing',
  'jewelry',
  'texture',
];
const adornments = ['tattoo', 'piercing', 'jewelry'];
const isAdornment = (cat) => adornments.includes(cat);
const singleSlots = order.filter((cat) => !isAdornment(cat));
const optionalSlot = (cat) =>
  ['beard', 'glasses', 'antlers', 'gills', 'fins', 'texture'].includes(cat);
const emptyItem = { id: null, name: 'None', empty: true };
const focusedLayer = {};
let sourceFilter = 'all';
const opts = {};
let state,
  initial,
  activeCat = 'eyes',
  activeGroup = 'features',
  page = 0,
  revision = 0,
  noticeTimer,
  ready = false;
let past = [],
  future = [],
  archive = readLocal('facepress.archive.v1', []),
  pendingRender = Promise.resolve();
if (!Array.isArray(archive)) archive = [];
const draftKey = 'facepress.draft.v1';
const layerCache = new Map(),
  limit = 48,
  pageSize = 6;
const limits = {
  x: [-210, 210],
  y: [-210, 210],
  scale: [30, 220],
  width: [25, 250],
  height: [25, 250],
  tilt: [-90, 90],
  spacing: [-70, 110],
  opacity: [0, 100],
  light: [-50, 50],
};
const newTransform = () => ({
  x: 0,
  y: 0,
  scale: 100,
  width: 100,
  height: 100,
  tilt: 0,
  spacing: 0,
  opacity: 100,
  light: 0,
  blend: 'multiply',
});
const paired = (cat) => cat === 'eyes' || cat === 'eyebrows';
const hasSpacing = (cat) => paired(cat) || cat === 'ears';
const clone = (obj) => JSON.parse(JSON.stringify(obj));
function readLocal(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}
function persist() {
  try {
    localStorage.setItem(draftKey, JSON.stringify(state));
  } catch {
    /* The editor also works in memory. */
  }
}
function notify(msg) {
  $('notice').textContent = msg;
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => ($('notice').textContent = ''), 3200);
}
function setBusy(busy) {
  ['shuffle', 'save'].forEach((id) => ($(id).disabled = busy));
}
function surface(width, height = width) {
  const c = document.createElement('canvas');
  c.width = width;
  c.height = height;
  return c;
}
function imageFor(src) {
  if (layerCache.has(src)) {
    const result = layerCache.get(src);
    layerCache.delete(src);
    layerCache.set(src, result);
    return result;
  }
  const result = new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => {
      layerCache.delete(src);
      reject(new Error('Could not read ' + src));
    };
    img.src = src;
  });
  layerCache.set(src, result);
  if (layerCache.size > limit)
    layerCache.delete(layerCache.keys().next().value);
  return result;
}
function itemById(cat, id) {
  return opts[cat]?.find((item) => item.id === id);
}
function layerIndex(cat) {
  const last = state.layers[cat].length - 1;
  return Math.min(focusedLayer[cat] ?? last, last);
}
function editTarget(cat) {
  if (isAdornment(cat)) return state.layers[cat][layerIndex(cat)];
  if (state.legacyAnimal?.category === cat) return state.legacyAnimal;
  return { id: state.picks[cat], transform: state.transforms[cat] };
}
function choice(cat) {
  return itemById(cat, editTarget(cat)?.id) || emptyItem;
}
// Older prints used one animal overlay in front of the human feature.
// Preserve its appearance until the user edits that anatomical slot.
function adoptAnimal(cat) {
  if (state.legacyAnimal?.category !== cat) return;
  const { id, transform } = state.legacyAnimal;
  state.picks[cat] = id;
  state.transforms[cat] = transform;
  if (cat === 'eyes') state.eyeMode = 'original';
  delete state.legacyAnimal;
}
function layersFor(s) {
  const layers = [];
  const add = (cat, id, transform, overlay = false) => {
    const item = itemById(cat, id);
    if (item && !item.empty) layers.push({ cat, item, transform, overlay });
  };
  for (const cat of order) {
    if (isAdornment(cat)) {
      for (const layer of s.layers[cat]) add(cat, layer.id, layer.transform);
    } else {
      if (cat === 'texture' && s.legacyAnimal) {
        const { category, id, transform } = s.legacyAnimal;
        add(category, id, transform, true);
      }
      add(cat, s.picks[cat], s.transforms[cat]);
    }
  }
  return layers;
}
function catalog() {
  if (sourceFilter === 'all') return opts[activeCat];
  const matches = opts[activeCat].filter(
    (item) => item.origin === sourceFilter,
  );
  // In a portrait collection, show the most detailed crops first.
  if (sourceFilter === 'photo' || sourceFilter === 'synthetic') {
    matches.sort((a, b) => (b.pixels || 512) - (a.pixels || 512));
  }
  const clear = opts[activeCat].find((item) => item.empty);
  return clear ? [...matches, clear] : matches;
}
function snap() {
  return JSON.stringify(state);
}
function record(before) {
  if (before === snap()) return;
  past.push(before);
  if (past.length > 60) past.shift();
  future = [];
  persist();
  historyButtons();
}
function historyButtons() {
  $('undo').disabled = !past.length;
  $('redo').disabled = !future.length;
}
function applyChange(fn) {
  const before = snap();
  fn();
  record(before);
  refresh();
}
function restore(from, to) {
  if (!from.length) return;
  to.push(snap());
  state = JSON.parse(from.pop());
  persist();
  showSelectionPage();
  refresh();
}
function checkedState(saved) {
  const clean = clone(initial);
  if (!saved || typeof saved !== 'object') return clean;
  clean.edition = Math.max(
    1,
    Math.min(999999, Number.parseInt(saved.edition) || 1),
  );
  clean.ink = bounded(saved.ink, 0, 100, initial.ink);
  clean.dotSize = bounded(saved.dotSize, 2, 9, initial.dotSize);
  clean.eyeMode = ['original', 'left', 'right'].includes(saved.eyeMode)
    ? saved.eyeMode
    : 'original';
  for (const cat of singleSlots) {
    const id = saved.picks?.[cat];
    if (itemById(cat, id)) clean.picks[cat] = id;
    else if (typeof id === 'string' && id.startsWith('draw-'))
      clean.picks[cat] = 'none-' + cat;
    else if (saved.picks && !id && cat === 'beard')
      clean.picks[cat] = 'none-beard';
    if (saved.transforms?.[cat])
      clean.transforms[cat] = checkedTransform(saved.transforms[cat]);
  }
  for (const cat of adornments) {
    const entries = Array.isArray(saved.layers?.[cat])
      ? saved.layers[cat]
      : [{ id: saved.picks?.[cat], transform: saved.transforms?.[cat] }];
    clean.layers[cat] = entries
      .filter((entry) => entry && itemById(cat, entry.id))
      .map((entry) => ({
        id: entry.id,
        transform: checkedTransform(entry.transform),
      }));
  }
  const animal = saved.legacyAnimal || {
    id: saved.picks?.animal,
    transform: saved.transforms?.animal,
  };
  if (animal.id) {
    const category = singleSlots.find(
      (cat) => itemById(cat, animal.id)?.origin === 'animal',
    );
    if (category)
      clean.legacyAnimal = {
        category,
        id: animal.id,
        transform: checkedTransform(animal.transform),
      };
  }
  return clean;
}
function checkedTransform(input) {
  const result = newTransform();
  for (const [key, [min, max]] of Object.entries(limits))
    result[key] = bounded(input?.[key], min, max, result[key]);
  if (['multiply', 'source-over', 'darken'].includes(input?.blend))
    result.blend = input.blend;
  return result;
}
function bounded(val, min, max, fallback) {
  return Number.isFinite(val)
    ? Math.min(max, Math.max(min, Math.round(val)))
    : fallback;
}
function drawPair(ctx, image, t, cy, eyeMode, reach, tilt) {
  // Each half is cut from the original aligned photo. Reflection swaps only the designated eye.
  for (const side of [-1, 1]) {
    const sourceSide = eyeMode === 'left' ? -1 : eyeMode === 'right' ? 1 : side;
    const pivot = 256 + side * reach;
    ctx.save();
    ctx.translate(pivot + (side * t.spacing) / 2, cy);
    ctx.rotate((-side * tilt * Math.PI) / 180);
    ctx.scale(t.width / 100, t.height / 100);
    if (side !== sourceSide) ctx.scale(-1, 1);
    ctx.translate(-(256 + sourceSide * reach), -cy);
    const sx = sourceSide < 0 ? 0 : 256;
    const half = image.naturalWidth / 2;
    ctx.drawImage(
      image,
      sourceSide < 0 ? 0 : half,
      0,
      half,
      image.naturalHeight,
      sx,
      0,
      256,
      512,
    );
    ctx.restore();
  }
}
function drawCutout(ctx, layer, image, s) {
  const { cat, item, transform: t, overlay } = layer;
  const symmetric = paired(cat) && !overlay;
  const split = hasSpacing(cat) && !overlay;
  const [x, y, w, h] = item.bounds;
  const cx = symmetric ? 256 : x + w / 2,
    cy = y + h / 2;
  ctx.save();
  if (cat === 'chin') {
    ctx.globalAlpha = t.opacity / 100;
    ctx.globalCompositeOperation = t.blend;
    if (t.light) ctx.filter = 'brightness(' + (100 + t.light) + '%)';
  }
  ctx.translate(cx + t.x, cy + t.y);
  ctx.scale(t.scale / 100, t.scale / 100);
  if (!symmetric) ctx.rotate((t.tilt * Math.PI) / 180);
  if (!split) ctx.scale(t.width / 100, t.height / 100);
  ctx.translate(-cx, -cy);
  if (split)
    drawPair(
      ctx,
      image,
      t,
      cy,
      cat === 'eyes' ? s.eyeMode : 'original',
      cat === 'ears' ? w * 0.43 : 55,
      symmetric ? t.tilt : 0,
    );
  else ctx.drawImage(image, 0, 0, 512, 512);
  ctx.restore();
}
async function compose(canvas, s) {
  const layers = layersFor(s);
  const images = await Promise.all(
    layers.map((layer) => imageFor(layer.item.src)),
  );
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(0, (canvas.height - canvas.width) / 2);
  ctx.scale(canvas.width / 512, canvas.width / 512);
  ctx.imageSmoothingQuality = 'high';
  layers.forEach((layer, i) => drawCutout(ctx, layer, images[i], s));
  ctx.restore();
  PortraitPrint.apply(canvas, {
    ink: s.ink,
    dotSize: Math.max(2, (s.dotSize * canvas.width) / 800),
  });
  return layers.map((layer) => layer.item);
}
async function render() {
  const version = ++revision,
    s = clone(state),
    target = surface(800, 880);
  try {
    const items = await compose(target, s);
    if (version !== revision) return;
    $('portrait').getContext('2d').drawImage(target, 0, 0);
    $('loading').hidden = true;
    $('save').disabled = false;
    const blob = await new Promise((resolve) =>
      $('portrait').toBlob(resolve, 'image/png'),
    );
    if (version !== revision) return;
    if (!blob) throw new Error('Could not encode the print as a PNG');
    const link = $('export');
    link.download = 'face-press-' + String(s.edition).padStart(3, '0') + '.png';
    link.href = URL.createObjectURL(creditPng(blob, selectedCredits(items)));
    link.removeAttribute('aria-disabled');
  } catch (e) {
    if (version === revision) {
      $('loading').textContent =
        'Could not load a part. Choose another or reload.';
      $('loading').hidden = false;
      $('save').disabled = true;
    }
    console.error(e);
  }
}
function redraw() {
  const link = $('export');
  if (link.hasAttribute('href')) URL.revokeObjectURL(link.href);
  link.removeAttribute('href');
  link.setAttribute('aria-disabled', 'true');
  $('save').disabled = true;
  pendingRender = render();
}
function showSelectionPage() {
  if (sourceFilter !== 'all' && !catalog().includes(choice(activeCat)))
    sourceFilter = 'all';
  page = Math.max(
    0,
    Math.floor(catalog().indexOf(choice(activeCat)) / pageSize),
  );
}
function changeCategory(cat) {
  activeCat = cat;
  sourceFilter = 'all';
  showSelectionPage();
  renderCategories();
  renderVariants();
  renderLayerPicker();
  renderTransforms();
}
function renderCategories() {
  $('categories').replaceChildren(
    ...groups[activeGroup].map((cat) => {
      const b = document.createElement('button');
      b.textContent = names[cat];
      b.setAttribute('aria-pressed', cat === activeCat);
      b.classList.toggle('active', cat === activeCat);
      b.onclick = () => changeCategory(cat);
      return b;
    }),
  );
  $('categories').hidden = groups[activeGroup].length === 1;
  document.querySelectorAll('[data-group]').forEach((b) => {
    const active = b.dataset.group === activeGroup;
    b.classList.toggle('selected', active);
    b.setAttribute('aria-pressed', active);
  });
}
async function drawThumb(c, item) {
  const ctx = c.getContext('2d');
  if (item.empty) {
    ctx.strokeStyle = '#939889';
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    ctx.arc(c.width / 2, c.height / 2, 17, 0, 2 * Math.PI);
    ctx.moveTo(c.width / 2 - 12, c.height / 2 + 12);
    ctx.lineTo(c.width / 2 + 12, c.height / 2 - 12);
    ctx.stroke();
    return;
  }
  try {
    const img = await imageFor(item.src),
      [x, y, w, h] = item.bounds;
    const fit = Math.min((c.width - 24) / w, (c.height - 14) / h);
    const pixelScale = img.naturalWidth / 512;
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(
      img,
      x * pixelScale,
      y * pixelScale,
      w * pixelScale,
      h * pixelScale,
      (c.width - w * fit) / 2,
      (c.height - h * fit) / 2,
      w * fit,
      h * fit,
    );
    PortraitPrint.apply(c, state);
  } catch {
    c.setAttribute('aria-label', 'Image unavailable');
  }
}
function renderVariants() {
  const cat = activeCat,
    list = catalog(),
    pages = Math.ceil(list.length / pageSize);
  page = Math.max(0, Math.min(pages - 1, page));
  const multi = isAdornment(cat);
  const origins = new Set(
    opts[cat].filter((item) => !item.empty).map((item) => item.origin),
  );
  $('originPicker').hidden = origins.size < 2;
  const select = $('originSelect');
  const sourceNames = {
    all: 'All cutouts',
    photo: 'Photographed people',
    synthetic: 'Synthetic portraits',
    animal: 'Animal',
    object: 'Objects',
  };
  select.replaceChildren(
    ...Object.entries(sourceNames)
      .filter(([value]) => value === 'all' || origins.has(value))
      .map(([value, label]) => new Option(label, value)),
  );
  select.value = sourceFilter;
  $('catTitle').textContent = names[cat];
  $('addHint').hidden = !multi;
  $('partCount').textContent = list.length + ' options';
  $('page').textContent = page + 1 + ' / ' + pages;
  $('prev').disabled = page === 0;
  $('next').disabled = page === pages - 1;
  $('variants').replaceChildren(
    ...list.slice(page * pageSize, (page + 1) * pageSize).map((item) => {
      const b = document.createElement('button'),
        c = surface(270, 115),
        label = document.createElement('span');
      const active = choice(cat).id === item.id;
      b.className = 'variant' + (active ? ' active' : '');
      if (multi) {
        b.classList.add('add-tile');
        b.setAttribute('aria-label', 'Add ' + item.name);
        const badge = document.createElement('span');
        badge.className = 'add-mark';
        const copies = state.layers[cat].filter(
          (layer) => layer.id === item.id,
        ).length;
        badge.textContent = copies ? '×' + copies : '+';
        b.title =
          'Add ' + item.name + (copies ? ' (' + copies + ' on portrait)' : '');
        b.append(badge);
      } else b.setAttribute('aria-pressed', active);
      label.className = 'vlabel';
      label.textContent = item.name;
      c.setAttribute('aria-hidden', 'true');
      b.append(c, label);
      drawThumb(c, item);
      b.onclick = () => {
        if (multi) applyChange(() => addLayer(cat, item.id));
        else if (
          state.picks[cat] !== item.id ||
          state.legacyAnimal?.category === cat
        )
          applyChange(() => {
            adoptAnimal(cat);
            state.picks[cat] = item.id;
          });
      };
      return b;
    }),
  );
}
function addLayer(cat, id) {
  const layers = state.layers[cat],
    transform = newTransform();
  const last = layers.findLast((layer) => layer.id === id);
  if (last) {
    transform.x = bounded(last.transform.x + 12, ...limits.x, 0);
    transform.y = bounded(last.transform.y + 8, ...limits.y, 0);
  }
  focusedLayer[cat] = layers.length;
  layers.push({ id, transform });
}
function renderLayerPicker() {
  const cat = activeCat,
    multi = isAdornment(cat);
  $('layerPicker').hidden = !multi || !state.layers[cat].length;
  if (!multi) return;
  const layers = state.layers[cat],
    selected = layerIndex(cat);
  $('layerSelect').replaceChildren(
    ...layers.map((layer, i) => {
      const option = new Option(
        i + 1 + ' · ' + itemById(cat, layer.id).name,
        String(i),
      );
      option.selected = i === selected;
      return option;
    }),
  );
  $('layerCount').textContent = '(' + layers.length + ')';
}
const adjustments = [
  {
    key: 'scale',
    label: 'Size',
    unit: '%',
    delta: 5,
    decrease: 'Shrink',
    increase: 'Enlarge',
  },
  {
    key: 'width',
    label: 'Width',
    unit: '%',
    delta: 5,
    decrease: 'Narrow part',
    increase: 'Widen part',
  },
  {
    key: 'height',
    label: 'Height',
    unit: '%',
    delta: 5,
    decrease: 'Shorten part',
    increase: 'Lengthen part',
  },
  {
    key: 'tilt',
    label: 'Tilt',
    unit: '°',
    delta: 3,
    decrease: 'Decrease tilt',
    increase: 'Increase tilt',
  },
  {
    key: 'spacing',
    label: 'Spacing',
    unit: '',
    delta: 4,
    decrease: 'Bring closer',
    increase: 'Spread apart',
  },
];
const numberFields = new Map();
function writeAdjustment(key, value, editing = null) {
  const target = editTarget(activeCat);
  if (!target || !Number.isFinite(value)) return false;
  const next = bounded(value, ...limits[key], target.transform[key]);
  if (target.transform[key] === next) return false;
  adoptAnimal(activeCat);
  editTarget(activeCat).transform[key] = next;
  renderTransforms(editing);
  redraw();
  return true;
}
function nudge(key, delta) {
  const before = snap();
  if (writeAdjustment(key, editTarget(activeCat).transform[key] + delta))
    record(before);
}
function numberField(key, label, unit) {
  const box = document.createElement('span');
  box.className = 'number-field';
  const input = document.createElement('input');
  input.type = 'number';
  input.id = 'value-' + key;
  [input.min, input.max] = limits[key];
  input.step = '1';
  input.setAttribute('aria-label', label);
  input.title = 'Type a value, use the arrow keys, or scroll to adjust';
  numberFields.set(key, input);
  box.append(input);
  if (unit) {
    const suffix = document.createElement('span');
    suffix.textContent = unit;
    suffix.setAttribute('aria-hidden', 'true');
    box.append(suffix);
  }

  // Keep all keystrokes in one undo entry and allow incomplete signed numbers.
  let editStart = null;
  function applyTyped(final) {
    const value = input.valueAsNumber;
    if (!final && !input.validity.valid) return;
    const before = editStart ?? snap();
    if (writeAdjustment(key, value, input)) {
      if (editStart === null) record(before);
      else persist();
      editStart = before;
    }
  }
  function finish() {
    applyTyped(true);
    if (editStart && past.at(-1) === editStart && snap() === editStart) {
      past.pop();
      historyButtons();
    }
    editStart = null;
    input.value = editTarget(activeCat).transform[key];
  }
  input.addEventListener('input', () => applyTyped(false));
  input.addEventListener('blur', finish);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      input.blur();
    } else if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
      event.preventDefault();
      finish();
      nudge(key, event.key === 'ArrowUp' ? 1 : -1);
    }
  });
  let travel = 0,
    lastWheel = 0;
  box.addEventListener(
    'wheel',
    (event) => {
      if (
        event.ctrlKey ||
        event.metaKey ||
        !event.deltaY ||
        Math.abs(event.deltaX) > Math.abs(event.deltaY)
      )
        return;
      event.preventDefault();
      const delta =
        event.deltaY *
        (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 100 : 1);
      if (
        event.timeStamp - lastWheel > 200 ||
        Math.sign(delta) !== Math.sign(travel)
      )
        travel = 0;
      lastWheel = event.timeStamp;
      travel += delta;
      if (Math.abs(travel) < 24) return;
      if (
        document.activeElement !== input &&
        document.activeElement?.matches('.number-field input')
      ) {
        document.activeElement.blur();
      }
      finish();
      nudge(key, -Math.sign(travel));
      travel = 0;
    },
    { passive: false },
  );
  return box;
}
function buildSteppers() {
  for (const { key, label, unit, delta, decrease, increase } of adjustments) {
    const row = document.createElement('div');
    row.className = 'step-row';
    row.id = 'row-' + key;
    const text = document.createElement('label');
    text.htmlFor = 'value-' + key;
    text.textContent = label;
    const value = numberField(key, label, unit);
    const step = (amount, symbol, name) => {
      const b = document.createElement('button');
      b.textContent = symbol;
      b.dataset.step = key;
      b.dataset.amount = amount;
      b.setAttribute('aria-label', name);
      b.title = name;
      return b;
    };
    const controls = document.createElement('div');
    controls.className = 'step-controls';
    controls.append(
      step(-delta, key === 'tilt' ? '↶' : '−', decrease),
      value,
      step(delta, key === 'tilt' ? '↷' : '+', increase),
    );
    row.append(text, controls);
    $('steppers').append(row);
  }
  for (const [key, label] of [
    ['x', 'Horizontal position'],
    ['y', 'Vertical position'],
  ]) {
    const axis = document.createElement('label');
    axis.textContent = key.toUpperCase();
    axis.htmlFor = 'value-' + key;
    axis.append(numberField(key, label, ''));
    $('coordinates').append(axis);
  }
  $('opacityField').append(numberField('opacity', 'Jaw opacity', '%'));
  $('lightField').append(numberField('light', 'Jaw lighting', '%'));
}
function selectedCredits(items) {
  const sources = items
    .filter((item) => !item.empty)
    .map((item) => item.credit);
  return Array.from(
    new Map(sources.map((source) => [source.url, source])).values(),
  );
}
function renderTransforms(editing = null) {
  const item = choice(activeCat),
    t = editTarget(activeCat)?.transform ?? newTransform(),
    movable = !item.empty && activeCat !== 'texture';
  $('adjustTitle').textContent = isAdornment(activeCat)
    ? names[activeCat] + ' on portrait'
    : 'Adjust ' + names[activeCat].toLowerCase();
  $('position').hidden = activeCat === 'texture';
  $('resetPart').hidden = !movable;
  $('placementHint').textContent = item.empty
    ? isAdornment(activeCat)
      ? 'Add a cutout from the library to place it here.'
      : 'Choose a cutout above to adjust its placement.'
    : item.name + ' · Drag on the portrait or use the controls.';
  $('transformControls').hidden = !movable;
  $('eyePair').hidden = !movable || activeCat !== 'eyes';
  $('row-spacing').hidden = !hasSpacing(activeCat);
  $('jawControls').hidden = !movable || activeCat !== 'chin';
  for (const [key, input] of numberFields) {
    if (input !== editing) input.value = t[key];
  }
  document.querySelectorAll('[data-step]').forEach((b) => {
    const key = b.dataset.step,
      [min, max] = limits[key];
    b.disabled =
      !movable ||
      (Number(b.dataset.amount) < 0 ? t[key] <= min : t[key] >= max);
  });
  document
    .querySelectorAll('[data-eye]')
    .forEach((b) =>
      b.setAttribute(
        'aria-pressed',
        b.dataset.eye ===
          (state.legacyAnimal?.category === 'eyes'
            ? 'original'
            : state.eyeMode),
      ),
    );
  $('jawOpacity').value = t.opacity;
  $('jawLight').value = t.light;
  $('jawBlend').value = t.blend;
}
function bindAdjustments() {
  buildSteppers();
  document.querySelectorAll('[data-step]').forEach((button) => {
    button.onclick = () =>
      nudge(button.dataset.step, Number(button.dataset.amount));
  });
  document.querySelectorAll('[data-eye]').forEach(
    (b) =>
      (b.onclick = () =>
        applyChange(() => {
          adoptAnimal('eyes');
          state.eyeMode = b.dataset.eye;
        })),
  );
  $('resetPart').onclick = () =>
    applyChange(() => {
      adoptAnimal(activeCat);
      Object.assign(editTarget(activeCat).transform, newTransform());
      if (activeCat === 'eyes') state.eyeMode = 'original';
    });
  for (const [id, key] of [
    ['jawOpacity', 'opacity'],
    ['jawLight', 'light'],
  ]) {
    bindRange(id, (value) => {
      state.transforms.chin[key] = value;
      renderTransforms();
    });
  }
  $('jawBlend').onchange = () =>
    applyChange(() => {
      state.transforms.chin.blend = $('jawBlend').value;
    });
}
function bindRange(id, update) {
  const input = $(id);
  let before;
  input.oninput = () => {
    before ??= snap();
    update(Number(input.value));
    redraw();
  };
  input.onchange = () => {
    if (before) record(before);
    before = null;
  };
}
function refresh() {
  historyButtons();
  renderCategories();
  renderVariants();
  renderLayerPicker();
  renderTransforms();
  $('dotSize').value = state.dotSize;
  $('dotValue').value = state.dotSize + ' px';
  $('ink').value = state.ink;
  $('inkValue').value = state.ink + '%';
  redraw();
}
function showTab(tab) {
  const studio = tab === 'studio';
  $('studio').hidden = !studio;
  $('archive').hidden = studio;
  for (const key of ['studio', 'archive']) {
    const b = $(key + 'Tab');
    b.classList.toggle('active', key === tab);
    if (key === tab) b.setAttribute('aria-current', 'page');
    else b.removeAttribute('aria-current');
  }
  if (!studio) renderArchive();
}
let archiveObserver;
function renderArchive() {
  $('archiveCount').textContent = archive.length;
  if ($('archive').hidden) return;
  archiveObserver?.disconnect();
  archiveObserver = new IntersectionObserver(
    (entries) => {
      for (const { target, isIntersecting } of entries) {
        if (!isIntersecting) continue;
        archiveObserver.unobserve(target);
        const saved = archive[Number(target.dataset.index)];
        compose(target, checkedState(saved.state)).catch((error) =>
          console.error('Archive preview:', error),
        );
      }
    },
    { rootMargin: '160px' },
  );
  if (!archive.length) {
    $('prints').innerHTML =
      '<div class="empty"><strong>Your archive is empty.</strong>Use “Save to archive” beneath a composition to keep an editable copy here.</div>';
    return;
  }
  $('prints').replaceChildren(
    ...archive.map((entry, index) => {
      const b = document.createElement('button'),
        preview = surface(400, 440),
        caption = document.createElement('span');
      b.className = 'print-card';
      preview.setAttribute('aria-hidden', 'true');
      preview.dataset.index = String(index);
      archiveObserver.observe(preview);
      caption.textContent =
        'Portrait ' + String(entry.state.edition).padStart(3, '0');
      b.append(preview, caption);
      b.onclick = () => {
        applyChange(() => (state = checkedState(entry.state)));
        showSelectionPage();
        renderVariants();
        showTab('studio');
      };
      return b;
    }),
  );
}
function savePrint() {
  if (archive.some((a) => JSON.stringify(a.state) === snap())) {
    notify('This version is already in your archive.');
    return;
  }
  const next = [{ state: clone(state) }, ...archive];
  try {
    localStorage.setItem('facepress.archive.v1', JSON.stringify(next));
    archive = next;
    renderArchive();
    notify('Print saved to your archive.');
  } catch {
    notify(
      'Browser storage is full or unavailable. Use Export PNG to keep this print.',
    );
  }
}
function dialog(creditsOnly) {
  $('info').querySelector('h2').textContent = creditsOnly
    ? 'Image sources & credits'
    : 'About Face Press';
  $('infoBody').innerHTML =
    (creditsOnly
      ? ''
      : '<p>Face Press is a free browser-based identikit studio inspired by cut-and-paste portraiture. Choose a cutout, then drag it on the portrait or use its position pad. Size, tilt, and spacing controls update the print immediately. Either photographed eye can supply a mirrored pair. Adjust the ink density and dot size, then export the newsprint portrait as a PNG.</p><p>Your draft and archive stay in this browser.</p>') +
    '<p>Portrait fragments are extracted from reusable headshots. The credits list the source collections, licenses, and extraction method.</p><p><a href="CREDITS.md" target="_blank" rel="noopener">Face credits</a> · <a href="assets/adornments/CREDITS.md" target="_blank" rel="noopener">Adornment credits</a> · <a href="assets/specimens/CREDITS.md" target="_blank" rel="noopener">Animal, eyewear &amp; texture credits</a> · <a href="assets/brand/CREDITS.md" target="_blank" rel="noopener">Logo credits</a> · <a href="assets/type/OFL.txt" target="_blank" rel="noopener">Font license</a></p>';
  if (creditsOnly) {
    const heading = document.createElement('h3');
    heading.textContent = 'Sources in this print';
    const list = document.createElement('ul');
    for (const credit of selectedCredits(
      layersFor(state).map((layer) => layer.item),
    )) {
      const link = document.createElement('a'),
        li = document.createElement('li');
      link.href = credit.url;
      link.textContent = credit.title;
      link.target = '_blank';
      link.rel = 'noopener';
      li.append(
        link,
        ' · ' +
          [credit.creator || credit.credit, credit.rights]
            .filter(Boolean)
            .join(' · '),
      );
      list.append(li);
    }
    $('infoBody').append(heading, list);
  }
  $('info').showModal();
}
// Convert a screen drag to a displacement in the source cutout coordinates.
function enableCanvasDrag() {
  const canvas = $('portrait');
  let gesture = null;
  canvas.onpointerdown = (e) => {
    if (e.button !== 0 || activeCat === 'texture' || choice(activeCat).empty)
      return;
    const t = editTarget(activeCat).transform;
    gesture = {
      cat: activeCat,
      id: e.pointerId,
      before: snap(),
      x: e.clientX,
      y: e.clientY,
      tx: t.x,
      ty: t.y,
      ratio: 512 / canvas.clientWidth,
    };
    canvas.setPointerCapture(e.pointerId);
  };
  canvas.onpointermove = (e) => {
    if (!gesture || gesture.id !== e.pointerId) return;
    const g = gesture;
    adoptAnimal(g.cat);
    const t = editTarget(g.cat)?.transform;
    if (!t) return;
    t.x = bounded(g.tx + (e.clientX - g.x) * g.ratio, ...limits.x, 0);
    t.y = bounded(g.ty + (e.clientY - g.y) * g.ratio, ...limits.y, 0);
    renderTransforms();
    redraw();
  };
  canvas.onpointerup = canvas.onlostpointercapture = () => {
    if (gesture) {
      record(gesture.before);
      gesture = null;
    }
  };
}
function bind() {
  enableCanvasDrag();
  bindAdjustments();
  $('originSelect').onchange = () => {
    sourceFilter = $('originSelect').value;
    page = 0;
    renderVariants();
  };
  $('layerSelect').onchange = () => {
    focusedLayer[activeCat] = Number($('layerSelect').value);
    showSelectionPage();
    renderVariants();
    renderTransforms();
  };
  $('removeLayer').onclick = () =>
    applyChange(() => {
      const index = layerIndex(activeCat);
      if (index >= 0) state.layers[activeCat].splice(index, 1);
      focusedLayer[activeCat] = Math.max(0, index - 1);
      showSelectionPage();
    });
  document.querySelectorAll('[data-group]').forEach(
    (b) =>
      (b.onclick = () => {
        activeGroup = b.dataset.group;
        changeCategory(groups[activeGroup][0]);
      }),
  );
  $('prev').onclick = () => {
    page--;
    renderVariants();
  };
  $('next').onclick = () => {
    page++;
    renderVariants();
  };
  $('undo').onclick = () => restore(past, future);
  $('redo').onclick = () => restore(future, past);
  $('shuffle').onclick = () =>
    applyChange(() => {
      state.edition++;
      state.eyeMode = 'original';
      delete state.legacyAnimal;
      for (const cat of adornments) {
        state.layers[cat] = [];
        if (Math.random() < 0.25) {
          const list = opts[cat];
          addLayer(cat, list[Math.floor(Math.random() * list.length)].id);
        }
      }
      for (const cat of singleSlots) {
        const list = opts[cat];
        if (
          optionalSlot(cat) &&
          Math.random() < (cat === 'glasses' ? 0.45 : 0.75)
        )
          state.picks[cat] = list[0].id;
        else {
          const visible = list.filter((o) => !o.empty);
          state.picks[cat] = (
            visible[Math.floor(Math.random() * visible.length)] || list[0]
          ).id;
        }
        state.transforms[cat] = newTransform();
      }
      showSelectionPage();
    });
  $('reference').onclick = () =>
    applyChange(() => {
      state = clone(initial);
      activeGroup = 'features';
      activeCat = 'eyes';
      sourceFilter = 'all';
      showSelectionPage();
    });
  $('grid').onclick = () => {
    const on = $('surface').classList.toggle('has-grid');
    $('grid').setAttribute('aria-pressed', on);
  };
  function expand() {
    const on = document
      .querySelector('.composition')
      .classList.toggle('expanded');
    document.body.classList.toggle('zoomed', on);
    $('expand').setAttribute(
      'aria-label',
      on ? 'Close expanded composition' : 'Expand composition',
    );
    $('expand').title = $('expand').getAttribute('aria-label');
    $('expand').setAttribute('aria-pressed', on);
  }
  $('expand').onclick = expand;
  document.addEventListener('keydown', (e) => {
    if ($('info').open) return;
    if (e.key === 'Escape' && document.body.classList.contains('zoomed'))
      expand();
    if (!ready || $('studio').hidden || e.target.tagName === 'INPUT') return;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') {
      e.preventDefault();
      e.shiftKey ? restore(future, past) : restore(past, future);
    }
  });
  bindRange('ink', (value) => {
    state.ink = value;
    $('inkValue').value = value + '%';
    renderVariants();
  });
  bindRange('dotSize', (value) => {
    state.dotSize = value;
    $('dotValue').value = value + ' px';
    renderVariants();
  });
  $('save').onclick = async () => {
    await pendingRender;
    if (!$('save').disabled) savePrint();
  };
  $('studioTab').onclick = $('back').onclick = () => showTab('studio');
  document.querySelector('.wordmark').onclick = (e) => {
    e.preventDefault();
    showTab('studio');
  };
  $('archiveTab').onclick = () => showTab('archive');
  $('about').onclick = () => dialog(false);
  $('credits').onclick = () => dialog(true);
  $('close').onclick = () => $('info').close();
  $('info').onclick = (e) => {
    if (e.target === $('info')) $('info').close();
  };
}
async function start() {
  setBusy(true);
  $('undo').disabled = $('redo').disabled = true;
  try {
    const libraries = await Promise.all(
      ['parts', 'adornments', 'specimens'].map(async (folder) => {
        const res = await fetch('assets/' + folder + '/library.json', {
          cache: 'no-cache',
        });
        if (!res.ok) throw new Error('Missing ' + folder + ' library');
        const library = await res.json();
        return { ...library, folder };
      }),
    );
    for (const cat of order) {
      const photos = libraries.flatMap((lib) =>
        (lib.parts[cat] || []).map((item) => ({
          ...item,
          origin:
            item.origin ||
            (lib.folder === 'specimens' && groups.features.includes(cat)
              ? 'animal'
              : lib.folder === 'parts'
                ? lib.sources[item.source].kind || 'photo'
                : 'object'),
          credit: { title: item.name, ...lib.sources[item.source] },
        })),
      );
      const clear = { id: 'none-' + cat, name: 'None', empty: true };
      opts[cat] = isAdornment(cat)
        ? photos
        : optionalSlot(cat)
          ? [clear, ...photos]
          : [...photos, clear];
      if (!photos.length) throw new Error('No photographic cutouts for ' + cat);
    }
    initial = {
      edition: 1,
      ink: 41,
      dotSize: 5,
      eyeMode: 'original',
      picks: {},
      transforms: {},
      layers: { tattoo: [], piercing: [], jewelry: [] },
    };
    for (const cat of singleSlots) {
      initial.picks[cat] = opts[cat][0].id;
      initial.transforms[cat] = newTransform();
    }
    const firstPrint = {
      chin: '001-0251',
      hair: 'gov-4',
      eyes: '001-0011',
      eyebrows: '001-0381',
      mouth: '001-0231',
      nose: 'gov-4',
      beard: 'gov-14',
      ears: '001-0191',
    };
    for (const [cat, source] of Object.entries(firstPrint)) {
      initial.picks[cat] = (
        opts[cat].find((p) => p.source === source) || opts[cat][0]
      ).id;
    }
    initial.transforms.eyes.scale = 108;
    initial.transforms.mouth.scale = 111;
    initial.picks.glasses = 'none-glasses';
    initial.picks.ears = 'none-ears';
    const launch = new URL(location.href);
    if (launch.searchParams.get('mix') === 'reference') {
      state = clone(initial);
      launch.searchParams.delete('mix');
      history.replaceState(null, '', launch);
    } else {
      state = checkedState(readLocal(draftKey, null));
    }
    ready = true;
    showSelectionPage();
    bind();
    renderArchive();
    setBusy(false);
    refresh();
  } catch (e) {
    $('loading').textContent =
      'Library unavailable. Open the studio through its web server and reload.';
    console.error(e);
  }
}
start();
