# import numpy as np
# import cv2
# from typing import List, Dict, Tuple

# # from .face_detector import FaceDetector
# # from .landmark_detector import LandmarkDetector
# # from .eye_analyzer import EyeAnalyzer




# from face_detector import FaceDetector
# from landmark_detector import LandmarkDetector
# from eye_analyzer import EyeAnalyzer

# import os

# class FeatureExtractor:
#     def __init__(self):
#         """Initialize feature extractor with all components"""
#         self.face_detector = FaceDetector()
#         self.landmark_detector = LandmarkDetector()
#         self.eye_analyzer = EyeAnalyzer()
    
#     def extract_video_features(self, video_path: str) -> Dict:
#         """
#         Extract features from a video file
#         """
#         if not os.path.exists(video_path):
#             raise FileNotFoundError(f"Video file not found: {video_path}")
        
#         cap = cv2.VideoCapture(video_path)
#         if not cap.isOpened():
#             raise ValueError(f"Could not open video file: {video_path}")
        
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         frame_count = 0
        
#         left_ear_sequence = []
#         right_ear_sequence = []
#         timestamps = []
        
#         print(f"Processing video: {video_path}")
        
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
            
#             timestamp = frame_count / fps
            
#             # Detect faces
#             faces = self.face_detector.detect_faces(frame)
#             largest_face = self.face_detector.get_largest_face(faces)
            
#             if largest_face is not None:
#                 # Extract face region
#                 x, y, w, h = largest_face
#                 face_region = frame[y:y+h, x:x+w]
                
#                 # Detect landmarks
#                 landmarks = self.landmark_detector.detect_landmarks(face_region)
                
#                 if landmarks is not None:
#                     # Adjust landmarks to original frame coordinates
#                     landmarks[:, 0] += x
#                     landmarks[:, 1] += y
                    
#                     # Get eye landmarks
#                     left_eye, right_eye = self.landmark_detector.get_eye_landmarks(landmarks)
                    
#                     # Calculate EAR for both eyes
#                     left_ear = self.eye_analyzer.calculate_eye_aspect_ratio(left_eye[:6])
#                     right_ear = self.eye_analyzer.calculate_eye_aspect_ratio(right_eye[:6])
                    
#                     left_ear_sequence.append(left_ear)
#                     right_ear_sequence.append(right_ear)
#                     timestamps.append(timestamp)
            
#             frame_count += 1
            
#             # Print progress
#             if frame_count % 100 == 0:
#                 print(f"Processed {frame_count} frames")
        
#         cap.release()
        
#         if len(left_ear_sequence) == 0:
#             print(f"Warning: No valid frames found in {video_path}")
#             return self._get_default_features()
        
#         # Calculate features for both eyes
#         left_features = self.eye_analyzer.calculate_blink_features(left_ear_sequence, timestamps)
#         right_features = self.eye_analyzer.calculate_blink_features(right_ear_sequence, timestamps)
        
#         # Combine features
#         combined_features = {}
        
#         # Add left eye features
#         for key, value in left_features.items():
#             combined_features[f'left_{key}'] = value
        
#         # Add right eye features
#         for key, value in right_features.items():
#             combined_features[f'right_{key}'] = value
        
#         # Add combined features
#         avg_ear_sequence = [(l + r) / 2 for l, r in zip(left_ear_sequence, right_ear_sequence)]
#         avg_features = self.eye_analyzer.calculate_blink_features(avg_ear_sequence, timestamps)
        
#         for key, value in avg_features.items():
#             combined_features[f'avg_{key}'] = value
        
#         # Add video-level features
#         combined_features['video_duration'] = timestamps[-1] if timestamps else 0
#         combined_features['total_frames'] = len(timestamps)
#         combined_features['fps'] = fps
        
#         return combined_features
    
#     def _get_default_features(self) -> Dict:
#         """Return default features when no face is detected"""
#         feature_names = [
#             'blink_rate', 'avg_blink_duration', 'std_blink_duration',
#             'max_blink_duration', 'min_blink_duration', 'avg_blink_cycle',
#             'std_blink_cycle', 'avg_ear', 'std_ear', 'min_ear', 'max_ear',
#             'avg_blink_completeness'
#         ]
        
#         features = {}
#         for prefix in ['left_', 'right_', 'avg_']:
#             for name in feature_names:
#                 features[f'{prefix}{name}'] = 0.0
        
#         features['video_duration'] = 0
#         features['total_frames'] = 0
#         features['fps'] = 0
        
#         return features




#new update
#!/usr/bin/env python3
"""
feature_extractor.py — Eye Blink + Facial Dynamics Feature Extraction

═══════════════════════════════════════════════════════════════════
BLINK BUG — ROOT CAUSE & FIX
═══════════════════════════════════════════════════════════════════

YOUR LandmarkDetector.detect_landmarks(face_region) works like this:
  • Input : face_region  (cropped frame, e.g. 200×200 pixels)
  • Output: np.array shape (468, 2) — pixel coords INSIDE face_region

YOUR LandmarkDetector.get_eye_landmarks(landmarks) works like this:
  • Returns landmarks[LEFT_EYE_INDICES]  &  landmarks[RIGHT_EYE_INDICES]
    where the index lists = [33, 7, 163, 144, 145, 153 ...]
    i.e. those numbers are ARRAY INDICES into the 468-point array.

OLD BUGGY CODE did:
    landmarks[:, 0] += x     # shift every coord to full-frame
    landmarks[:, 1] += y
    left_eye = get_eye_landmarks(landmarks)   # returns 16 points
    ear = calculate_ear(left_eye[:6])         # WRONG: [:6] ≠ EAR 6-point set

  Result: EAR ≈ 1.43 (should be 0.25–0.35) → no blinks ever detected.

FIX:
  1. Use the correct 6 MediaPipe EAR indices directly on the 468-pt array
     (in face_region coords — no offset needed for EAR).
  2. Only offset landmarks to full-frame coords for FacialDynamicsAnalyzer.
═══════════════════════════════════════════════════════════════════
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple

from face_detector import FaceDetector
from landmark_detector import LandmarkDetector
from eye_analyzer import EyeAnalyzer
from facial_dynamics_analyzer import FacialDynamicsAnalyzer


# ── Correct 6-point EAR indices from MediaPipe 468-landmark model ────────────
# Left eye:  outer-corner, upper-outer, upper-inner, inner-corner, lower-inner, lower-outer
_LEFT_EAR_IDX  = [33, 160, 158, 133, 153, 144]
# Right eye: same anatomical order, mirrored indices
_RIGHT_EAR_IDX = [362, 385, 387, 263, 373, 380]


class FeatureExtractor:
    def __init__(self):
        self.face_detector     = FaceDetector()
        self.landmark_detector = LandmarkDetector()
        self.eye_analyzer      = EyeAnalyzer()
        self.facial_dynamics   = FacialDynamicsAnalyzer()

    # ─────────────────────────────────────────────────────────────
    # MAIN
    # ─────────────────────────────────────────────────────────────

    def extract_video_features(self, video_path: str) -> Dict:
        """
        Extract all features from a video:
          • Eye blink EAR sequences  (blink_rate, avg_ear, etc.)
          • Per-frame facial dynamics (edge artifacts, skin texture,
            symmetry, head pose, mouth dynamics, optical flow)
          • Temporal consistency metrics (jitter, velocity, smoothness)
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25.0

        frame_count        = 0
        left_ear_sequence  : List[float] = []
        right_ear_sequence : List[float] = []
        timestamps         : List[float] = []
        per_frame_dynamics : List[Dict]  = []

        prev_frame               : Optional[np.ndarray] = None
        prev_landmarks_fullframe : Optional[np.ndarray] = None

        print(f"  Processing: {os.path.basename(video_path)}")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp    = frame_count / fps
            faces        = self.face_detector.detect_faces(frame)
            largest_face = self.face_detector.get_largest_face(faces)

            if largest_face is not None:
                x, y, w, h = largest_face
                face_region = frame[y:y+h, x:x+w]

                # Returns (468, 2) pixel coords relative to face_region
                landmarks_crop = self.landmark_detector.detect_landmarks(face_region)

                if landmarks_crop is not None:

                    # ── EAR — use crop coords, correct 6-pt indices ───────
                    # No (x,y) offset needed: EAR only cares about relative
                    # distances between the 6 points, not absolute position.
                    left_ear  = self._calc_ear(landmarks_crop, _LEFT_EAR_IDX)
                    right_ear = self._calc_ear(landmarks_crop, _RIGHT_EAR_IDX)

                    left_ear_sequence.append(left_ear)
                    right_ear_sequence.append(right_ear)
                    timestamps.append(timestamp)

                    # ── Full-frame coords for FacialDynamicsAnalyzer ──────
                    landmarks_full = landmarks_crop.copy().astype(float)
                    landmarks_full[:, 0] += x
                    landmarks_full[:, 1] += y

                    # ── Facial dynamics (every 3 frames for speed) ────────
                    if frame_count % 3 == 0:
                        dyn = self.facial_dynamics.analyze_frame(
                            frame,
                            face_bbox      = (x, y, w, h),
                            prev_frame     = prev_frame,
                            prev_landmarks = prev_landmarks_fullframe,
                        )
                        if dyn:
                            per_frame_dynamics.append(dyn)

                    prev_landmarks_fullframe = landmarks_full

                prev_frame = frame.copy()

            frame_count += 1
            if frame_count % 100 == 0:
                print(f"    {frame_count} frames processed...")

        cap.release()

        # ── No face ───────────────────────────────────────────────
        if not left_ear_sequence:
            print(f"  ⚠  No face detected: {os.path.basename(video_path)}")
            return self._get_default_features()

        # ── EAR sanity check (printed so you can verify the fix) ──
        avg_ear_val = float(np.mean(
            [(l + r) / 2 for l, r in zip(left_ear_sequence, right_ear_sequence)]
        ))
        print(f"    avg_EAR={avg_ear_val:.4f}  "
              f"(expected 0.20–0.35 open eye)  "
              f"frames_with_face={len(left_ear_sequence)}")

        # ── Blink features ────────────────────────────────────────
        left_feats = self.eye_analyzer.calculate_blink_features(
            left_ear_sequence, timestamps)
        right_feats = self.eye_analyzer.calculate_blink_features(
            right_ear_sequence, timestamps)
        avg_ear_seq = [(l + r) / 2 for l, r in zip(left_ear_sequence, right_ear_sequence)]
        avg_feats   = self.eye_analyzer.calculate_blink_features(avg_ear_seq, timestamps)

        combined: Dict = {}
        for k, v in left_feats.items():
            combined[f"left_{k}"]  = v
        for k, v in right_feats.items():
            combined[f"right_{k}"] = v
        for k, v in avg_feats.items():
            combined[f"avg_{k}"]   = v

        combined["video_duration"] = timestamps[-1] if timestamps else 0.0
        combined["total_frames"]   = len(timestamps)
        combined["fps"]            = fps

        # ── Facial dynamics ───────────────────────────────────────
        if per_frame_dynamics:
            combined.update(self._aggregate_dynamics(per_frame_dynamics))
            temporal = self.facial_dynamics.compute_temporal_features(per_frame_dynamics)
            combined.update({f"temporal_{k}": v for k, v in temporal.items()})
            print(f"    dynamics_frames={len(per_frame_dynamics)}")
        else:
            print(f"    ⚠  No facial dynamics frames collected")

        return combined

    # ─────────────────────────────────────────────────────────────
    # EAR
    # ─────────────────────────────────────────────────────────────

    def _calc_ear(self, landmarks: np.ndarray, idx6: List[int]) -> float:
        """
        Eye Aspect Ratio from 6 landmark indices:
          idx6 = [outer_corner, upper_outer, upper_inner,
                  inner_corner, lower_inner, lower_outer]

        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        Normal open eye ≈ 0.25–0.35. Blink threshold ≈ 0.20.
        """
        try:
            pts = landmarks[idx6].astype(float)   # (6, 2)
            A = np.linalg.norm(pts[1] - pts[5])   # upper-outer ↔ lower-outer
            B = np.linalg.norm(pts[2] - pts[4])   # upper-inner ↔ lower-inner
            C = np.linalg.norm(pts[0] - pts[3])   # outer-corner ↔ inner-corner
            return float((A + B) / (2.0 * C)) if C > 1e-6 else 0.0
        except Exception:
            return 0.0

    # ─────────────────────────────────────────────────────────────
    # AGGREGATION
    # ─────────────────────────────────────────────────────────────

    def _aggregate_dynamics(self, per_frame: List[Dict]) -> Dict:
        """
        Aggregate per-frame facial dynamics into video-level stats.
        For every feature: mean, std, min, max, median, p90.
        All output keys are prefixed with "dyn_".
        """
        if not per_frame:
            return {}

        all_keys: set = set()
        for fd in per_frame:
            all_keys.update(fd.keys())

        agg: Dict = {}
        for key in all_keys:
            vals = [
                f[key] for f in per_frame
                if key in f
                and isinstance(f[key], (int, float))
                and np.isfinite(float(f[key]))
            ]
            if not vals:
                continue
            arr = np.array(vals, dtype=float)
            agg[f"dyn_{key}_mean"]   = float(arr.mean())
            agg[f"dyn_{key}_std"]    = float(arr.std())
            agg[f"dyn_{key}_min"]    = float(arr.min())
            agg[f"dyn_{key}_max"]    = float(arr.max())
            agg[f"dyn_{key}_median"] = float(np.median(arr))
            agg[f"dyn_{key}_p90"]    = float(np.percentile(arr, 90))
        return agg

    # ─────────────────────────────────────────────────────────────
    # DEFAULT
    # ─────────────────────────────────────────────────────────────

    def _get_default_features(self) -> Dict:
        """Zero-valued feature dict when no face is detected in video."""
        blink_names = [
            "blink_rate", "blink_count",
            "avg_blink_duration", "std_blink_duration",
            "max_blink_duration", "min_blink_duration",
            "avg_blink_cycle",    "std_blink_cycle",
            "avg_ear",            "std_ear",
            "min_ear",            "max_ear",
            "avg_blink_completeness",
        ]
        features: Dict = {}
        for prefix in ("left_", "right_", "avg_"):
            for name in blink_names:
                features[f"{prefix}{name}"] = 0.0

        features["video_duration"] = 0.0
        features["total_frames"]   = 0
        features["fps"]            = 0.0

        stat_suffixes = ("_mean", "_std", "_min", "_max", "_median", "_p90")
        try:
            dyn_keys = self.facial_dynamics.get_all_feature_names()
        except Exception:
            dyn_keys = []
        for key in dyn_keys:
            for suf in stat_suffixes:
                features[f"dyn_{key}{suf}"] = 0.0

        return features