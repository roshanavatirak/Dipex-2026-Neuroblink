// import React from 'react';
// import { motion } from 'framer-motion';
// import { Shield, AlertTriangle, Clock, Eye, Activity, BarChart3, FileVideo } from 'lucide-react';

// interface ResultDisplayProps {
//   result: {
//     success: boolean;
//     prediction: string;
//     confidence: number;
//     processing_time: number;
//     video_info: {
//       filename: string;
//       duration: number;
//       total_frames: number;
//       fps: number;
//     };
//     features?: {
//       blink_rate: number;
//       avg_blink_duration: number;
//       avg_ear: number;
//       blink_completeness: number;
//     };
//     error?: string;
//   };
// }

// const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
//   const isReal = result.prediction === 'REAL';
//   const confidencePercentage = (result.confidence * 100).toFixed(2);

//   const getConfidenceColor = (confidence: number) => {
//     if (confidence >= 0.8) return 'text-green-400';
//     if (confidence >= 0.6) return 'text-yellow-400';
//     return 'text-red-400';
//   };

//   const getConfidenceBarColor = (confidence: number) => {
//     if (confidence >= 0.8) return 'bg-gradient-to-r from-green-500 to-green-400';
//     if (confidence >= 0.6) return 'bg-gradient-to-r from-yellow-500 to-yellow-400';
//     return 'bg-gradient-to-r from-red-500 to-red-400';
//   };

//   return (
//     <motion.div
//       initial={{ opacity: 0, scale: 0.9 }}
//       animate={{ opacity: 1, scale: 1 }}
//       transition={{ duration: 0.5 }}
//       className="space-y-8"
//     >
//       {/* Main Result Card */}
//       <div className={`p-8 rounded-2xl ${isReal ? 'result-card-real' : 'result-card-fake'}`}>
//         <div className="flex items-center justify-between mb-6">
//           <div className="flex items-center space-x-4">
//             {isReal ? (
//               <Shield className="w-12 h-12 text-green-400" />
//             ) : (
//               <AlertTriangle className="w-12 h-12 text-red-400" />
//             )}
//             <div>
//               <h2 className="text-3xl font-bold text-white mb-1">
//                 {result.prediction}
//               </h2>
//               <p className="text-gray-300">
//                 {isReal ? 'This video appears to be authentic' : 'This video may be a deepfake'}
//               </p>
//             </div>
//           </div>
          
//           <div className="text-right">
//             <div className={`text-4xl font-bold ${getConfidenceColor(result.confidence)}`}>
//               {confidencePercentage}%
//             </div>
//             <p className="text-gray-400 text-sm">Confidence</p>
//           </div>
//         </div>

//         {/* Confidence Bar */}
//         <div className="mb-6">
//           <div className="flex justify-between items-center mb-2">
//             <span className="text-gray-300 text-sm">Confidence Level</span>
//             <span className="text-gray-300 text-sm">{confidencePercentage}%</span>
//           </div>
//           <div className="w-full bg-gray-700 rounded-full h-3">
//             <motion.div
//               className={`h-3 rounded-full ${getConfidenceBarColor(result.confidence)}`}
//               initial={{ width: 0 }}
//               animate={{ width: `${result.confidence * 100}%` }}
//               transition={{ duration: 1, delay: 0.3 }}
//             />
//           </div>
//         </div>

//         {/* Processing Info */}
//         <div className="flex items-center justify-between text-sm text-gray-400 border-t border-gray-600 pt-4">
//           <div className="flex items-center space-x-2">
//             <Clock className="w-4 h-4" />
//             <span>Processed in {result.processing_time.toFixed(2)}s</span>
//           </div>
//           <div className="flex items-center space-x-2">
//             <Eye className="w-4 h-4" />
//             <span>Eye Blink Analysis</span>
//           </div>
//         </div>
//       </div>

//       {/* Video Information */}
//       <div className="glass-morphism p-6 rounded-2xl">
//         <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
//           <FileVideo className="w-6 h-6 mr-2" />
//           Video Information
//         </h3>
        
//         <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
//           <div className="text-center">
//             <div className="text-2xl font-bold text-blue-400 mb-1">
//               {result.video_info.duration.toFixed(1)}s
//             </div>
//             <p className="text-gray-400 text-sm">Duration</p>
//           </div>
          
//           <div className="text-center">
//             <div className="text-2xl font-bold text-purple-400 mb-1">
//               {result.video_info.total_frames}
//             </div>
//             <p className="text-gray-400 text-sm">Frames</p>
//           </div>
          
//           <div className="text-center">
//             <div className="text-2xl font-bold text-cyan-400 mb-1">
//               {result.video_info.fps.toFixed(0)}
//             </div>
//             <p className="text-gray-400 text-sm">FPS</p>
//           </div>
          
//           <div className="text-center">
//             <div className="text-2xl font-bold text-green-400 mb-1 truncate">
//               {result.video_info.filename.length > 10 
//                 ? result.video_info.filename.substring(0, 10) + '...' 
//                 : result.video_info.filename}
//             </div>
//             <p className="text-gray-400 text-sm">Filename</p>
//           </div>
//         </div>
//       </div>

//       {/* Feature Analysis */}
//       {result.features && (
//         <div className="glass-morphism p-6 rounded-2xl">
//           <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
//             <BarChart3 className="w-6 h-6 mr-2" />
//             Feature Analysis
//           </h3>
          
//           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//             <div className="space-y-4">
//               <div className="flex justify-between items-center">
//                 <span className="text-gray-300">Blink Rate</span>
//                 <div className="flex items-center space-x-2">
//                   <Activity className="w-4 h-4 text-blue-400" />
//                   <span className="text-blue-400 font-semibold">
//                     {result.features.blink_rate.toFixed(3)}/s
//                   </span>
//                 </div>
//               </div>
              
//               <div className="flex justify-between items-center">
//                 <span className="text-gray-300">Avg Blink Duration</span>
//                 <div className="flex items-center space-x-2">
//                   <Clock className="w-4 h-4 text-purple-400" />
//                   <span className="text-purple-400 font-semibold">
//                     {(result.features.avg_blink_duration * 1000).toFixed(0)}ms
//                   </span>
//                 </div>
//               </div>
//             </div>
            
//             <div className="space-y-4">
//               <div className="flex justify-between items-center">
//                 <span className="text-gray-300">Eye Aspect Ratio</span>
//                 <div className="flex items-center space-x-2">
//                   <Eye className="w-4 h-4 text-cyan-400" />
//                   <span className="text-cyan-400 font-semibold">
//                     {result.features.avg_ear.toFixed(3)}
//                   </span>
//                 </div>
//               </div>
              
//               <div className="flex justify-between items-center">
//                 <span className="text-gray-300">Blink Completeness</span>
//                 <div className="flex items-center space-x-2">
//                   <Shield className="w-4 h-4 text-green-400" />
//                   <span className="text-green-400 font-semibold">
//                     {result.features.blink_completeness.toFixed(3)}
//                   </span>
//                 </div>
//               </div>
//             </div>
//           </div>

//           <div className="mt-6 p-4 bg-gray-800/50 rounded-lg">
//             <p className="text-gray-400 text-sm">
//               <strong>Analysis:</strong> These features represent eye movement patterns extracted from your video. 
//               Deepfakes often exhibit irregular blinking patterns that differ from natural human behavior.
//             </p>
//           </div>
//         </div>
//       )}

//       {/* Recommendation */}
//       <div className={`p-6 rounded-2xl border ${
//         isReal 
//           ? 'bg-green-900/20 border-green-500/30' 
//           : 'bg-red-900/20 border-red-500/30'
//       }`}>
//         <h3 className="text-lg font-semibold text-white mb-3">
//           {isReal ? 'Verification Result' : 'Detection Alert'}
//         </h3>
//         <p className="text-gray-300 mb-4">
//           {isReal 
//             ? 'Our analysis indicates this video shows natural human behavior patterns consistent with authentic footage.'
//             : 'Our analysis has detected patterns that may indicate artificial manipulation. Consider additional verification if authenticity is critical.'
//           }
//         </p>
        
//         <div className="flex items-center space-x-2 text-sm">
//           {isReal ? (
//             <Shield className="w-4 h-4 text-green-400" />
//           ) : (
//             <AlertTriangle className="w-4 h-4 text-red-400" />
//           )}
//           <span className={isReal ? 'text-green-400' : 'text-red-400'}>
//             Confidence: {confidencePercentage}%
//           </span>
//         </div>
//       </div>
//     </motion.div>
//   );
// };

// export default ResultDisplay;

//new update
'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, AlertTriangle, Clock, Eye, Activity, BarChart3,
  FileVideo, ChevronDown, Layers, Crosshair, Wind, Scan,
  Palette, Cpu, TrendingUp,
} from 'lucide-react';

interface ResultDisplayProps {
  result: {
    success: boolean;
    prediction: string;
    confidence: number;
    processing_time: number;
    video_info: {
      filename: string;
      duration_sec?: number;
      duration?: number;
      total_frames: number;
      fps: number;
    };
    blink_features?: {
      blink_rate: number;
      avg_blink_duration: number;
      avg_ear: number;
      blink_completeness: number;
    };
    facial_dynamics?: {
      sharpness: number;
      symmetry: number;
      noise_level: number;
      texture_entropy: number;
      mouth_aspect_ratio: number;
      optical_flow: number;
      head_yaw_jitter: number;
      color_consistency: number;
      skin_ratio: number;
      boundary_flow_ratio: number;
    };
    error?: string;
  };
}

// ── Mini bar gauge ──────────────────────────────────────────────────────────
const Gauge = ({
  value, max = 1, color, label, sublabel,
}: { value: number; max?: number; color: string; label: string; sublabel?: string }) => {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="group">
      <div className="flex justify-between items-baseline mb-1">
        <span className="text-xs font-mono text-gray-400 group-hover:text-gray-200 transition-colors">{label}</span>
        <span className="text-xs font-mono" style={{ color }}>{value.toFixed(3)}</span>
      </div>
      <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: 'easeOut', delay: 0.1 }}
        />
      </div>
      {sublabel && <p className="text-gray-600 text-[10px] font-mono mt-0.5">{sublabel}</p>}
    </div>
  );
};

// ── Collapsible section ──────────────────────────────────────────────────────
const Section = ({
  title, icon: Icon, color, children, defaultOpen = false,
}: { title: string; icon: React.ElementType; color: string; children: React.ReactNode; defaultOpen?: boolean }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-800 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 bg-gray-900/60 hover:bg-gray-900/90 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Icon className="w-4 h-4" style={{ color }} />
          <span className="text-sm font-mono font-semibold tracking-wider uppercase text-gray-300">{title}</span>
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.25 }}>
          <ChevronDown className="w-4 h-4 text-gray-600" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-5 py-4 bg-black/20">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ── Main component ──────────────────────────────────────────────────────────
export default function ResultDisplay({ result }: ResultDisplayProps) {
  const isReal = result.prediction === 'REAL';
  const conf = result.confidence;
  const pct = (conf * 100).toFixed(1);
  const duration = result.video_info.duration_sec ?? result.video_info.duration ?? 0;

  const accentColor = isReal ? '#10b981' : '#ef4444';
  const accentGlow  = isReal ? '#10b98140' : '#ef444440';

  // Risk interpretation
  const riskLabel =
    conf >= 0.85 ? (isReal ? 'High Authenticity' : 'High Risk')
    : conf >= 0.65 ? (isReal ? 'Likely Authentic' : 'Moderate Risk')
    : 'Uncertain';

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-4 max-w-2xl mx-auto"
    >
      {/* ── Hero verdict card ── */}
      <div
        className="relative rounded-2xl overflow-hidden p-6"
        style={{
          background: `linear-gradient(135deg, ${accentGlow} 0%, #0a0a0a 60%)`,
          border: `1px solid ${accentColor}40`,
          boxShadow: `0 0 40px ${accentGlow}`,
        }}
      >
        {/* Decorative grid lines */}
        <div className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(${accentColor} 1px, transparent 1px), linear-gradient(90deg, ${accentColor} 1px, transparent 1px)`,
            backgroundSize: '32px 32px',
          }}
        />

        <div className="relative flex items-start justify-between gap-4">
          {/* Icon + label */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <motion.div
                className="absolute inset-0 rounded-full blur-lg"
                style={{ background: accentColor }}
                animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 2.5, repeat: Infinity }}
              />
              {isReal
                ? <Shield className="w-12 h-12 relative" style={{ color: accentColor }} />
                : <AlertTriangle className="w-12 h-12 relative" style={{ color: accentColor }} />
              }
            </div>
            <div>
              <p className="text-xs font-mono tracking-widest uppercase text-gray-500 mb-1">Analysis Result</p>
              <h2 className="text-4xl font-black tracking-tight" style={{ color: accentColor }}>
                {result.prediction}
              </h2>
              <p className="text-gray-400 text-sm mt-1">{riskLabel}</p>
            </div>
          </div>

          {/* Confidence ring */}
          <div className="flex-shrink-0 text-center">
            <div className="relative w-20 h-20">
              <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="34" fill="none" stroke="#1f2937" strokeWidth="6" />
                <motion.circle
                  cx="40" cy="40" r="34"
                  fill="none"
                  stroke={accentColor}
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 34}`}
                  initial={{ strokeDashoffset: 2 * Math.PI * 34 }}
                  animate={{ strokeDashoffset: 2 * Math.PI * 34 * (1 - conf) }}
                  transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
                  style={{ filter: `drop-shadow(0 0 6px ${accentColor})` }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-black text-white leading-none">{pct}%</span>
                <span className="text-gray-500 text-[9px] font-mono">conf.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Processing meta */}
        <div className="relative flex items-center gap-6 mt-5 pt-4 border-t border-gray-800">
          <div className="flex items-center gap-2 text-gray-500 text-xs font-mono">
            <Clock className="w-3 h-3" />
            <span>{result.processing_time.toFixed(2)}s processing</span>
          </div>
          <div className="flex items-center gap-2 text-gray-500 text-xs font-mono">
            <Eye className="w-3 h-3" />
            <span>EAR + Dynamics pipeline</span>
          </div>
          <div className="flex items-center gap-2 text-gray-500 text-xs font-mono ml-auto">
            <Cpu className="w-3 h-3" />
            <span>Gradient Boosting</span>
          </div>
        </div>
      </div>

      {/* ── Video info strip ── */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { label: 'Duration', value: `${duration.toFixed(1)}s`, color: '#00f5ff' },
          { label: 'Frames', value: result.video_info.total_frames, color: '#a855f7' },
          { label: 'FPS', value: result.video_info.fps.toFixed(0), color: '#f59e0b' },
          { label: 'File', value: result.video_info.filename.split('.').pop()?.toUpperCase() ?? '—', color: '#10b981' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-gray-900/60 border border-gray-800 rounded-xl p-3 text-center">
            <p className="text-lg font-black" style={{ color }}>{value}</p>
            <p className="text-gray-600 text-xs font-mono mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* ── Eye blink section ── */}
      {result.blink_features && (
        <Section title="Eye Blink Analysis" icon={Eye} color="#00f5ff" defaultOpen>
          <div className="grid grid-cols-2 gap-x-6 gap-y-3">
            <Gauge
              value={result.blink_features.blink_rate}
              max={0.5}
              color="#00f5ff"
              label="Blink Rate"
              sublabel="blinks / second"
            />
            <Gauge
              value={result.blink_features.avg_ear}
              max={0.5}
              color="#a855f7"
              label="Eye Aspect Ratio"
              sublabel="avg EAR value"
            />
            <Gauge
              value={result.blink_features.avg_blink_duration}
              max={0.5}
              color="#f59e0b"
              label="Blink Duration"
              sublabel="avg seconds"
            />
            <Gauge
              value={result.blink_features.blink_completeness}
              max={0.3}
              color="#10b981"
              label="Blink Completeness"
              sublabel="eye closure depth"
            />
          </div>
          <p className="text-gray-600 text-xs font-mono mt-3 leading-relaxed">
            Natural human blink rate: 0.2–0.4/s · EAR closed threshold: &lt;0.25 · Duration: 150–400ms
          </p>
        </Section>
      )}

      {/* ── Facial dynamics sections ── */}
      {result.facial_dynamics && (() => {
        const fd = result.facial_dynamics!;
        return (
          <>
            {/* Edge & sharpness */}
            <Section title="Edge & Artifact Detection" icon={Scan} color="#00f5ff">
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <Gauge value={fd.sharpness} max={200} color="#00f5ff" label="Sharpness Score" sublabel="Laplacian variance" />
                <Gauge value={fd.noise_level} max={20} color="#ef4444" label="Noise Level" sublabel="high-pass residual σ" />
                <Gauge value={fd.texture_entropy} max={8} color="#f59e0b" label="Texture Entropy" sublabel="LBP distribution" />
              </div>
              <p className="text-gray-600 text-xs font-mono mt-3">
                Deepfakes often show elevated noise and reduced sharpness near face boundaries.
              </p>
            </Section>

            {/* Symmetry */}
            <Section title="Facial Symmetry" icon={Layers} color="#a855f7">
              <div className="grid grid-cols-1 gap-3">
                <Gauge value={fd.symmetry} max={1} color="#a855f7" label="Symmetry Score" sublabel="left/right mirror similarity" />
              </div>
              <div className="mt-3 flex items-center gap-3">
                <div className="flex-1 h-px bg-gray-800" />
                <span className="text-xs font-mono text-gray-600">
                  {fd.symmetry > 0.85 ? '⬆ Unusually high — GAN artifact possible'
                    : fd.symmetry > 0.65 ? '✓ Normal range'
                    : '⬇ Low — lighting or pose asymmetry'}
                </span>
                <div className="flex-1 h-px bg-gray-800" />
              </div>
            </Section>

            {/* Head pose */}
            <Section title="Head Pose & Motion" icon={Crosshair} color="#f59e0b">
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <Gauge value={Math.abs(fd.head_yaw_jitter)} max={5} color="#f59e0b" label="Yaw Jitter" sublabel="temporal instability" />
                <Gauge value={fd.boundary_flow_ratio} max={3} color="#ef4444" label="Boundary Flow Ratio" sublabel="edge vs interior motion" />
              </div>
              <p className="text-gray-600 text-xs font-mono mt-3">
                High yaw jitter or boundary flow spikes indicate inconsistent face synthesis.
              </p>
            </Section>

            {/* Optical flow */}
            <Section title="Optical Flow" icon={Wind} color="#10b981">
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <Gauge value={fd.optical_flow} max={5} color="#10b981" label="Flow Mean" sublabel="overall motion magnitude" />
                <Gauge value={fd.mouth_aspect_ratio} max={0.6} color="#00f5ff" label="Mouth Aspect Ratio" sublabel="lip dynamics" />
              </div>
            </Section>

            {/* Color & skin */}
            <Section title="Color & Skin Analysis" icon={Palette} color="#ec4899">
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <Gauge value={fd.color_consistency} max={0.5} color="#ec4899" label="Hue Consistency" sublabel="skin tone uniformity" />
                <Gauge value={fd.skin_ratio} max={1} color="#f59e0b" label="Skin Pixel Ratio" sublabel="YCrCb skin detection" />
              </div>
              <p className="text-gray-600 text-xs font-mono mt-3">
                GAN-generated faces sometimes show unusual hue gradients or incorrect skin tone distributions.
              </p>
            </Section>
          </>
        );
      })()}

      {/* ── Verdict summary ── */}
      <div
        className="rounded-xl p-5"
        style={{ background: `${accentGlow}`, border: `1px solid ${accentColor}30` }}
      >
        <div className="flex items-start gap-3">
          <TrendingUp className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: accentColor }} />
          <div>
            <p className="text-sm font-mono font-semibold text-gray-200 mb-1">
              {isReal ? 'No significant deepfake indicators found.' : 'Deepfake indicators detected.'}
            </p>
            <p className="text-xs font-mono text-gray-500 leading-relaxed">
              {isReal
                ? `Blink patterns, facial symmetry, texture entropy, and optical flow are all consistent with natural human video. Confidence: ${pct}%.`
                : `Abnormalities detected across one or more feature groups. Review highlighted metrics above. Confidence: ${pct}%. Consider secondary verification.`}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}