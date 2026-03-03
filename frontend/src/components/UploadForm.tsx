// 'use client';


// import React, { useCallback, useState } from 'react';
// import { useDropzone } from 'react-dropzone';
// import { motion } from 'framer-motion';
// import { Upload, FileVideo, AlertCircle, CheckCircle } from 'lucide-react';

// interface UploadFormProps {
//   onFileUpload: (file: File) => void;
// }

// const UploadForm: React.FC<UploadFormProps> = ({ onFileUpload }) => {
//   const [selectedFile, setSelectedFile] = useState<File | null>(null);
//   const [dragActive, setDragActive] = useState(false);

//   const onDrop = useCallback((acceptedFiles: File[]) => {
//     const file = acceptedFiles[0];
//     if (file) {
//       setSelectedFile(file);
//     }
//   }, []);

//   const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
//     onDrop,
//     accept: {
//       'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
//     },
//     multiple: false,
//     maxSize: 100 * 1024 * 1024, // 100MB
//     onDragEnter: () => setDragActive(true),
//     onDragLeave: () => setDragActive(false),
//   });

//   const handleUpload = () => {
//     if (selectedFile) {
//       onFileUpload(selectedFile);
//     }
//   };

//   const resetFile = () => {
//     setSelectedFile(null);
//   };

//   const formatFileSize = (bytes: number) => {
//     if (bytes === 0) return '0 Bytes';
//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
//   };

//   return (
//     <div className="w-full max-w-2xl mx-auto">
//       {!selectedFile ? (
//         <motion.div
//           {...getRootProps()}
//           className={`
//             relative p-12 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300
//             ${isDragActive || dragActive 
//               ? 'border-blue-400 bg-blue-500/10 upload-area-hover' 
//               : 'border-gray-600 hover:border-blue-400 hover:bg-blue-500/5'
//             }
//           `}
//           whileHover={{ scale: 1.02 }}
//           whileTap={{ scale: 0.98 }}
//         >
//           <input {...getInputProps()} />
          
//           {/* Scanning animation overlay when dragging */}
//           {(isDragActive || dragActive) && (
//             <div className="absolute inset-0 rounded-2xl overflow-hidden">
//               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent scanning-line"></div>
//             </div>
//           )}
          
//           <div className="text-center">
//             <motion.div
//               animate={{ 
//                 y: isDragActive ? -10 : 0,
//                 scale: isDragActive ? 1.1 : 1 
//               }}
//               transition={{ duration: 0.2 }}
//             >
//               <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
//             </motion.div>
            
//             <h3 className="text-xl font-semibold text-white mb-2">
//               {isDragActive ? 'Drop your video here' : 'Upload Video File'}
//             </h3>
            
//             <p className="text-gray-400 mb-4">
//               Drag and drop your video file here, or click to browse
//             </p>
            
//             <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
//               <span className="bg-gray-800 px-3 py-1 rounded-full">.MP4</span>
//               <span className="bg-gray-800 px-3 py-1 rounded-full">.AVI</span>
//               <span className="bg-gray-800 px-3 py-1 rounded-full">.MOV</span>
//               <span className="bg-gray-800 px-3 py-1 rounded-full">.MKV</span>
//             </div>
            
//             <p className="text-xs text-gray-500 mt-4">
//               Maximum file size: 100MB
//             </p>
//           </div>
//         </motion.div>
//       ) : (
//         <motion.div
//           initial={{ opacity: 0, scale: 0.9 }}
//           animate={{ opacity: 1, scale: 1 }}
//           className="glass-morphism p-6 rounded-2xl cyber-border"
//         >
//           <div className="flex items-start space-x-4">
//             <div className="flex-shrink-0">
//               <FileVideo className="w-12 h-12 text-blue-400" />
//             </div>
            
//             <div className="flex-grow">
//               <div className="flex items-center space-x-2 mb-2">
//                 <CheckCircle className="w-5 h-5 text-green-400" />
//                 <h3 className="text-lg font-semibold text-white">File Selected</h3>
//               </div>
              
//               <p className="text-gray-300 font-medium mb-1">{selectedFile.name}</p>
//               <p className="text-gray-400 text-sm mb-4">
//                 Size: {formatFileSize(selectedFile.size)} • Type: {selectedFile.type}
//               </p>
              
//               <div className="flex space-x-3">
//                 <motion.button
//                   onClick={handleUpload}
//                   className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 px-6 py-2 rounded-lg font-semibold transition-all duration-300"
//                   whileHover={{ scale: 1.05 }}
//                   whileTap={{ scale: 0.95 }}
//                 >
//                   Analyze Video
//                 </motion.button>
                
//                 <motion.button
//                   onClick={resetFile}
//                   className="bg-gray-700 hover:bg-gray-600 px-6 py-2 rounded-lg font-semibold transition-all duration-300"
//                   whileHover={{ scale: 1.05 }}
//                   whileTap={{ scale: 0.95 }}
//                 >
//                   Choose Different File
//                 </motion.button>
//               </div>
//             </div>
//           </div>
//         </motion.div>
//       )}
      
//       {/* File rejection errors */}
//       {fileRejections.length > 0 && (
//         <motion.div
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           className="mt-4 p-4 bg-red-900/50 border border-red-500 rounded-lg"
//         >
//           <div className="flex items-center space-x-2 mb-2">
//             <AlertCircle className="w-5 h-5 text-red-400" />
//             <h4 className="text-red-200 font-semibold">Upload Error</h4>
//           </div>
          
//           {fileRejections.map(({ file, errors }) => (
//             <div key={file.name} className="text-red-200 text-sm">
//               <p className="font-medium">{file.name}</p>
//               <ul className="list-disc list-inside ml-4 space-y-1">
//                 {errors.map((error) => (
//                   <li key={error.code}>
//                     {error.code === 'file-too-large' && 'File is too large (max 100MB)'}
//                     {error.code === 'file-invalid-type' && 'Invalid file type (only video files allowed)'}
//                     {error.code !== 'file-too-large' && error.code !== 'file-invalid-type' && error.message}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//           ))}
//         </motion.div>
//       )}
//     </div>
//   );
// };

// export default UploadForm;

//new update

'use client';
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileVideo, AlertCircle, CheckCircle, X } from 'lucide-react';

interface UploadFormProps {
  onFileUpload: (file: File) => void;
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const s = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${s[i]}`;
};

export default function UploadForm({ onFileUpload }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: { 'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'] },
    multiple: false,
    maxSize: 100 * 1024 * 1024,
  });

  return (
    <div className="w-full max-w-xl mx-auto">
      <AnimatePresence mode="wait">
        {!file ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            transition={{ duration: 0.25 }}
          >
            <div
              {...getRootProps()}
              className="relative cursor-pointer group"
            >
              <input {...getInputProps()} />

              {/* Outer border glow */}
              <motion.div
                className="absolute -inset-px rounded-2xl"
                style={{
                  background: isDragActive
                    ? 'linear-gradient(135deg, #00f5ff, #a855f7, #00f5ff)'
                    : 'linear-gradient(135deg, #1f2937, #374151, #1f2937)',
                  backgroundSize: '200% 200%',
                }}
                animate={isDragActive ? { backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'] } : {}}
                transition={{ duration: 2, repeat: Infinity }}
              />

              <div
                className="relative rounded-2xl p-10 text-center transition-all duration-300"
                style={{
                  background: isDragActive ? '#0a0a0f' : '#080810',
                  border: '1px solid transparent',
                }}
              >
                {/* Scan line on drag */}
                <AnimatePresence>
                  {isDragActive && (
                    <motion.div
                      className="absolute left-0 right-0 h-px pointer-events-none"
                      style={{
                        background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)',
                        boxShadow: '0 0 12px #00f5ff',
                      }}
                      initial={{ top: '0%' }}
                      animate={{ top: '100%' }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    />
                  )}
                </AnimatePresence>

                <motion.div
                  animate={isDragActive ? { y: -8, scale: 1.15 } : { y: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className="mb-5"
                >
                  <Upload
                    className="w-14 h-14 mx-auto"
                    style={{ color: isDragActive ? '#00f5ff' : '#4b5563' }}
                  />
                </motion.div>

                <h3 className="text-lg font-mono font-bold text-gray-200 mb-2 tracking-wide">
                  {isDragActive ? 'Drop to analyze' : 'Drop video file'}
                </h3>
                <p className="text-gray-600 text-sm font-mono mb-6">
                  or <span className="text-cyan-500 underline underline-offset-2">click to browse</span>
                </p>

                <div className="flex flex-wrap justify-center gap-2">
                  {['MP4', 'AVI', 'MOV', 'MKV', 'WMV'].map((ext) => (
                    <span
                      key={ext}
                      className="px-2.5 py-1 rounded-md text-xs font-mono border border-gray-800 text-gray-500"
                    >
                      .{ext}
                    </span>
                  ))}
                </div>

                <p className="text-gray-700 text-xs font-mono mt-4">Max 100 MB</p>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25 }}
            className="rounded-2xl border border-gray-800 bg-gray-900/50 p-5"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0">
                <FileVideo className="w-6 h-6 text-cyan-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <CheckCircle className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
                  <p className="text-gray-200 text-sm font-mono font-semibold truncate">{file.name}</p>
                </div>
                <p className="text-gray-600 text-xs font-mono">{formatFileSize(file.size)} · {file.type}</p>
              </div>
              <button onClick={() => setFile(null)} className="text-gray-700 hover:text-gray-400 transition-colors p-1">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex gap-3 mt-4">
              <motion.button
                onClick={() => onFileUpload(file)}
                className="flex-1 py-2.5 rounded-xl text-sm font-mono font-bold tracking-wider uppercase transition-all"
                style={{
                  background: 'linear-gradient(135deg, #00f5ff22, #a855f722)',
                  border: '1px solid #00f5ff50',
                  color: '#00f5ff',
                }}
                whileHover={{ scale: 1.02, boxShadow: '0 0 20px #00f5ff30' }}
                whileTap={{ scale: 0.98 }}
              >
                Analyze Video
              </motion.button>
              <motion.button
                onClick={() => setFile(null)}
                className="px-5 py-2.5 rounded-xl text-sm font-mono text-gray-500 border border-gray-800 hover:border-gray-700 hover:text-gray-300 transition-all"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Change
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rejection errors */}
      <AnimatePresence>
        {fileRejections.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 p-4 rounded-xl border border-red-900/50 bg-red-950/30"
          >
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <span className="text-red-300 text-xs font-mono font-semibold uppercase tracking-wider">Upload Error</span>
            </div>
            {fileRejections.map(({ file, errors }) => (
              <div key={file.name}>
                {errors.map((e) => (
                  <p key={e.code} className="text-red-500 text-xs font-mono">
                    {e.code === 'file-too-large' ? '— File exceeds 100MB limit'
                      : e.code === 'file-invalid-type' ? '— Only video files are accepted'
                      : `— ${e.message}`}
                  </p>
                ))}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}