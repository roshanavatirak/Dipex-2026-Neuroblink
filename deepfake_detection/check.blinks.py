#!/usr/bin/env python3
"""
debug_blinks.py  —  Diagnose why blink_rate = 0
Now uses the REAL APIs:
  - LandmarkDetector.detect_landmarks(frame) → np.ndarray (468, 2) pixel coords
  - LandmarkDetector.get_eye_landmarks(landmarks) → (left_16pts, right_16pts)
  - EyeAnalyzer.calculate_eye_aspect_ratio(eye_6pts) → float

Run:  python debug_blinks.py --video data/real/00000.mp4
"""
import sys, os, argparse
import cv2
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, "src")
for p in (BASE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── The correct 6-point EAR indices within MediaPipe's 468-point set ─────────
# Standard EAR uses 6 points: left-corner, top1, top2, right-corner, bot2, bot1
# These are the correct MediaPipe indices for the 6-point EAR formula
LEFT_EAR_6  = [33,  160, 158, 133, 153, 144]   # p1-p6 for left eye
RIGHT_EAR_6 = [362, 385, 387, 263, 373, 380]   # p1-p6 for right eye


def ear_from_6pts(landmarks: np.ndarray, indices: list) -> float:
    """Compute EAR directly from 468-point landmark array using 6 specific indices."""
    from scipy.spatial import distance as dist
    pts = landmarks[indices]  # shape (6, 2)
    A = dist.euclidean(pts[1], pts[5])  # vertical 1
    B = dist.euclidean(pts[2], pts[4])  # vertical 2
    C = dist.euclidean(pts[0], pts[3])  # horizontal
    return (A + B) / (2.0 * C) if C > 0 else 0.0


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video",  required=True)
    parser.add_argument("--frames", type=int, default=200)
    args = parser.parse_args()

    # ── Open video ────────────────────────────────────────────────────
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"❌ Cannot open: {args.video}"); sys.exit(1)

    fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"\n📹  {args.video}")
    print(f"    {W}×{H}  {fps:.1f}fps  {total} frames")

    # ── Import detectors ──────────────────────────────────────────────
    try:
        from landmark_detector import LandmarkDetector
        ld = LandmarkDetector()
        print("✅  LandmarkDetector loaded")
    except Exception as e:
        print(f"❌  LandmarkDetector: {e}"); sys.exit(1)

    try:
        from eye_analyzer import EyeAnalyzer
        ea = EyeAnalyzer()
        print("✅  EyeAnalyzer loaded")
    except Exception as e:
        print(f"❌  EyeAnalyzer: {e}"); sys.exit(1)

    # ── Frame loop ────────────────────────────────────────────────────
    section("FRAME-BY-FRAME EAR SCAN")

    left_ears, right_ears, timestamps = [], [], []
    face_found = face_missed = 0

    for fi in range(min(args.frames, total)):
        ret, frame = cap.read()
        if not ret:
            break

        landmarks = ld.detect_landmarks(frame)
        if landmarks is None:
            face_missed += 1
            continue
        face_found += 1

        # ── Method A: direct 6-point EAR from full 468-pt array ──────
        try:
            left_ear  = ear_from_6pts(landmarks, LEFT_EAR_6)
            right_ear = ear_from_6pts(landmarks, RIGHT_EAR_6)
        except Exception:
            left_ear = right_ear = 0.0

        # ── Method B: via EyeAnalyzer.calculate_eye_aspect_ratio ─────
        # The method needs exactly 6 points in order [p1..p6]
        # We use the same 6-point indices
        try:
            left_6  = landmarks[LEFT_EAR_6]   # (6,2)
            right_6 = landmarks[RIGHT_EAR_6]  # (6,2)
            left_ear_b  = ea.calculate_eye_aspect_ratio(left_6)
            right_ear_b = ea.calculate_eye_aspect_ratio(right_6)
        except Exception as exc:
            left_ear_b = right_ear_b = None

        left_ears.append(left_ear)
        right_ears.append(right_ear)
        timestamps.append(fi / fps)

        if fi < 12 or fi % 30 == 0:
            b_str = (f"  API_B: L={left_ear_b:.4f} R={right_ear_b:.4f}"
                     if left_ear_b is not None else "  API_B: ❌ failed")
            print(f"  Frame {fi:04d} | "
                  f"L-EAR={left_ear:.4f}  R-EAR={right_ear:.4f}  "
                  f"AVG={(left_ear+right_ear)/2:.4f}{b_str}")

    cap.release()

    # ── Statistics ────────────────────────────────────────────────────
    section("EAR STATISTICS")
    la = np.array(left_ears)
    ra = np.array(right_ears)
    avg_a = (la + ra) / 2.0

    print(f"  Faces found  : {face_found}/{face_found+face_missed} frames")
    print(f"\n               Left     Right    Avg")
    print(f"  Min EAR    : {la.min():.4f}   {ra.min():.4f}   {avg_a.min():.4f}")
    print(f"  Max EAR    : {la.max():.4f}   {ra.max():.4f}   {avg_a.max():.4f}")
    print(f"  Mean EAR   : {la.mean():.4f}   {ra.mean():.4f}   {avg_a.mean():.4f}")
    print(f"  Std  EAR   : {la.std():.4f}   {ra.std():.4f}   {avg_a.std():.4f}")

    # ── Blink simulation with different thresholds ────────────────────
    section("BLINK DETECTION — THRESHOLD SWEEP")
    print(f"  (EAR drops BELOW threshold = eye closed = blink)\n")

    # Adaptive threshold: 65% of each eye's own baseline (75th percentile)
    left_baseline  = np.percentile(la, 75)
    right_baseline = np.percentile(ra, 75)
    adaptive_left  = left_baseline  * 0.65
    adaptive_right = right_baseline * 0.65

    thresholds = {
        "Fixed 0.25 (default)":   (0.25,          0.25),
        "Fixed 0.20":              (0.20,          0.20),
        "Adaptive (75th×0.65)":   (adaptive_left, adaptive_right),
        "Very loose 0.85×mean":   (la.mean()*0.85, ra.mean()*0.85),
    }

    for name, (lt, rt) in thresholds.items():
        left_blinks  = int(np.sum(np.diff((la < lt).astype(int)) == 1))
        right_blinks = int(np.sum(np.diff((ra < rt).astype(int)) == 1))
        duration_s   = len(la) / fps
        rate = ((left_blinks + right_blinks) / 2) / duration_s if duration_s > 0 else 0
        print(f"  [{name}]")
        print(f"    Threshold  : L={lt:.4f}  R={rt:.4f}")
        print(f"    Blinks     : L={left_blinks}  R={right_blinks}")
        print(f"    Blink rate : {rate:.3f}/s  (normal human = 0.2–0.4/s)")
        print()

    # ── Root cause diagnosis ──────────────────────────────────────────
    section("ROOT CAUSE DIAGNOSIS")

    mean_ear = avg_a.mean()

    # The EAR your training shows is 1.44 — that's pixels not normalised!
    if mean_ear > 0.8:
        print(f"  ❌ CRITICAL: Mean EAR = {mean_ear:.3f}")
        print(f"     EAR should be 0.20–0.35 for open eyes.")
        print(f"     Your value is ~{mean_ear/0.28:.1f}× too high.")
        print(f"")
        print(f"  ROOT CAUSE: LandmarkDetector converts landmarks to PIXEL")
        print(f"     coordinates (int(landmark.x * w)), but EAR formula")
        print(f"     expects NORMALISED coordinates (0.0–1.0).")
        print(f"     Pixel distances make EAR proportional to face size,")
        print(f"     so it's always >> 0.25 and no blink is ever detected.")
        print(f"")
        print(f"  FIX → Edit src/landmark_detector.py, detect_landmarks():")
        print(f"     Change lines:")
        print(f"       x = int(landmark.x * w)   ← REMOVE the *w")
        print(f"       y = int(landmark.y * h)   ← REMOVE the *h")
        print(f"     To:")
        print(f"       x = landmark.x             ← normalised 0–1")
        print(f"       y = landmark.y             ← normalised 0–1")
        print(f"     And change return type:")
        print(f"       landmark_points.append([x, y])   ← keep as float")
        print(f"")
        print(f"  After fix, expected EAR range: 0.20–0.35 (open), <0.20 (closed)")
        print(f"  Adaptive threshold will then be: ~{0.28*0.65:.3f}")

    elif mean_ear < 0.05:
        print(f"  ❌ Mean EAR too low ({mean_ear:.4f}) — landmark indices are wrong")
        print(f"     The 6-point indices {LEFT_EAR_6} may not match your MediaPipe version")
    elif la.min() > 0.20:
        adaptive = mean_ear * 0.65
        print(f"  ⚠️  EAR scale looks correct (mean={mean_ear:.3f})")
        print(f"     but EAR never drops below 0.20 in {args.frames} frames")
        print(f"     → These frames may not contain a blink")
        print(f"     → Run with --frames 450 to sample the full video")
        print(f"     → Or: fix eye_analyzer.py threshold to {adaptive:.3f}")
    else:
        print(f"  ✅ EAR range looks healthy. Check eye_analyzer.py blink threshold.")
        print(f"     Recommended adaptive threshold: {mean_ear * 0.65:.3f}")

    # ── Fix summary ───────────────────────────────────────────────────
    section("REQUIRED FIXES SUMMARY")
    print(f"""
  1. src/landmark_detector.py  — detect_landmarks()
     CHANGE:  x = int(landmark.x * w)   →  x = landmark.x
              y = int(landmark.y * h)   →  y = landmark.y
     WHY:     EAR formula needs normalised coords, not pixels

  2. src/eye_analyzer.py  — calculate_blink_features()
     CHANGE:  blink_threshold = 0.25
     TO:      baseline = np.percentile(ear_array, 75)
              blink_threshold = baseline * 0.65
     WHY:     Adaptive threshold handles all face sizes correctly

  3. src/feature_extractor.py  — wherever it calls EyeAnalyzer
     ENSURE:  It passes 6-point arrays using indices {LEFT_EAR_6}
              NOT the 16-point LEFT_EYE_INDICES from LandmarkDetector
     WHY:     EAR formula only works with exactly 6 specific points
""")

if __name__ == "__main__":
    main()