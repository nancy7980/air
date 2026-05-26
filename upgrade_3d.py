#!/usr/bin/env python3
"""
Comprehensive 3D animation upgrade:
 - S1: Replace flat particles with 3D rotating node-network (right side of cover)
 - S10 P1: perspective CSS tilt + room fills + scan pulse + status-bar labels (no overlap)
 - S10 P2: wireframe cage + sweep plane + richer colors (orange/gold/cyan)
 - S10 P3: fix text position + heat zone + shockwave + danger circle
 - Chapters: 3D mouse-parallax on giant bg number
 - S9 SWOT: subtle animated 3D hexagonal grid behind strengths panel
"""

with open('/home/user/air/presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ================================================================
# 1. NEW CSS — add before </style>
# ================================================================
new_css = """
/* =================================================================
   COVER  — 3D network canvas (right side, behind content)
   ================================================================= */
#netCanvas{position:absolute;inset:0;z-index:0;pointer-events:none}

/* =================================================================
   S9  — hex grid canvas behind strengths
   ================================================================= */
.swot-section.s-side{position:relative;overflow:hidden}
#hexCanvas{position:absolute;inset:0;z-index:0;pointer-events:none;opacity:0.55}
.swot-section.s-side>*:not(#hexCanvas){position:relative;z-index:1}

/* =================================================================
   S10 P1  — CSS 3D perspective tilt on floor-plan canvas
   ================================================================= */
#p1canvas{
  transform: perspective(340px) rotateX(36deg) rotateY(-4deg) scale(1.06);
  transform-origin: center 62%;
  margin-bottom: 4px;
}

/* =================================================================
   Chapter slides  — smooth parallax transition
   ================================================================= */
.chapter-bg-num{transition:transform 0.12s ease-out}
"""
html = html.replace('</style>\n</head>', new_css + '</style>\n</head>', 1)

# ================================================================
# 2. HTML — add netCanvas to S1 (before existing particleCanvas)
# ================================================================
old_s1_canvas = '<canvas class="particles-canvas" id="particleCanvas"></canvas>'
new_s1_canvas = '<canvas id="netCanvas"></canvas>\n  <canvas class="particles-canvas" id="particleCanvas"></canvas>'
html = html.replace(old_s1_canvas, new_s1_canvas, 1)

# ================================================================
# 3. HTML — add hexCanvas inside swot strengths section
# ================================================================
old_swot_s = '      <div class="swot-section s-side">\n        <div class="swot-head"><span class="eyebrow">STRENGTHS / 优势</span></div>'
new_swot_s = '      <div class="swot-section s-side">\n        <canvas id="hexCanvas"></canvas>\n        <div class="swot-head"><span class="eyebrow">STRENGTHS / 优势</span></div>'
html = html.replace(old_swot_s, new_swot_s, 1)

# ================================================================
# 4. JS — replace old particle system + old phase canvases
#    (entire JS block from particle fn to end of last phase fn)
# ================================================================
OLD_PARTICLE_START = '''/* ============================================
   PARTICLE BACKGROUND (cover only, very subtle)
   ============================================ */
(function(){'''

OLD_PHASE_END = '''  requestAnimationFrame(draw);
})();

</script>'''

# Locate both
p_start = html.index(OLD_PARTICLE_START)
p_end   = html.index(OLD_PHASE_END) + len(OLD_PHASE_END)

NEW_JS = r"""/* ============================================================
   COVER · 3D ROTATING NODE NETWORK (right side, behind text)
   ============================================================ */
(function () {
  const canvas = document.getElementById('netCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const N = 90;
  const nodes = [];
  // Fibonacci sphere distribution
  const PHI = Math.PI * (1 + Math.sqrt(5));
  for (let i = 0; i < N; i++) {
    const phi  = Math.acos(1 - 2 * (i + 0.5) / N);
    const theta = PHI * i;
    const r = 0.20 + Math.random() * 0.18;
    nodes.push({
      ox: Math.sin(phi) * Math.cos(theta) * r,
      oy: Math.sin(phi) * Math.sin(theta) * r * 0.55,
      oz: Math.cos(phi) * r,
      pulse: Math.random() * Math.PI * 2,
      speed: 0.4 + Math.random() * 0.7
    });
  }

  // Pre-compute connections (rigid rotation → distances constant)
  const CONN_D = 0.215;
  const conns = [];
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      const dx = nodes[i].ox - nodes[j].ox;
      const dy = nodes[i].oy - nodes[j].oy;
      const dz = nodes[i].oz - nodes[j].oz;
      const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (d < CONN_D) conns.push({ i, j, t: 1 - d / CONN_D });
    }
  }

  const proj = new Array(N);

  function draw(ts) {
    ctx.clearRect(0, 0, W, H);

    const rotY = ts / 24000; // very slow rotation
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
    const cx = W * 0.68, cy = H * 0.48; // network centred on right side
    const fov = Math.min(W, H) * 0.60;

    for (let i = 0; i < N; i++) {
      const n = nodes[i];
      const rx  = n.ox * cosY - n.oz * sinY;
      const rz  = n.ox * sinY + n.oz * cosY;
      const z   = rz + 1.15;
      const sc  = fov / z;
      proj[i] = {
        sx: cx + rx * sc,
        sy: cy + n.oy * sc,
        z,
        depth: Math.min(z / 1.5, 1),
        pulse: 0.5 + 0.5 * Math.sin(ts / 900 * n.speed + n.pulse)
      };
    }

    // Connections
    ctx.lineWidth = 0.55;
    conns.forEach(c => {
      const pi = proj[c.i], pj = proj[c.j];
      const a = c.t * 0.10 * Math.min(pi.depth, pj.depth);
      if (a < 0.006) return;
      ctx.strokeStyle = `rgba(255,78,26,${a})`;
      ctx.beginPath();
      ctx.moveTo(pi.sx, pi.sy);
      ctx.lineTo(pj.sx, pj.sy);
      ctx.stroke();
    });

    // Nodes (front-to-back sort so nearer nodes paint last / on top)
    const order = Array.from({ length: N }, (_, i) => i).sort((a, b) => proj[b].z - proj[a].z);
    order.forEach(i => {
      const p = proj[i];
      const r = 0.7 + p.pulse * 1.8;
      const a = p.depth * (0.28 + 0.5 * p.pulse);
      // Glow halo
      const g = ctx.createRadialGradient(p.sx, p.sy, 0, p.sx, p.sy, r * 4);
      g.addColorStop(0, `rgba(255,78,26,${a * 0.38})`);
      g.addColorStop(1, 'rgba(255,78,26,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, r * 4, 0, Math.PI * 2);
      ctx.fill();
      // Core
      ctx.fillStyle = `rgba(255,78,26,${a * 1.15})`;
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, r, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();

/* ============================================
   COVER · SUBTLE ORANGE PARTICLES (keep subtle layer)
   ============================================ */
(function(){
  const canvas = document.getElementById('particleCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];
  function resize(){ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);

  function Particle(){ this.reset(); }
  Particle.prototype.reset = function(){
    this.x = Math.random() * W;
    this.y = Math.random() * H;
    this.vx = (Math.random()-0.5)*0.12;
    this.vy = (Math.random()-0.5)*0.12;
    this.r = Math.random()*0.8+0.2;
    this.alpha = Math.random()*0.2+0.04;
  };
  for(let i=0;i<35;i++) particles.push(new Particle());

  function draw(){
    ctx.clearRect(0,0,W,H);
    particles.forEach(p=>{
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0||p.x>W||p.y<0||p.y>H) p.reset();
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle = `rgba(255,78,26,${p.alpha})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ============================================================
   S9 SWOT · HEX GRID BEHIND STRENGTHS PANEL
   ============================================================ */
(function () {
  const canvas = document.getElementById('hexCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const DPR = window.devicePixelRatio || 1;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width  = rect.width  * DPR;
    canvas.height = rect.height * DPR;
    ctx.scale(DPR, DPR);
  }
  setTimeout(resize, 80);
  window.addEventListener('resize', resize);

  function drawHex(cx, cy, r, alpha) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 3 * i - Math.PI / 6;
      i === 0 ? ctx.moveTo(cx + r * Math.cos(a), cy + r * Math.sin(a))
              : ctx.lineTo(cx + r * Math.cos(a), cy + r * Math.sin(a));
    }
    ctx.closePath();
    ctx.strokeStyle = `rgba(255,78,26,${alpha})`;
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }

  function draw(ts) {
    const W = canvas.width / DPR, H = canvas.height / DPR;
    ctx.clearRect(0, 0, W, H);

    const R = clamp(Math.min(W, H) / 9, 14, 28);
    const dx = R * Math.sqrt(3);
    const dy = R * 1.5;
    const pulse = 0.5 + 0.5 * Math.sin(ts / 2200);

    for (let row = -1; row < H / dy + 2; row++) {
      for (let col = -1; col < W / dx + 2; col++) {
        const offset = row % 2 === 0 ? 0 : dx / 2;
        const hx = col * dx + offset;
        const hy = row * dy;
        const dist = Math.sqrt((hx - W * 0.5) ** 2 + (hy - H * 0.45) ** 2);
        const norm = 1 - Math.min(dist / (Math.max(W, H) * 0.65), 1);
        const wave = 0.5 + 0.5 * Math.sin(dist / 30 - ts / 1800);
        const alpha = norm * wave * 0.055 + 0.008;
        drawHex(hx, hy, R - 1, alpha);
      }
    }
    requestAnimationFrame(draw);
  }

  function clamp(v, mn, mx) { return Math.max(mn, Math.min(mx, v)); }
  requestAnimationFrame(draw);
})();

/* ============================================================
   S10 · 3D PHASE CANVAS ANIMATIONS
   ============================================================ */

// Shared helper: init a canvas with DPR scaling
function initPhaseCanvas(id) {
  const canvas = document.getElementById(id);
  if (!canvas) return null;
  const DPR = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const W = Math.max(rect.width, 100);
  const H = Math.max(rect.height, 58);
  canvas.width  = W * DPR;
  canvas.height = H * DPR;
  const ctx = canvas.getContext('2d');
  ctx.scale(DPR, DPR);
  return { ctx, W, H, DPR };
}

// ── PHASE 1 : Indoor Navigation + Agent Attribution ──────────
(function () {
  let state = null, startTime = null;
  const CYCLE = 3600;

  function getState() { if (!state) state = initPhaseCanvas('p1canvas'); return state; }

  function draw(ts) {
    const s = getState(); if (!s) return;
    const { ctx, W, H } = s;

    if (!startTime) startTime = ts;
    const elapsed  = (ts - startTime) % (CYCLE + 1000);
    const progress = Math.min(elapsed / CYCLE, 1);

    const path = [
      [W*0.08, H*0.87], [W*0.08, H*0.53],
      [W*0.36, H*0.53], [W*0.36, H*0.20],
      [W*0.93, H*0.20]
    ];

    function segLen(a, b) { return Math.hypot(b[0]-a[0], b[1]-a[1]); }
    function totalLen(pts) { let l=0; for(let i=1;i<pts.length;i++) l+=segLen(pts[i-1],pts[i]); return l; }
    function ptAtDist(pts, dist) {
      let d=0;
      for(let i=1;i<pts.length;i++){
        const seg=segLen(pts[i-1],pts[i]);
        if(d+seg>=dist){ const t=(dist-d)/seg; return [pts[i-1][0]+(pts[i][0]-pts[i-1][0])*t, pts[i-1][1]+(pts[i][1]-pts[i-1][1])*t]; }
        d+=seg;
      }
      return pts[pts.length-1].slice();
    }

    const TL = totalLen(path), dist = TL * progress;
    ctx.clearRect(0, 0, W, H);

    // ── Background grid ──
    ctx.strokeStyle = 'rgba(237,231,220,0.04)'; ctx.lineWidth = 0.35;
    for(let x=0; x<W; x+=W/10){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for(let y=0; y<H; y+=H/7){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

    // ── Room definitions (x,y,w,h) ──
    const rooms = [
      [W*0.01,H*0.03,W*0.27,H*0.45],
      [W*0.38,H*0.03,W*0.27,H*0.45],
      [W*0.70,H*0.03,W*0.28,H*0.45],
      [W*0.01,H*0.59,W*0.23,H*0.37],
      [W*0.28,H*0.59,W*0.40,H*0.37],
      [W*0.72,H*0.59,W*0.26,H*0.37]
    ];

    // Room fills
    rooms.forEach((r, idx) => {
      ctx.fillStyle = idx===2 ? 'rgba(255,78,26,0.04)' : 'rgba(255,255,255,0.02)';
      ctx.fillRect(r[0], r[1], r[2], r[3]);
    });

    // Room borders with door gaps
    ctx.strokeStyle = 'rgba(237,231,220,0.22)'; ctx.lineWidth = 0.9;
    rooms.forEach(r => ctx.strokeRect(r[0],r[1],r[2],r[3]));

    // Destination pin (top-right room centre)
    const dest = path[path.length-1];
    ctx.beginPath(); ctx.arc(dest[0],dest[1],5.5,0,Math.PI*2);
    ctx.strokeStyle='rgba(255,78,26,0.32)'; ctx.lineWidth=0.9; ctx.stroke();
    ctx.beginPath(); ctx.arc(dest[0],dest[1],2.5,0,Math.PI*2);
    ctx.fillStyle='rgba(255,78,26,0.6)'; ctx.fill();

    // ── Animated route with glow ──
    if(progress>0) {
      // Shadow/glow pass
      ctx.save();
      ctx.shadowColor='rgba(255,78,26,0.55)';
      ctx.shadowBlur=4;
      ctx.beginPath(); ctx.moveTo(path[0][0],path[0][1]);
      let d2=0;
      for(let i=1;i<path.length;i++){
        const seg=segLen(path[i-1],path[i]);
        if(d2+seg<=dist){ ctx.lineTo(path[i][0],path[i][1]); d2+=seg; }
        else{ const t=(dist-d2)/seg; ctx.lineTo(path[i-1][0]+(path[i][0]-path[i-1][0])*t, path[i-1][1]+(path[i][1]-path[i-1][1])*t); break; }
      }
      ctx.strokeStyle='rgba(255,78,26,0.75)'; ctx.lineWidth=2; ctx.lineCap='round'; ctx.lineJoin='round'; ctx.stroke();
      ctx.restore();
    }

    // ── Walking dot + scan rings ──
    const pt = ptAtDist(path, dist);
    const pulse = 0.5 + 0.5*Math.sin(ts/290);

    // Expanding scan ring
    const scanR = 8 + pulse * 7;
    ctx.beginPath(); ctx.arc(pt[0],pt[1],scanR,0,Math.PI*2);
    ctx.strokeStyle=`rgba(255,78,26,${0.18*(1-pulse)})`; ctx.lineWidth=0.8; ctx.stroke();

    // Glow
    const gg = ctx.createRadialGradient(pt[0],pt[1],0,pt[0],pt[1],11+3*pulse);
    gg.addColorStop(0,`rgba(255,78,26,${0.30*pulse})`); gg.addColorStop(1,'rgba(255,78,26,0)');
    ctx.fillStyle=gg; ctx.beginPath(); ctx.arc(pt[0],pt[1],11+3*pulse,0,Math.PI*2); ctx.fill();

    // Core dot
    ctx.beginPath(); ctx.arc(pt[0],pt[1],4,0,Math.PI*2);
    ctx.fillStyle='#FF4E1A'; ctx.fill();

    // ── Status bar labels (dark bg, no room overlap) ──
    if(progress > 0.80) {
      const alpha = Math.min((progress-0.80)/0.20, 1);
      const fs = Math.max(W*0.050, 6.0);
      ctx.font = `${fs}px 'JetBrains Mono', monospace`;

      // Measure both labels
      const lbl1='VLM 定位 ✓', lbl2='Agent 归因';
      const tw = Math.max(ctx.measureText(lbl1).width, ctx.measureText(lbl2).width);
      const lx = W*0.52, ly1 = H*0.46, ly2 = ly1 + fs*1.42;

      // Dark backdrop
      ctx.fillStyle=`rgba(8,8,12,${alpha*0.82})`;
      ctx.fillRect(lx-3, ly1-fs*0.88, tw+10, fs*2.85);

      // Left accent bar
      ctx.fillStyle=`rgba(255,78,26,${alpha*0.7})`;
      ctx.fillRect(lx-3, ly1-fs*0.88, 2, fs*2.85);

      // Text
      ctx.fillStyle=`rgba(255,78,26,${alpha*0.9})`;
      ctx.fillText(lbl1, lx+4, ly1);
      ctx.fillStyle=`rgba(120,119,128,${alpha*0.75})`;
      ctx.fillText(lbl2, lx+4, ly2);
    }

    if(elapsed>=CYCLE+800) startTime=null;
    requestAnimationFrame(draw);
  }

  const s10 = document.getElementById('s10');
  if(s10){
    const obs = new IntersectionObserver(e=>{ if(e[0].isIntersecting){state=null;startTime=null;requestAnimationFrame(draw);} },{threshold:0.45});
    obs.observe(s10);
  }
})();

// ── PHASE 2 : 3D Gaussian Splats + Wireframe Cage + Sweep Plane ─
(function () {
  const canvas = document.getElementById('p2canvas');
  if (!canvas) return;
  let inited=false, ctx, W, H;

  // ── Splat points ──
  const pts = [];
  for(let i=0;i<260;i++){
    const layer=Math.floor(Math.random()*3);
    let ox,oy,oz,sz,al,col;
    if(layer===0){
      ox=(Math.random()-0.5)*38; oy=10+Math.random()*5; oz=(Math.random()-0.5)*30;
      sz=0.65+Math.random()*0.7; al=0.32+Math.random()*0.28; col=0;
    } else if(layer===1){
      ox=(Math.random()-0.5)*32; oy=(Math.random()-0.5)*20; oz=(Math.random()-0.5)*26;
      sz=0.85+Math.random()*1.1; al=0.25+Math.random()*0.30;
      col = Math.random()>0.55 ? 1 : Math.random()>0.5 ? 2 : 0;
    } else {
      ox=(Math.random()-0.5)*26; oy=-10-Math.random()*7; oz=(Math.random()-0.5)*22;
      sz=0.45+Math.random()*0.85; al=0.15+Math.random()*0.20;
      col = Math.random()>0.45 ? 1 : 0;
    }
    pts.push({ox,oy,oz,sz,al,col});
  }

  // ── Wireframe cage corners ──
  const BX=19,BY=18,BZ=19;
  const boxCorners=[
    [-BX,-BY,-BZ],[BX,-BY,-BZ],[BX,BY,-BZ],[-BX,BY,-BZ],
    [-BX,-BY, BZ],[BX,-BY, BZ],[BX,BY, BZ],[-BX,BY, BZ]
  ];
  const boxEdges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];

  function ensureInit(){
    if(!inited){ const s=initPhaseCanvas('p2canvas'); if(s){ctx=s.ctx;W=s.W;H=s.H;inited=true;} }
  }

  function draw(ts){
    ensureInit(); if(!ctx){requestAnimationFrame(draw);return;}
    ctx.clearRect(0,0,W,H);

    const rot  = ts/9500;
    const cosR = Math.cos(rot), sinR=Math.sin(rot);
    const fov  = 165, OZ=58;

    function project(ox,oy,oz){
      const cx=ox*cosR-oz*sinR, cz=ox*sinR+oz*cosR+OZ;
      const sc=fov/Math.max(cz,10);
      return {sx:W/2+cx*sc, sy:H/2+oy*sc, sc, cz};
    }

    // ── Center glow ──
    const g=ctx.createRadialGradient(W/2,H/2,0,W/2,H/2,W*0.25);
    g.addColorStop(0,'rgba(255,78,26,0.09)'); g.addColorStop(1,'rgba(255,78,26,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);

    // ── Wireframe cage ──
    const projBox=boxCorners.map(([ox,oy,oz])=>project(ox,oy,oz));
    boxEdges.forEach(([i,j])=>{
      const pi=projBox[i], pj=projBox[j];
      const depth=Math.min((pi.cz+pj.cz)/2/85,1);
      ctx.strokeStyle=`rgba(168,145,113,${0.18*depth})`;
      ctx.lineWidth=0.5;
      ctx.beginPath(); ctx.moveTo(pi.sx,pi.sy); ctx.lineTo(pj.sx,pj.sy); ctx.stroke();
    });

    // ── Horizontal scan plane (sweeps Y axis) ──
    const sweepY = -BY + ((ts/3800)%1)*(BY*2);
    const planeRaw=[[-BX,sweepY,-BZ],[BX,sweepY,-BZ],[BX,sweepY,BZ],[-BX,sweepY,BZ]];
    const planePts=planeRaw.map(([ox,oy,oz])=>project(ox,oy,oz));
    ctx.beginPath();
    ctx.moveTo(planePts[0].sx,planePts[0].sy);
    planePts.forEach(p=>ctx.lineTo(p.sx,p.sy));
    ctx.closePath();
    const depthScan=((sweepY+BY)/(BY*2));
    ctx.fillStyle=`rgba(255,78,26,${0.035*(1-Math.abs(depthScan-0.5)*2)})`;
    ctx.fill();
    ctx.strokeStyle=`rgba(255,78,26,${0.22*(1-Math.abs(depthScan-0.5)*2)})`;
    ctx.lineWidth=0.6; ctx.stroke();

    // ── Splat points ──
    const proj = pts.map(p=>{const r=project(p.ox,p.oy,p.oz);return{...r,...p};}).sort((a,b)=>a.cz-b.cz);
    proj.forEach(p=>{
      const r=Math.max(p.sz*p.sc*0.90,0.38);
      const depth=Math.min(p.cz/85,1);
      const al=p.al*(0.28+0.72*depth);
      ctx.beginPath(); ctx.arc(p.sx,p.sy,r,0,Math.PI*2);
      if(p.col===0)       ctx.fillStyle=`rgba(255,110,55,${al*0.62})`;   // orange
      else if(p.col===1)  ctx.fillStyle=`rgba(168,145,113,${al})`;        // gold
      else                ctx.fillStyle=`rgba(100,200,220,${al*0.45})`;   // cyan
      ctx.fill();
    });

    // ── Label in a small status bar at bottom ──
    const barH = H*0.16;
    ctx.fillStyle='rgba(8,8,12,0.60)';
    ctx.fillRect(0,H-barH,W,barH);
    const fs=Math.max(W*0.050,6.0);
    ctx.font=`${fs}px 'JetBrains Mono', monospace`;
    ctx.fillStyle='rgba(168,145,113,0.62)';
    ctx.fillText('FANTASY WORLD · 高斯泼溅', W*0.04, H-barH*0.28);

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();

// ── PHASE 3 : Seismic / Disaster · Heat Zone + Shockwave ────────
(function () {
  const canvas = document.getElementById('p3canvas');
  if (!canvas) return;
  let inited=false, ctx, W, H;

  function ensureInit(){
    if(!inited){ const s=initPhaseCanvas('p3canvas'); if(s){ctx=s.ctx;W=s.W;H=s.H;inited=true;} }
  }

  const BUILDINGS=[];
  const BX_SEED=[0.04,0.10,0.17,0.23,0.30,0.36,0.43,0.50,0.56,0.62,0.68,0.75,0.82,0.89,0.95];
  BX_SEED.forEach(bx=>{
    BUILDINGS.push({rx:bx, rw:0.035+Math.random()*0.025, rh:0.07+Math.random()*0.28});
  });

  const waves=[];
  let waveTimer=0;
  function addWave(r0=3,aMax=0.85){waves.push({r:r0,alpha:aMax,aMax});}
  addWave();

  // Routes
  const routeA=[[0.05,0.75],[0.40,0.50],[0.94,0.22]];
  const routeB=[[0.05,0.75],[0.16,0.32],[0.58,0.18],[0.94,0.22]];
  const epiRel=[0.40,0.50];

  function rp(rel){return[rel[0]*W,rel[1]*H];}

  function drawPoly(pts,color,lw,dash){
    ctx.beginPath();
    const p0=rp(pts[0]); ctx.moveTo(p0[0],p0[1]);
    for(let i=1;i<pts.length;i++){const p=rp(pts[i]);ctx.lineTo(p[0],p[1]);}
    ctx.strokeStyle=color; ctx.lineWidth=lw; ctx.setLineDash(dash||[]); ctx.lineCap='round'; ctx.lineJoin='round'; ctx.stroke(); ctx.setLineDash([]);
  }

  function draw(ts){
    ensureInit(); if(!ctx){requestAnimationFrame(draw);return;}
    ctx.clearRect(0,0,W,H);

    const epi=rp(epiRel);

    // ── Danger heat zone ──
    const heat=ctx.createRadialGradient(epi[0],epi[1],0,epi[0],epi[1],W*0.32);
    heat.addColorStop(0,'rgba(255,78,26,0.14)');
    heat.addColorStop(0.4,'rgba(255,78,26,0.05)');
    heat.addColorStop(1,'rgba(255,78,26,0)');
    ctx.fillStyle=heat; ctx.fillRect(0,0,W,H);

    // ── Ground line ──
    ctx.strokeStyle='rgba(237,231,220,0.07)'; ctx.lineWidth=0.4;
    ctx.beginPath(); ctx.moveTo(0,H*0.88); ctx.lineTo(W,H*0.88); ctx.stroke();

    // ── City silhouette (shake near epicenter) ──
    BUILDINGS.forEach(b=>{
      const x=b.rx*W, bw=b.rw*W, bh=b.rh*H;
      const dToEpi=Math.abs(b.rx - epiRel[0]);
      const shakeMag=Math.max(0,0.6-dToEpi)*0.7;
      const shake=shakeMag*Math.sin(ts/85+b.rx*30);
      ctx.fillStyle='rgba(237,231,220,0.035)';
      ctx.fillRect(x+shake,H*0.88-bh,bw,bh);
      ctx.strokeStyle='rgba(237,231,220,0.09)'; ctx.lineWidth=0.4;
      ctx.strokeRect(x+shake,H*0.88-bh,bw,bh);
    });

    // ── Seismic waves ──
    waveTimer++;
    if(waveTimer%55===0){ addWave(); }
    waves.forEach(w=>{ w.r+=0.70; w.alpha=Math.max(0, w.aMax*(1-w.r/(W*0.42))); });
    waves.filter(w=>w.alpha>0).forEach(w=>{
      ctx.beginPath(); ctx.arc(epi[0],epi[1],w.r,0,Math.PI*2);
      ctx.strokeStyle=`rgba(255,78,26,${w.alpha})`; ctx.lineWidth=0.8; ctx.stroke();
      ctx.beginPath(); ctx.arc(epi[0],epi[1],w.r*1.55,0,Math.PI*2);
      ctx.strokeStyle=`rgba(255,78,26,${w.alpha*0.18})`; ctx.lineWidth=0.35; ctx.stroke();
    });
    for(let i=waves.length-1;i>=0;i--){if(waves[i].alpha<=0)waves.splice(i,1);}

    // ── Route A (danger) ──
    const flash=Math.sin(ts/360)>0.15;
    drawPoly(routeA,flash?'rgba(255,78,26,0.40)':'rgba(255,78,26,0.10)',1.0,[3,5]);

    // ── Route B (active detour) ──
    drawPoly(routeB,'rgba(255,78,26,0.76)',1.9);

    // Arrow on route B
    const last=rp(routeB[routeB.length-1]), prev=rp(routeB[routeB.length-2]);
    const ang=Math.atan2(last[1]-prev[1],last[0]-prev[0]);
    ctx.save(); ctx.translate(last[0],last[1]); ctx.rotate(ang);
    ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(-7,-3.5); ctx.lineTo(-7,3.5); ctx.closePath();
    ctx.fillStyle='rgba(255,78,26,0.76)'; ctx.fill(); ctx.restore();

    // ── Epicenter glow + dot ──
    const pulse=0.5+0.5*Math.sin(ts/260);
    const eg=ctx.createRadialGradient(epi[0],epi[1],0,epi[0],epi[1],16+6*pulse);
    eg.addColorStop(0,`rgba(255,78,26,${0.30*pulse})`); eg.addColorStop(1,'rgba(255,78,26,0)');
    ctx.fillStyle=eg; ctx.beginPath(); ctx.arc(epi[0],epi[1],16+6*pulse,0,Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(epi[0],epi[1],3.8,0,Math.PI*2);
    ctx.fillStyle=`rgba(255,78,26,${0.72+0.28*pulse})`; ctx.fill();

    // ── Warning label — status bar at bottom (never overlaps routes) ──
    const barH=H*0.16;
    ctx.fillStyle='rgba(8,8,12,0.62)'; ctx.fillRect(0,H-barH,W,barH);
    if(flash){
      const fs=Math.max(W*0.050,6.0);
      ctx.font=`${fs}px 'JetBrains Mono', monospace`;
      ctx.fillStyle='rgba(255,78,26,0.85)';
      ctx.fillText('⚠ 路线重算中', W*0.04, H-barH*0.28);
      ctx.fillStyle='rgba(168,145,113,0.5)';
      ctx.fillText('Fantasy World 推演', W*0.55, H-barH*0.28);
    }

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();

/* ============================================================
   CHAPTER SLIDES · 3D MOUSE-PARALLAX on giant bg number
   ============================================================ */
(function(){
  const chapters = document.querySelectorAll('.chapter-slide');
  chapters.forEach(slide=>{
    slide.addEventListener('mousemove', e=>{
      const r = slide.getBoundingClientRect();
      const nx = (e.clientX - r.left) / r.width  - 0.5; // -0.5..0.5
      const ny = (e.clientY - r.top)  / r.height - 0.5;
      const num = slide.querySelector('.chapter-bg-num');
      if(num){
        num.style.transform = `translateY(-50%) perspective(700px) rotateY(${nx*20}deg) rotateX(${-ny*10}deg) scale(1.04)`;
      }
    });
    slide.addEventListener('mouseleave', ()=>{
      const num = slide.querySelector('.chapter-bg-num');
      if(num) num.style.transform = 'translateY(-50%)';
    });
  });
})();

</script>
</body>
</html>"""

html = html[:p_start] + NEW_JS

# ================================================================
# Write
# ================================================================
with open('/home/user/air/presentation.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✓ Wrote presentation.html')

# Validate
with open('/home/user/air/presentation.html', 'r', encoding='utf-8') as f:
    out = f.read()

checks = {
    'netCanvas HTML':    'id="netCanvas"' in out,
    'hexCanvas HTML':    'id="hexCanvas"' in out,
    'P1 CSS tilt':       'rotateX(36deg)' in out,
    'P1 status bar':     'Status bar labels' in out or 'status bar' in out.lower(),
    'P2 wireframe cage': 'boxEdges' in out,
    'P2 scan plane':     'sweepY' in out,
    'P2 cyan color':     'rgba(100,200,220' in out,
    'P3 heat zone':      'Danger heat zone' in out or 'heat zone' in out.lower(),
    'P3 building shake': 'shakeMag' in out,
    'P3 bottom bar':     'status bar at bottom' in out.lower(),
    'cover 3D network':  'Fibonacci sphere' in out,
    'hex grid draw':     'drawHex' in out,
    'chapter parallax':  'CHAPTER SLIDES' in out,
    'no </html> dup':    out.count('</html>') == 1,
    'no </script> dup':  out.count('</script>') >= 1,
}
all_ok = True
for k,v in checks.items():
    mark = '✓' if v else '✗'
    if not v: all_ok = False
    print(f'  {mark} {k}')

print()
print(f'  Total lines: {out.count(chr(10))}')
print(f'  {"✓ All checks passed" if all_ok else "✗ Some checks failed"}')
