# import numpy as np
# from typing import Tuple, List
# from scipy.spatial import distance as dist

# class EyeAnalyzer:
#     def __init__(self):
#         """Initialize eye analyzer"""
#         pass
    
#     def calculate_eye_aspect_ratio(self, eye_landmarks: np.ndarray) -> float:
#         """
#         Calculate Eye Aspect Ratio (EAR)
#         EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
#         """
#         # Vertical eye landmarks
#         A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
#         B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        
#         # Horizontal eye landmark
#         C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        
#         # Calculate EAR
#         ear = (A + B) / (2.0 * C)
#         return ear
    
#     def calculate_eye_closure_ratio(self, upper_eyelid: np.ndarray, lower_eyelid: np.ndarray) -> float:
#         """
#         Calculate eye closure ratio based on eyelid distance
#         """
#         # Calculate average distance between upper and lower eyelids
#         distances = []
#         min_len = min(len(upper_eyelid), len(lower_eyelid))
        
#         for i in range(min_len):
#             distance = dist.euclidean(upper_eyelid[i], lower_eyelid[i])
#             distances.append(distance)
        
#         avg_distance = np.mean(distances)
        
#         # Normalize by eye width (approximate)
#         eye_width = dist.euclidean(upper_eyelid[0], upper_eyelid[-1])
#         closure_ratio = avg_distance / eye_width if eye_width > 0 else 0
        
#         return closure_ratio
    
#     def detect_blink(self, ear: float, threshold: float = 0.25) -> bool:
#         """
#         Detect if eye is blinking based on EAR threshold
#         """
#         return ear < threshold
    
#     def calculate_blink_features(self, ear_sequence: List[float], 
#                                timestamps: List[float]) -> dict:
#         """
#         Calculate blink-related features from EAR sequence
#         """
#         ear_array = np.array(ear_sequence)
#         time_array = np.array(timestamps)
        
#         # Detect blinks
#         blink_threshold = 0.25
#         is_blink = ear_array < blink_threshold
        
#         # Find blink events
#         blink_starts = []
#         blink_ends = []
#         in_blink = False
        
#         for i, blink in enumerate(is_blink):
#             if blink and not in_blink:
#                 blink_starts.append(i)
#                 in_blink = True
#             elif not blink and in_blink:
#                 blink_ends.append(i)
#                 in_blink = False
        
#         # Ensure equal number of starts and ends
#         min_len = min(len(blink_starts), len(blink_ends))
#         blink_starts = blink_starts[:min_len]
#         blink_ends = blink_ends[:min_len]
        
#         # Calculate features
#         features = {}
        
#         # Blink rate (blinks per second)
#         total_time = time_array[-1] - time_array[0] if len(time_array) > 1 else 1
#         features['blink_rate'] = len(blink_starts) / total_time
        
#         # Blink durations
#         blink_durations = []
#         for start, end in zip(blink_starts, blink_ends):
#             duration = time_array[end] - time_array[start]
#             blink_durations.append(duration)
        
#         if blink_durations:
#             features['avg_blink_duration'] = np.mean(blink_durations)
#             features['std_blink_duration'] = np.std(blink_durations)
#             features['max_blink_duration'] = np.max(blink_durations)
#             features['min_blink_duration'] = np.min(blink_durations)
#         else:
#             features['avg_blink_duration'] = 0
#             features['std_blink_duration'] = 0
#             features['max_blink_duration'] = 0
#             features['min_blink_duration'] = 0
        
#         # Blink cycles (time between blinks)
#         blink_cycles = []
#         for i in range(1, len(blink_starts)):
#             cycle = time_array[blink_starts[i]] - time_array[blink_starts[i-1]]
#             blink_cycles.append(cycle)
        
#         if blink_cycles:
#             features['avg_blink_cycle'] = np.mean(blink_cycles)
#             features['std_blink_cycle'] = np.std(blink_cycles)
#         else:
#             features['avg_blink_cycle'] = 0
#             features['std_blink_cycle'] = 0
        
#         # EAR statistics
#         features['avg_ear'] = np.mean(ear_array)
#         features['std_ear'] = np.std(ear_array)
#         features['min_ear'] = np.min(ear_array)
#         features['max_ear'] = np.max(ear_array)
        
#         # Blink completeness (how closed eyes get during blinks)
#         if blink_durations:
#             min_ear_during_blinks = []
#             for start, end in zip(blink_starts, blink_ends):
#                 min_ear = np.min(ear_array[start:end+1])
#                 min_ear_during_blinks.append(min_ear)
#             features['avg_blink_completeness'] = np.mean(min_ear_during_blinks)
#         else:
#             features['avg_blink_completeness'] = features['min_ear']
        
#         return features

#new update

import numpy as np
from typing import List
from scipy.spatial import distance as dist
from scipy.ndimage import median_filter

# 6-point MediaPipe indices for the EAR formula
# Order: [left-corner, top1, top2, right-corner, bot2, bot1]
LEFT_EAR_INDICES  = [33,  160, 158, 133, 153, 144]
RIGHT_EAR_INDICES = [362, 385, 387, 263, 373, 380]


class EyeAnalyzer:
    def __init__(self):
        """Initialize eye analyzer with adaptive blink detection."""
        self.ear_threshold = 0.20  # fallback only; adaptive threshold used when enough data

    # ── Core EAR calculation ───────────────────────────────────────────
    def calculate_eye_aspect_ratio(self, eye_landmarks: np.ndarray) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) from 6 landmark points.
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)

        eye_landmarks : np.ndarray shape (6, 2), NORMALISED coords (0–1)
        Points order  : [left-corner, top1, top2, right-corner, bot2, bot1]

        Expected output: ~0.25–0.45 (open eye), < 0.20 (closed eye)
        """
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        return (A + B) / (2.0 * C) if C > 0 else 0.0

    def get_ear_from_landmarks(self, landmarks: np.ndarray) -> dict:
        """
        Compute left/right/avg EAR from the full 468-point normalised array.
        landmarks : np.ndarray (468, 2) in 0–1 range
        """
        left_ear  = self.calculate_eye_aspect_ratio(landmarks[LEFT_EAR_INDICES])
        right_ear = self.calculate_eye_aspect_ratio(landmarks[RIGHT_EAR_INDICES])
        return {
            "left_ear":  left_ear,
            "right_ear": right_ear,
            "avg_ear":   (left_ear + right_ear) / 2.0,
        }

    # ── Adaptive threshold ─────────────────────────────────────────────
    def _adaptive_threshold(self, ear_array: np.ndarray) -> float:
        """
        Per-video adaptive threshold = 75th-percentile (open-eye baseline) × 0.65.
        Handles any face size or lighting without manual tuning.
        Falls back to fixed 0.20 if fewer than 10 samples.
        """
        if len(ear_array) < 10:
            return self.ear_threshold
        return float(np.percentile(ear_array, 75)) * 0.65

    # ── Blink detection helper ─────────────────────────────────────────
    def detect_blink(self, ear: float, threshold: float = None) -> bool:
        thresh = threshold if threshold is not None else self.ear_threshold
        return ear < thresh

    # ── Full feature extraction ────────────────────────────────────────
    def calculate_blink_features(self,
                                  ear_sequence: List[float],
                                  timestamps: List[float]) -> dict:
        """
        Calculate all blink features from an EAR time-series.

        ear_sequence : avg EAR per frame (use NORMALISED landmark coords)
        timestamps   : time in seconds per frame

        Pipeline:
          1. 3-frame median smooth  → removes single-frame noise
          2. Adaptive threshold     → 75th-pct × 0.65
          3. Edge detection         → blink start/end frames
          4. Duration filter        → 2–15 frames (≈67ms–500ms at 30fps)
             removes noise spikes and half-open-eye false positives
        """
        ear_array  = np.array(ear_sequence, dtype=np.float32)
        time_array = np.array(timestamps,   dtype=np.float32)

        if len(ear_array) == 0:
            return self._zero_features()

        # ── 1. Smooth to kill 1-frame noise spikes ────────────────────
        smoothed = median_filter(ear_array, size=3) if len(ear_array) >= 3 else ear_array

        # ── 2. Adaptive threshold ─────────────────────────────────────
        blink_threshold = self._adaptive_threshold(smoothed)
        is_blink = smoothed < blink_threshold

        # ── 3. Find raw blink events (edges) ─────────────────────────
        raw_starts, raw_ends = [], []
        in_blink = False
        for i, closed in enumerate(is_blink):
            if closed and not in_blink:
                raw_starts.append(i)
                in_blink = True
            elif not closed and in_blink:
                raw_ends.append(i)
                in_blink = False
        if in_blink:
            raw_ends.append(len(ear_array) - 1)

        n_raw = min(len(raw_starts), len(raw_ends))
        raw_starts = raw_starts[:n_raw]
        raw_ends   = raw_ends[:n_raw]

        # ── 4. Duration filter: 2–15 frames ──────────────────────────
        # Estimates FPS from timestamp gaps; defaults to 30 if uniform
        if len(time_array) > 1:
            dt = float(time_array[1] - time_array[0])
            fps_est = 1.0 / dt if dt > 0 else 30.0
        else:
            fps_est = 30.0

        min_frames = 2                        # ~67ms — removes noise
        max_frames = int(fps_est * 0.5)       # 500ms — removes stuck eyes
        max_frames = max(max_frames, 6)       # at least 6 frames minimum cap

        valid_pairs = [
            (s, e) for s, e in zip(raw_starts, raw_ends)
            if min_frames <= (e - s) <= max_frames
        ]
        blink_starts = [s for s, e in valid_pairs]
        blink_ends   = [e for s, e in valid_pairs]
        n = len(blink_starts)

        features = {}

        # ── Blink rate ─────────────────────────────────────────────────
        total_time = float(time_array[-1] - time_array[0]) if len(time_array) > 1 else 1.0
        features['blink_rate'] = n / total_time if total_time > 0 else 0.0

        # ── Blink durations ────────────────────────────────────────────
        blink_durations = []
        for s, e in zip(blink_starts, blink_ends):
            dur = float(time_array[e] - time_array[s])
            if dur > 0:
                blink_durations.append(dur)

        if blink_durations:
            features['avg_blink_duration'] = float(np.mean(blink_durations))
            features['std_blink_duration'] = float(np.std(blink_durations))
            features['max_blink_duration'] = float(np.max(blink_durations))
            features['min_blink_duration'] = float(np.min(blink_durations))
        else:
            features['avg_blink_duration'] = 0.0
            features['std_blink_duration'] = 0.0
            features['max_blink_duration'] = 0.0
            features['min_blink_duration'] = 0.0

        # ── Inter-blink intervals ──────────────────────────────────────
        blink_cycles = [
            float(time_array[blink_starts[i]] - time_array[blink_starts[i - 1]])
            for i in range(1, n)
        ]
        if blink_cycles:
            features['avg_blink_cycle'] = float(np.mean(blink_cycles))
            features['std_blink_cycle'] = float(np.std(blink_cycles))
        else:
            features['avg_blink_cycle'] = 0.0
            features['std_blink_cycle'] = 0.0

        # ── EAR statistics (on RAW, unsmoothed) ───────────────────────
        features['avg_ear']             = float(np.mean(ear_array))
        features['std_ear']             = float(np.std(ear_array))
        features['min_ear']             = float(np.min(ear_array))
        features['max_ear']             = float(np.max(ear_array))
        features['ear_range']           = float(np.max(ear_array) - np.min(ear_array))
        features['ear_threshold_used']  = float(blink_threshold)

        # ── Blink completeness (min EAR during each blink) ────────────
        if n > 0:
            min_ears = [
                float(np.min(ear_array[s:e + 1]))
                for s, e in zip(blink_starts, blink_ends)
                if e + 1 > s
            ]
            features['avg_blink_completeness'] = float(np.mean(min_ears)) if min_ears else features['min_ear']
        else:
            features['avg_blink_completeness'] = features['min_ear']

        # ── Blink regularity (CV of inter-blink intervals) ────────────
        if blink_cycles and np.mean(blink_cycles) > 0:
            features['blink_regularity'] = float(np.std(blink_cycles) / np.mean(blink_cycles))
        else:
            features['blink_regularity'] = 0.0

        # ── Debug info (won't affect model, useful for inspection) ─────
        features['n_blinks_raw']      = n_raw   # before duration filter
        features['n_blinks_filtered'] = n       # after duration filter

        return features

    def _zero_features(self) -> dict:
        return {
            'blink_rate': 0.0, 'avg_blink_duration': 0.0, 'std_blink_duration': 0.0,
            'max_blink_duration': 0.0, 'min_blink_duration': 0.0,
            'avg_blink_cycle': 0.0, 'std_blink_cycle': 0.0,
            'avg_ear': 0.0, 'std_ear': 0.0, 'min_ear': 0.0, 'max_ear': 0.0,
            'ear_range': 0.0, 'ear_threshold_used': 0.0,
            'avg_blink_completeness': 0.0, 'blink_regularity': 0.0,
            'n_blinks_raw': 0, 'n_blinks_filtered': 0,
        }

    # ── Legacy compatibility ───────────────────────────────────────────
    def calculate_eye_closure_ratio(self, upper_eyelid: np.ndarray,
                                     lower_eyelid: np.ndarray) -> float:
        distances = [dist.euclidean(upper_eyelid[i], lower_eyelid[i])
                     for i in range(min(len(upper_eyelid), len(lower_eyelid)))]
        avg_distance = float(np.mean(distances)) if distances else 0.0
        eye_width = dist.euclidean(upper_eyelid[0], upper_eyelid[-1])
        return avg_distance / eye_width if eye_width > 0 else 0.0