# #!/usr/bin/env python3
# """
# facial_dynamics_analyzer.py  —  Per-frame Facial Dynamics Feature Extraction
# ─────────────────────────────────────────────────────────────────────────────
# Features extracted per frame:
#   - Sharpness / edge / high-frequency artifact detection
#   - Skin texture  (LBP entropy, noise level, multi-scale energy)
#   - Facial symmetry
#   - Head pose     (yaw, pitch, roll via solvePnP)
#   - Mouth / lip dynamics (MAR, corner asymmetry)
#   - Frame-to-frame landmark motion
#   - Dense optical flow
#   - Color / skin-tone consistency

# Temporal features (across all frames):
#   - Pose jitter (yaw / pitch / roll std-dev)
#   - EAR jitter, symmetry jitter, flow jitter
# """

# import cv2
# import numpy as np
# from typing import Dict, List, Optional, Tuple


# # ─────────────────────────────────────────────────────────────────────────────
# # 3-D model points for solvePnP head-pose estimation
# # ─────────────────────────────────────────────────────────────────────────────
# _MODEL_POINTS_3D = np.array([
#     (0.0,    0.0,    0.0),      # Nose tip
#     (0.0,   -330.0, -65.0),     # Chin
#     (-225.0,  170.0, -135.0),   # Left eye outer corner
#     ( 225.0,  170.0, -135.0),   # Right eye outer corner
#     (-150.0, -150.0, -125.0),   # Left mouth corner
#     ( 150.0, -150.0, -125.0),   # Right mouth corner
# ], dtype=np.float64)

# # MediaPipe 468-landmark indices for the 6 pose points above
# _POSE_LM_IDX = [4, 152, 33, 263, 61, 291]

# # MediaPipe mouth landmark indices (subset for MAR calculation)
# _MOUTH_VERTICAL_IDX  = [(13, 14), (312, 317), (82, 87)]  # (upper, lower) pairs
# _MOUTH_HORIZONTAL_IDX = (78, 308)                          # (left, right)
# _MOUTH_CORNER_LEFT   = 61
# _MOUTH_CORNER_RIGHT  = 291


# class FacialDynamicsAnalyzer:
#     """
#     Extracts per-frame facial-dynamics features and temporal consistency metrics.
#     Designed to work alongside the eye-blink pipeline in FeatureExtractor.
#     """

#     # ------------------------------------------------------------------
#     # Feature name catalogue (used for zero-filling in _get_default_features)
#     # ------------------------------------------------------------------
#     _BASE_FEATURE_NAMES = [
#         # Edge / sharpness
#         "sharpness_score", "high_freq_energy", "edge_density_high", "freq_ratio",
#         # Color / skin
#         "hue_consistency", "color_smoothness", "skin_ratio",
#         # Texture
#         "lbp_entropy", "noise_level", "texture_energy",
#         # Symmetry
#         "avg_symmetry_score", "std_symmetry_score",
#         # Head pose
#         "yaw", "pitch", "roll",
#         # Mouth
#         "mouth_aspect_ratio", "mouth_corner_asymmetry",
#         # Motion (landmark)
#         "global_motion_mean", "eye_motion_asymmetry",
#         # Optical flow
#         "flow_mean", "flow_std", "boundary_flow_ratio", "flow_direction_entropy",
#     ]

#     # ------------------------------------------------------------------
#     # Public: list of base feature names
#     # ------------------------------------------------------------------
#     def get_all_feature_names(self) -> List[str]:
#         return list(self._BASE_FEATURE_NAMES)

#     # ------------------------------------------------------------------
#     # Public: per-frame analysis
#     # ------------------------------------------------------------------
#     def analyze_frame(
#         self,
#         frame: np.ndarray,
#         face_bbox: Tuple[int, int, int, int],
#         prev_frame: Optional[np.ndarray] = None,
#         prev_landmarks: Optional[np.ndarray] = None,
#         landmarks: Optional[np.ndarray] = None,
#     ) -> Dict:
#         """
#         Extract all facial dynamics features for a single frame.

#         Args:
#             frame         : Full BGR video frame.
#             face_bbox     : (x, y, w, h) of the detected face.
#             prev_frame    : Previous full BGR frame (for optical flow / motion).
#             prev_landmarks: Previous landmark array (for landmark motion).
#             landmarks     : 468-point MediaPipe landmark array (optional).

#         Returns:
#             Dict of scalar feature values, or empty dict on failure.
#         """
#         try:
#             x, y, w, h = face_bbox
#             if w <= 0 or h <= 0:
#                 return {}
#             face_roi = frame[y: y + h, x: x + w]
#             if face_roi.size == 0:
#                 return {}

#             features: Dict = {}

#             # ── 1. Edge / sharpness / artifact features ───────────────
#             features.update(self._edge_artifact_features(face_roi))

#             # ── 2. Color / skin features ──────────────────────────────
#             features.update(self._color_skin_features(face_roi))

#             # ── 3. Texture features ───────────────────────────────────
#             features.update(self._texture_features(face_roi))

#             # ── 4. Facial symmetry ────────────────────────────────────
#             features.update(self._symmetry_features(face_roi))

#             # ── 5. Head pose (needs landmarks) ────────────────────────
#             if landmarks is not None:
#                 features.update(self._head_pose_features(landmarks, frame.shape))
#                 # ── 6. Mouth dynamics ──────────────────────────────────
#                 features.update(self._mouth_features(landmarks))
#                 # ── 7. Landmark motion ─────────────────────────────────
#                 if prev_landmarks is not None:
#                     features.update(self._landmark_motion_features(landmarks, prev_landmarks))
#             else:
#                 # Provide neutral defaults so the feature vector stays consistent
#                 features.update({k: 0.0 for k in [
#                     "yaw", "pitch", "roll",
#                     "mouth_aspect_ratio", "mouth_corner_asymmetry",
#                     "global_motion_mean", "eye_motion_asymmetry",
#                 ]})

#             # ── 8. Optical flow ───────────────────────────────────────
#             if prev_frame is not None:
#                 features.update(self._optical_flow_features(frame, prev_frame, face_bbox))
#             else:
#                 features.update({k: 0.0 for k in [
#                     "flow_mean", "flow_std",
#                     "boundary_flow_ratio", "flow_direction_entropy",
#                 ]})

#             # Replace any NaN / Inf with 0
#             return {k: float(v) if np.isfinite(float(v)) else 0.0
#                     for k, v in features.items()}

#         except Exception:
#             return {}

#     # ------------------------------------------------------------------
#     # Public: temporal consistency across all per-frame dicts
#     # ------------------------------------------------------------------
#     def compute_temporal_features(self, per_frame_dynamics: List[Dict]) -> Dict:
#         """
#         Compute temporal consistency / jitter metrics from the list of
#         per-frame feature dicts.

#         Returns a flat dict (keys will be prefixed with "temporal_" by caller).
#         """
#         if not per_frame_dynamics:
#             return {}

#         temporal: Dict = {}
#         jitter_keys = [
#             "yaw", "pitch", "roll",
#             "avg_symmetry_score",
#             "sharpness_score",
#             "flow_mean",
#             "mouth_aspect_ratio",
#             "lbp_entropy",
#             "hue_consistency",
#         ]

#         for key in jitter_keys:
#             vals = [f[key] for f in per_frame_dynamics
#                     if key in f and np.isfinite(f.get(key, float("nan")))]
#             if len(vals) < 2:
#                 temporal[f"{key}_jitter"] = 0.0
#                 temporal[f"{key}_trend"]  = 0.0
#                 continue
#             arr = np.array(vals, dtype=float)
#             # Jitter = standard deviation of frame-to-frame differences
#             temporal[f"{key}_jitter"] = float(np.std(np.diff(arr)))
#             # Trend = slope of linear fit (positive = increasing over time)
#             if len(arr) >= 3:
#                 slope = np.polyfit(np.arange(len(arr)), arr, 1)[0]
#                 temporal[f"{key}_trend"] = float(slope)
#             else:
#                 temporal[f"{key}_trend"] = 0.0

#         # Overall flow consistency
#         flow_vals = [f.get("flow_mean", 0.0) for f in per_frame_dynamics
#                      if np.isfinite(f.get("flow_mean", float("nan")))]
#         if flow_vals:
#             temporal["flow_consistency"] = float(1.0 / (1.0 + np.std(flow_vals)))
#         else:
#             temporal["flow_consistency"] = 0.0

#         # Symmetry consistency
#         sym_vals = [f.get("avg_symmetry_score", 0.0) for f in per_frame_dynamics
#                     if np.isfinite(f.get("avg_symmetry_score", float("nan")))]
#         if sym_vals:
#             temporal["symmetry_consistency"] = float(1.0 / (1.0 + np.std(sym_vals)))
#         else:
#             temporal["symmetry_consistency"] = 0.0

#         return temporal

#     # ==================================================================
#     # PRIVATE FEATURE EXTRACTORS
#     # ==================================================================

#     # ------------------------------------------------------------------
#     # 1. Edge / sharpness / high-frequency artifacts
#     # ------------------------------------------------------------------
#     def _edge_artifact_features(self, face_roi: np.ndarray) -> Dict:
#         gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

#         # Laplacian sharpness
#         lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

#         # High-frequency energy via DFT
#         dft = np.fft.fft2(gray.astype(np.float32))
#         dft_shift = np.fft.fftshift(dft)
#         magnitude = np.abs(dft_shift)
#         h, w = gray.shape
#         cy, cx = h // 2, w // 2
#         r_low  = min(cy, cx) // 4
#         r_high = min(cy, cx) // 2

#         y_idx, x_idx = np.ogrid[:h, :w]
#         dist = np.sqrt((y_idx - cy) ** 2 + (x_idx - cx) ** 2)
#         low_mask  = dist <= r_low
#         high_mask = (dist > r_low) & (dist <= r_high)
#         total_mask = dist <= r_high

#         low_energy   = float(magnitude[low_mask].sum())
#         high_energy  = float(magnitude[high_mask].sum())
#         total_energy = float(magnitude[total_mask].sum()) + 1e-8

#         # Canny edge density
#         edges = cv2.Canny(gray, 50, 150)
#         edge_density = float(edges.mean())

#         freq_ratio = high_energy / (low_energy + 1e-8)

#         return {
#             "sharpness_score":    lap_var,
#             "high_freq_energy":   high_energy / total_energy,
#             "edge_density_high":  edge_density,
#             "freq_ratio":         freq_ratio,
#         }

#     # ------------------------------------------------------------------
#     # 2. Color / skin-tone consistency
#     # ------------------------------------------------------------------
#     def _color_skin_features(self, face_roi: np.ndarray) -> Dict:
#         hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
#         h_ch = hsv[:, :, 0].astype(np.float32)
#         s_ch = hsv[:, :, 1].astype(np.float32)

#         # Hue consistency: low std → consistent skin tone
#         hue_std = float(h_ch.std()) + 1e-8
#         hue_consistency = 1.0 / hue_std

#         # Color smoothness: mean gradient magnitude in BGR
#         gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
#         gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
#         gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
#         grad_mag = np.sqrt(gx ** 2 + gy ** 2)
#         color_smoothness = 1.0 / (float(grad_mag.mean()) + 1e-8)

#         # Skin-pixel ratio (YCrCb skin model)
#         ycrcb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2YCrCb)
#         cr = ycrcb[:, :, 1]
#         cb = ycrcb[:, :, 2]
#         skin_mask = (cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)
#         skin_ratio = float(skin_mask.mean())

#         return {
#             "hue_consistency":   hue_consistency,
#             "color_smoothness":  color_smoothness,
#             "skin_ratio":        skin_ratio,
#         }

#     # ------------------------------------------------------------------
#     # 3. Texture (LBP entropy, noise, multi-scale energy)
#     # ------------------------------------------------------------------
#     def _texture_features(self, face_roi: np.ndarray) -> Dict:
#         gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY).astype(np.float32)

#         # Simple LBP (uniform, radius=1, 8 neighbours)
#         lbp = self._compute_lbp(gray.astype(np.uint8))
#         hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
#         hist = hist.astype(np.float32) + 1e-8
#         hist /= hist.sum()
#         lbp_entropy = float(-np.sum(hist * np.log2(hist + 1e-12)))

#         # Noise level: std of high-pass residual
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#         residual = gray - blurred
#         noise_level = float(residual.std())

#         # Multi-scale texture energy (Gaussian pyramid level 2)
#         pyr = cv2.pyrDown(cv2.pyrDown(gray))
#         texture_energy = float(pyr.std())

#         return {
#             "lbp_entropy":    lbp_entropy,
#             "noise_level":    noise_level,
#             "texture_energy": texture_energy,
#         }

#     @staticmethod
#     def _compute_lbp(gray: np.ndarray) -> np.ndarray:
#         """Basic LBP implementation (no sklearn dependency)."""
#         h, w = gray.shape
#         lbp = np.zeros((h, w), dtype=np.uint8)
#         neighbors = [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]
#         center = gray[1:-1, 1:-1]
#         for bit, (dy, dx) in enumerate(neighbors):
#             nb = gray[1+dy: h-1+dy, 1+dx: w-1+dx] if (dy != 0 or dx != 0) else center
#             # Handle edge slicing for negative offsets
#             ny0 = max(0, 1 + dy)
#             ny1 = h - 1 + dy if dy <= 0 else h - 1 + dy
#             nx0 = max(0, 1 + dx)
#             nx1 = w - 1 + dx if dx <= 0 else w - 1 + dx
#             nb = gray[ny0:ny1 or None, nx0:nx1 or None]
#             try:
#                 lbp[1:-1, 1:-1] |= ((nb >= center).astype(np.uint8) << bit)
#             except ValueError:
#                 pass  # shape mismatch on edge — skip
#         return lbp

#     # ------------------------------------------------------------------
#     # 4. Facial symmetry
#     # ------------------------------------------------------------------
#     def _symmetry_features(self, face_roi: np.ndarray) -> Dict:
#         gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
#         h, w = gray.shape
#         if w < 4:
#             return {"avg_symmetry_score": 0.0, "std_symmetry_score": 0.0}

#         # Mirror left half vs right half at multiple vertical slices
#         scores = []
#         for frac in [0.45, 0.50, 0.55]:
#             mid = int(w * frac)
#             left  = gray[:, :mid]
#             right = gray[:, mid:]
#             right_flip = np.fliplr(right)
#             min_w = min(left.shape[1], right_flip.shape[1])
#             if min_w < 2:
#                 continue
#             l_crop = left[:, -min_w:]
#             r_crop = right_flip[:, :min_w]
#             diff = np.abs(l_crop.astype(np.float32) - r_crop.astype(np.float32))
#             score = 1.0 / (1.0 + float(diff.mean()))
#             scores.append(score)

#         if not scores:
#             return {"avg_symmetry_score": 0.0, "std_symmetry_score": 0.0}

#         return {
#             "avg_symmetry_score": float(np.mean(scores)),
#             "std_symmetry_score": float(np.std(scores)),
#         }

#     # ------------------------------------------------------------------
#     # 5. Head pose (yaw, pitch, roll) via solvePnP
#     # ------------------------------------------------------------------
#     def _head_pose_features(
#         self,
#         landmarks: np.ndarray,
#         frame_shape: Tuple,
#     ) -> Dict:
#         h, w = frame_shape[:2]
#         focal = w  # approximate focal length
#         cam_matrix = np.array([
#             [focal, 0,     w / 2],
#             [0,     focal, h / 2],
#             [0,     0,     1   ],
#         ], dtype=np.float64)
#         dist_coeffs = np.zeros((4, 1), dtype=np.float64)

#         # Use whichever landmarks are available
#         n_lm = len(landmarks)
#         available = [i for i in _POSE_LM_IDX if i < n_lm]
#         if len(available) < 4:
#             return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

#         idx_map = {orig: pos for pos, orig in enumerate(_POSE_LM_IDX)}
#         pts_2d = np.array([landmarks[i][:2] for i in available], dtype=np.float64)
#         pts_3d = np.array([_MODEL_POINTS_3D[idx_map[i]] for i in available], dtype=np.float64)

#         try:
#             success, rvec, tvec = cv2.solvePnP(
#                 pts_3d, pts_2d, cam_matrix, dist_coeffs,
#                 flags=cv2.SOLVEPNP_ITERATIVE,
#             )
#             if not success:
#                 return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

#             rmat, _ = cv2.Rodrigues(rvec)
#             # Decompose rotation matrix to Euler angles
#             sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
#             singular = sy < 1e-6
#             if not singular:
#                 pitch = float(np.degrees(np.arctan2( rmat[2, 1], rmat[2, 2])))
#                 yaw   = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
#                 roll  = float(np.degrees(np.arctan2( rmat[1, 0], rmat[0, 0])))
#             else:
#                 pitch = float(np.degrees(np.arctan2(-rmat[1, 2], rmat[1, 1])))
#                 yaw   = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
#                 roll  = 0.0
#         except Exception:
#             return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

#         return {"yaw": yaw, "pitch": pitch, "roll": roll}

#     # ------------------------------------------------------------------
#     # 6. Mouth dynamics (MAR, corner asymmetry)
#     # ------------------------------------------------------------------
#     def _mouth_features(self, landmarks: np.ndarray) -> Dict:
#         n_lm = len(landmarks)
#         # Mouth Aspect Ratio (MAR)
#         # Use landmarks 61-291 (horizontal) and 13-14 (vertical) if available
#         if n_lm <= max(_MOUTH_CORNER_LEFT, _MOUTH_CORNER_RIGHT, 13, 14):
#             return {"mouth_aspect_ratio": 0.0, "mouth_corner_asymmetry": 0.0}

#         try:
#             left_corner  = landmarks[_MOUTH_CORNER_LEFT][:2].astype(float)
#             right_corner = landmarks[_MOUTH_CORNER_RIGHT][:2].astype(float)
#             upper_lip    = landmarks[13][:2].astype(float)
#             lower_lip    = landmarks[14][:2].astype(float)

#             mouth_width  = float(np.linalg.norm(right_corner - left_corner))
#             mouth_height = float(np.linalg.norm(lower_lip - upper_lip))
#             mar = mouth_height / (mouth_width + 1e-8)

#             # Corner height asymmetry
#             mid_y = (left_corner[1] + right_corner[1]) / 2.0
#             asym  = abs(left_corner[1] - mid_y) - abs(right_corner[1] - mid_y)
#             asym  = float(abs(asym)) / (mouth_width + 1e-8)
#         except Exception:
#             return {"mouth_aspect_ratio": 0.0, "mouth_corner_asymmetry": 0.0}

#         return {
#             "mouth_aspect_ratio":       mar,
#             "mouth_corner_asymmetry":   asym,
#         }

#     # ------------------------------------------------------------------
#     # 7. Landmark motion (frame-to-frame)
#     # ------------------------------------------------------------------
#     def _landmark_motion_features(
#         self,
#         landmarks: np.ndarray,
#         prev_landmarks: np.ndarray,
#     ) -> Dict:
#         try:
#             n = min(len(landmarks), len(prev_landmarks))
#             if n < 10:
#                 return {"global_motion_mean": 0.0, "eye_motion_asymmetry": 0.0}

#             cur  = landmarks[:n, :2].astype(float)
#             prev = prev_landmarks[:n, :2].astype(float)
#             motion = np.linalg.norm(cur - prev, axis=1)
#             global_motion = float(motion.mean())

#             # Eye-region motion asymmetry (left vs right)
#             # Left eye region: indices ~33-133, right: ~263-362
#             l_idx = [i for i in range(33, min(134, n))]
#             r_idx = [i for i in range(263, min(363, n))]
#             if l_idx and r_idx:
#                 l_motion = float(motion[l_idx].mean())
#                 r_motion = float(motion[r_idx].mean())
#                 eye_asym = abs(l_motion - r_motion)
#             else:
#                 eye_asym = 0.0
#         except Exception:
#             return {"global_motion_mean": 0.0, "eye_motion_asymmetry": 0.0}

#         return {
#             "global_motion_mean":    global_motion,
#             "eye_motion_asymmetry":  eye_asym,
#         }

#     # ------------------------------------------------------------------
#     # 8. Dense optical flow
#     # ------------------------------------------------------------------
#     def _optical_flow_features(
#         self,
#         frame: np.ndarray,
#         prev_frame: np.ndarray,
#         face_bbox: Tuple[int, int, int, int],
#     ) -> Dict:
#         default = {
#             "flow_mean": 0.0, "flow_std": 0.0,
#             "boundary_flow_ratio": 0.0, "flow_direction_entropy": 0.0,
#         }
#         try:
#             x, y, w, h = face_bbox
#             # Crop to face region for efficiency
#             cur_gray  = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
#             prev_gray = cv2.cvtColor(prev_frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)

#             if cur_gray.shape != prev_gray.shape or cur_gray.size == 0:
#                 return default

#             # Resize to max 128×128 for speed
#             scale = min(1.0, 128.0 / max(cur_gray.shape))
#             if scale < 1.0:
#                 new_w = max(4, int(cur_gray.shape[1] * scale))
#                 new_h = max(4, int(cur_gray.shape[0] * scale))
#                 cur_gray  = cv2.resize(cur_gray,  (new_w, new_h))
#                 prev_gray = cv2.resize(prev_gray, (new_w, new_h))

#             flow = cv2.calcOpticalFlowFarneback(
#                 prev_gray, cur_gray,
#                 None, 0.5, 3, 15, 3, 5, 1.2, 0,
#             )
#             mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

#             flow_mean = float(mag.mean())
#             flow_std  = float(mag.std())

#             # Boundary vs interior flow ratio
#             border_w = max(1, mag.shape[1] // 6)
#             border_h = max(1, mag.shape[0] // 6)
#             border_mask = np.zeros_like(mag, dtype=bool)
#             border_mask[:border_h, :] = True
#             border_mask[-border_h:, :] = True
#             border_mask[:, :border_w] = True
#             border_mask[:, -border_w:] = True
#             interior_mask = ~border_mask

#             border_flow   = float(mag[border_mask].mean())   if border_mask.any()   else 0.0
#             interior_flow = float(mag[interior_mask].mean()) if interior_mask.any() else 0.0
#             boundary_ratio = border_flow / (interior_flow + 1e-8)

#             # Direction entropy
#             ang_deg = np.degrees(ang).ravel()
#             hist, _ = np.histogram(ang_deg, bins=16, range=(0, 360))
#             hist = hist.astype(float) + 1e-8
#             hist /= hist.sum()
#             direction_entropy = float(-np.sum(hist * np.log2(hist + 1e-12)))

#         except Exception:
#             return default

#         return {
#             "flow_mean":              flow_mean,
#             "flow_std":               flow_std,
#             "boundary_flow_ratio":    boundary_ratio,
#             "flow_direction_entropy": direction_entropy,
#         }


#new update
#!/usr/bin/env python3
"""
Facial Dynamics Analyzer
Detects facial behavior patterns: micro-expressions, edge/color artifacts,
texture consistency, facial symmetry, skin tone variations, and motion dynamics.
These features complement eye blink analysis for deepfake detection.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.signal import find_peaks
import mediapipe as mp


class FacialDynamicsAnalyzer:
    def __init__(self):
        """Initialize facial dynamics analyzer with MediaPipe components"""
        # Face mesh for landmark-based analysis
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # MediaPipe face detection for quality checks
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

        # Key landmark groups for facial analysis
        # Lips
        self.LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
                           375, 321, 405, 314, 17, 84, 181, 91, 146]
        self.LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308,
                           324, 318, 402, 317, 14, 87, 178, 88, 95]

        # Eyebrows
        self.LEFT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
        self.RIGHT_EYEBROW = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]

        # Nose bridge & tip
        self.NOSE = [1, 2, 98, 327, 168, 6, 197, 195, 5, 4, 45, 220, 115, 48,
                     64, 98, 240, 99, 60, 20, 242, 141, 94]

        # Jawline
        self.JAWLINE = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
                        288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
                        150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

        # Face oval (boundary)
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                          397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                          172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10]

        # Cheek regions (for skin texture)
        self.LEFT_CHEEK = [116, 117, 118, 119, 100, 101, 102, 36, 205, 187, 123]
        self.RIGHT_CHEEK = [345, 346, 347, 348, 329, 330, 331, 266, 425, 411, 352]

        # For optical flow (motion tracking)
        self._prev_gray = None
        self._prev_landmarks = None
        self._optical_flow_params = dict(
            winSize=(15, 15),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )

    # ─────────────────────────────────────────────────────────────
    # 1. EDGE & COLOR ARTIFACT DETECTION
    # ─────────────────────────────────────────────────────────────

    def detect_edge_artifacts(self, face_roi: np.ndarray) -> Dict:
        """
        Detect unnatural edges and color bleeding artifacts common in deepfakes.
        GAN-generated faces often have inconsistent edge sharpness at boundaries.
        """
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        # Canny edge detection at multiple thresholds
        edges_low = cv2.Canny(gray, 30, 90)
        edges_high = cv2.Canny(gray, 100, 200)

        # Laplacian for blur/sharpness
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()

        # Sobel gradients for directional edge strength
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)

        # High-frequency noise (deepfakes often have checkerboard artifacts)
        dft = np.fft.fft2(gray.astype(np.float32))
        dft_shift = np.fft.fftshift(dft)
        magnitude_spectrum = 20 * np.log(np.abs(dft_shift) + 1e-8)

        h, w = gray.shape
        center_y, center_x = h // 2, w // 2
        radius = min(h, w) // 4

        # Energy in high-frequency region (corners of spectrum)
        mask_high = np.ones((h, w), dtype=bool)
        Y, X = np.ogrid[:h, :w]
        mask_low = (X - center_x)**2 + (Y - center_y)**2 <= radius**2
        mask_high[mask_low] = False

        high_freq_energy = magnitude_spectrum[mask_high].mean()
        low_freq_energy = magnitude_spectrum[mask_low].mean()
        freq_ratio = high_freq_energy / (low_freq_energy + 1e-8)

        # Color channel inconsistency (BGR)
        b, g, r = cv2.split(face_roi.astype(np.float32))
        channel_std = np.std([b.std(), g.std(), r.std()])

        # Local edge density variance (real faces have consistent edge patterns)
        edge_density_map = cv2.boxFilter(edges_high.astype(np.float32), -1, (15, 15))
        edge_density_variance = edge_density_map.var()

        return {
            "sharpness_score": float(sharpness),
            "edge_density_low": float(edges_low.sum() / edges_low.size),
            "edge_density_high": float(edges_high.sum() / edges_high.size),
            "gradient_mean": float(gradient_magnitude.mean()),
            "gradient_std": float(gradient_magnitude.std()),
            "high_freq_energy": float(high_freq_energy),
            "freq_ratio": float(freq_ratio),
            "color_channel_std": float(channel_std),
            "edge_density_variance": float(edge_density_variance),
        }

    def analyze_color_consistency(self, face_roi: np.ndarray,
                                   landmarks: np.ndarray, frame_shape: Tuple) -> Dict:
        """
        Analyze color consistency across facial regions.
        Deepfakes often have mismatched skin tones or lighting.
        """
        h, w = face_roi.shape[:2]
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2Lab)

        # Sample skin color from key face regions
        regions = {
            "forehead": face_roi[int(h * 0.05):int(h * 0.20), int(w * 0.3):int(w * 0.7)],
            "left_cheek": face_roi[int(h * 0.35):int(h * 0.60), int(w * 0.05):int(w * 0.30)],
            "right_cheek": face_roi[int(h * 0.35):int(h * 0.60), int(w * 0.70):int(w * 0.95)],
            "chin": face_roi[int(h * 0.75):int(h * 0.95), int(w * 0.3):int(w * 0.7)],
        }

        region_hues = []
        region_saturations = []
        region_values = []
        region_l_values = []

        for name, region in regions.items():
            if region.size == 0:
                continue
            region_hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            region_lab = cv2.cvtColor(region, cv2.COLOR_BGR2Lab)
            region_hues.append(region_hsv[:, :, 0].mean())
            region_saturations.append(region_hsv[:, :, 1].mean())
            region_values.append(region_hsv[:, :, 2].mean())
            region_l_values.append(region_lab[:, :, 0].mean())

        # Consistency metrics — real faces have lower variance across regions
        hue_consistency = float(np.std(region_hues)) if region_hues else 0.0
        saturation_consistency = float(np.std(region_saturations)) if region_saturations else 0.0
        brightness_consistency = float(np.std(region_values)) if region_values else 0.0
        luminance_consistency = float(np.std(region_l_values)) if region_l_values else 0.0

        # Skin tone naturalness (human skin sits in a specific HSV range)
        skin_mask = (
            (hsv[:, :, 0] >= 0) & (hsv[:, :, 0] <= 50) &
            (hsv[:, :, 1] >= 30) & (hsv[:, :, 1] <= 200) &
            (hsv[:, :, 2] >= 80)
        )
        skin_ratio = float(skin_mask.sum() / (h * w))

        # Local color variance (GAN artifacts show sudden color jumps)
        local_var_b = cv2.boxFilter(face_roi[:, :, 0].astype(np.float32), -1, (9, 9))
        local_var_map = np.abs(face_roi[:, :, 0].astype(np.float32) - local_var_b)
        color_smoothness = float(local_var_map.mean())

        return {
            "hue_consistency": hue_consistency,
            "saturation_consistency": saturation_consistency,
            "brightness_consistency": brightness_consistency,
            "luminance_consistency": luminance_consistency,
            "skin_ratio": skin_ratio,
            "color_smoothness": color_smoothness,
        }

    # ─────────────────────────────────────────────────────────────
    # 2. FACIAL SYMMETRY ANALYSIS
    # ─────────────────────────────────────────────────────────────

    def analyze_facial_symmetry(self, landmarks: np.ndarray, frame_shape: Tuple) -> Dict:
        """
        Analyze left-right facial symmetry.
        Human faces have natural asymmetry, but deepfakes often show
        either too much or too little symmetry.
        """
        if landmarks is None or len(landmarks) < 468:
            return self._default_symmetry_features()

        # Paired landmark indices (left, right) for key facial points
        landmark_pairs = [
            (33, 263),    # Eye corners (outer)
            (133, 362),   # Eye corners (inner)
            (70, 300),    # Eyebrow ends
            (105, 334),   # Eyebrow peaks
            (61, 291),    # Mouth corners
            (40, 270),    # Upper lip sides
            (91, 321),    # Lower lip sides
            (116, 345),   # Cheek points
            (234, 454),   # Jaw corners
            (172, 397),   # Chin sides
        ]

        symmetry_scores = []
        vertical_distances = []

        # Nose tip as approximate center (landmark 1)
        nose_tip = landmarks[1]
        face_center_x = nose_tip[0]

        for left_idx, right_idx in landmark_pairs:
            if left_idx >= len(landmarks) or right_idx >= len(landmarks):
                continue
            left_pt = landmarks[left_idx]
            right_pt = landmarks[right_idx]

            # Distance from center line
            left_dist = abs(left_pt[0] - face_center_x)
            right_dist = abs(right_pt[0] - face_center_x)

            # Symmetry score: 1.0 = perfect symmetry
            if left_dist + right_dist > 0:
                sym = 1.0 - abs(left_dist - right_dist) / (left_dist + right_dist)
                symmetry_scores.append(sym)

            # Vertical alignment (y-coordinate match)
            vertical_diff = abs(left_pt[1] - right_pt[1])
            vertical_distances.append(vertical_diff)

        avg_symmetry = float(np.mean(symmetry_scores)) if symmetry_scores else 0.5
        std_symmetry = float(np.std(symmetry_scores)) if symmetry_scores else 0.0
        avg_vertical_diff = float(np.mean(vertical_distances)) if vertical_distances else 0.0

        # Texture symmetry via image mirroring
        return {
            "avg_symmetry_score": avg_symmetry,
            "std_symmetry_score": std_symmetry,
            "avg_vertical_alignment": avg_vertical_diff,
            "min_symmetry": float(min(symmetry_scores)) if symmetry_scores else 0.0,
            "max_symmetry": float(max(symmetry_scores)) if symmetry_scores else 0.0,
        }

    # ─────────────────────────────────────────────────────────────
    # 3. FACIAL MOTION & MICRO-EXPRESSION DYNAMICS
    # ─────────────────────────────────────────────────────────────

    def analyze_facial_motion(self, current_landmarks: np.ndarray,
                               prev_landmarks: np.ndarray) -> Dict:
        """
        Analyze frame-to-frame facial landmark motion.
        Deepfakes often have unnatural motion — either too smooth or jittery.
        """
        if current_landmarks is None or prev_landmarks is None:
            return self._default_motion_features()

        if len(current_landmarks) != len(prev_landmarks):
            return self._default_motion_features()

        # Per-landmark displacement
        displacements = np.linalg.norm(
            current_landmarks.astype(float) - prev_landmarks.astype(float), axis=1
        )

        # Regional motion analysis
        regions = {
            "left_eye": self._region_motion(displacements, [33, 7, 163, 144, 145, 153, 154, 155, 133]),
            "right_eye": self._region_motion(displacements, [362, 382, 381, 380, 374, 373, 390, 249, 263]),
            "mouth": self._region_motion(displacements, [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]),
            "left_eyebrow": self._region_motion(displacements, self.LEFT_EYEBROW),
            "right_eyebrow": self._region_motion(displacements, self.RIGHT_EYEBROW),
            "nose": self._region_motion(displacements, self.NOSE[:10]),
            "jawline": self._region_motion(displacements, self.JAWLINE[:10]),
        }

        # Asymmetry in eye motion (real faces blink together; deepfakes may not)
        eye_motion_diff = abs(regions["left_eye"] - regions["right_eye"])
        eyebrow_motion_diff = abs(regions["left_eyebrow"] - regions["right_eyebrow"])

        return {
            "global_motion_mean": float(displacements.mean()),
            "global_motion_std": float(displacements.std()),
            "global_motion_max": float(displacements.max()),
            "eye_motion_asymmetry": float(eye_motion_diff),
            "eyebrow_motion_asymmetry": float(eyebrow_motion_diff),
            "mouth_motion": float(regions["mouth"]),
            "jaw_motion": float(regions["jawline"]),
            "nose_motion": float(regions["nose"]),
            "left_eye_motion": float(regions["left_eye"]),
            "right_eye_motion": float(regions["right_eye"]),
        }

    def _region_motion(self, displacements: np.ndarray, indices: List[int]) -> float:
        valid = [displacements[i] for i in indices if i < len(displacements)]
        return float(np.mean(valid)) if valid else 0.0

    # ─────────────────────────────────────────────────────────────
    # 4. SKIN TEXTURE ANALYSIS
    # ─────────────────────────────────────────────────────────────

    def analyze_skin_texture(self, face_roi: np.ndarray) -> Dict:
        """
        Analyze skin texture using LBP-style patterns and GLCM statistics.
        GANs often produce overly smooth or patterned skin textures.
        """
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Crop to central face area (avoid hair/background)
        face_center = gray[int(h * 0.1):int(h * 0.9), int(w * 0.15):int(w * 0.85)]

        if face_center.size == 0:
            return self._default_texture_features()

        # Local Binary Pattern (manual implementation for speed)
        lbp_map = self._compute_lbp(face_center)
        lbp_hist, _ = np.histogram(lbp_map.ravel(), bins=256, range=(0, 256))
        lbp_hist = lbp_hist.astype(float) / (lbp_hist.sum() + 1e-8)

        # Entropy of LBP histogram (real faces → higher entropy)
        lbp_entropy = float(-np.sum(lbp_hist * np.log2(lbp_hist + 1e-10)))

        # GLCM-inspired texture stats using gradient
        dx = cv2.Sobel(face_center, cv2.CV_64F, 1, 0)
        dy = cv2.Sobel(face_center, cv2.CV_64F, 0, 1)

        # Texture energy, contrast, homogeneity approximations
        texture_energy = float(np.mean(dx**2 + dy**2))
        texture_contrast = float(np.std(dx**2 + dy**2))

        # Noise level estimation using local std dev in smooth regions
        blur = cv2.GaussianBlur(face_center, (5, 5), 0)
        noise_map = np.abs(face_center.astype(float) - blur.astype(float))
        noise_level = float(noise_map.mean())

        # Haralick-like features: correlation
        normalized = face_center.astype(float) / 255.0
        mean_intensity = float(normalized.mean())
        std_intensity = float(normalized.std())

        # Micro-texture: difference from Gaussian-blurred version at multiple scales
        multiscale_texture = []
        for ksize in [3, 5, 9, 15]:
            blurred = cv2.GaussianBlur(face_center, (ksize, ksize), 0)
            diff = np.abs(face_center.astype(float) - blurred.astype(float))
            multiscale_texture.append(float(diff.mean()))

        return {
            "lbp_entropy": lbp_entropy,
            "texture_energy": texture_energy,
            "texture_contrast": texture_contrast,
            "noise_level": noise_level,
            "mean_intensity": mean_intensity,
            "std_intensity": std_intensity,
            "texture_scale_3": multiscale_texture[0],
            "texture_scale_5": multiscale_texture[1],
            "texture_scale_9": multiscale_texture[2],
            "texture_scale_15": multiscale_texture[3],
        }

    def _compute_lbp(self, gray: np.ndarray, radius: int = 1) -> np.ndarray:
        """Simple LBP computation"""
        rows, cols = gray.shape
        lbp = np.zeros_like(gray, dtype=np.uint8)
        neighbors = 8
        angles = [2 * np.pi * n / neighbors for n in range(neighbors)]

        for n, angle in enumerate(angles):
            dx = int(round(radius * np.cos(angle)))
            dy = int(round(-radius * np.sin(angle)))
            x0, x1 = max(0, -dx), min(cols, cols - dx)
            y0, y1 = max(0, -dy), min(rows, rows - dy)
            neighbor = gray[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
            center = gray[y0:y1, x0:x1]
            lbp[y0:y1, x0:x1] |= (neighbor >= center).astype(np.uint8) << n

        return lbp

    # ─────────────────────────────────────────────────────────────
    # 5. HEAD POSE & ORIENTATION
    # ─────────────────────────────────────────────────────────────

    def estimate_head_pose(self, landmarks: np.ndarray, frame_shape: Tuple) -> Dict:
        """
        Estimate head pose (yaw, pitch, roll) from landmarks.
        Deepfakes may have inconsistent or jittery head pose.
        """
        if landmarks is None or len(landmarks) < 468:
            return self._default_pose_features()

        h, w = frame_shape[:2]

        # 3D reference face model points (generic)
        model_points = np.array([
            [0.0, 0.0, 0.0],          # Nose tip (1)
            [0.0, -330.0, -65.0],      # Chin (152)
            [-225.0, 170.0, -135.0],   # Left eye corner (263)
            [225.0, 170.0, -135.0],    # Right eye corner (33)
            [-150.0, -150.0, -125.0],  # Left mouth corner (291)
            [150.0, -150.0, -125.0],   # Right mouth corner (61)
        ], dtype=np.float64)

        # Corresponding 2D image points
        key_indices = [1, 152, 263, 33, 291, 61]
        image_points = np.array([landmarks[i] for i in key_indices], dtype=np.float64)

        # Camera internals (approximation)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))

        try:
            # image_points must be float64 and shaped (N,1,2) for solvePnP
            img_pts = image_points.reshape(-1, 1, 2).astype(np.float64)
            obj_pts = model_points.reshape(-1, 1, 3).astype(np.float64)

            success, rotation_vector, translation_vector = cv2.solvePnP(
                obj_pts, img_pts, camera_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if not success:
                # Fallback: estimate yaw from eye midpoint offset from nose tip
                # This gives a rough but non-zero yaw even when solvePnP fails.
                nose_tip  = landmarks[1].astype(float)
                left_eye  = landmarks[263].astype(float)
                right_eye = landmarks[33].astype(float)
                eye_mid   = (left_eye + right_eye) / 2.0
                yaw_approx = float((nose_tip[0] - eye_mid[0]) / (w / 2) * 45.0)
                pitch_approx = float((nose_tip[1] - eye_mid[1]) / (h / 2) * 30.0)
                return {"yaw": yaw_approx, "pitch": pitch_approx, "roll": 0.0}

            # Convert rotation vector to Euler angles
            rot_mat, _ = cv2.Rodrigues(rotation_vector)
            sy = np.sqrt(rot_mat[0, 0]**2 + rot_mat[1, 0]**2)
            singular = sy < 1e-6

            if not singular:
                roll  = float(np.arctan2( rot_mat[2, 1], rot_mat[2, 2]) * 180 / np.pi)
                pitch = float(np.arctan2(-rot_mat[2, 0], sy)             * 180 / np.pi)
                yaw   = float(np.arctan2( rot_mat[1, 0], rot_mat[0, 0])  * 180 / np.pi)
            else:
                roll  = float(np.arctan2(-rot_mat[1, 2], rot_mat[1, 1]) * 180 / np.pi)
                pitch = float(np.arctan2(-rot_mat[2, 0], sy)             * 180 / np.pi)
                # Singular case: use geometric fallback for yaw
                nose_tip  = landmarks[1].astype(float)
                eye_mid   = ((landmarks[263] + landmarks[33]) / 2.0).astype(float)
                yaw = float((nose_tip[0] - eye_mid[0]) / (w / 2) * 45.0)

            return {"yaw": yaw, "pitch": pitch, "roll": roll}

        except Exception:
            return self._default_pose_features()

    # ─────────────────────────────────────────────────────────────
    # 6. MOUTH / LIP DYNAMICS
    # ─────────────────────────────────────────────────────────────

    def analyze_mouth_dynamics(self, landmarks: np.ndarray) -> Dict:
        """
        Analyze mouth opening/closing, lip movement, and jaw dynamics.
        """
        if landmarks is None or len(landmarks) < 468:
            return self._default_mouth_features()

        # Mouth aspect ratio (similar to EAR for blink detection)
        # Vertical mouth openings
        top_lip = landmarks[13]
        bottom_lip = landmarks[14]
        left_corner = landmarks[61]
        right_corner = landmarks[291]

        vertical_dist = float(np.linalg.norm(top_lip.astype(float) - bottom_lip.astype(float)))
        horizontal_dist = float(np.linalg.norm(left_corner.astype(float) - right_corner.astype(float)))

        mar = vertical_dist / (horizontal_dist + 1e-8)  # Mouth Aspect Ratio

        # Lip thickness
        upper_outer = landmarks[0]
        upper_inner = landmarks[13]
        lower_outer = landmarks[17]
        lower_inner = landmarks[14]

        upper_lip_thickness = float(np.linalg.norm(upper_outer.astype(float) - upper_inner.astype(float)))
        lower_lip_thickness = float(np.linalg.norm(lower_outer.astype(float) - lower_inner.astype(float)))

        # Mouth corner symmetry
        mouth_center_y = (left_corner[1] + right_corner[1]) / 2
        left_corner_offset = float(left_corner[1] - mouth_center_y)
        right_corner_offset = float(right_corner[1] - mouth_center_y)
        mouth_corner_asymmetry = abs(left_corner_offset - right_corner_offset)

        return {
            "mouth_aspect_ratio": float(mar),
            "mouth_vertical_dist": float(vertical_dist),
            "mouth_horizontal_dist": float(horizontal_dist),
            "upper_lip_thickness": float(upper_lip_thickness),
            "lower_lip_thickness": float(lower_lip_thickness),
            "mouth_corner_asymmetry": float(mouth_corner_asymmetry),
        }

    # ─────────────────────────────────────────────────────────────
    # 7. TEMPORAL CONSISTENCY ACROSS FRAMES
    # ─────────────────────────────────────────────────────────────

    def compute_temporal_features(self, feature_history: List[Dict]) -> Dict:
        """
        Compute temporal consistency features from per-frame feature sequences.
        Deepfakes have inconsistent temporal dynamics.
        """
        if len(feature_history) < 5:
            return self._default_temporal_features()

        # Extract time-series for each feature
        def extract_series(key: str) -> np.ndarray:
            vals = [f.get(key, 0.0) for f in feature_history if key in f]
            return np.array(vals, dtype=float)

        results = {}
        temporal_keys = [
            "yaw", "pitch", "roll",
            "mouth_aspect_ratio",
            "avg_symmetry_score",
            "noise_level",
            "sharpness_score",
            "hue_consistency",
        ]

        for key in temporal_keys:
            series = extract_series(key)
            if len(series) < 3:
                continue

            # First-order differences (velocity)
            diffs = np.diff(series)

            results[f"{key}_temporal_mean"] = float(series.mean())
            results[f"{key}_temporal_std"] = float(series.std())
            results[f"{key}_velocity_mean"] = float(np.abs(diffs).mean())
            results[f"{key}_velocity_std"] = float(diffs.std())
            results[f"{key}_jitter"] = float(np.diff(diffs).std())  # Acceleration jitter

        # Pose smoothness (head movement should be smooth)
        for angle in ["yaw", "pitch", "roll"]:
            series = extract_series(angle)
            if len(series) >= 5:
                x         = np.arange(len(series))
                coeffs    = np.polyfit(x, series, 2)
                fitted    = np.polyval(coeffs, x)
                residuals = series - fitted
                results[f"{angle}_motion_smoothness"] = float(residuals.std())

        # Flow consistency across frames
        flow_series = extract_series("boundary_flow_ratio")
        if len(flow_series) >= 3:
            results["flow_consistency"] = float(flow_series.std())
        else:
            results.setdefault("flow_consistency", 0.0)

        # Hue consistency jitter
        hue_series = extract_series("hue_consistency")
        if len(hue_series) >= 3:
            results["hue_consistency_jitter"] = float(np.diff(hue_series).std())
        else:
            results.setdefault("hue_consistency_jitter", 0.0)

        return results

    # ─────────────────────────────────────────────────────────────
    # 8. OPTICAL FLOW ANALYSIS
    # ─────────────────────────────────────────────────────────────

    def analyze_optical_flow(self, current_frame: np.ndarray,
                              prev_frame: np.ndarray,
                              face_bbox: Tuple) -> Dict:
        """
        Dense optical flow analysis on the face region.
        Deepfakes often show unnatural flow patterns at face boundaries.
        """
        if prev_frame is None:
            return self._default_flow_features()

        x, y, w, h = face_bbox

        # Crop face regions
        curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)[y:y+h, x:x+w]
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)[y:y+h, x:x+w]

        if curr_gray.size == 0 or prev_gray.size == 0:
            return self._default_flow_features()

        # Resize for speed
        target_size = (128, 128)
        curr_resized = cv2.resize(curr_gray, target_size)
        prev_resized = cv2.resize(prev_gray, target_size)

        # Farneback dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_resized, curr_resized, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )

        magnitude, angle = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])

        # Flow statistics
        flow_mean = float(magnitude.mean())
        flow_std = float(magnitude.std())
        flow_max = float(magnitude.max())

        # Flow direction consistency (real motion → consistent direction)
        angle_hist, _ = np.histogram(angle.ravel(), bins=16, range=(0, 2 * np.pi))
        angle_hist = angle_hist.astype(float) / (angle_hist.sum() + 1e-8)
        direction_entropy = float(-np.sum(angle_hist * np.log2(angle_hist + 1e-10)))

        # Boundary vs. center flow ratio (deepfakes show artifacts at boundaries)
        border = 16
        center_flow = magnitude[border:-border, border:-border].mean()
        border_flow = np.concatenate([
            magnitude[:border, :].ravel(),
            magnitude[-border:, :].ravel(),
            magnitude[:, :border].ravel(),
            magnitude[:, -border:].ravel()
        ]).mean()
        boundary_ratio = float(border_flow / (center_flow + 1e-8))

        return {
            "flow_mean": flow_mean,
            "flow_std": flow_std,
            "flow_max": flow_max,
            "flow_direction_entropy": direction_entropy,
            "boundary_flow_ratio": boundary_ratio,
        }

    # ─────────────────────────────────────────────────────────────
    # COMBINED PER-FRAME ANALYSIS
    # ─────────────────────────────────────────────────────────────

    def analyze_frame(self, frame: np.ndarray, face_bbox: Tuple,
                      prev_frame: Optional[np.ndarray] = None,
                      prev_landmarks: Optional[np.ndarray] = None) -> Dict:
        """
        Full per-frame facial dynamics analysis.
        Returns a flat feature dictionary for this frame.
        """
        x, y, w, h = face_bbox
        face_roi = frame[y:y+h, x:x+w]

        if face_roi.size == 0:
            return {}

        # Get MediaPipe landmarks on full frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        landmarks = None
        if results.multi_face_landmarks:
            fh, fw = frame.shape[:2]
            pts = []
            for lm in results.multi_face_landmarks[0].landmark:
                pts.append([int(lm.x * fw), int(lm.y * fh)])
            landmarks = np.array(pts)

        frame_features = {}

        # 1. Edge & color artifacts
        edge_feats = self.detect_edge_artifacts(face_roi)
        frame_features.update(edge_feats)

        # 2. Color consistency
        color_feats = self.analyze_color_consistency(face_roi, landmarks, frame.shape)
        frame_features.update(color_feats)

        # 3. Symmetry
        sym_feats = self.analyze_facial_symmetry(landmarks, frame.shape)
        frame_features.update(sym_feats)

        # 4. Skin texture
        tex_feats = self.analyze_skin_texture(face_roi)
        frame_features.update(tex_feats)

        # 5. Head pose
        pose_feats = self.estimate_head_pose(landmarks, frame.shape)
        frame_features.update(pose_feats)

        # 6. Mouth dynamics
        mouth_feats = self.analyze_mouth_dynamics(landmarks)
        frame_features.update(mouth_feats)

        # 7. Landmark motion
        motion_feats = self.analyze_facial_motion(landmarks, prev_landmarks)
        frame_features.update(motion_feats)

        # 8. Optical flow
        flow_feats = self.analyze_optical_flow(frame, prev_frame, face_bbox)
        frame_features.update(flow_feats)

        return frame_features

    # ─────────────────────────────────────────────────────────────
    # DEFAULT FEATURE DICTS (when frame/landmarks unavailable)
    # ─────────────────────────────────────────────────────────────

    def _default_symmetry_features(self) -> Dict:
        return {k: 0.0 for k in ["avg_symmetry_score", "std_symmetry_score",
                                  "avg_vertical_alignment", "min_symmetry", "max_symmetry"]}

    def _default_motion_features(self) -> Dict:
        return {k: 0.0 for k in ["global_motion_mean", "global_motion_std",
                                  "global_motion_max", "eye_motion_asymmetry",
                                  "eyebrow_motion_asymmetry", "mouth_motion",
                                  "jaw_motion", "nose_motion",
                                  "left_eye_motion", "right_eye_motion"]}

    def _default_texture_features(self) -> Dict:
        return {k: 0.0 for k in ["lbp_entropy", "texture_energy", "texture_contrast",
                                  "noise_level", "mean_intensity", "std_intensity",
                                  "texture_scale_3", "texture_scale_5",
                                  "texture_scale_9", "texture_scale_15"]}

    def _default_pose_features(self) -> Dict:
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

    def _default_mouth_features(self) -> Dict:
        return {k: 0.0 for k in ["mouth_aspect_ratio", "mouth_vertical_dist",
                                  "mouth_horizontal_dist", "upper_lip_thickness",
                                  "lower_lip_thickness", "mouth_corner_asymmetry"]}

    def _default_flow_features(self) -> Dict:
        return {k: 0.0 for k in ["flow_mean", "flow_std", "flow_max",
                                  "flow_direction_entropy", "boundary_flow_ratio"]}

    def _default_temporal_features(self) -> Dict:
        """Return zeroed temporal features so keys always exist in the feature dict."""
        keys = []
        for base in ["yaw", "pitch", "roll", "mouth_aspect_ratio",
                     "avg_symmetry_score", "noise_level", "sharpness_score",
                     "hue_consistency"]:
            for suffix in ["_temporal_mean", "_temporal_std",
                           "_velocity_mean", "_velocity_std", "_jitter"]:
                keys.append(f"{base}{suffix}")
        for angle in ["yaw", "pitch", "roll"]:
            keys.append(f"{angle}_motion_smoothness")
        keys += ["flow_consistency", "hue_consistency_jitter"]
        return {k: 0.0 for k in keys}

    def get_all_feature_names(self) -> List[str]:
        """Return list of all feature names produced by this analyzer."""
        dummy = {
            **self._default_symmetry_features(),
            **self._default_motion_features(),
            **self._default_texture_features(),
            **self._default_pose_features(),
            **self._default_mouth_features(),
            **self._default_flow_features(),
        }
        return list(dummy.keys())