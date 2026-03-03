#!/usr/bin/env python3
"""
Migration Script — Add Facial Dynamics Features to Existing Cached Data
────────────────────────────────────────────────────────────────────────
If you already trained on 2000 videos with eye-blink-only features,
this script re-processes those videos to ADD the new facial dynamics
features to existing .npz cache files WITHOUT re-running eye blink extraction.

Usage:
  python migrate_features.py --video-dir data/real_videos --label 0 --cache-dir features
  python migrate_features.py --video-dir data/fake_videos --label 1 --cache-dir features

After running for both dirs, use retrain.py to retrain with the enriched features.
"""

import os
import sys
import argparse
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from facial_dynamics_analyzer import FacialDynamicsAnalyzer
from face_detector import FaceDetector
from landmark_detector import LandmarkDetector


def extract_dynamics_only(video_path: str,
                           analyzer: FacialDynamicsAnalyzer,
                           face_detector: FaceDetector) -> Dict:
    """
    Extract ONLY facial dynamics features from a video.
    Does NOT re-run eye blink analysis.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = 0
    per_frame: List[Dict] = []
    prev_frame: Optional[np.ndarray] = None
    prev_landmarks = None

    lm_detector = LandmarkDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = face_detector.detect_faces(frame)
        largest = face_detector.get_largest_face(faces)

        if largest is not None and frame_count % 3 == 0:
            x, y, w, h = largest
            face_region = frame[y:y+h, x:x+w]
            landmarks = lm_detector.detect_landmarks(face_region)

            if landmarks is not None:
                landmarks[:, 0] += x
                landmarks[:, 1] += y

                dyn = analyzer.analyze_frame(
                    frame, face_bbox=(x, y, w, h),
                    prev_frame=prev_frame,
                    prev_landmarks=prev_landmarks
                )
                if dyn:
                    per_frame.append(dyn)
                prev_landmarks = landmarks.copy()

        prev_frame = frame.copy()
        frame_count += 1

        if frame_count % 100 == 0:
            print(f"    {frame_count} frames...")

    cap.release()
    return per_frame


def aggregate(per_frame: List[Dict]) -> Dict:
    if not per_frame:
        return {}
    all_keys = set()
    for f in per_frame:
        all_keys.update(f.keys())
    aggregated = {}
    for key in all_keys:
        vals = [f[key] for f in per_frame if key in f and np.isfinite(f.get(key, float("nan")))]
        if not vals:
            continue
        arr = np.array(vals)
        aggregated[f"dyn_{key}_mean"] = float(arr.mean())
        aggregated[f"dyn_{key}_std"] = float(arr.std())
        aggregated[f"dyn_{key}_min"] = float(arr.min())
        aggregated[f"dyn_{key}_max"] = float(arr.max())
        aggregated[f"dyn_{key}_median"] = float(np.median(arr))
        aggregated[f"dyn_{key}_p90"] = float(np.percentile(arr, 90))
    return aggregated


def migrate_directory(video_dir: str, cache_dir: str, force: bool = False):
    """
    Enrich all cached .npz files in cache_dir that correspond to videos in video_dir.
    """
    print(f"\n📂 Migrating: {video_dir}")
    analyzer = FacialDynamicsAnalyzer()
    face_detector = FaceDetector()

    video_exts = (".mp4", ".avi", ".mov", ".mkv")
    videos = [f for f in os.listdir(video_dir) if f.lower().endswith(video_exts)]
    total = len(videos)
    print(f"   Found {total} videos")

    updated = 0
    skipped = 0
    errors = 0

    for i, filename in enumerate(sorted(videos), 1):
        video_name = os.path.splitext(filename)[0]
        cache_file = os.path.join(cache_dir, f"{video_name}.npz")
        video_path = os.path.join(video_dir, filename)

        print(f"\n[{i}/{total}] {filename}")

        # Load existing cache
        if not os.path.exists(cache_file):
            print(f"  ⚠ No cache found — skipping (run main training first)")
            skipped += 1
            continue

        try:
            data = np.load(cache_file, allow_pickle=True)
            existing_features: Dict = data["features"].item()

            # Check if already migrated
            already_done = any(k.startswith("dyn_") for k in existing_features)
            if already_done and not force:
                print(f"  ✔ Already has dynamics features — skipping (use --force to redo)")
                skipped += 1
                continue

            # Extract dynamics
            print(f"  ➡ Extracting facial dynamics...")
            per_frame = extract_dynamics_only(video_path, analyzer, face_detector)

            if not per_frame:
                print(f"  ⚠ No dynamics extracted")
                errors += 1
                continue

            new_dyn = aggregate(per_frame)
            from facial_dynamics_analyzer import FacialDynamicsAnalyzer as FDA
            _a = FDA()
            temporal = _a.compute_temporal_features(per_frame)
            temporal_prefixed = {f"temporal_{k}": v for k, v in temporal.items()}

            # Merge into existing
            existing_features.update(new_dyn)
            existing_features.update(temporal_prefixed)

            # Save back
            np.savez_compressed(cache_file, features=existing_features)
            print(f"  ✅ Updated cache with {len(new_dyn)} dynamics features")
            updated += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1

    print(f"\n─────────────────────────────────────────")
    print(f"Migration complete: {updated} updated, {skipped} skipped, {errors} errors")
    return updated, skipped, errors


def main():
    parser = argparse.ArgumentParser(description="Migrate cached features to include facial dynamics")
    parser.add_argument("--real-dir", required=True, help="Real videos directory")
    parser.add_argument("--fake-dir", required=True, help="Fake videos directory")
    parser.add_argument("--cache-dir", default="features", help="Features cache directory")
    parser.add_argument("--force", action="store_true", help="Re-extract even if already migrated")
    args = parser.parse_args()

    print("🔄 Facial Dynamics Migration Tool")
    print("=" * 50)

    migrate_directory(args.real_dir, args.cache_dir, args.force)
    migrate_directory(args.fake_dir, args.cache_dir, args.force)

    print("\n✅ Migration complete!")
    print("\nNext step: retrain the model with enriched features:")
    print(f"  python main.py --mode train --real-dir {args.real_dir} --fake-dir {args.fake_dir} --model-type gradient_boosting")


if __name__ == "__main__":
    main()