#!/usr/bin/env python3
"""
Apply S9 tech references + 3D effects, S10 premium canvas animations, S13 update.
"""
with open('/home/user/air/presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. NEW CSS — insert before </style>
# ============================================================
new_css = """
/* =================================================================
   S9 · TECH CHIP BAR
   ================================================================= */
.tech-bar{display:flex;gap:clamp(4px,0.8vw,8px);flex-wrap:wrap;padding:clamp(5px,1.2vh,9px) 0 0;border-top:1px solid var(--line);margin-top:clamp(5px,1.2vh,8px)}
.tech-chip{display:inline-flex;align-items:center;gap:5px;background:rgba(255,78,26,0.055);border:1px solid rgba(255,78,26,0.2);border-radius:3px;padding:3px 8px;font-family:'JetBrains Mono',monospace;font-size:clamp(0.55rem,0.63vw,0.61rem);color:var(--orange-dim);position:relative;overflow:hidden;white-space:nowrap}
.tech-chip::after{content:'';position:absolute;inset:0;background:linear-gradient(105deg,transparent 10%,rgba(255,78,26,0.16) 50%,transparent 90%);transform:translateX(-120%);animation:chip-scan 3.8s linear infinite}
.tech-chip:nth-child(2)::after{animation-delay:.95s}
.tech-chip:nth-child(3)::after{animation-delay:1.9s}
.tech-chip:nth-child(4)::after{animation-delay:2.85s}
@keyframes chip-scan{0%{transform:translateX(-120%)}100%{transform:translateX(320%)}}
.tech-chip-dot{width:4px;height:4px;border-radius:50%;background:var(--orange);box-shadow:0 0 4px var(--orange);animation:chip-dot-pulse 2s ease-in-out infinite;flex-shrink:0}
.tech-chip:nth-child(2) .tech-chip-dot{animation-delay:.5s}
.tech-chip:nth-child(3) .tech-chip-dot{animation-delay:1s}
.tech-chip:nth-child(4) .tech-chip-dot{animation-delay:1.5s}
@keyframes chip-dot-pulse{0%,100%{opacity:1;box-shadow:0 0 4px var(--orange)}50%{opacity:0.2;box-shadow:0 0 2px var(--orange)}}

/* =================================================================
   S10 · 3D ROADMAP CANVAS CONTAINERS
   ================================================================= */
.rm-canvas{width:100%;display:block;border-radius:2px;cursor:default;height:clamp(58px,9.5vh,90px)}
.rm-phase.p1 .rm-canvas{border:1px solid rgba(255,78,26,0.15)}
.rm-phase.p2 .rm-canvas{border:1px solid rgba(168,145,113,0.15)}
.rm-phase.p3 .rm-canvas{border:1px solid rgba(255,78,26,0.2)}
"""

html = html.replace('</style>\n</head>', new_css + '</style>\n</head>', 1)

# ============================================================
# 2. S9 — update strength descriptions to reference actual tech
# ============================================================

# S/01: Fantasy World
old01 = '            <p class="swot-item-desc">170M+ DAU + 实时路况 + 200M+ POI——十余年用户积累的飞轮，Google 在中国不可用，百度数据规模落后</p>'
new01 = '            <p class="swot-item-desc">170M+ DAU · 实时路况 · 200M+ POI，加之自研 <em style="font-style:normal;color:var(--orange-dim)">Fantasy World</em> 持续三维建图——地图数据飞轮十年积累，Google 在中国不可用，百度规模落后</p>'

# S/02: Qwen / VLM
old02 = '            <p class="swot-item-desc">直连阿里大模型与阿里云算力，无需第三方 API——独立导航公司在 AI 时代没有这个条件</p>'
new02 = '            <p class="swot-item-desc">直连 <em style="font-style:normal;color:var(--orange-dim)">通义千问 (Qwen)</em> 与阿里云 GPU 算力，VLM 视觉语言模型内部调用——独立导航公司在 AI 时代没有这个条件</p>'

# S/04: Gaussian Splatting
old04 = '            <p class="swot-item-desc">春运、演唱会散场、节假日商圈——场景密度和极端情况多样性是国际模型无法获得的训练素材</p>'
new04 = '            <p class="swot-item-desc">春运 · 演唱会散场 · 节假日商圈——极端场景信号密度无可比拟，配合 <em style="font-style:normal;color:var(--orange-dim)">高斯泼溅</em> 三维重建积累，国际模型难以复制</p>'

html = html.replace(old01, new01, 1)
html = html.replace(old02, new02, 1)
html = html.replace(old04, new04, 1)

# ============================================================
# 3. S9 — add tech chip bar after swot-verdict
# ============================================================
old_verdict = '''          <div class="swot-verdict">
            <strong>战略定位</strong>　不做全球 3D，不追赶智驾。<br>做中国出行链路上<em>数据最密、生态最全</em>的空间智能平台。
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- =============================================
     SLIDE 6 · COMPETITORS'''

new_verdict = '''          <div class="swot-verdict">
            <strong>战略定位</strong>　不做全球 3D，不追赶智驾。<br>做中国出行链路上<em>数据最密、生态最全</em>的空间智能平台。
          </div>
          <div class="tech-bar reveal d6">
            <span class="tech-chip"><span class="tech-chip-dot"></span>Fantasy World</span>
            <span class="tech-chip"><span class="tech-chip-dot"></span>Qwen · VLM</span>
            <span class="tech-chip"><span class="tech-chip-dot"></span>高斯泼溅</span>
            <span class="tech-chip"><span class="tech-chip-dot"></span>阿里云 GPU</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- =============================================
     SLIDE 6 · COMPETITORS'''

html = html.replace(old_verdict, new_verdict, 1)

# ============================================================
# 4. S10 — Phase 1: replace SVG art + update tagline + item 2
# ============================================================
old_p1 = '''      <div class="rm-phase p1 reveal d2">
        <div class="rm-num">PHASE 01 / 0–12 MO</div>
        <div class="rm-period">近场可验证</div>
        <div class="rm-tagline">让用户感受到「高德懂我在哪 + 懂我为什么」</div>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">室内连续导航：停车场 / 地铁站 / 商圈楼层级引导</div>
          <div class="rm-item">路线推荐归因：每次导航附带理由卡片</div>
          <div class="rm-item">复杂路口风险提示：「预计延误 8 分钟，建议绕行」</div>
          <div class="rm-art"><svg viewBox="0 0 64 42" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:60px"><circle cx="32" cy="21" r="16" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.4"/><circle cx="32" cy="21" r="10" stroke="currentColor" stroke-width="0.9" stroke-opacity="0.6"/><circle cx="32" cy="21" r="4" stroke="currentColor" stroke-width="1.2"/><line x1="32" y1="2" x2="32" y2="11" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.4"/><line x1="32" y1="31" x2="32" y2="40" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.4"/><line x1="12" y1="21" x2="21" y2="21" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.4"/><line x1="43" y1="21" x2="52" y2="21" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.4"/></svg></div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>室内定位准确率 ↑ 采纳率 ↑</div>
      </div>'''

new_p1 = '''      <div class="rm-phase p1 reveal d2">
        <div class="rm-num">PHASE 01 / 0–12 MO</div>
        <div class="rm-period">近场可验证</div>
        <div class="rm-tagline">VLM 识图定位 + Qwen 归因解释，让导航「懂我在哪、懂我为什么」</div>
        <canvas id="p1canvas" class="rm-canvas"></canvas>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">室内连续导航：停车场 / 地铁站 / 商圈楼层级引导</div>
          <div class="rm-item">Agent 归因解释：VLM 识图 + Qwen 生成可读理由卡</div>
          <div class="rm-item">复杂路口风险：「预计延误 8 min，建议绕行」</div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>室内定位准确率 ↑ 归因采纳率 ↑</div>
      </div>'''

html = html.replace(old_p1, new_p1, 1)

# ============================================================
# 5. S10 — Phase 2: replace SVG art + update tagline + items
# ============================================================
old_p2 = '''      <div class="rm-phase p2 reveal d3">
        <div class="rm-num">PHASE 02 / 1–2 YR</div>
        <div class="rm-period">3D 空间铺开</div>
        <div class="rm-tagline">核心枢纽三维化，主动出行规划落地</div>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">Top-100 枢纽三维场景上线（机场/高铁站/商圈）</div>
          <div class="rm-item">主动规划：感知场景变化，提前推送规避路线</div>
          <div class="rm-item">AR 空间导航：相机画面实时叠加路径指引</div>
          <div class="rm-art"><svg viewBox="0 0 80 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:72px"><circle cx="12" cy="16" r="5" stroke="currentColor" stroke-width="1"/><circle cx="40" cy="16" r="5" stroke="currentColor" stroke-width="1"/><circle cx="68" cy="16" r="5" stroke="currentColor" stroke-width="1"/><line x1="17" y1="16" x2="35" y2="16" stroke="currentColor" stroke-width="0.9" stroke-opacity="0.5"/><line x1="45" y1="16" x2="63" y2="16" stroke="currentColor" stroke-width="0.9" stroke-opacity="0.5"/><polyline points="30,12.5 35,16 30,19.5" stroke="currentColor" stroke-width="0.9" fill="none" stroke-opacity="0.5"/><polyline points="58,12.5 63,16 58,19.5" stroke="currentColor" stroke-width="0.9" fill="none" stroke-opacity="0.5"/></svg></div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>3D覆盖城市数 ↑ ETA误差 ↓</div>
      </div>'''

new_p2 = '''      <div class="rm-phase p2 reveal d3">
        <div class="rm-num">PHASE 02 / 1–2 YR</div>
        <div class="rm-period">3D 空间铺开</div>
        <div class="rm-tagline">Fantasy World + 高斯泼溅，Top-100 枢纽全面三维化</div>
        <canvas id="p2canvas" class="rm-canvas"></canvas>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">高斯泼溅三维重建：机场 / 高铁站 / 商圈室内外建模</div>
          <div class="rm-item">Fantasy World 主动推演：感知场景变化提前规避</div>
          <div class="rm-item">AR 空间导航：相机实时叠加楼层路径 + 指引</div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>3D枢纽覆盖数 ↑ ETA误差 ↓</div>
      </div>'''

html = html.replace(old_p2, new_p2, 1)

# ============================================================
# 6. S10 — Phase 3: replace SVG art + update tagline
# ============================================================
old_p3 = '''      <div class="rm-phase p3 reveal d4">
        <div class="rm-num">PHASE 03 / 2–3 YR+</div>
        <div class="rm-period">灾难预演 · 城市级</div>
        <div class="rm-tagline">从服务出行升级为城市应急基础设施</div>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">极端事件推演：地震 / 洪水疏散路线实时重算</div>
          <div class="rm-item">城市级应急调度：政府 / 交管 B 端接口</div>
          <div class="rm-item">空间智能 API：车企 / 机器人 / 城市治理接入</div>
          <div class="rm-art"><svg viewBox="0 0 80 50" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:72px"><circle cx="40" cy="25" r="6" stroke="currentColor" stroke-width="1.2"/><circle cx="12" cy="10" r="3.5" stroke="currentColor" stroke-width="0.9"/><circle cx="68" cy="10" r="3.5" stroke="currentColor" stroke-width="0.9"/><circle cx="12" cy="40" r="3.5" stroke="currentColor" stroke-width="0.9"/><circle cx="68" cy="40" r="3.5" stroke="currentColor" stroke-width="0.9"/><circle cx="40" cy="4" r="2.5" stroke="currentColor" stroke-width="0.8"/><circle cx="40" cy="46" r="2.5" stroke="currentColor" stroke-width="0.8"/><line x1="40" y1="25" x2="15" y2="12" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="40" y1="25" x2="65" y2="12" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="40" y1="25" x2="15" y2="38" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="40" y1="25" x2="65" y2="38" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="40" y1="25" x2="40" y2="6.5" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="40" y1="25" x2="40" y2="43.5" stroke="currentColor" stroke-width="0.7" stroke-opacity="0.5"/><line x1="15" y1="10" x2="65" y2="10" stroke="currentColor" stroke-width="0.4" stroke-opacity="0.22"/><line x1="15" y1="40" x2="65" y2="40" stroke="currentColor" stroke-width="0.4" stroke-opacity="0.22"/></svg></div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>灾害预演准确率 · B端接入量</div>
      </div>'''

new_p3 = '''      <div class="rm-phase p3 reveal d4">
        <div class="rm-num">PHASE 03 / 2–3 YR+</div>
        <div class="rm-period">灾难预演 · 城市级</div>
        <div class="rm-tagline">Fantasy World 仿真推演：地震 / 洪水疏散路线实时重算</div>
        <canvas id="p3canvas" class="rm-canvas"></canvas>
        <div class="rm-divider"></div>
        <div class="rm-items">
          <div class="rm-item">极端事件推演：地震 / 洪水 / 台风疏散路线实时重算</div>
          <div class="rm-item">城市级应急调度：政府 / 交管 B 端接口</div>
          <div class="rm-item">空间智能 API：车企 / 机器人 / 城市治理接入</div>
        </div>
        <div class="rm-metric"><span>METRICS</span><br>预演准确率 ↑ B端接入数 ↑</div>
      </div>'''

html = html.replace(old_p3, new_p3, 1)

# ============================================================
# 7. S13 — update L/02 key-ability column to add disaster examples
# ============================================================
old_s13_l02 = '          <div class="sol-cell">\n          <div class="sol-cell-main">感知演唱会 / 商场关闭等事件，预测路网变化提前规划</div>\n        </div>'
new_s13_l02 = '          <div class="sol-cell">\n          <div class="sol-cell-main">感知演唱会 / 商场关闭 / 地震等极端事件，预测路网变化提前规划</div>\n        </div>'

html = html.replace(old_s13_l02, new_s13_l02, 1)

# ============================================================
# 8. Add Canvas 3D animation JS before closing </script>
# ============================================================
canvas_js = r"""
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
  const H = Math.max(rect.height, 60);
  canvas.width = W * DPR;
  canvas.height = H * DPR;
  const ctx = canvas.getContext('2d');
  ctx.scale(DPR, DPR);
  return { ctx, W, H, DPR };
}

// ── PHASE 1 : Indoor Navigation + Agent Attribution ──────────
(function () {
  let state = null;
  let startTime = null;
  const CYCLE = 3400; // draw + hold time in ms

  function getState() {
    if (!state) state = initPhaseCanvas('p1canvas');
    return state;
  }

  function draw(ts) {
    const s = getState();
    if (!s) return;
    const { ctx, W, H } = s;

    if (!startTime) startTime = ts;
    const elapsed = (ts - startTime) % (CYCLE + 900);
    const progress = Math.min(elapsed / CYCLE, 1);

    // Waypoints for indoor nav path
    const path = [
      [W * 0.08, H * 0.87],
      [W * 0.08, H * 0.54],
      [W * 0.36, H * 0.54],
      [W * 0.36, H * 0.22],
      [W * 0.92, H * 0.22]
    ];

    function segLen(a, b) {
      return Math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2);
    }
    function totalLen(pts) {
      let l = 0;
      for (let i = 1; i < pts.length; i++) l += segLen(pts[i - 1], pts[i]);
      return l;
    }
    function ptAtDist(pts, dist) {
      let d = 0;
      for (let i = 1; i < pts.length; i++) {
        const seg = segLen(pts[i - 1], pts[i]);
        if (d + seg >= dist) {
          const t = (dist - d) / seg;
          return [
            pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t,
            pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t
          ];
        }
        d += seg;
      }
      return pts[pts.length - 1].slice();
    }

    const TL = totalLen(path);
    const dist = TL * progress;

    ctx.clearRect(0, 0, W, H);

    // Grid
    ctx.strokeStyle = 'rgba(237,231,220,0.045)';
    ctx.lineWidth = 0.4;
    for (let x = 0; x < W; x += W / 9) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += H / 6) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // Rooms
    const rooms = [
      [W * 0.02, H * 0.04, W * 0.26, H * 0.44],
      [W * 0.38, H * 0.04, W * 0.26, H * 0.44],
      [W * 0.70, H * 0.04, W * 0.27, H * 0.44],
      [W * 0.02, H * 0.60, W * 0.23, H * 0.35],
      [W * 0.30, H * 0.60, W * 0.38, H * 0.35],
      [W * 0.72, H * 0.60, W * 0.25, H * 0.35]
    ];
    ctx.strokeStyle = 'rgba(237,231,220,0.15)';
    ctx.lineWidth = 0.8;
    rooms.forEach(r => ctx.strokeRect(r[0], r[1], r[2], r[3]));

    // Destination marker
    const dest = path[path.length - 1];
    ctx.beginPath();
    ctx.arc(dest[0], dest[1], 5, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,78,26,0.28)';
    ctx.lineWidth = 0.8;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(dest[0], dest[1], 2.2, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,78,26,0.45)';
    ctx.fill();

    // Animated route
    if (progress > 0) {
      ctx.beginPath();
      ctx.moveTo(path[0][0], path[0][1]);
      let d2 = 0;
      for (let i = 1; i < path.length; i++) {
        const seg = segLen(path[i - 1], path[i]);
        if (d2 + seg <= dist) {
          ctx.lineTo(path[i][0], path[i][1]);
          d2 += seg;
        } else {
          const t = (dist - d2) / seg;
          ctx.lineTo(
            path[i - 1][0] + (path[i][0] - path[i - 1][0]) * t,
            path[i - 1][1] + (path[i][1] - path[i - 1][1]) * t
          );
          break;
        }
      }
      ctx.strokeStyle = 'rgba(255,78,26,0.72)';
      ctx.lineWidth = 1.8;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();
    }

    // Walking dot
    const pt = ptAtDist(path, dist);
    const pulse = 0.5 + 0.5 * Math.sin(ts / 290);
    const g = ctx.createRadialGradient(pt[0], pt[1], 0, pt[0], pt[1], 10 + 3 * pulse);
    g.addColorStop(0, `rgba(255,78,26,${0.22 * pulse})`);
    g.addColorStop(1, 'rgba(255,78,26,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(pt[0], pt[1], 10 + 3 * pulse, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(pt[0], pt[1], 3.8, 0, Math.PI * 2);
    ctx.fillStyle = '#FF4E1A';
    ctx.fill();

    // Attribution labels (fade in near end)
    if (progress > 0.78) {
      const alpha = Math.min((progress - 0.78) / 0.22, 1);
      const fs = Math.max(W * 0.054, 7);
      ctx.font = `${fs}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = `rgba(255,78,26,${alpha * 0.82})`;
      ctx.fillText('VLM 定位 ✓', W * 0.55, H * 0.50);
      ctx.fillStyle = `rgba(120,119,128,${alpha * 0.7})`;
      ctx.fillText('Agent 归因', W * 0.55, H * 0.66);
    }

    if (elapsed >= CYCLE + 700) startTime = null;
    requestAnimationFrame(draw);
  }

  // Start once s10 enters viewport (and re-trigger each time)
  const s10 = document.getElementById('s10');
  if (s10) {
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { state = null; startTime = null; requestAnimationFrame(draw); }
    }, { threshold: 0.45 });
    obs.observe(s10);
  }
})();

// ── PHASE 2 : 3D Gaussian Splats Point Cloud ────────────────
(function () {
  const canvas = document.getElementById('p2canvas');
  if (!canvas) return;
  let inited = false;
  let ctx, W, H;

  // Generate 3D scene points once
  const pts = [];
  for (let i = 0; i < 240; i++) {
    const layer = Math.floor(Math.random() * 3);
    let ox, oy, oz, sz, al, hue;
    if (layer === 0) {      // ground floor
      ox = (Math.random() - 0.5) * 38; oy = 10 + Math.random() * 5; oz = (Math.random() - 0.5) * 30;
      sz = 0.7 + Math.random() * 0.7; al = 0.35 + Math.random() * 0.3; hue = 0;
    } else if (layer === 1) { // mid-height (walls, objects)
      ox = (Math.random() - 0.5) * 32; oy = (Math.random() - 0.5) * 20; oz = (Math.random() - 0.5) * 26;
      sz = 0.9 + Math.random() * 1.1; al = 0.28 + Math.random() * 0.32; hue = Math.random() > 0.6 ? 1 : 0;
    } else {                // ceiling / high points
      ox = (Math.random() - 0.5) * 26; oy = -10 - Math.random() * 7; oz = (Math.random() - 0.5) * 22;
      sz = 0.5 + Math.random() * 0.9; al = 0.18 + Math.random() * 0.22; hue = Math.random() > 0.45 ? 1 : 0;
    }
    pts.push({ ox, oy, oz, sz, al, hue });
  }

  function ensureInit() {
    if (!inited) {
      const s = initPhaseCanvas('p2canvas');
      if (s) { ctx = s.ctx; W = s.W; H = s.H; inited = true; }
    }
  }

  function draw(ts) {
    ensureInit();
    if (!ctx) { requestAnimationFrame(draw); return; }

    ctx.clearRect(0, 0, W, H);
    const rot = ts / 9500;
    const cosR = Math.cos(rot), sinR = Math.sin(rot);

    // Sort back-to-front (painter's algo)
    const proj = pts.map(p => {
      const cx = p.ox * cosR - p.oz * sinR;
      const cz = p.ox * sinR + p.oz * cosR + 58;
      const fov = 170;
      const sc = fov / Math.max(cz, 12);
      return { sx: W / 2 + cx * sc, sy: H / 2 + p.oy * sc, sc, sz: p.sz, al: p.al, hue: p.hue, cz };
    }).sort((a, b) => a.cz - b.cz);

    // Center glow
    const g = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, W * 0.24);
    g.addColorStop(0, 'rgba(255,78,26,0.08)'); g.addColorStop(1, 'rgba(255,78,26,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    // Gaussian splats
    proj.forEach(p => {
      const r = Math.max(p.sz * p.sc * 0.85, 0.35);
      const depth = Math.min(p.cz / 85, 1);
      const al = p.al * (0.3 + 0.7 * depth);
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, r, 0, Math.PI * 2);
      ctx.fillStyle = p.hue === 1
        ? `rgba(168,145,113,${al})`
        : `rgba(255,100,50,${al * 0.6})`;
      ctx.fill();
    });

    // Label
    const fs = Math.max(W * 0.052, 6.5);
    ctx.font = `${fs}px 'JetBrains Mono', monospace`;
    ctx.fillStyle = 'rgba(168,145,113,0.48)';
    ctx.fillText('FANTASY WORLD · 高斯泼溅', W * 0.06, H * 0.93);

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();

// ── PHASE 3 : Seismic / Disaster Simulation ─────────────────
(function () {
  const canvas = document.getElementById('p3canvas');
  if (!canvas) return;
  let inited = false;
  let ctx, W, H;

  function ensureInit() {
    if (!inited) {
      const s = initPhaseCanvas('p3canvas');
      if (s) { ctx = s.ctx; W = s.W; H = s.H; inited = true; }
    }
  }

  // City buildings (generated once, relative coords 0..1)
  const buildings = [];
  const seed = [0.04,0.11,0.18,0.25,0.32,0.39,0.46,0.53,0.60,0.67,0.74,0.81,0.88,0.95];
  seed.forEach(bx => {
    buildings.push({
      rx: bx, rw: 0.04 + Math.random() * 0.025,
      rh: 0.08 + Math.random() * 0.26
    });
  });

  const waves = [];
  let waveTimer = 0;
  function addWave() { waves.push({ r: 3, alpha: 0.82 }); }
  addWave();

  // Routes (relative coords)
  const routeA = [[0.06, 0.74], [0.40, 0.50], [0.94, 0.22]]; // through epicenter (danger)
  const routeB = [[0.06, 0.74], [0.18, 0.30], [0.62, 0.18], [0.94, 0.22]]; // detour (active)
  const epiRel = [0.40, 0.50];

  function rp(rel) { return [rel[0] * W, rel[1] * H]; }

  function drawPoly(pts, color, lw, dash) {
    ctx.beginPath();
    const p0 = rp(pts[0]);
    ctx.moveTo(p0[0], p0[1]);
    for (let i = 1; i < pts.length; i++) { const p = rp(pts[i]); ctx.lineTo(p[0], p[1]); }
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    ctx.setLineDash(dash || []);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
    ctx.setLineDash([]);
  }

  function draw(ts) {
    ensureInit();
    if (!ctx) { requestAnimationFrame(draw); return; }

    ctx.clearRect(0, 0, W, H);

    // Ground line
    ctx.strokeStyle = 'rgba(237,231,220,0.07)'; ctx.lineWidth = 0.4;
    ctx.beginPath(); ctx.moveTo(0, H * 0.88); ctx.lineTo(W, H * 0.88); ctx.stroke();

    // City silhouette
    buildings.forEach(b => {
      const x = b.rx * W, bw = b.rw * W, bh = b.rh * H;
      ctx.fillStyle = 'rgba(237,231,220,0.03)';
      ctx.fillRect(x, H * 0.88 - bh, bw, bh);
      ctx.strokeStyle = 'rgba(237,231,220,0.08)';
      ctx.lineWidth = 0.35;
      ctx.strokeRect(x, H * 0.88 - bh, bw, bh);
    });

    // Seismic waves
    waveTimer++;
    if (waveTimer % 60 === 0) addWave();
    const epi = rp(epiRel);
    waves.forEach(w => {
      w.r += 0.65;
      w.alpha = Math.max(0, 0.82 - w.r / (W * 0.43));
    });
    waves.filter(w => w.alpha > 0).forEach(w => {
      ctx.beginPath();
      ctx.arc(epi[0], epi[1], w.r, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255,78,26,${w.alpha})`;
      ctx.lineWidth = 0.8;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(epi[0], epi[1], w.r * 1.5, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255,78,26,${w.alpha * 0.2})`;
      ctx.lineWidth = 0.35;
      ctx.stroke();
    });
    for (let i = waves.length - 1; i >= 0; i--) { if (waves[i].alpha <= 0) waves.splice(i, 1); }

    // Route A (danger — broken, dim, flashing)
    const flash = Math.sin(ts / 360) > 0.2;
    drawPoly(routeA, flash ? 'rgba(255,78,26,0.38)' : 'rgba(255,78,26,0.1)', 1.0, [3, 5]);

    // Route B (active detour)
    drawPoly(routeB, 'rgba(255,78,26,0.72)', 1.8);

    // Arrow at end of route B
    const last = rp(routeB[routeB.length - 1]);
    const prev = rp(routeB[routeB.length - 2]);
    const ang = Math.atan2(last[1] - prev[1], last[0] - prev[0]);
    ctx.save();
    ctx.translate(last[0], last[1]);
    ctx.rotate(ang);
    ctx.beginPath();
    ctx.moveTo(0, 0); ctx.lineTo(-6, -3); ctx.lineTo(-6, 3); ctx.closePath();
    ctx.fillStyle = 'rgba(255,78,26,0.72)';
    ctx.fill();
    ctx.restore();

    // Epicenter glow + dot
    const pulse = 0.5 + 0.5 * Math.sin(ts / 260);
    const eg = ctx.createRadialGradient(epi[0], epi[1], 0, epi[0], epi[1], 14 + 5 * pulse);
    eg.addColorStop(0, `rgba(255,78,26,${0.28 * pulse})`);
    eg.addColorStop(1, 'rgba(255,78,26,0)');
    ctx.fillStyle = eg;
    ctx.beginPath();
    ctx.arc(epi[0], epi[1], 14 + 5 * pulse, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(epi[0], epi[1], 3.5, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,78,26,${0.7 + 0.3 * pulse})`;
    ctx.fill();

    // Warning text
    if (flash) {
      const fs = Math.max(W * 0.052, 6.5);
      ctx.font = `${fs}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = 'rgba(255,78,26,0.78)';
      ctx.fillText('⚠ 路线重算中', W * 0.52, H * 0.20);
    }

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();
"""

html = html.replace('\n</script>', canvas_js + '\n</script>', 1)

# ============================================================
# Write out
# ============================================================
with open('/home/user/air/presentation.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Done: S9 tech refs + chip bar, S10 3D canvas animations, S13 L/02 update.")

# Quick validation
with open('/home/user/air/presentation.html', 'r', encoding='utf-8') as f:
    out = f.read()

checks = {
    'S9 Fantasy World in text': 'Fantasy World</em>' in out,
    'S9 Qwen in text': '通义千问 (Qwen)</em>' in out,
    'S9 Gaussian in text': '高斯泼溅</em>' in out,
    'S9 tech chip bar': 'tech-bar reveal d6' in out,
    'P1 canvas': 'id="p1canvas"' in out,
    'P2 canvas': 'id="p2canvas"' in out,
    'P3 canvas': 'id="p3canvas"' in out,
    'P1 tagline Qwen': 'VLM 识图定位 + Qwen 归因解释' in out,
    'P2 tagline Gaussian': 'Fantasy World + 高斯泼溅' in out,
    'P3 tagline Fantasy World': 'Fantasy World 仿真推演' in out,
    'S13 L02 disaster': '地震等极端事件' in out,
    'canvas JS draw fn': 'initPhaseCanvas' in out,
}

for k, v in checks.items():
    print(f"  {'✓' if v else '✗'} {k}")
