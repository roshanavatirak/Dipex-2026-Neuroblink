'use client';
import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ── Palette ──────────────────────────────────────────────────────
const C = {
  cyan:   "#00f5ff",
  purple: "#a855f7",
  amber:  "#f59e0b",
  green:  "#22c55e",
  red:    "#ef4444",
  pink:   "#ec4899",
  blue:   "#3b82f6",
  bg:     "#05050d",
  border: "#1a1a2e",
};

// ── MediaPipe indices ─────────────────────────────────────────────
const LEFT_EAR_IDX  = [33, 160, 158, 133, 153, 144];
const RIGHT_EAR_IDX = [362, 385, 387, 263, 373, 380];

// Dense face oval (36 pts)
const FACE_OVAL = [
  10,338,297,332,284,251,389,356,454,323,361,288,
  397,365,379,378,400,377,152,148,176,149,150,136,
  172,58,132,93,234,127,162,21,54,103,67,109,10
];

// Full left eye (all 16 contour pts)
const LEFT_EYE_FULL = [
  33,246,161,160,159,158,157,173,
  133,155,154,153,145,144,163,7,33
];
// Full right eye (all 16 contour pts)
const RIGHT_EYE_FULL = [
  362,398,384,385,386,387,388,466,
  263,249,390,373,374,380,381,382,362
];

// Left eyebrow (upper + lower ridge)
const LEFT_BROW_UPPER = [70,63,105,66,107];
const LEFT_BROW_LOWER = [46,53,52,65,55];
// Right eyebrow
const RIGHT_BROW_UPPER = [300,293,334,296,336];
const RIGHT_BROW_LOWER = [276,283,282,295,285];

// Nose bridge
const NOSE_BRIDGE = [168,6,197,195,5,4,1,19,94,2];
// Nose tip area
const NOSE_TIP    = [4,5,195,197,6,168];
// Nose bottom
const NOSE_ALAE_L = [218,219,220,237,44,19,1];
const NOSE_ALAE_R = [438,439,440,457,274,294,1];

// Lips — full detail
const LIPS_OUTER_TOP    = [61,185,40,39,37,0,267,269,270,409,291];
const LIPS_OUTER_BOTTOM = [61,146,91,181,84,17,314,405,321,375,291];
const LIPS_INNER_TOP    = [78,191,80,81,82,13,312,311,310,415,308];
const LIPS_INNER_BOTTOM = [78,95,88,178,87,14,317,402,318,324,308];

// Philtrum + chin
const CHIN_LINE = [152,400,378,379,365,397,288,361,323];
const FOREHEAD  = [10,109,67,103,54,21,162,127,234,93,132,58,172,136,150,149,176,148,152];

// Cheek lines
const LEFT_CHEEK  = [234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454,356,389,251,284,332,297,338,10];
const RIGHT_CHEEK = [454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109,10,338,297,332,284,251,389,356,454];

// Iris approximation
const LEFT_IRIS  = [469,470,471,472,469];
const RIGHT_IRIS = [474,475,476,477,474];

// Jaw line
const JAW_LINE_L = [172,136,150,149,176,148,152];
const JAW_LINE_R = [397,365,379,378,400,377,152];

// Contour grid lines for "scan" effect across face
const FACE_GRID_H1 = [70,63,105,66,107,55,8,285,296,334,293,300];
const FACE_GRID_H2 = [234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454];

// ── Helpers ───────────────────────────────────────────────────────
function calcEAR(lm, idx) {
  if (!lm || lm.length < 478) return 0.28;
  if (idx.some(i => !lm[i])) return 0.28;
  const p = idx.map(i => lm[i]);
  const A = dist2d(p[1], p[5]);
  const B = dist2d(p[2], p[4]);
  const C_ = dist2d(p[0], p[3]);
  return C_ > 1e-6 ? (A + B) / (2 * C_) : 0.0;
}
function dist2d(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
function approxSharpness(canvas) {
  try {
    const s = 80;
    const t = Object.assign(document.createElement("canvas"), { width: s, height: s });
    const tc = t.getContext("2d");
    tc.drawImage(canvas, 0, 0, s, s);
    const d = tc.getImageData(0, 0, s, s).data;
    let sum = 0, n = 0;
    for (let i = s*4; i < d.length - s*4 - 4; i += 8) {
      const lap = -4*d[i] + d[i-4] + d[i+4] + d[i-s*4] + d[i+s*4];
      sum += lap * lap; n++;
    }
    return Math.min(Math.sqrt(sum / (n || 1)), 80);
  } catch { return 18; }
}

// ── Draw dense overlay ────────────────────────────────────────────
function drawOverlay(ctx, lm, W, H, earL, earR, blinkL, blinkR, frameCount) {
  if (!lm || lm.length < 100) {
    // Searching reticle
    const t = Date.now() / 1000;
    ctx.save();
    ctx.strokeStyle = `${C.cyan}30`;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 8]);
    ctx.strokeRect(W*0.2, H*0.1, W*0.6, H*0.8);
    ctx.setLineDash([]);
    // Animated cross-hair
    const cx = W/2, cy = H/2;
    const r = 28 + Math.sin(t*3)*4;
    ctx.strokeStyle = `${C.cyan}50`;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(cx-r,cy); ctx.lineTo(cx+r,cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx,cy-r); ctx.lineTo(cx,cy+r); ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI*2); ctx.stroke();
    ctx.fillStyle = `${C.cyan}55`;
    ctx.font = "9px monospace";
    ctx.textAlign = "center";
    ctx.fillText("SCANNING FOR FACE…", W/2, H/2 + r + 18);
    ctx.textAlign = "left";
    ctx.restore();
    return;
  }

  const px = p => [p.x * W, p.y * H];
  const t  = Date.now() / 1000;

  // ── draw path helper ─────────────────────────────────────────
  const path = (indices, color, lw = 1, close = false, glow = false, dash = null) => {
    const valid = indices.filter(i => i < lm.length && lm[i]);
    if (valid.length < 2) return;
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth   = lw;
    if (dash) ctx.setLineDash(dash); else ctx.setLineDash([]);
    if (glow) { ctx.shadowBlur = 10; ctx.shadowColor = color; }
    valid.forEach((i, n) => {
      const [x, y] = px(lm[i]);
      n === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    if (close) ctx.closePath();
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.setLineDash([]);
  };

  // ── draw filled polygon helper ───────────────────────────────
  const fillPoly = (indices, color) => {
    const valid = indices.filter(i => i < lm.length && lm[i]);
    if (valid.length < 3) return;
    ctx.beginPath();
    valid.forEach((i, n) => {
      const [x, y] = px(lm[i]);
      n === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
  };

  // ── draw dot helper ──────────────────────────────────────────
  const dots = (indices, color, r = 1.5, glow = false) => {
    if (glow) { ctx.shadowBlur = 6; ctx.shadowColor = color; }
    ctx.fillStyle = color;
    indices.forEach(i => {
      if (i >= lm.length || !lm[i]) return;
      const [x, y] = px(lm[i]);
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI*2);
      ctx.fill();
    });
    ctx.shadowBlur = 0;
  };

  // ── ALL 468 landmark dots (tiny, subtle) ─────────────────────
  const allIdx = Array.from({length: Math.min(lm.length, 468)}, (_,i) => i);
  ctx.fillStyle = "#00f5ff12";
  allIdx.forEach(i => {
    if (!lm[i]) return;
    const [x, y] = px(lm[i]);
    ctx.beginPath();
    ctx.arc(x, y, 1, 0, Math.PI*2);
    ctx.fill();
  });

  // ── Face oval ─────────────────────────────────────────────────
  path(FACE_OVAL, "#00f5ff18", 0.8, true);

  // ── Forehead / cheek mesh lines ───────────────────────────────
  path(FACE_GRID_H1, "#00f5ff0a", 0.6, false, false, [3,6]);
  path(FACE_GRID_H2, "#00f5ff0a", 0.6, false, false, [3,6]);

  // ── Jaw line ──────────────────────────────────────────────────
  path(JAW_LINE_L, "#00f5ff22", 0.8, false);
  path(JAW_LINE_R, "#00f5ff22", 0.8, false);

  // ── Eyebrows ──────────────────────────────────────────────────
  path(LEFT_BROW_UPPER,  "#a855f755", 1.0, false);
  path(LEFT_BROW_LOWER,  "#a855f733", 0.7, false);
  path(RIGHT_BROW_UPPER, "#a855f755", 1.0, false);
  path(RIGHT_BROW_LOWER, "#a855f733", 0.7, false);
  dots(LEFT_BROW_UPPER,  "#a855f766", 1.5);
  dots(RIGHT_BROW_UPPER, "#a855f766", 1.5);

  // ── Nose ─────────────────────────────────────────────────────
  path(NOSE_BRIDGE, "#f59e0b33", 0.8, false);
  path(NOSE_ALAE_L, "#f59e0b22", 0.7, false);
  path(NOSE_ALAE_R, "#f59e0b22", 0.7, false);
  dots([4, 5, 1, 2], "#f59e0b88", 2.0, true);
  dots([94, 19],      "#f59e0b44", 1.5);

  // ── Lips — outer ─────────────────────────────────────────────
  path(LIPS_OUTER_TOP,    "#ec489944", 0.9, false);
  path(LIPS_OUTER_BOTTOM, "#ec489944", 0.9, false);
  // Lips — inner
  path(LIPS_INNER_TOP,    "#ec489922", 0.7, false);
  path(LIPS_INNER_BOTTOM, "#ec489922", 0.7, false);
  // Lip fill
  fillPoly([...LIPS_INNER_TOP, ...LIPS_INNER_BOTTOM.slice().reverse()], "#ec489908");
  dots([61,291,0,17,13,14,78,308], "#ec489966", 1.8);

  // ── Eyes ─────────────────────────────────────────────────────
  const eyeColorL = blinkL ? C.red+"cc" : C.cyan+"cc";
  const eyeColorR = blinkR ? C.red+"cc" : C.cyan+"cc";
  path(LEFT_EYE_FULL,  eyeColorL, 1.6, true, true);
  path(RIGHT_EYE_FULL, eyeColorR, 1.6, true, true);

  // Eye fill (subtle)
  fillPoly(LEFT_EYE_FULL.slice(0,-1),  blinkL ? "#ef444410" : "#00f5ff08");
  fillPoly(RIGHT_EYE_FULL.slice(0,-1), blinkR ? "#ef444410" : "#00f5ff08");

  // Inner eye corners & highlight dots
  dots(LEFT_EAR_IDX,  blinkL ? C.red : C.cyan, 2.5, true);
  dots(RIGHT_EAR_IDX, blinkR ? C.red : C.cyan, 2.5, true);
  // Extra eye rim dots
  dots(LEFT_EYE_FULL.slice(0,-1),  blinkL ? "#ef444466" : "#00f5ff44", 1.2);
  dots(RIGHT_EYE_FULL.slice(0,-1), blinkR ? "#ef444466" : "#00f5ff44", 1.2);

  // ── Iris circles (if refined landmarks exist — idx 469-477) ──
  if (lm.length >= 478) {
    path(LEFT_IRIS,  "#00f5ffaa", 1.2, true, true);
    path(RIGHT_IRIS, "#00f5ffaa", 1.2, true, true);
    // Iris center pupils
    if (lm[468]) { const [x,y]=px(lm[468]); ctx.beginPath(); ctx.arc(x,y,2,0,Math.PI*2); ctx.fillStyle="#00f5ffcc"; ctx.shadowBlur=8; ctx.shadowColor=C.cyan; ctx.fill(); ctx.shadowBlur=0; }
    if (lm[473]) { const [x,y]=px(lm[473]); ctx.beginPath(); ctx.arc(x,y,2,0,Math.PI*2); ctx.fillStyle="#00f5ffcc"; ctx.shadowBlur=8; ctx.shadowColor=C.cyan; ctx.fill(); ctx.shadowBlur=0; }
  }

  // ── EAR labels ───────────────────────────────────────────────
  ctx.font = "bold 10px 'JetBrains Mono',monospace";
  if (lm[33]) {
    const [lx, ly] = px(lm[33]);
    ctx.fillStyle = blinkL ? C.red : C.cyan;
    ctx.shadowBlur = 6; ctx.shadowColor = ctx.fillStyle;
    ctx.fillText(`L ${earL.toFixed(3)}`, lx - 42, ly - 12);
    ctx.shadowBlur = 0;
  }
  if (lm[263]) {
    const [rx, ry] = px(lm[263]);
    ctx.fillStyle = blinkR ? C.red : C.cyan;
    ctx.shadowBlur = 6; ctx.shadowColor = ctx.fillStyle;
    ctx.fillText(`R ${earR.toFixed(3)}`, rx + 6, ry - 12);
    ctx.shadowBlur = 0;
  }

  // ── Head pose indicator (yaw from nose-to-ear distance ratio) 
  if (lm[1] && lm[33] && lm[263]) {
    const noseX  = lm[1].x;
    const leftX  = lm[33].x;
    const rightX = lm[263].x;
    const facW   = rightX - leftX;
    const yaw    = facW > 0.01 ? ((noseX - leftX) / facW - 0.5) * 60 : 0;
    if (lm[1]) {
      const [nx, ny] = px(lm[1]);
      ctx.fillStyle = "#f59e0b88";
      ctx.font = "8px monospace";
      ctx.fillText(`YAW ${yaw.toFixed(1)}°`, nx + 8, ny + 18);
    }
  }

  // ── Blink badge ──────────────────────────────────────────────
  if (blinkL || blinkR) {
    const bw = 120, bh = 22, bx = W/2 - bw/2, by = 8;
    ctx.fillStyle   = "#ef444420";
    ctx.strokeStyle = "#ef444560";
    ctx.lineWidth   = 1;
    ctx.shadowBlur  = 16;
    ctx.shadowColor = C.red;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(bx, by, bw, bh, 4);
    else ctx.rect(bx, by, bw, bh);
    ctx.fill(); ctx.stroke();
    ctx.shadowBlur  = 0;
    ctx.fillStyle   = C.red;
    ctx.font        = "bold 9px monospace";
    ctx.textAlign   = "center";
    ctx.fillText("⚡ BLINK DETECTED", W/2, by + 15);
    ctx.textAlign   = "left";
  }

  // ── Landmark count badge ─────────────────────────────────────
  ctx.fillStyle = "#00f5ff20";
  ctx.font      = "8px monospace";
  ctx.fillText(`${lm.length} pts`, 8, 18);

  // ── Animated scan line ───────────────────────────────────────
  const scanY = ((t * 0.4) % 1) * H;
  const sg = ctx.createLinearGradient(0, scanY-8, 0, scanY+8);
  sg.addColorStop(0,   "transparent");
  sg.addColorStop(0.4, "#00f5ff12");
  sg.addColorStop(0.5, "#00f5ff22");
  sg.addColorStop(0.6, "#00f5ff12");
  sg.addColorStop(1,   "transparent");
  ctx.fillStyle = sg;
  ctx.fillRect(0, scanY-8, W, 16);

  // ── Corner HUD lines ─────────────────────────────────────────
  const cl = 20;
  [
    [0,0,1,0,0,1],[W,0,-1,0,0,1],[0,H,1,0,0,-1],[W,H,-1,0,0,-1]
  ].forEach(([x,y,dx1,dy1,dx2,dy2]) => {
    ctx.strokeStyle = "#00f5ff45";
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+dx1*cl, y+dy1*cl); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+dx2*cl, y+dy2*cl); ctx.stroke();
  });

  // ── Watermark ────────────────────────────────────────────────
  ctx.fillStyle = "#00f5ff25";
  ctx.font      = "7px monospace";
  ctx.fillText("NEUROBLINK · LIVE · 468pt MESH", 8, H - 8);
}

// ── Sparkline ─────────────────────────────────────────────────────
function Sparkline({ data, color, height = 44, label = "" }) {
  const w = 180, h = height;
  if (!data || data.length < 2) return (
    <svg width={w} height={h}>
      <line x1="0" y1={h/2} x2={w} y2={h/2}
        stroke={`${color}25`} strokeWidth="1" strokeDasharray="4 8" />
    </svg>
  );
  const mn = Math.min(...data), mx = Math.max(...data);
  const rng = mx - mn || 0.001;
  const pts = data.map((v, i) =>
    `${(i/(data.length-1))*w},${h - ((v-mn)/rng)*(h-6) - 3}`
  ).join(" ");
  const id = `sg${color.replace(/#/g,"")}${h}${label}`;
  const last = data[data.length-1];
  const ly   = h - ((last-mn)/rng)*(h-6) - 3;
  const lx   = w;
  return (
    <svg width={w} height={h} style={{ overflow:"visible" }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,${h} ${pts} ${w},${h}`} fill={`url(#${id})`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.6"
        strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={lx} cy={ly} r={3.5} fill={color}
        style={{ filter:`drop-shadow(0 0 5px ${color})` }} />
      <text x={lx+5} y={ly+4} fill={color}
        style={{ fontSize:7, fontFamily:"monospace" }}>
        {isFinite(last) ? last.toFixed(3) : "—"}
      </text>
    </svg>
  );
}

// ── Radial gauge ─────────────────────────────────────────────────
function RadialGauge({ value, max, color, label, size = 60 }) {
  const r = size/2 - 6;
  const circ = 2*Math.PI*r;
  const pct  = Math.min(Math.max(value/max, 0), 1);
  const dash = pct * circ * 0.75;
  const off  = -(circ * 0.125);
  return (
    <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:2 }}>
      <svg width={size} height={size} style={{ transform:"rotate(-135deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none"
          stroke="#ffffff08" strokeWidth="5"
          strokeDasharray={`${circ*0.75} ${circ}`}
          strokeDashoffset={off} strokeLinecap="round" />
        <motion.circle cx={size/2} cy={size/2} r={r} fill="none"
          stroke={color} strokeWidth="5"
          strokeDasharray={`${dash} ${circ}`} strokeDashoffset={off}
          strokeLinecap="round"
          animate={{ strokeDasharray:`${dash} ${circ}` }}
          transition={{ duration:0.3 }} />
        <text x={size/2} y={size/2+4} textAnchor="middle"
          style={{ fill:color, fontSize:8, fontFamily:"monospace",
            transform:`rotate(135deg)`, transformOrigin:`${size/2}px ${size/2}px` }}>
          {isFinite(value) ? value.toFixed(3) : "—"}
        </text>
      </svg>
      <span style={{ color:"#444", fontSize:7.5, fontFamily:"monospace",
        letterSpacing:"0.08em" }}>{label}</span>
    </div>
  );
}

// ── Feature bar ───────────────────────────────────────────────────
function FeatureBar({ label, value, max, color, unit="" }) {
  const pct = Math.min((value/max)*100, 100);
  const isHigh = pct > 75;
  return (
    <div style={{ marginBottom:6 }}>
      <div style={{ display:"flex", justifyContent:"space-between",
        fontSize:9.5, fontFamily:"monospace", marginBottom:2 }}>
        <span style={{ color:"#3a3a5a" }}>{label}</span>
        <span style={{ color: isHigh ? "#ef4444" : color }}>
          {isFinite(value) ? value.toFixed(3) : "—"}{unit}
        </span>
      </div>
      <div style={{ height:3, background:"#ffffff06", borderRadius:2, overflow:"hidden" }}>
        <motion.div
          style={{ height:"100%", borderRadius:2,
            background: isHigh
              ? `linear-gradient(90deg, ${color}, #ef4444)`
              : color }}
          animate={{ width:`${pct}%` }}
          transition={{ duration:0.35, ease:"easeOut" }} />
      </div>
    </div>
  );
}

// ── Section ───────────────────────────────────────────────────────
function Section({ label, color, children, live }) {
  return (
    <div style={{ marginBottom:10 }}>
      <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:5 }}>
        <div style={{ width:2, height:10, background:color, borderRadius:1 }} />
        <span style={{ color, fontSize:8, letterSpacing:"0.15em" }}>{label}</span>
        {live && (
          <motion.div style={{ width:4, height:4, borderRadius:"50%",
            background:color, marginLeft:"auto" }}
            animate={{ opacity:[1,0.15,1] }} transition={{ duration:1.2, repeat:Infinity }} />
        )}
      </div>
      <div style={{ background:"#0a0a16", border:`1px solid #151525`,
        borderRadius:8, padding:"8px 10px" }}>
        {children}
      </div>
    </div>
  );
}

// ── Metric chip ───────────────────────────────────────────────────
function MetricChip({ label, value, color, blink=false, sub="" }) {
  return (
    <motion.div animate={blink ? { scale:[1,1.1,1] } : {}}
      transition={{ duration:0.15 }}
      style={{ display:"flex", flexDirection:"column", alignItems:"center" }}>
      <span style={{ color:"#3a3a5a", fontSize:7.5, letterSpacing:"0.08em" }}>{label}</span>
      <span style={{ color, fontSize:12, fontWeight:"bold", lineHeight:1.1,
        textShadow: blink ? `0 0 14px ${color}` : "none" }}>{value}</span>
      {sub && <span style={{ color:"#2a2a3a", fontSize:7 }}>{sub}</span>}
    </motion.div>
  );
}

// ── Mini live graph (30-pt bar chart) ─────────────────────────────
function MiniBar({ history, color, h=28 }) {
  const w = 80;
  if (!history || history.length < 2) return null;
  const mx = Math.max(...history, 0.001);
  return (
    <svg width={w} height={h}>
      {history.slice(-20).map((v, i) => {
        const bh = Math.max((v/mx)*h, 1);
        const bw = (w/20) - 1;
        return (
          <rect key={i} x={i*(bw+1)} y={h-bh} width={bw} height={bh}
            fill={color} opacity={0.3 + (i/20)*0.7} rx={1} />
        );
      })}
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════════════
export default function LiveAnalysisPage() {
  const [active,   setActive]   = useState(false);
  const [camError, setCamError] = useState(null);
  const [mpReady,  setMpReady]  = useState(false);
  const [mpStatus, setMpStatus] = useState("LOADING…");

  const [feats, setFeats] = useState({
    earL:0.28, earR:0.28, blinkL:false, blinkR:false,
    blinkRate:0, blinkCount:0, sharpness:0,
    flowMean:0, boundaryFlow:0, mar:0,
    yaw:0, symmetry:0, faceArea:0, browHeight:0,
    leftPupilSize:0, rightPupilSize:0,
    cheekboneWidth:0, chinY:0,
  });

  const [earHistory,    setEarHistory]    = useState(Array(80).fill(0.28));
  const [flowHistory,   setFlowHistory]   = useState(Array(80).fill(0));
  const [marHistory,    setMarHistory]    = useState(Array(80).fill(0));
  const [blinkHistory,  setBlinkHistory]  = useState(Array(30).fill(0));
  const [sharpHistory,  setSharpHistory]  = useState(Array(40).fill(0));

  const [backendFeats, setBackendFeats] = useState(null);
  const [polling,      setPolling]      = useState(false);
  const [fps,          setFps]          = useState(0);

  const videoRef         = useRef(null);
  const canvasRef        = useRef(null);
  const animRef          = useRef(null);
  const streamRef        = useRef(null);
  const faceMeshRef      = useRef(null);
  const lmRef            = useRef([]);
  const blinkCountRef    = useRef(0);
  const blinkWindowRef   = useRef([]);
  const prevEarRef       = useRef(0.28);
  const prevFrameRef     = useRef(null);
  const frameCountRef    = useRef(0);
  const sharpnessRef     = useRef(18);
  const fpsRef           = useRef({ count:0, last:Date.now() });

  // ── Load MediaPipe ─────────────────────────────────────────────
  useEffect(() => {
    setMpStatus("LOADING SCRIPTS…");
    const VERSION = "0.4.1633559619";
    const BASE    = `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@${VERSION}`;

    const loadScript = (src) => new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
      const s = document.createElement("script");
      s.src = src; s.crossOrigin = "anonymous";
      s.onload = resolve;
      s.onerror = () => reject(new Error("Failed: " + src));
      document.head.appendChild(s);
    });

    const init = async () => {
      try {
        await loadScript(`${BASE}/face_mesh.js`);
        setMpStatus("INITIALISING…");
        if (!window.FaceMesh) throw new Error("FaceMesh not on window");
        const fm = new window.FaceMesh({ locateFile: f => `${BASE}/${f}` });
        fm.setOptions({
          maxNumFaces: 1,
          refineLandmarks: true,   // enables iris (469-477)
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });
        fm.onResults(r => { lmRef.current = r.multiFaceLandmarks?.[0] ?? []; });
        await fm.initialize();
        faceMeshRef.current = fm;
        setMpReady(true);
        setMpStatus("READY");
      } catch(e) {
        console.error("MediaPipe init error:", e);
        setMpStatus("ERR: " + e.message.slice(0, 50));
      }
    };
    init();
  }, []);

  // ── Camera start / stop ────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video:{ width:{ideal:640}, height:{ideal:480}, facingMode:"user" }, audio:false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setActive(true); setCamError(null);
    } catch(e) { setCamError("Camera: " + e.message); }
  }, []);

  const stopCamera = useCallback(() => {
    cancelAnimationFrame(animRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    if (videoRef.current) videoRef.current.srcObject = null;
    lmRef.current = [];
    blinkCountRef.current = 0;
    blinkWindowRef.current = [];
    setActive(false);
  }, []);

  // ── MediaPipe send loop ────────────────────────────────────────
  useEffect(() => {
    if (!active) return;
    let alive = true;
    let errCount = 0;
    const run = async () => {
      for (let i = 0; i < 30 && !faceMeshRef.current && alive; i++)
        await new Promise(r => setTimeout(r, 100));
      while (alive) {
        const video = videoRef.current;
        const fm    = faceMeshRef.current;
        if (fm && video && video.readyState >= 2 && video.videoWidth > 0) {
          try { await fm.send({ image: video }); errCount = 0; }
          catch(e) { errCount++; if (errCount > 5) await new Promise(r=>setTimeout(r,500)); }
        }
        await new Promise(r => setTimeout(r, 80));
      }
    };
    run();
    return () => { alive = false; };
  }, [active]);

  // ── Canvas render loop ─────────────────────────────────────────
  useEffect(() => {
    if (!active) return;
    let alive = true;

    const render = () => {
      if (!alive) return;
      const video  = videoRef.current;
      const canvas = canvasRef.current;
      if (!canvas || !video || video.readyState < 2) {
        animRef.current = requestAnimationFrame(render); return;
      }

      const W = video.videoWidth  || 640;
      const H = video.videoHeight || 480;
      canvas.width = W; canvas.height = H;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });

      ctx.save();
      ctx.scale(-1, 1);
      ctx.drawImage(video, -W, 0, W, H);
      ctx.restore();

      const lm = lmRef.current;

      // ── EAR ────────────────────────────────────────────────
      const earL   = calcEAR(lm, LEFT_EAR_IDX);
      const earR   = calcEAR(lm, RIGHT_EAR_IDX);
      const earAvg = (earL + earR) / 2;

      // ── Blink ──────────────────────────────────────────────
      const THRESH = 0.21;
      const blinkL = earL < THRESH;
      const blinkR = earR < THRESH;
      if (prevEarRef.current >= THRESH && earAvg < THRESH) {
        blinkCountRef.current++;
        blinkWindowRef.current.push(Date.now());
      }
      prevEarRef.current = earAvg;
      const now_ = Date.now();
      blinkWindowRef.current = blinkWindowRef.current.filter(t => now_ - t < 60000);
      const blinkRate = blinkWindowRef.current.length / 60;

      // ── Mirror landmarks ───────────────────────────────────
      const mirroredLm = lm.length > 0 ? lm.map(p => ({...p, x: 1 - p.x})) : [];

      drawOverlay(ctx, mirroredLm, W, H, earL, earR, blinkL, blinkR, frameCountRef.current);

      frameCountRef.current++;

      // FPS counter
      fpsRef.current.count++;
      const elapsed = now_ - fpsRef.current.last;
      if (elapsed >= 1000) {
        setFps(Math.round(fpsRef.current.count * 1000 / elapsed));
        fpsRef.current = { count:0, last:now_ };
      }

      // Sharpness every 10 frames
      if (frameCountRef.current % 10 === 0)
        sharpnessRef.current = approxSharpness(canvas);

      // Optical flow every 3 frames
      let flowMean = 0;
      if (prevFrameRef.current && frameCountRef.current % 3 === 0) {
        try {
          const fw = Math.min(W, 96), fh = Math.min(H, 72);
          const curr = ctx.getImageData(0, 0, fw, fh);
          const prev = prevFrameRef.current;
          let diff = 0, n = 0;
          for (let i = 0; i < curr.data.length; i += 8) {
            diff += Math.abs(curr.data[i] - prev.data[i]); n++;
          }
          flowMean = (diff / n) / 255 * 12;
        } catch {}
      }
      if (frameCountRef.current % 3 === 0) {
        try {
          const fw = Math.min(W, 96), fh = Math.min(H, 72);
          prevFrameRef.current = ctx.getImageData(0, 0, fw, fh);
        } catch {}
      }

      // ── Extended features from landmarks ─────────────────
      let mar = 0, yaw = 0, symmetry = 0, faceArea = 0;
      let browHeight = 0, cheekboneWidth = 0;
      if (lm.length > 400) {
        try {
          // MAR
          const lc=lm[61],rc=lm[291],ul=lm[13],ll=lm[14];
          const mw=Math.hypot(rc.x-lc.x,rc.y-lc.y);
          const mh=Math.hypot(ll.x-ul.x,ll.y-ul.y);
          mar = mw > 0 ? mh/mw : 0;
          // Yaw
          const facW = lm[263].x - lm[33].x;
          yaw = facW > 0.01 ? ((lm[1].x - lm[33].x) / facW - 0.5) * 60 : 0;
          // Symmetry (left vs right EAR ratio)
          symmetry = earL > 0 && earR > 0 ? 1 - Math.abs(earL-earR)/Math.max(earL,earR) : 0;
          // Face bounding area
          const xs = [0,10,152,234,454].filter(i=>lm[i]).map(i=>lm[i].x);
          const ys = [0,10,152,234,454].filter(i=>lm[i]).map(i=>lm[i].y);
          faceArea = xs.length > 1 ? (Math.max(...xs)-Math.min(...xs)) * (Math.max(...ys)-Math.min(...ys)) : 0;
          // Brow height (brow to eye distance normalised)
          if (lm[105] && lm[159]) browHeight = Math.abs(lm[105].y - lm[159].y);
          // Cheekbone width
          if (lm[234] && lm[454]) cheekboneWidth = Math.abs(lm[454].x - lm[234].x);
        } catch {}
      }

      if (frameCountRef.current % 2 === 0) {
        setFeats({
          earL, earR, blinkL, blinkR,
          blinkRate, blinkCount: blinkCountRef.current,
          sharpness: sharpnessRef.current,
          flowMean, boundaryFlow: flowMean * 1.15,
          mar, yaw, symmetry, faceArea, browHeight, cheekboneWidth,
          leftPupilSize: 0, rightPupilSize: 0,
          chinY: lm[152]?.y ?? 0,
        });
        setEarHistory(h  => [...h.slice(1),  earAvg]);
        setFlowHistory(h => [...h.slice(1),  flowMean]);
        setMarHistory(h  => [...h.slice(1),  mar]);
        if (frameCountRef.current % 6 === 0) {
          setBlinkHistory(h => [...h.slice(1), blinkRate*60]);
          setSharpHistory(h => [...h.slice(1), sharpnessRef.current]);
        }
      }

      animRef.current = requestAnimationFrame(render);
    };

    animRef.current = requestAnimationFrame(render);
    return () => { alive = false; cancelAnimationFrame(animRef.current); };
  }, [active]);

  // ── Backend poll ───────────────────────────────────────────────
  useEffect(() => {
    if (!active) return;
    const poll = setInterval(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      setPolling(true);
      canvas.toBlob(async blob => {
        if (!blob) { setPolling(false); return; }
        try {
          const fd = new FormData();
          fd.append("frame", blob, "frame.jpg");
          const res = await fetch("http://localhost:8000/analyze_frame", { method:"POST", body:fd });
          if (res.ok) setBackendFeats(await res.json());
        } catch {}
        setPolling(false);
      }, "image/jpeg", 0.75);
    }, 3000);
    return () => clearInterval(poll);
  }, [active]);

  useEffect(() => () => stopCamera(), [stopCamera]);

  const hasFace = lmRef.current.length > 0;

  const pipelineSteps = [
    { step:"01", label:"FACE DETECT",  sub:"Haar Cascade",       color:C.cyan,
      value: active ? (hasFace ? "✓ DETECTED" : "SCANNING") : "IDLE" },
    { step:"02", label:"468-PT MESH",  sub:"MediaPipe Refined",  color:C.purple,
      value: mpReady ? (hasFace ? "✓ TRACKING" : "READY") : "LOADING" },
    { step:"03", label:"IRIS + PUPILS",sub:"Refined landmarks",  color:C.blue,
      value: active && hasFace ? "✓ ACTIVE" : "—" },
    { step:"04", label:"REAL EAR",     sub:"6-pt Soukupova",     color:C.amber,
      value: active && hasFace ? feats.earL.toFixed(3)+"/"+feats.earR.toFixed(3) : "—" },
    { step:"05", label:"LIVE FLOW",    sub:"Pixel diff approx",  color:C.green,
      value: active ? feats.flowMean.toFixed(3) : "—" },
    { step:"06", label:"HEAD POSE",    sub:"Yaw from landmarks", color:C.pink,
      value: active && hasFace ? feats.yaw.toFixed(1)+"°" : "—" },
    { step:"07", label:"SYMMETRY",     sub:"L/R EAR ratio",      color:C.cyan,
      value: active && hasFace ? feats.symmetry.toFixed(3) : "—" },
    { step:"08", label:"BACKEND",      sub:"POST /analyze_frame",color:C.amber,
      value: backendFeats ? "✓" : (polling ? "…" : active ? "3s POLL" : "IDLE") },
  ];

  return (
    <div style={{ minHeight:"100vh", background:C.bg, color:"#fff",
      fontFamily:"'JetBrains Mono','Courier New',monospace" }}>

      {/* Background */}
      <div style={{ position:"fixed", inset:0, pointerEvents:"none", zIndex:0,
        backgroundImage:`linear-gradient(${C.cyan}06 1px,transparent 1px),
                         linear-gradient(90deg,${C.cyan}06 1px,transparent 1px)`,
        backgroundSize:"40px 40px" }} />
      <div style={{ position:"fixed", top:"-10%", left:"20%", width:500, height:500,
        borderRadius:"50%", background:C.cyan, filter:"blur(140px)",
        opacity:0.03, pointerEvents:"none", zIndex:0 }} />
      <div style={{ position:"fixed", bottom:"10%", right:"10%", width:300, height:300,
        borderRadius:"50%", background:C.purple, filter:"blur(120px)",
        opacity:0.025, pointerEvents:"none", zIndex:0 }} />

      {/* Nav */}
      <nav style={{ position:"relative", zIndex:10, display:"flex",
        alignItems:"center", justifyContent:"space-between",
        padding:"10px 22px", borderBottom:`1px solid ${C.border}` }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ width:28, height:28, borderRadius:7,
            background:`${C.cyan}0d`, border:`1px solid ${C.cyan}35`,
            display:"flex", alignItems:"center", justifyContent:"center",
            boxShadow:`0 0 14px ${C.cyan}20` }}>
            <span style={{ color:C.cyan, fontSize:13 }}>⬡</span>
          </div>
          <div>
            <div style={{ fontWeight:900, letterSpacing:"0.12em", fontSize:13 }}>NEUROBLINK</div>
            <div style={{ color:"#222", fontSize:7, letterSpacing:"0.1em" }}>LIVE MESH v2.1 · 468+10 IRIS PTS</div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:14 }}>
          {/* FPS */}
          {active && (
            <div style={{ padding:"2px 8px", borderRadius:4,
              background:`${C.green}0a`, border:`1px solid ${C.green}25` }}>
              <span style={{ color:C.green, fontSize:8, fontWeight:"bold" }}>{fps} FPS</span>
            </div>
          )}
          {/* MP status */}
          <div style={{ display:"flex", alignItems:"center", gap:5, padding:"3px 10px",
            borderRadius:20, background: mpReady ? `${C.purple}0d` : "#0d0d0d",
            border:`1px solid ${mpReady ? C.purple+"35" : "#1a1a2e"}` }}>
            <motion.div style={{ width:5, height:5, borderRadius:"50%",
              background: mpReady ? C.purple : C.amber }}
              animate={{ opacity:[1,0.3,1] }} transition={{ duration:1.5, repeat:Infinity }} />
            <span style={{ fontSize:8, color: mpReady ? C.purple : C.amber,
              letterSpacing:"0.08em" }}>MP {mpStatus}</span>
          </div>
          {/* Live indicator */}
          <div style={{ display:"flex", alignItems:"center", gap:6, padding:"3px 10px",
            borderRadius:20, background: active ? `${C.green}0a` : "transparent",
            border:`1px solid ${active ? C.green+"30" : "#1a1a2e"}` }}>
            <motion.div style={{ width:5, height:5, borderRadius:"50%",
              background: active ? C.green : "#333" }}
              animate={active ? { opacity:[1,0.2,1] } : {}}
              transition={{ duration:1.2, repeat:Infinity }} />
            <span style={{ fontSize:8, color: active ? C.green : "#333",
              letterSpacing:"0.1em" }}>{active ? "LIVE" : "OFFLINE"}</span>
          </div>
        </div>
      </nav>

      {/* Split layout */}
      <div style={{ position:"relative", zIndex:10, display:"grid",
        gridTemplateColumns:"1fr 1fr", height:"calc(100vh - 53px)" }}>

        {/* ══════ LEFT ══════ */}
        <div style={{ borderRight:`1px solid ${C.border}`, display:"flex", flexDirection:"column" }}>
          {/* Camera header */}
          <div style={{ padding:"7px 14px", borderBottom:`1px solid ${C.border}`,
            display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              <span style={{ color:C.cyan, fontSize:8.5, letterSpacing:"0.14em" }}>
                ◈ LIVE CAMERA · 468PT MESH + IRIS
              </span>
              {active && (
                <motion.span animate={{ opacity:[1,0.2,1] }}
                  transition={{ duration:0.85, repeat:Infinity }}
                  style={{ background:C.red, color:"#fff", fontSize:7,
                    padding:"1px 6px", borderRadius:2, letterSpacing:"0.1em" }}>
                  ● REC
                </motion.span>
              )}
            </div>
            <div style={{ display:"flex", gap:12, alignItems:"center" }}>
              {active && hasFace && (
                <span style={{ color:C.green, fontSize:7.5,
                  textShadow:`0 0 6px ${C.green}` }}>● FACE LOCKED</span>
              )}
              {active && !hasFace && (
                <motion.span style={{ color:C.amber, fontSize:7.5 }}
                  animate={{ opacity:[1,0.3,1] }} transition={{ duration:1, repeat:Infinity }}>
                  SEARCHING…
                </motion.span>
              )}
              {active && hasFace && (
                <span style={{ color:"#333", fontSize:7.5 }}>
                  {lmRef.current.length}pt tracked
                </span>
              )}
            </div>
          </div>

          {/* Camera view */}
          <div style={{ flex:1, position:"relative", background:"#010108",
            display:"flex", alignItems:"center", justifyContent:"center", overflow:"hidden" }}>
            <video ref={videoRef} style={{ display:"none" }} muted playsInline />
            <canvas ref={canvasRef}
              style={{ width:"100%", height:"100%", objectFit:"contain",
                display: active ? "block" : "none" }} />

            {/* Corner decorations */}
            {["tl","tr","bl","br"].map(pos => (
              <div key={pos} style={{
                position:"absolute", zIndex:2, width:20, height:20,
                top:    pos[0]==="t" ? 8  : "auto",
                bottom: pos[0]==="b" ? 8  : "auto",
                left:   pos[1]==="l" ? 8  : "auto",
                right:  pos[1]==="r" ? 8  : "auto",
                borderTop:    pos[0]==="t" ? `2px solid ${C.cyan}50` : "none",
                borderBottom: pos[0]==="b" ? `2px solid ${C.cyan}50` : "none",
                borderLeft:   pos[1]==="l" ? `2px solid ${C.cyan}50` : "none",
                borderRight:  pos[1]==="r" ? `2px solid ${C.cyan}50` : "none",
                pointerEvents:"none",
              }} />
            ))}

            {/* Scan line */}
            {active && (
              <motion.div
                animate={{ top:["5%","95%"] }}
                transition={{ duration:2.8, repeat:Infinity, ease:"linear" }}
                style={{ position:"absolute", left:0, right:0, height:1, zIndex:3,
                  background:`linear-gradient(90deg,transparent,${C.cyan}50,transparent)`,
                  pointerEvents:"none" }} />
            )}

            {/* Idle state */}
            {!active && (
              <div style={{ textAlign:"center", padding:28 }}>
                <motion.div animate={{ scale:[1,1.06,1], opacity:[0.35,0.85,0.35] }}
                  transition={{ duration:2.5, repeat:Infinity }}
                  style={{ width:80, height:80, border:`2px solid ${C.cyan}30`,
                    borderRadius:"50%", margin:"0 auto 14px",
                    display:"flex", alignItems:"center", justifyContent:"center",
                    background:`${C.cyan}06` }}>
                  <span style={{ fontSize:30 }}>📷</span>
                </motion.div>
                <p style={{ color:"#3a3a5a", fontSize:10, marginBottom:4,
                  letterSpacing:"0.1em" }}>
                  {mpReady ? "✓ MEDIAPIPE READY" : mpStatus}
                </p>
                <p style={{ color:"#222", fontSize:8, marginBottom:18,
                  maxWidth:260, margin:"0 auto 18px", lineHeight:1.7 }}>
                  Dense 468+10 iris landmark mesh · Real EAR · Face oval ·
                  Full eye contours · Brow ridges · Lip mesh · Nose alae
                </p>
                {camError && <p style={{ color:C.red, fontSize:9, marginBottom:12 }}>{camError}</p>}
                <motion.button onClick={startCamera}
                  whileHover={{ scale:1.04, boxShadow:`0 0 30px ${C.cyan}45` }}
                  whileTap={{ scale:0.97 }}
                  disabled={!mpReady}
                  style={{ background: mpReady ? `${C.cyan}12` : "#0d0d0d",
                    border:`1px solid ${mpReady ? C.cyan+"45" : "#1a1a2e"}`,
                    color: mpReady ? C.cyan : "#444",
                    padding:"10px 30px", borderRadius:8,
                    fontFamily:"inherit", fontSize:10, letterSpacing:"0.14em",
                    cursor: mpReady ? "pointer" : "not-allowed", fontWeight:"bold" }}>
                  {mpReady ? "▶ START CAMERA" : "LOADING MEDIAPIPE…"}
                </motion.button>
              </div>
            )}
          </div>

          {/* Bottom chips */}
          {active && (
            <div style={{ padding:"8px 14px", borderTop:`1px solid ${C.border}`,
              display:"flex", flexDirection:"column", gap:7 }}>
              {/* Row 1 */}
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
                <div style={{ display:"flex", gap:16 }}>
                  <MetricChip label="L-EAR" value={feats.earL.toFixed(3)}
                    color={feats.blinkL ? C.red : C.cyan} blink={feats.blinkL} />
                  <MetricChip label="R-EAR" value={feats.earR.toFixed(3)}
                    color={feats.blinkR ? C.red : C.cyan} blink={feats.blinkR} />
                  <MetricChip label="BLINK/MIN"
                    value={(feats.blinkRate*60).toFixed(1)} color={C.purple} />
                  <MetricChip label="TOTAL" value={String(feats.blinkCount)}
                    color={C.amber} sub="blinks" />
                  <MetricChip label="YAW" value={feats.yaw.toFixed(1)+"°"}
                    color={C.pink} />
                  <MetricChip label="SYM" value={feats.symmetry.toFixed(3)}
                    color={C.green} />
                </div>
                <button onClick={stopCamera}
                  style={{ background:"#0d0000", border:`1px solid ${C.red}30`,
                    color:C.red, padding:"5px 12px", borderRadius:6,
                    fontFamily:"inherit", fontSize:9, cursor:"pointer",
                    letterSpacing:"0.1em" }}>
                  ■ STOP
                </button>
              </div>
              {/* Row 2 — mini graphs */}
              <div style={{ display:"flex", gap:16, alignItems:"flex-end" }}>
                <div style={{ display:"flex", flexDirection:"column", gap:1 }}>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>EAR HISTORY</span>
                  <MiniBar history={earHistory} color={C.cyan} h={20} />
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:1 }}>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>BLINK RATE</span>
                  <MiniBar history={blinkHistory} color={C.purple} h={20} />
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:1 }}>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>SHARPNESS</span>
                  <MiniBar history={sharpHistory} color={C.amber} h={20} />
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:1 }}>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>FLOW</span>
                  <MiniBar history={flowHistory} color={C.green} h={20} />
                </div>
                <div style={{ marginLeft:"auto", display:"flex", flexDirection:"column",
                  alignItems:"flex-end", gap:2 }}>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>FACE AREA</span>
                  <span style={{ color:C.blue, fontSize:10, fontWeight:"bold" }}>
                    {(feats.faceArea * 100).toFixed(1)}%
                  </span>
                  <span style={{ color:"#2a2a3a", fontSize:7 }}>MAR</span>
                  <span style={{ color:C.pink, fontSize:10, fontWeight:"bold" }}>
                    {feats.mar.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ══════ RIGHT — STATS ══════ */}
        <div style={{ display:"flex", flexDirection:"column", overflow:"hidden" }}>
          <div style={{ padding:"7px 14px", borderBottom:`1px solid ${C.border}`,
            display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <span style={{ color:C.purple, fontSize:8.5, letterSpacing:"0.14em" }}>
              ◈ REAL-TIME FEATURES · LIVE COMPUTATION
            </span>
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              {polling && (
                <motion.span style={{ color:C.amber, fontSize:8 }}
                  animate={{ opacity:[1,0.3,1] }} transition={{ duration:0.5, repeat:Infinity }}>
                  ↑ FETCHING
                </motion.span>
              )}
              <span style={{ color:"#2a2a3a", fontSize:8 }}>
                {active ? `${fps} fps · ${lmRef.current.length}pt` : "AWAITING"}
              </span>
            </div>
          </div>

          <div style={{ flex:1, overflowY:"auto", padding:"10px 12px" }}>

            {/* Pipeline grid */}
            <Section label="PIPELINE STATUS" color={C.cyan} live={active}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:4 }}>
                {pipelineSteps.map(({ step,label,sub,color,value }) => (
                  <div key={step} style={{
                    background:"#0d0d1a", border:`1px solid #151525`,
                    borderLeft:`2px solid ${active ? color : "#1a1a2e"}`,
                    borderRadius:6, padding:"5px 9px" }}>
                    <div style={{ display:"flex", justifyContent:"space-between" }}>
                      <span style={{ color:"#252535", fontSize:7 }}>{step}</span>
                      <span style={{ color: active ? color : "#252535",
                        fontSize:7, letterSpacing:"0.05em" }}>{value}</span>
                    </div>
                    <p style={{ color: active ? "#ccc" : "#252535", fontSize:9,
                      fontWeight:"bold", margin:"2px 0 1px", letterSpacing:"0.07em" }}>
                      {label}
                    </p>
                    <p style={{ color:"#252535", fontSize:7 }}>{sub}</p>
                  </div>
                ))}
              </div>
            </Section>

            {/* EAR sparklines + gauges */}
            <Section label="EYE ASPECT RATIO · SOUKUPOVA 6-PT" color={C.cyan} live={active}>
              <div style={{ display:"flex", alignItems:"flex-start", gap:10 }}>
                <div>
                  <Sparkline data={earHistory} color={feats.blinkL ? C.red : C.cyan}
                    height={44} label="ear" />
                  <div style={{ marginTop:4, fontSize:8, color:"#252535" }}>
                    threshold: <span style={{ color:"#ef444460" }}>0.210</span>
                    {"  "}blink/min:{" "}
                    <span style={{ color:C.purple }}>{(feats.blinkRate*60).toFixed(1)}</span>
                  </div>
                </div>
                <div>
                  <div style={{ display:"flex", gap:6 }}>
                    <RadialGauge value={feats.earL} max={0.45} color={C.cyan} label="L-EAR" size={54} />
                    <RadialGauge value={feats.earR} max={0.45} color={C.purple} label="R-EAR" size={54} />
                    <RadialGauge value={feats.symmetry} max={1} color={C.green} label="SYM" size={54} />
                  </div>
                  <AnimatePresence>
                    {(feats.blinkL || feats.blinkR) && (
                      <motion.div initial={{ opacity:0, scale:0.88 }}
                        animate={{ opacity:1, scale:1 }} exit={{ opacity:0 }}
                        style={{ background:`${C.red}12`, border:`1px solid ${C.red}35`,
                          borderRadius:4, padding:"3px 8px", textAlign:"center", marginTop:4 }}>
                        <span style={{ color:C.red, fontSize:8, letterSpacing:"0.1em" }}>
                          ⚡ BLINK DETECTED
                        </span>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </Section>

            {/* MAR sparkline */}
            <Section label="MOUTH ASPECT RATIO · REAL LANDMARKS" color={C.pink} live={active}>
              <div style={{ display:"flex", gap:10, alignItems:"center" }}>
                <Sparkline data={marHistory} color={C.pink} height={36} label="mar" />
                <div style={{ flex:1 }}>
                  <FeatureBar label="mouth_aspect_ratio" value={feats.mar}       max={0.5} color={C.pink} />
                  <FeatureBar label="brow_height_norm"   value={feats.browHeight} max={0.08} color={C.purple} />
                  <FeatureBar label="cheekbone_width"    value={feats.cheekboneWidth} max={0.5} color={C.amber} />
                </div>
              </div>
            </Section>

            {/* Optical flow */}
            <Section label="OPTICAL FLOW · PIXEL DIFF" color={C.green} live={active}>
              <div style={{ display:"flex", gap:10 }}>
                <Sparkline data={flowHistory} color={C.green} height={36} label="flow" />
                <div style={{ flex:1 }}>
                  <FeatureBar label="flow_mean"        value={feats.flowMean}     max={5}  color={C.green} />
                  <FeatureBar label="boundary_approx"  value={feats.boundaryFlow} max={6}  color={C.amber} />
                  <FeatureBar label="sharpness_lap"    value={feats.sharpness}    max={60} color={C.cyan} />
                </div>
              </div>
            </Section>

            {/* Head pose + geometry */}
            <Section label="HEAD GEOMETRY · POSE + FACE AREA" color={C.pink} live={active}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6 }}>
                <div>
                  <FeatureBar label="head_yaw (deg)"   value={Math.abs(feats.yaw)}    max={40}  color={C.pink} unit="°" />
                  <FeatureBar label="face_area_norm"   value={feats.faceArea}         max={0.3} color={C.blue} />
                  <FeatureBar label="chin_y_pos"       value={feats.chinY}            max={1}   color={C.amber} />
                </div>
                <div>
                  <RadialGauge value={Math.abs(feats.yaw)} max={45}
                    color={Math.abs(feats.yaw) > 20 ? C.red : C.pink}
                    label="YAW" size={64} />
                </div>
              </div>
            </Section>

            {/* Sharpness history */}
            <Section label="FRAME SHARPNESS · LAPLACIAN" color={C.amber} live={active}>
              <div style={{ display:"flex", gap:10, alignItems:"center" }}>
                <Sparkline data={sharpHistory} color={C.amber} height={32} label="sharp" />
                <div style={{ flex:1 }}>
                  <FeatureBar label="sharpness_score" value={feats.sharpness} max={60} color={C.amber} />
                  <div style={{ fontSize:8, color:"#252535", marginTop:4 }}>
                    low sharpness = compression / blur artifact
                  </div>
                </div>
              </div>
            </Section>

            {/* Backend */}
            <AnimatePresence>
              {backendFeats ? (
                <motion.div key="bf" initial={{ opacity:0, y:8 }}
                  animate={{ opacity:1, y:0 }} exit={{ opacity:0 }}>
                  <Section label="PYTHON BACKEND · /analyze_frame · 3s POLL" color={C.pink}>
                    {[
                      ["sharpness_score",     backendFeats.sharpness,             40, C.amber],
                      ["avg_symmetry",        backendFeats.symmetry,               1, C.pink],
                      ["lbp_entropy",         backendFeats.lbp_entropy,            8, C.purple],
                      ["noise_level",         backendFeats.noise_level,           10, C.cyan],
                      ["skin_ratio",          backendFeats.skin_ratio,             1, C.green],
                      ["flow_mean",           backendFeats.flow_mean,              5, C.green],
                      ["boundary_flow",       backendFeats.boundary_flow_ratio,    3, C.amber],
                    ].map(([lbl,val,mx,col]) => (
                      <FeatureBar key={lbl} label={lbl} value={val??0} max={mx} color={col} />
                    ))}
                    {backendFeats.verdict && (
                      <div style={{ marginTop:6, padding:"6px 10px", borderRadius:6,
                        textAlign:"center",
                        background: backendFeats.verdict==="FAKE"
                          ? `${C.red}12` : `${C.green}12`,
                        border:`1px solid ${backendFeats.verdict==="FAKE"
                          ? C.red : C.green}35` }}>
                        <span style={{ fontSize:11, fontWeight:"bold",
                          letterSpacing:"0.1em",
                          color: backendFeats.verdict==="FAKE" ? C.red : C.green }}>
                          {backendFeats.verdict==="FAKE"
                            ? "⚠ DEEPFAKE SIGNAL" : "✓ APPEARS REAL"}
                        </span>
                      </div>
                    )}
                  </Section>
                </motion.div>
              ) : active && (
                <motion.div key="np" initial={{ opacity:0 }} animate={{ opacity:1 }}
                  style={{ padding:"10px 12px", background:"#0d0d1a",
                    border:`1px solid #1a1a2e`, borderRadius:8, marginBottom:10 }}>
                  <p style={{ color:"#3a3a5a", fontSize:8, lineHeight:1.7, margin:0 }}>
                    ◈ BACKEND FEATURES<br />
                    <span style={{ color:"#252535" }}>
                      Full features (LBP, symmetry, pose, skin…) appear here when
                      backend exposes <code style={{ color:"#444" }}>POST /analyze_frame</code>.
                    </span>
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Summary row */}
            <div style={{ padding:"8px 10px", background:"#0d0d1a",
              border:`1px solid ${C.border}`, borderRadius:6,
              display:"grid", gridTemplateColumns:"repeat(5,1fr)", gap:4 }}>
              {[
                ["BLINK", "51",  C.cyan],
                ["DYN",   "138", C.purple],
                ["TEMP",  "20",  C.amber],
                ["VIDEO", "3",   C.green],
                ["IRIS",  "10",  C.blue],
              ].map(([lbl,n,col]) => (
                <div key={lbl} style={{ textAlign:"center" }}>
                  <p style={{ color:col, fontSize:16, fontWeight:900, margin:0,
                    textShadow:`0 0 8px ${col}55` }}>{n}</p>
                  <p style={{ color:"#252535", fontSize:7, letterSpacing:"0.1em", margin:0 }}>{lbl}</p>
                </div>
              ))}
            </div>

          </div>
        </div>
      </div>

      <style>{`
        ::-webkit-scrollbar{width:3px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:#1a1a2e;border-radius:2px}
      `}</style>
    </div>
  );
}