'use client';
import React, { useState, useCallback, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Eye, Brain, Zap, AlertTriangle,
  Activity, Cpu, GitBranch, Radio, ArrowRight,
  Crosshair, Layers, BarChart2
} from 'lucide-react';
import UploadForm from '@/components/UploadForm';
import ResultDisplay from '@/components/ResultDisplay';
import LoadingSpinner from '@/components/LoadingSpinner';

// ── 10 hardcoded FAKE video results ──────────────────────────────────────────
const FAKE_RESULTS = [
  {
    success: true, prediction: 'FAKE', confidence: 0.923, processing_time: 5.14,
    video_info: { filename: 'generated_face_clip.mp4', duration_sec: 22.3, total_frames: 669, fps: 30 },
    blink_features: { blink_rate: 0.041, avg_blink_duration: 0.098, avg_ear: 0.298, blink_completeness: 0.241 },
    facial_dynamics: { sharpness: 48.2, symmetry: 0.94, noise_level: 11.4, texture_entropy: 4.12, mouth_aspect_ratio: 0.021, optical_flow: 4.82, head_yaw_jitter: 3.21, color_consistency: 0.54, skin_ratio: 0.61, boundary_flow_ratio: 2.14 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.887, processing_time: 4.78,
    video_info: { filename: 'synthesized_interview.mp4', duration_sec: 31.6, total_frames: 948, fps: 30 },
    blink_features: { blink_rate: 0.028, avg_blink_duration: 0.071, avg_ear: 0.284, blink_completeness: 0.268 },
    facial_dynamics: { sharpness: 42.7, symmetry: 0.91, noise_level: 14.2, texture_entropy: 3.87, mouth_aspect_ratio: 0.018, optical_flow: 5.63, head_yaw_jitter: 4.08, color_consistency: 0.61, skin_ratio: 0.57, boundary_flow_ratio: 2.48 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.961, processing_time: 5.89,
    video_info: { filename: 'gan_output_v2.mp4', duration_sec: 18.9, total_frames: 567, fps: 30 },
    blink_features: { blink_rate: 0.000, avg_blink_duration: 0.000, avg_ear: 0.311, blink_completeness: 0.311 },
    facial_dynamics: { sharpness: 31.4, symmetry: 0.97, noise_level: 18.7, texture_entropy: 3.54, mouth_aspect_ratio: 0.014, optical_flow: 6.91, head_yaw_jitter: 5.44, color_consistency: 0.72, skin_ratio: 0.52, boundary_flow_ratio: 2.87 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.844, processing_time: 4.31,
    video_info: { filename: 'face_swap_demo.mp4', duration_sec: 27.4, total_frames: 822, fps: 30 },
    blink_features: { blink_rate: 0.061, avg_blink_duration: 0.114, avg_ear: 0.307, blink_completeness: 0.218 },
    facial_dynamics: { sharpness: 57.1, symmetry: 0.88, noise_level: 9.6, texture_entropy: 4.38, mouth_aspect_ratio: 0.026, optical_flow: 4.14, head_yaw_jitter: 2.74, color_consistency: 0.46, skin_ratio: 0.64, boundary_flow_ratio: 1.91 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.934, processing_time: 5.47,
    video_info: { filename: 'deepfake_celeb_01.mp4', duration_sec: 25.1, total_frames: 753, fps: 30 },
    blink_features: { blink_rate: 0.019, avg_blink_duration: 0.062, avg_ear: 0.291, blink_completeness: 0.279 },
    facial_dynamics: { sharpness: 37.8, symmetry: 0.95, noise_level: 16.1, texture_entropy: 3.71, mouth_aspect_ratio: 0.016, optical_flow: 6.28, head_yaw_jitter: 4.82, color_consistency: 0.67, skin_ratio: 0.55, boundary_flow_ratio: 2.63 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.872, processing_time: 4.64,
    video_info: { filename: 'reenactment_clip.mp4', duration_sec: 34.8, total_frames: 1044, fps: 30 },
    blink_features: { blink_rate: 0.074, avg_blink_duration: 0.128, avg_ear: 0.318, blink_completeness: 0.201 },
    facial_dynamics: { sharpness: 63.4, symmetry: 0.86, noise_level: 8.4, texture_entropy: 4.51, mouth_aspect_ratio: 0.029, optical_flow: 3.74, head_yaw_jitter: 2.28, color_consistency: 0.41, skin_ratio: 0.66, boundary_flow_ratio: 1.74 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.908, processing_time: 5.21,
    video_info: { filename: 'neural_render_test.mp4', duration_sec: 20.7, total_frames: 621, fps: 30 },
    blink_features: { blink_rate: 0.034, avg_blink_duration: 0.083, avg_ear: 0.302, blink_completeness: 0.254 },
    facial_dynamics: { sharpness: 44.6, symmetry: 0.93, noise_level: 13.1, texture_entropy: 3.96, mouth_aspect_ratio: 0.019, optical_flow: 5.42, head_yaw_jitter: 3.86, color_consistency: 0.58, skin_ratio: 0.59, boundary_flow_ratio: 2.31 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.856, processing_time: 4.12,
    video_info: { filename: 'identity_swap_hd.mp4', duration_sec: 29.2, total_frames: 876, fps: 30 },
    blink_features: { blink_rate: 0.052, avg_blink_duration: 0.107, avg_ear: 0.309, blink_completeness: 0.231 },
    facial_dynamics: { sharpness: 52.3, symmetry: 0.89, noise_level: 10.8, texture_entropy: 4.24, mouth_aspect_ratio: 0.023, optical_flow: 4.47, head_yaw_jitter: 3.02, color_consistency: 0.49, skin_ratio: 0.62, boundary_flow_ratio: 2.02 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.947, processing_time: 5.63,
    video_info: { filename: 'diffusion_portrait.mp4', duration_sec: 16.4, total_frames: 492, fps: 30 },
    blink_features: { blink_rate: 0.000, avg_blink_duration: 0.000, avg_ear: 0.288, blink_completeness: 0.288 },
    facial_dynamics: { sharpness: 28.9, symmetry: 0.98, noise_level: 19.8, texture_entropy: 3.41, mouth_aspect_ratio: 0.012, optical_flow: 7.34, head_yaw_jitter: 5.91, color_consistency: 0.76, skin_ratio: 0.50, boundary_flow_ratio: 3.02 },
  },
  {
    success: true, prediction: 'FAKE', confidence: 0.899, processing_time: 4.97,
    video_info: { filename: 'voice_dubbed_fake.mp4', duration_sec: 38.1, total_frames: 1143, fps: 30 },
    blink_features: { blink_rate: 0.047, avg_blink_duration: 0.102, avg_ear: 0.304, blink_completeness: 0.244 },
    facial_dynamics: { sharpness: 55.7, symmetry: 0.90, noise_level: 12.3, texture_entropy: 4.08, mouth_aspect_ratio: 0.022, optical_flow: 5.01, head_yaw_jitter: 3.54, color_consistency: 0.56, skin_ratio: 0.60, boundary_flow_ratio: 2.19 },
  },
];

// ── Constants (same as main page) ────────────────────────────────
const FEATURE_PILLS = [
  { label: 'Eye Aspect Ratio', color: '#00f5ff' },
  { label: 'LBP Texture',      color: '#a855f7' },
  { label: 'Head Pose',        color: '#f59e0b' },
  { label: 'Optical Flow',     color: '#10b981' },
  { label: 'Symmetry',         color: '#ec4899' },
  { label: 'Skin Ratio',       color: '#00f5ff' },
  { label: 'Blink Dynamics',   color: '#a855f7' },
  { label: 'Noise Level',      color: '#ef4444' },
  { label: 'Yaw Jitter',       color: '#f59e0b' },
];

const STATS = [
  { icon: Cpu,       label: 'Model',    value: 'Gradient Boosting', color: '#00f5ff' },
  { icon: GitBranch, label: 'Features', value: '212 signals',       color: '#a855f7' },
  { icon: Zap,       label: 'Pipeline', value: 'EAR + Dynamics',    color: '#f59e0b' },
];

const PIPELINE_STEPS = [
  { icon: Eye,      step: '01', label: 'Face Detection',   sub: 'Haar + DNN',          color: '#00f5ff' },
  { icon: Brain,    step: '02', label: 'Landmark Mesh',    sub: '468-point MediaPipe', color: '#a855f7' },
  { icon: Activity, step: '03', label: 'Feature Extract',  sub: 'EAR + 9 domains',     color: '#f59e0b' },
  { icon: Shield,   step: '04', label: 'Classification',   sub: 'Gradient Boosting',   color: '#10b981' },
];

function Counter({ to, suffix = '' }: { to: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  React.useEffect(() => {
    let frame = 0;
    const total = 60;
    const tick = () => {
      frame++;
      setVal(Math.round((frame / total) * to));
      if (frame < total) requestAnimationFrame(tick);
    };
    const t = setTimeout(() => requestAnimationFrame(tick), 400);
    return () => clearTimeout(t);
  }, [to]);
  return <>{val}{suffix}</>;
}

export default function DemoFakePage() {
  const router = useRouter();
  const [phase, setPhase] = useState<'upload' | 'loading' | 'result'>('upload');
  const [resultIdx, setResultIdx] = useState(0);
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    setResultIdx(Math.floor(Math.random() * FAKE_RESULTS.length));
  }, []);

  const handleUpload = useCallback((file: File) => {
    setFileName(file.name);
    setPhase('loading');
    setTimeout(() => {
      setResultIdx(prev => (prev + 1) % FAKE_RESULTS.length);
      setPhase('result');
    }, 3600 + Math.random() * 2800);
  }, []);

  const reset = useCallback(() => setPhase('upload'), []);

  const activeResult = {
    ...FAKE_RESULTS[resultIdx],
    video_info: {
      ...FAKE_RESULTS[resultIdx].video_info,
      filename: fileName || FAKE_RESULTS[resultIdx].video_info.filename,
    },
  };

  const result = phase === 'result' ? activeResult : null;

  return (
    <div
      className="min-h-screen text-white"
      style={{ background: '#05050d', fontFamily: "'JetBrains Mono','Space Mono',monospace" }}
    >
      {/* ── Ambient background (same as main) ───────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full blur-[120px]"
          style={{ background: '#00f5ff', opacity: 0.04 }} />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full blur-[100px]"
          style={{ background: '#a855f7', opacity: 0.04 }} />
        <div className="absolute inset-0"
          style={{
            backgroundImage: 'linear-gradient(#00f5ff09 1px,transparent 1px),linear-gradient(90deg,#00f5ff09 1px,transparent 1px)',
            backgroundSize: '48px 48px',
          }}
        />
        <div style={{
          position: 'absolute', top: 0, right: '30%', width: 1, height: '100%',
          background: 'linear-gradient(180deg,transparent,#00f5ff15,transparent)',
          transform: 'skewX(-20deg)',
        }} />
      </div>

      {/* ── Navigation (same as main) ────────────────────────────────────── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4"
        style={{ borderBottom: '1px solid #0f0f1e' }}>

        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-3 select-none"
          style={{ cursor: 'default', background: 'none', border: 'none', padding: 0 }}
        >
          <div className="relative">
            <motion.div className="absolute inset-0 rounded-lg blur-md"
              style={{ background: '#00f5ff' }}
              animate={{ opacity: [0.15, 0.45, 0.15] }}
              transition={{ duration: 3, repeat: Infinity }} />
            <div className="relative w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: '#00f5ff0d', border: '1px solid #00f5ff35' }}>
              <Shield className="w-4 h-4" style={{ color: '#00f5ff' }} />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-black text-base tracking-[0.15em] text-white">NEUROBLINK</span>
            <span className="text-[9px] tracking-widest" style={{ color: '#333' }}>
              DEEPFAKE DETECTION SYSTEM
            </span>
          </div>
        </button>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: '#22c55e' }}
              animate={{ opacity: [1, 0.3, 1], scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span style={{ color: '#22c55e', fontSize: 9, letterSpacing: '0.1em' }}>API ONLINE</span>
          </div>
          <div style={{ width: 1, height: 20, background: '#1a1a2e' }} />
          <Link href="/live">
            <motion.div
              className="flex items-center gap-2 cursor-pointer"
              style={{ background: '#ef444408', border: '1px solid #ef444430', borderRadius: 8, padding: '6px 14px' }}
              whileHover={{ scale: 1.03, boxShadow: '0 0 20px #ef444420' }}
              whileTap={{ scale: 0.97 }}
            >
              <motion.div className="w-1.5 h-1.5 rounded-full" style={{ background: '#ef4444' }}
                animate={{ opacity: [1, 0.2, 1] }} transition={{ duration: 1, repeat: Infinity }} />
              <Radio className="w-3 h-3" style={{ color: '#ef4444' }} />
              <span style={{ color: '#ef4444', fontSize: 10, letterSpacing: '0.12em', fontWeight: 'bold' }}>LIVE</span>
              <ArrowRight className="w-3 h-3" style={{ color: '#ef444460' }} />
            </motion.div>
          </Link>
        </div>
      </nav>

      {/* ── Page content ─────────────────────────────────────── */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 py-14">

        {/* ── Hero (only when idle) ── */}
        {phase === 'upload' && (
          <>
            <motion.div
              className="text-center mb-14"
              initial={{ opacity: 0, y: -24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
            >
              <motion.div
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-8"
                style={{ border: '1px solid #00f5ff20', background: '#00f5ff08' }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Activity className="w-3 h-3" style={{ color: '#00f5ff' }} />
                <span style={{ color: '#00f5ff', fontSize: 9, letterSpacing: '0.18em', fontFamily: 'inherit' }}>
                  FACIAL DYNAMICS + EYE BLINK · 212 FEATURES · ML CLASSIFIER
                </span>
              </motion.div>

              <h1 className="font-black tracking-tighter leading-none mb-6"
                style={{ fontSize: 'clamp(52px,8vw,88px)' }}>
                <span style={{ background: 'linear-gradient(135deg,#fff 20%,#00f5ff 80%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'block' }}>
                  Deepfake
                </span>
                <span style={{ background: 'linear-gradient(135deg,#a855f7 10%,#00f5ff 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'block' }}>
                  Detection
                </span>
              </h1>

              <p style={{ color: '#444', fontSize: 13, maxWidth: 480, margin: '0 auto 32px', lineHeight: 1.7 }}>
                Multi-signal analysis across 9 feature domains — blink dynamics,
                head pose, optical flow, texture, symmetry, and more.
                Upload a video or try live camera analysis.
              </p>

              <div className="flex items-center justify-center gap-4 mb-10">
                <motion.button
                  onClick={() => document.getElementById('upload-zone')?.scrollIntoView({ behavior: 'smooth' })}
                  style={{ background: '#00f5ff12', border: '1px solid #00f5ff40', color: '#00f5ff', padding: '10px 24px', borderRadius: 10, fontFamily: 'inherit', fontSize: 11, letterSpacing: '0.12em', cursor: 'pointer', fontWeight: 'bold' }}
                  whileHover={{ scale: 1.04, boxShadow: '0 0 28px #00f5ff25' }}
                  whileTap={{ scale: 0.97 }}
                >
                  ↑ UPLOAD VIDEO
                </motion.button>
                <Link href="/live">
                  <motion.div
                    className="flex items-center gap-2 cursor-pointer"
                    style={{ background: '#ef444410', border: '1px solid #ef444445', color: '#ef4444', padding: '10px 24px', borderRadius: 10, fontSize: 11, letterSpacing: '0.12em', fontWeight: 'bold' }}
                    whileHover={{ scale: 1.04, boxShadow: '0 0 28px #ef444425' }}
                    whileTap={{ scale: 0.97 }}
                  >
                    <motion.div className="w-1.5 h-1.5 rounded-full bg-red-500"
                      animate={{ opacity: [1, 0.2, 1] }} transition={{ duration: 0.8, repeat: Infinity }} />
                    LIVE CAMERA →
                  </motion.div>
                </Link>
              </div>

              <div className="flex flex-wrap justify-center gap-2">
                {FEATURE_PILLS.map((p, i) => (
                  <motion.span key={p.label}
                    initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + i * 0.055 }}
                    style={{ color: p.color, borderColor: `${p.color}25`, background: `${p.color}08`, border: '1px solid', padding: '3px 10px', borderRadius: 999, fontSize: 10, letterSpacing: '0.06em' }}
                  >
                    {p.label}
                  </motion.span>
                ))}
              </div>
            </motion.div>

            {/* ── Stats bar ── */}
            <motion.div className="grid grid-cols-3 gap-3 mb-10"
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              {[
                { icon: Eye,       n: 51,  label: 'Blink Features',    color: '#00f5ff' },
                { icon: Layers,    n: 138, label: 'Dynamics Features', color: '#a855f7' },
                { icon: BarChart2, n: 23,  label: 'Temporal + Video',  color: '#f59e0b' },
              ].map(({ icon: Icon, n, label, color }) => (
                <div key={label} style={{ background: '#0a0a18', border: '1px solid #1a1a2e', borderRadius: 12, padding: '14px 16px', borderTop: `2px solid ${color}30` }}>
                  <div className="flex items-center gap-2 mb-1">
                    <Icon className="w-4 h-4" style={{ color }} />
                    <span style={{ color: '#444', fontSize: 9, letterSpacing: '0.1em' }}>{label}</span>
                  </div>
                  <p style={{ color, fontSize: 28, fontWeight: 900, lineHeight: 1 }}><Counter to={n} /></p>
                </div>
              ))}
            </motion.div>

            {/* ── Model info row ── */}
            <motion.div className="grid grid-cols-3 gap-3 mb-10"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.55 }}>
              {STATS.map(({ icon: Icon, label, value, color }) => (
                <div key={label} className="flex items-center gap-3 rounded-xl p-3"
                  style={{ background: '#0a0a18', border: '1px solid #141425', cursor: 'default', userSelect: 'none' }}>
                  <div style={{ width: 32, height: 32, borderRadius: 8, flexShrink: 0, background: `${color}10`, border: `1px solid ${color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon className="w-4 h-4" style={{ color }} />
                  </div>
                  <div>
                    <p style={{ color: '#444', fontSize: 9, letterSpacing: '0.08em' }}>{label}</p>
                    <p style={{ color: '#ddd', fontSize: 11, fontWeight: 'bold' }}>{value}</p>
                  </div>
                </div>
              ))}
            </motion.div>
          </>
        )}

        {/* ── Upload / Loading / Result ── */}
        <div id="upload-zone">
          <AnimatePresence mode="wait">

            {phase === 'upload' && (
              <motion.div key="upload"
                initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.3 }}>
                <div style={{ borderRadius: 20, border: '1px solid #141425', background: '#07071280', padding: 32, boxShadow: '0 0 80px #00f5ff05, inset 0 1px 0 #ffffff06' }}>
                  <div className="flex items-center gap-3 mb-6">
                    <Crosshair className="w-4 h-4" style={{ color: '#00f5ff' }} />
                    <span style={{ color: '#00f5ff', fontSize: 10, letterSpacing: '0.15em' }}>VIDEO UPLOAD · DEEPFAKE ANALYSIS</span>
                    <div style={{ flex: 1, height: 1, background: '#0f0f1e' }} />
                  </div>
                  <UploadForm onFileUpload={handleUpload} />
                </div>

                <motion.div className="mt-4 flex items-center justify-center gap-3"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
                  <div style={{ height: 1, width: 60, background: '#1a1a2e' }} />
                  <span style={{ color: '#333', fontSize: 10, letterSpacing: '0.1em' }}>OR USE YOUR CAMERA</span>
                  <div style={{ height: 1, width: 60, background: '#1a1a2e' }} />
                </motion.div>

                <motion.div className="flex justify-center mt-4"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
                  <Link href="/live">
                    <motion.div className="flex items-center gap-3 cursor-pointer"
                      style={{ background: '#0d0d1a', border: '1px solid #1a1a2e', borderRadius: 12, padding: '12px 24px' }}
                      whileHover={{ scale: 1.02, borderColor: '#ef444440', boxShadow: '0 0 30px #ef444415' }}
                      whileTap={{ scale: 0.98 }}>
                      <div style={{ width: 36, height: 36, borderRadius: 8, flexShrink: 0, background: '#ef44440d', border: '1px solid #ef444430', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Radio className="w-4 h-4" style={{ color: '#ef4444' }} />
                      </div>
                      <div>
                        <p style={{ color: '#ddd', fontSize: 11, fontWeight: 'bold', letterSpacing: '0.1em' }}>LIVE CAMERA ANALYSIS</p>
                        <p style={{ color: '#444', fontSize: 9, marginTop: 1 }}>Real-time landmark overlay + feature dashboard</p>
                      </div>
                      <ArrowRight className="w-4 h-4 ml-2" style={{ color: '#ef444450' }} />
                    </motion.div>
                  </Link>
                </motion.div>
              </motion.div>
            )}

            {phase === 'loading' && (
              <motion.div key="loading"
                initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.97 }} transition={{ duration: 0.3 }}
                style={{ borderRadius: 20, border: '1px solid #141425', background: '#07071280', padding: '48px 32px', boxShadow: '0 0 80px #00f5ff05' }}>
                <LoadingSpinner />
                <div className="flex flex-col items-center gap-2 mt-8">
                  {[
                    { label: 'Detecting face & landmarks', color: '#00f5ff', delay: 0 },
                    { label: 'Computing EAR sequences',    color: '#a855f7', delay: 0.8 },
                    { label: 'Extracting 212 features',   color: '#f59e0b', delay: 1.6 },
                    { label: 'Running classifier',        color: '#10b981', delay: 2.4 },
                  ].map(({ label, color, delay }) => (
                    <motion.div key={label} className="flex items-center gap-2"
                      initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay }}>
                      <motion.div className="w-1 h-1 rounded-full" style={{ background: color }}
                        animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1.2, repeat: Infinity, delay }} />
                      <span style={{ color: '#555', fontSize: 10, fontFamily: 'inherit', letterSpacing: '0.06em' }}>{label}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {phase === 'result' && result && (
              <motion.div key="result"
                initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }} transition={{ duration: 0.4 }}>
                <ResultDisplay result={result} />
                <div className="text-center mt-8">
                  <motion.button onClick={reset}
                    style={{ background: '#00f5ff0d', border: '1px solid #00f5ff30', color: '#00f5ff', padding: '10px 28px', borderRadius: 10, fontFamily: 'inherit', fontSize: 10, letterSpacing: '0.14em', cursor: 'pointer', fontWeight: 'bold' }}
                    whileHover={{ scale: 1.03, boxShadow: '0 0 24px #00f5ff20' }}
                    whileTap={{ scale: 0.97 }}>
                    ← ANALYZE ANOTHER
                  </motion.button>
                </div>
              </motion.div>
            )}

          </AnimatePresence>
        </div>

        {/* ── Pipeline steps ── */}
        {phase === 'upload' && (
          <motion.div className="mt-12" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}>
            <div className="flex items-center gap-3 mb-4">
              <div style={{ height: 1, flex: 1, background: '#0f0f1e' }} />
              <span style={{ color: '#333', fontSize: 9, letterSpacing: '0.15em' }}>HOW IT WORKS</span>
              <div style={{ height: 1, flex: 1, background: '#0f0f1e' }} />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {PIPELINE_STEPS.map(({ icon: Icon, step, label, sub, color }, idx) => (
                <motion.div key={step}
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 + idx * 0.08 }}
                  style={{ borderRadius: 12, border: '1px solid #0f0f1e', background: '#07070f', padding: '14px 14px', borderLeft: `2px solid ${color}30` }}>
                  <div className="flex items-center gap-2 mb-3">
                    <span style={{ color: `${color}40`, fontSize: 8, letterSpacing: '0.1em' }}>{step}</span>
                    <div style={{ width: 24, height: 24, borderRadius: 6, background: `${color}0d`, border: `1px solid ${color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon className="w-3 h-3" style={{ color }} />
                    </div>
                  </div>
                  <p style={{ color: '#ccc', fontSize: 10, fontWeight: 'bold', letterSpacing: '0.06em', marginBottom: 2 }}>{label}</p>
                  <p style={{ color: '#333', fontSize: 9 }}>{sub}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* ── Footer ── */}
      <footer style={{ borderTop: '1px solid #0a0a18', padding: '20px 0', marginTop: 32 }}>
        <div className="flex items-center justify-center gap-6">
          <p style={{ color: '#222', fontSize: 9, letterSpacing: '0.12em', fontFamily: 'inherit' }}>
            NEUROBLINK · PROTECTING DIGITAL AUTHENTICITY
          </p>
          <Link href="/live">
            <span style={{ color: '#333', fontSize: 9, letterSpacing: '0.1em', cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: 3 }}>
              → LIVE MODE
            </span>
          </Link>
        </div>
      </footer>
    </div>
  );
}