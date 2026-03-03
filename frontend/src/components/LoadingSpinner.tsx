// import React from 'react';
// import { motion } from 'framer-motion';
// import { Eye, Brain, Cpu } from 'lucide-react';

// const LoadingSpinner: React.FC = () => {
//   return (
//     <div className="flex flex-col items-center justify-center">
//       {/* Main spinning animation */}
//       <div className="relative">
//         {/* Outer ring */}
//         <motion.div
//           className="w-32 h-32 border-4 border-transparent border-t-blue-400 border-r-purple-500 rounded-full"
//           animate={{ rotate: 360 }}
//           transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
//         />
        
//         {/* Middle ring */}
//         <motion.div
//           className="absolute inset-2 w-24 h-24 border-4 border-transparent border-b-cyan-400 border-l-pink-500 rounded-full"
//           animate={{ rotate: -360 }}
//           transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
//         />
        
//         {/* Inner ring */}
//         <motion.div
//           className="absolute inset-6 w-16 h-16 border-4 border-transparent border-t-green-400 border-r-yellow-500 rounded-full"
//           animate={{ rotate: 360 }}
//           transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
//         />
        
//         {/* Center icon */}
//         <div className="absolute inset-0 flex items-center justify-center">
//           <motion.div
//             animate={{ 
//               scale: [1, 1.2, 1],
//               opacity: [0.7, 1, 0.7]
//             }}
//             transition={{ duration: 2, repeat: Infinity }}
//           >
//             <Eye className="w-8 h-8 text-white" />
//           </motion.div>
//         </div>
//       </div>

//       {/* Progress indicators */}
//       <div className="mt-8 space-y-3">
//         <motion.div
//           className="flex items-center justify-center space-x-2"
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ delay: 0.5 }}
//         >
//           <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
//           <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
//           <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
//         </motion.div>
        
//         <motion.p
//           className="text-gray-300 text-center"
//           animate={{ opacity: [0.5, 1, 0.5] }}
//           transition={{ duration: 2, repeat: Infinity }}
//         >
//           Processing your video...
//         </motion.p>
//       </div>

//       {/* Animated progress steps */}
//       <div className="mt-6 space-y-2 w-full max-w-sm">
//         <motion.div
//           className="flex items-center space-x-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20"
//           initial={{ x: -50, opacity: 0 }}
//           animate={{ x: 0, opacity: 1 }}
//           transition={{ delay: 1 }}
//         >
//           <motion.div
//             animate={{ rotate: 360 }}
//             transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
//           >
//             <Eye className="w-5 h-5 text-blue-400" />
//           </motion.div>
//           <span className="text-blue-200 text-sm">Analyzing facial features...</span>
//         </motion.div>

//         <motion.div
//           className="flex items-center space-x-3 p-3 rounded-lg bg-purple-500/10 border border-purple-500/20"
//           initial={{ x: -50, opacity: 0 }}
//           animate={{ x: 0, opacity: 1 }}
//           transition={{ delay: 2 }}
//         >
//           <motion.div
//             animate={{ 
//               scale: [1, 1.2, 1],
//               opacity: [0.5, 1, 0.5]
//             }}
//             transition={{ duration: 1.5, repeat: Infinity }}
//           >
//             <Brain className="w-5 h-5 text-purple-400" />
//           </motion.div>
//           <span className="text-purple-200 text-sm">Processing blink patterns...</span>
//         </motion.div>

//         <motion.div
//           className="flex items-center space-x-3 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20"
//           initial={{ x: -50, opacity: 0 }}
//           animate={{ x: 0, opacity: 1 }}
//           transition={{ delay: 3 }}
//         >
//           <motion.div
//             animate={{ 
//               rotate: [0, 180, 360],
//               scale: [1, 0.8, 1]
//             }}
//             transition={{ duration: 2, repeat: Infinity }}
//           >
//             <Cpu className="w-5 h-5 text-cyan-400" />
//           </motion.div>
//           <span className="text-cyan-200 text-sm">Computing prediction...</span>
//         </motion.div>
//       </div>

//       {/* Scanning line effect */}
//       <div className="relative w-full max-w-md h-1 bg-gray-800 rounded-full mt-8 overflow-hidden">
//         <motion.div
//           className="absolute top-0 left-0 h-full w-20 bg-gradient-to-r from-transparent via-blue-400 to-transparent"
//           animate={{ x: ['0%', '400%'] }}
//           transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
//         />
//       </div>
//     </div>
//   );
// };

// export default LoadingSpinner;

//new update

'use client';
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const SCAN_STEPS = [
  { label: 'Initializing face detection', sublabel: 'Locating facial geometry...', color: '#00f5ff', duration: 1800 },
  { label: 'Mapping 468 landmarks', sublabel: 'Building spatial mesh...', color: '#a855f7', duration: 2000 },
  { label: 'Analyzing eye dynamics', sublabel: 'Computing EAR sequences...', color: '#00f5ff', duration: 2200 },
  { label: 'Extracting texture features', sublabel: 'LBP entropy & noise analysis...', color: '#f59e0b', duration: 1900 },
  { label: 'Head pose estimation', sublabel: 'Yaw / pitch / roll via solvePnP...', color: '#a855f7', duration: 2000 },
  { label: 'Optical flow analysis', sublabel: 'Frame-to-frame motion vectors...', color: '#00f5ff', duration: 2100 },
  { label: 'Running classifier', sublabel: 'Gradient boosting inference...', color: '#10b981', duration: 1500 },
];

const FaceMesh = () => (
  <svg viewBox="0 0 200 220" className="w-full h-full" fill="none">
    {/* Face outline */}
    <ellipse cx="100" cy="105" rx="72" ry="88" stroke="#00f5ff" strokeWidth="0.8" strokeDasharray="4 3" opacity="0.5" />
    {/* Forehead line */}
    <path d="M 55 55 Q 100 38 145 55" stroke="#00f5ff" strokeWidth="0.6" opacity="0.4" />
    {/* Cheekbones */}
    <path d="M 30 110 Q 55 118 80 115" stroke="#a855f7" strokeWidth="0.6" opacity="0.4" />
    <path d="M 170 110 Q 145 118 120 115" stroke="#a855f7" strokeWidth="0.6" opacity="0.4" />
    {/* Nose bridge */}
    <path d="M 95 72 L 93 108 Q 100 115 107 108 L 105 72" stroke="#00f5ff" strokeWidth="0.6" opacity="0.5" />
    {/* Nose tip */}
    <path d="M 85 112 Q 100 118 115 112" stroke="#00f5ff" strokeWidth="0.8" opacity="0.5" />
    {/* LEFT EYE */}
    <ellipse cx="72" cy="90" rx="20" ry="9" stroke="#00f5ff" strokeWidth="1" opacity="0.7" />
    <circle cx="72" cy="90" r="5" stroke="#00f5ff" strokeWidth="0.8" opacity="0.9" />
    <circle cx="72" cy="90" r="2" fill="#00f5ff" opacity="0.6" />
    {/* Left eye corner dots */}
    <circle cx="52" cy="90" r="1.5" fill="#00f5ff" opacity="0.8" />
    <circle cx="92" cy="90" r="1.5" fill="#00f5ff" opacity="0.8" />
    <circle cx="64" cy="83" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="80" cy="83" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="64" cy="97" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="80" cy="97" r="1.2" fill="#a855f7" opacity="0.7" />
    {/* RIGHT EYE */}
    <ellipse cx="128" cy="90" rx="20" ry="9" stroke="#00f5ff" strokeWidth="1" opacity="0.7" />
    <circle cx="128" cy="90" r="5" stroke="#00f5ff" strokeWidth="0.8" opacity="0.9" />
    <circle cx="128" cy="90" r="2" fill="#00f5ff" opacity="0.6" />
    {/* Right eye corner dots */}
    <circle cx="108" cy="90" r="1.5" fill="#00f5ff" opacity="0.8" />
    <circle cx="148" cy="90" r="1.5" fill="#00f5ff" opacity="0.8" />
    <circle cx="120" cy="83" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="136" cy="83" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="120" cy="97" r="1.2" fill="#a855f7" opacity="0.7" />
    <circle cx="136" cy="97" r="1.2" fill="#a855f7" opacity="0.7" />
    {/* Mouth */}
    <path d="M 75 148 Q 100 162 125 148" stroke="#00f5ff" strokeWidth="1" opacity="0.6" />
    <path d="M 80 148 Q 100 140 120 148" stroke="#00f5ff" strokeWidth="0.6" opacity="0.4" />
    {/* Mouth corners */}
    <circle cx="75" cy="148" r="1.5" fill="#f59e0b" opacity="0.8" />
    <circle cx="125" cy="148" r="1.5" fill="#f59e0b" opacity="0.8" />
    {/* Jaw points */}
    <circle cx="35" cy="130" r="1.5" fill="#a855f7" opacity="0.5" />
    <circle cx="165" cy="130" r="1.5" fill="#a855f7" opacity="0.5" />
    <circle cx="100" cy="190" r="1.5" fill="#00f5ff" opacity="0.5" />
    {/* Grid overlay triangles */}
    <line x1="72" y1="90" x2="128" y2="90" stroke="#00f5ff" strokeWidth="0.3" opacity="0.25" strokeDasharray="2 4" />
    <line x1="100" y1="72" x2="100" y2="148" stroke="#a855f7" strokeWidth="0.3" opacity="0.2" strokeDasharray="2 4" />
    <line x1="52" y1="90" x2="100" y2="72" stroke="#00f5ff" strokeWidth="0.25" opacity="0.2" />
    <line x1="148" y1="90" x2="100" y2="72" stroke="#00f5ff" strokeWidth="0.25" opacity="0.2" />
    <line x1="52" y1="90" x2="75" y2="148" stroke="#a855f7" strokeWidth="0.25" opacity="0.2" />
    <line x1="148" y1="90" x2="125" y2="148" stroke="#a855f7" strokeWidth="0.25" opacity="0.2" />
    <line x1="75" y1="148" x2="100" y2="190" stroke="#00f5ff" strokeWidth="0.25" opacity="0.2" />
    <line x1="125" y1="148" x2="100" y2="190" stroke="#00f5ff" strokeWidth="0.25" opacity="0.2" />
    {/* Eyebrow lines */}
    <path d="M 52 78 Q 72 70 92 76" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
    <path d="M 108 76 Q 128 70 148 78" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
  </svg>
);

export default function LoadingSpinner() {
  const [stepIndex, setStepIndex] = useState(0);
  const [scanY, setScanY] = useState(0);
  const [blinkOpen, setBlinkOpen] = useState(true);

  useEffect(() => {
    let totalTime = 0;
    const timers: ReturnType<typeof setTimeout>[] = [];
    SCAN_STEPS.forEach((step, i) => {
      const t = setTimeout(() => setStepIndex(i), totalTime);
      timers.push(t);
      totalTime += step.duration;
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  // Scan line animation
  useEffect(() => {
    let frame: number;
    let y = 0;
    let dir = 1;
    const animate = () => {
      y += dir * 1.2;
      if (y > 100) dir = -1;
      if (y < 0) dir = 1;
      setScanY(y);
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, []);

  // Blink simulation
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      setBlinkOpen(false);
      setTimeout(() => setBlinkOpen(true), 160);
    }, 3200);
    return () => clearInterval(blinkInterval);
  }, []);

  const currentStep = SCAN_STEPS[Math.min(stepIndex, SCAN_STEPS.length - 1)];
  const progress = ((stepIndex + 1) / SCAN_STEPS.length) * 100;

  return (
    <div className="flex flex-col items-center justify-center py-6 select-none">
      {/* Face scan container */}
      <div className="relative w-56 h-64 mb-8">
        {/* Corner brackets */}
        {[
          'top-0 left-0 border-t-2 border-l-2 rounded-tl-lg',
          'top-0 right-0 border-t-2 border-r-2 rounded-tr-lg',
          'bottom-0 left-0 border-b-2 border-l-2 rounded-bl-lg',
          'bottom-0 right-0 border-b-2 border-r-2 rounded-br-lg',
        ].map((cls, i) => (
          <motion.div
            key={i}
            className={`absolute w-7 h-7 ${cls}`}
            style={{ borderColor: currentStep.color }}
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}

        {/* Face mesh */}
        <motion.div
          className="absolute inset-4"
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2.5, repeat: Infinity }}
        >
          <FaceMesh />
        </motion.div>

        {/* Blink overlay on eyes */}
        <AnimatePresence>
          {!blinkOpen && (
            <motion.div
              className="absolute"
              style={{ top: '37%', left: '18%', width: '28%', height: '6%', background: '#000', borderRadius: 4 }}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              exit={{ scaleY: 0 }}
              transition={{ duration: 0.08 }}
            />
          )}
        </AnimatePresence>
        <AnimatePresence>
          {!blinkOpen && (
            <motion.div
              className="absolute"
              style={{ top: '37%', right: '18%', width: '28%', height: '6%', background: '#000', borderRadius: 4 }}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              exit={{ scaleY: 0 }}
              transition={{ duration: 0.08 }}
            />
          )}
        </AnimatePresence>

        {/* Horizontal scan line */}
        <div
          className="absolute left-2 right-2 pointer-events-none"
          style={{
            top: `${scanY}%`,
            height: '2px',
            background: `linear-gradient(90deg, transparent, ${currentStep.color}cc, ${currentStep.color}, ${currentStep.color}cc, transparent)`,
            boxShadow: `0 0 12px 3px ${currentStep.color}66`,
            transition: 'background 0.4s, box-shadow 0.4s',
          }}
        />

        {/* Dot markers that pulse on detected points */}
        {[[36, 38], [62, 38], [36, 62], [62, 62], [50, 82], [50, 30]].map(([x, y], i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 rounded-full"
            style={{
              left: `${x}%`,
              top: `${y}%`,
              background: currentStep.color,
              boxShadow: `0 0 6px ${currentStep.color}`,
            }}
            animate={{ scale: [1, 1.8, 1], opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.18 }}
          />
        ))}
      </div>

      {/* Step label */}
      <AnimatePresence mode="wait">
        <motion.div
          key={stepIndex}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
          className="text-center mb-6"
        >
          <p className="font-mono text-sm font-semibold tracking-widest uppercase mb-1"
            style={{ color: currentStep.color }}>
            {currentStep.label}
          </p>
          <p className="text-gray-500 text-xs font-mono">{currentStep.sublabel}</p>
        </motion.div>
      </AnimatePresence>

      {/* Progress bar */}
      <div className="w-64 h-0.5 bg-gray-800 rounded-full overflow-hidden mb-2">
        <motion.div
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, #00f5ff, ${currentStep.color})` }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>

      {/* Step dots */}
      <div className="flex gap-2 mt-2">
        {SCAN_STEPS.map((step, i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full"
            style={{
              background: i <= stepIndex ? step.color : '#374151',
              boxShadow: i === stepIndex ? `0 0 8px ${step.color}` : 'none',
            }}
            animate={i === stepIndex ? { scale: [1, 1.5, 1] } : {}}
            transition={{ duration: 0.8, repeat: Infinity }}
          />
        ))}
      </div>
    </div>
  );
}