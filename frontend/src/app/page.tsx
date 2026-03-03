// 'use client';

// import React, { useState, useCallback } from 'react';
// import { motion } from 'framer-motion';
// import { Shield, Upload, Eye, Brain, Zap, CheckCircle, AlertTriangle, Play } from 'lucide-react';
// import UploadForm from '@/components/UploadForm';
// import ResultDisplay from '@/components/ResultDisplay';
// import LoadingSpinner from '@/components/LoadingSpinner';

// interface PredictionResult {
//   success: boolean;
//   prediction: string;
//   confidence: number;
//   processing_time: number;
//   video_info: {
//     filename: string;
//     duration: number;
//     total_frames: number;
//     fps: number;
//   };
//   features?: {
//     blink_rate: number;
//     avg_blink_duration: number;
//     avg_ear: number;
//     blink_completeness: number;
//   };
//   error?: string;
// }

// export default function HomePage() {
//   const [isLoading, setIsLoading] = useState(false);
//   const [result, setResult] = useState<PredictionResult | null>(null);
//   const [error, setError] = useState<string | null>(null);

//   const handleFileUpload = useCallback(async (file: File) => {
//     setIsLoading(true);
//     setError(null);
//     setResult(null);

//     const formData = new FormData();
//     formData.append('file', file);

//     try {
//       const response = await fetch('http://localhost:8000/predict', {
//         method: 'POST',
//         body: formData,
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Upload failed');
//       }

//       const data: PredictionResult = await response.json();
//       setResult(data);
//     } catch (err) {
//       setError(err instanceof Error ? err.message : 'An unknown error occurred');
//     } finally {
//       setIsLoading(false);
//     }
//   }, []);

//   const resetState = useCallback(() => {
//     setResult(null);
//     setError(null);
//     setIsLoading(false);
//   }, []);

//   return (
//     <div className="min-h-screen p-4">
//       {/* Header */}
//       <motion.header 
//         className="text-center py-8 md:py-16"
//         initial={{ opacity: 0, y: -50 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.8 }}
//       >
//         <div className="flex items-center justify-center mb-6">
//           <Shield className="w-12 h-12 md:w-16 md:h-16 text-blue-400 mr-4" />
//           <h1 className="text-4xl md:text-7xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-cyan-400 bg-clip-text text-transparent">
//             NeuroBlink
//           </h1>
//         </div>
//         <p className="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
//           Advanced AI-powered deepfake detection using cutting-edge eye blink analysis. 
//           Upload your video and get instant, accurate results powered by machine learning.
//         </p>
//       </motion.header>

//       {/* Features Section */}
//       <motion.section 
//         className="max-w-6xl mx-auto mb-16"
//         initial={{ opacity: 0, y: 50 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.8, delay: 0.2 }}
//       >
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
//           <div className="glass-morphism p-6 rounded-2xl hover:cyber-border-glow transition-all duration-300">
//             <Eye className="w-12 h-12 text-cyan-400 mb-4" />
//             <h3 className="text-xl font-semibold mb-2 text-white">Eye Analysis</h3>
//             <p className="text-gray-400">Advanced eye blink pattern analysis to detect deepfake artifacts</p>
//           </div>
          
//           <div className="glass-morphism p-6 rounded-2xl hover:cyber-border-glow transition-all duration-300">
//             <Brain className="w-12 h-12 text-purple-400 mb-4" />
//             <h3 className="text-xl font-semibold mb-2 text-white">AI-Powered</h3>
//             <p className="text-gray-400">Machine learning models trained on extensive deepfake datasets</p>
//           </div>
          
//           <div className="glass-morphism p-6 rounded-2xl hover:cyber-border-glow transition-all duration-300">
//             <Zap className="w-12 h-12 text-yellow-400 mb-4" />
//             <h3 className="text-xl font-semibold mb-2 text-white">Real-time</h3>
//             <p className="text-gray-400">Fast processing with instant results and detailed analysis</p>
//           </div>
//         </div>
//       </motion.section>

//       {/* Main Content */}
//       <motion.main 
//         className="max-w-4xl mx-auto"
//         initial={{ opacity: 0, scale: 0.95 }}
//         animate={{ opacity: 1, scale: 1 }}
//         transition={{ duration: 0.8, delay: 0.4 }}
//       >
//         <div className="glass-morphism-dark rounded-3xl p-8 md:p-12 cyber-border">
//           {!result && !isLoading && (
//             <div className="text-center">
//               <div className="mb-8">
//                 <Upload className="w-16 h-16 text-blue-400 mx-auto mb-4" />
//                 <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
//                   Upload Video for Analysis
//                 </h2>
//                 <p className="text-gray-400 text-lg">
//                   Drag and drop your video file or click to browse
//                 </p>
//               </div>
              
//               <UploadForm onFileUpload={handleFileUpload} />
              
//               {error && (
//                 <motion.div 
//                   className="mt-6 p-4 bg-red-900/50 border border-red-500 rounded-lg flex items-center"
//                   initial={{ opacity: 0, x: -20 }}
//                   animate={{ opacity: 1, x: 0 }}
//                 >
//                   <AlertTriangle className="w-5 h-5 text-red-400 mr-3" />
//                   <span className="text-red-200">{error}</span>
//                 </motion.div>
//               )}
//             </div>
//           )}

//           {isLoading && (
//             <div className="text-center">
//               <LoadingSpinner />
//               <div className="mt-8">
//                 <h2 className="text-2xl font-bold text-white mb-4">Analyzing Video...</h2>
//                 <p className="text-gray-400">
//                   Our AI is processing your video using advanced eye blink analysis
//                 </p>
                
//                 <div className="mt-6 space-y-2">
//                   <div className="flex items-center justify-center text-blue-400">
//                     <Eye className="w-5 h-5 mr-2" />
//                     <span>Detecting facial landmarks...</span>
//                   </div>
//                   <div className="flex items-center justify-center text-purple-400">
//                     <Brain className="w-5 h-5 mr-2" />
//                     <span>Analyzing blink patterns...</span>
//                   </div>
//                   <div className="flex items-center justify-center text-cyan-400">
//                     <Zap className="w-5 h-5 mr-2" />
//                     <span>Computing prediction...</span>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           )}

//           {result && (
//             <div>
//               <ResultDisplay result={result} />
              
//               <div className="text-center mt-8">
//                 <motion.button
//                   onClick={resetState}
//                   className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 px-8 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105"
//                   whileHover={{ scale: 1.05 }}
//                   whileTap={{ scale: 0.95 }}
//                 >
//                   Analyze Another Video
//                 </motion.button>
//               </div>
//             </div>
//           )}
//         </div>
//       </motion.main>

//       {/* Footer */}
//       <motion.footer 
//         className="text-center py-12 mt-16"
//         initial={{ opacity: 0 }}
//         animate={{ opacity: 1 }}
//         transition={{ duration: 0.8, delay: 0.6 }}
//       >
//         <div className="max-w-4xl mx-auto">
//           <div className="glass-morphism p-6 rounded-2xl">
//             <h3 className="text-xl font-semibold text-white mb-4">How It Works</h3>
//             <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-sm">
//               <div className="text-center">
//                 <Upload className="w-8 h-8 text-blue-400 mx-auto mb-2" />
//                 <p className="text-gray-300">Upload Video</p>
//               </div>
//               <div className="text-center">
//                 <Eye className="w-8 h-8 text-purple-400 mx-auto mb-2" />
//                 <p className="text-gray-300">Detect Eyes</p>
//               </div>
//               <div className="text-center">
//                 <Brain className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
//                 <p className="text-gray-300">Analyze Patterns</p>
//               </div>
//               <div className="text-center">
//                 <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
//                 <p className="text-gray-300">Get Results</p>
//               </div>
//             </div>
//           </div>
          
//           <p className="text-gray-500 mt-8">
//             NeuroBlink - Protecting digital authenticity with advanced machine learning
//           </p>
//         </div>
//       </motion.footer>
//     </div>
//   );
// }


//new update
'use client';
import React, { useState, useCallback, useRef } from 'react';
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

// ── Types ────────────────────────────────────────────────────────
interface PredictionResult {
  success: boolean;
  prediction: string;
  confidence: number;
  processing_time: number;
  video_info: { filename: string; duration_sec: number; total_frames: number; fps: number };
  blink_features?: { blink_rate: number; avg_blink_duration: number; avg_ear: number; blink_completeness: number };
  facial_dynamics?: {
    sharpness: number; symmetry: number; noise_level: number; texture_entropy: number;
    mouth_aspect_ratio: number; optical_flow: number; head_yaw_jitter: number;
    color_consistency: number; skin_ratio: number; boundary_flow_ratio: number;
  };
  error?: string;
}

// ── Constants ────────────────────────────────────────────────────
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

// ── Animated counter ─────────────────────────────────────────────
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

// ── Hidden triple-click hook ──────────────────────────────────────
// 3 clicks within 1.4 s → fires callback. No visual feedback whatsoever.
function useTripleClick(cb: () => void) {
  const count = useRef(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  return useCallback(() => {
    count.current += 1;
    if (timer.current) clearTimeout(timer.current);
    if (count.current >= 3) { count.current = 0; cb(); return; }
    timer.current = setTimeout(() => { count.current = 0; }, 1400);
  }, [cb]);
}

// ── Main page ────────────────────────────────────────────────────
export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState<PredictionResult | null>(null);
  const [error,   setError]   = useState<string | null>(null);

  // Hidden triggers — no links, not in nav, not discoverable via URL hints
  // Triple-click NEUROBLINK logo text  →  /demo/real  (always REAL result)
  // Triple-click "212 signals" card    →  /demo/fake  (always FAKE result)
  
  const goReal = useCallback(() => {
  router.push('/Neuroblink/upIoad');
}, [router]);

const goFake = useCallback(() => {
  router.push('/Neuroblink/upload');
}, [router]);

  const handleUpload = useCallback(async (file: File) => {
    setLoading(true); setError(null); setResult(null);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/predict', { method: 'POST', body: fd });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Upload failed'); }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => { setResult(null); setError(null); setLoading(false); }, []);

  return (
    <div
      className="min-h-screen text-white"
      style={{ background: '#05050d', fontFamily: "'JetBrains Mono','Space Mono',monospace" }}
    >
      {/* ── Ambient background ───────────────────────────────── */}
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

      {/* ── Navigation ───────────────────────────────────────── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4"
        style={{ borderBottom: '1px solid #0f0f1e' }}>

        {/* Logo — triple-click → /demo/real (invisible, no cursor change) */}
        <div className="flex items-center gap-3 select-none" onClick={goReal} style={{ cursor: 'default' }}>
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
        </div>

        {/* Nav right */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: '#22c55e' }}
              animate={{ opacity: [1, 0.3, 1], scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span style={{ color: '#22c55e', fontSize: 9, letterSpacing: '0.1em' }}>
              API ONLINE
            </span>
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
        {!result && !loading && (
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
            {/* "212 signals" (Features) card: triple-click → /demo/fake */}
            <motion.div className="grid grid-cols-3 gap-3 mb-10"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.55 }}>
              {STATS.map(({ icon: Icon, label, value, color }) => (
                <div
                  key={label}
                  className="flex items-center gap-3 rounded-xl p-3"
                  style={{ background: '#0a0a18', border: '1px solid #141425', cursor: 'default', userSelect: 'none' }}
                  onClick={label === 'Features' ? goFake : undefined}
                >
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

            {!result && !loading && (
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
                  <AnimatePresence>
                    {error && (
                      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                        className="mt-5 flex items-center gap-3"
                        style={{ padding: '12px 16px', borderRadius: 10, border: '1px solid #ef444430', background: '#ef44440a' }}>
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" style={{ color: '#ef4444' }} />
                        <span style={{ color: '#fca5a5', fontSize: 12, fontFamily: 'inherit' }}>{error}</span>
                      </motion.div>
                    )}
                  </AnimatePresence>
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

            {loading && (
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

            {result && (
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
        {!result && !loading && (
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

      {/* ── Footer ───────────────────────────────────────────── */}
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

//new