# #!/usr/bin/env python3
# """
# Fixed Training script for deepfake detection model
# """

# import os
# import sys
# import argparse
# import json
# import time
# from typing import List, Dict, Tuple
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

# # Add the project root to Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from src.feature_extractor import FeatureExtractor
# from src.classifier import DeepfakeClassifier
# from utils.visualization import plot_confusion_matrix, plot_feature_importance, plot_roc_curve
# import warnings
# warnings.filterwarnings('ignore')

# def validate_dataset(real_dir: str, fake_dir: str) -> Tuple[List[str], List[str]]:
#     """
#     Validate dataset directories and get video file lists
#     """
#     print("🔍 Validating dataset...")
    
#     # Check directories exist
#     if not os.path.exists(real_dir):
#         raise FileNotFoundError(f"Real videos directory not found: {real_dir}")
    
#     if not os.path.exists(fake_dir):
#         raise FileNotFoundError(f"Fake videos directory not found: {fake_dir}")
    
#     # Get video files
#     video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    
#     real_videos = []
#     for file in os.listdir(real_dir):
#         if any(file.lower().endswith(ext) for ext in video_extensions):
#             real_videos.append(os.path.join(real_dir, file))
    
#     fake_videos = []
#     for file in os.listdir(fake_dir):
#         if any(file.lower().endswith(ext) for ext in video_extensions):
#             fake_videos.append(os.path.join(fake_dir, file))
    
#     print(f"📊 Dataset Summary:")
#     print(f"  • Real videos: {len(real_videos)}")
#     print(f"  • Fake videos: {len(fake_videos)}")
#     print(f"  • Total videos: {len(real_videos) + len(fake_videos)}")
    
#     if len(real_videos) == 0:
#         raise ValueError("No real videos found! Please add video files to the real_videos directory.")
    
#     if len(fake_videos) == 0:
#         raise ValueError("No fake videos found! Please add video files to the fake_videos directory.")
    
#     if len(real_videos) < 2 or len(fake_videos) < 2:
#         print("⚠️  Warning: Very few videos detected. For better accuracy, use at least 10-20 videos per class.")
    
#     return real_videos, fake_videos

# def extract_features_from_videos(video_paths: List[str], labels: List[int]) -> Tuple[List[Dict], List[int]]:
#     """
#     Extract features from all videos
#     """
#     print("🔧 Extracting features from videos...")
    
#     extractor = FeatureExtractor()
#     features_list = []
#     valid_labels = []
#     failed_videos = []
    
#     total_videos = len(video_paths)
    
#     for i, (video_path, label) in enumerate(zip(video_paths, labels), 1):
#         try:
#             print(f"[{i}/{total_videos}] Processing: {os.path.basename(video_path)}")
            
#             # Extract features
#             start_time = time.time()
#             features = extractor.extract_video_features(video_path)
#             processing_time = time.time() - start_time
            
#             # Check if features are valid
#             if features.get('total_frames', 0) == 0:
#                 print(f"  ⚠️  Skipping {os.path.basename(video_path)}: No valid frames found")
#                 failed_videos.append(video_path)
#                 continue
            
#             features_list.append(features)
#             valid_labels.append(label)
            
#             print(f"  ✅ Success ({processing_time:.2f}s) - Frames: {features.get('total_frames', 0)}, "
#                   f"Duration: {features.get('video_duration', 0):.2f}s")
            
#         except Exception as e:
#             print(f"  ❌ Error processing {os.path.basename(video_path)}: {e}")
#             failed_videos.append(video_path)
#             continue
    
#     print(f"\n📈 Feature Extraction Summary:")
#     print(f"  • Successfully processed: {len(features_list)} videos")
#     print(f"  • Failed: {len(failed_videos)} videos")
    
#     if failed_videos:
#         print(f"  • Failed videos: {[os.path.basename(f) for f in failed_videos]}")
    
#     if len(features_list) == 0:
#         raise ValueError("No features extracted! Please check your video files.")
    
#     return features_list, valid_labels

# def analyze_features(features_list: List[Dict], labels: List[int]) -> Dict:
#     """
#     Analyze extracted features
#     """
#     print("📊 Analyzing extracted features...")
    
#     # Convert to DataFrame
#     df = pd.DataFrame(features_list)
#     df['label'] = labels
    
#     # Basic statistics
#     real_features = df[df['label'] == 0]
#     fake_features = df[df['label'] == 1]
    
#     analysis = {
#         'total_samples': len(df),
#         'real_samples': len(real_features),
#         'fake_samples': len(fake_features),
#         'feature_count': len(df.columns) - 1,  # Exclude label column
#         'feature_names': [col for col in df.columns if col != 'label']
#     }
    
#     # Key feature comparisons
#     key_features = ['avg_blink_rate', 'avg_avg_blink_duration', 'avg_avg_ear', 'video_duration']
    
#     print(f"📋 Feature Analysis:")
#     print(f"  • Total features extracted: {analysis['feature_count']}")
#     print(f"  • Real videos: {analysis['real_samples']}")
#     print(f"  • Fake videos: {analysis['fake_samples']}")
    
#     print(f"\n🔍 Key Feature Comparison (Real vs Fake):")
#     for feature in key_features:
#         if feature in df.columns:
#             real_mean = real_features[feature].mean()
#             fake_mean = fake_features[feature].mean()
#             real_std = real_features[feature].std()
#             fake_std = fake_features[feature].std()
            
#             print(f"  • {feature}:")
#             print(f"    - Real: {real_mean:.6f} ± {real_std:.6f}")
#             print(f"    - Fake: {fake_mean:.6f} ± {fake_std:.6f}")
#             print(f"    - Difference: {abs(real_mean - fake_mean):.6f}")
    
#     return analysis

# def train_and_evaluate_model(features_list: List[Dict], labels: List[int], 
#                             model_type: str = 'random_forest',
#                             save_path: str = 'models/classifier.pkl') -> Dict:
#     """
#     Train and evaluate the deepfake detection model
#     """
#     print(f"🤖 Training {model_type} model...")
    
#     # Initialize classifier
#     classifier = DeepfakeClassifier(model_type=model_type)
    
#     # Train model
#     start_time = time.time()
#     results = classifier.train(features_list, labels)
#     training_time = time.time() - start_time
    
#     # Save model
#     os.makedirs(os.path.dirname(save_path), exist_ok=True)
#     classifier.save_model(save_path)
    
#     # Additional evaluation metrics
#     try:
#         X = classifier.prepare_features(features_list)
#         X_scaled = classifier.scaler.transform(X)
#         y_pred_proba = classifier.model.predict_proba(X_scaled)[:, 1]
#         auc_score = roc_auc_score(labels, y_pred_proba)
#         results['auc_score'] = auc_score
#     except Exception as e:
#         print(f"Warning: Could not calculate AUC score: {e}")
#         results['auc_score'] = 0.0
    
#     results['training_time'] = training_time
#     results['model_type'] = model_type
#     results['model_path'] = save_path
    
#     return results

# def save_training_report(results: Dict, analysis: Dict, output_file: str = 'training_report.json'):
#     """
#     Save comprehensive training report
#     """
#     report = {
#         'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
#         'dataset_analysis': analysis,
#         'training_results': results,
#         'model_info': {
#             'type': results.get('model_type', 'unknown'),
#             'path': results.get('model_path', ''),
#             'training_time': results.get('training_time', 0)
#         }
#     }
    
#     with open(output_file, 'w') as f:
#         json.dump(report, f, indent=2)
    
#     print(f"📄 Training report saved: {output_file}")

# def plot_training_results(results: Dict, features_list: List[Dict], labels: List[int]):
#     """
#     Create visualizations for training results
#     """
#     try:
#         print("📈 Creating visualizations...")
        
#         # Confusion Matrix
#         cm = np.array(results['confusion_matrix'])
#         plot_confusion_matrix(cm, ['Real', 'Fake'], 'training_confusion_matrix.png')
        
#         # Feature Importance (if available)
#         if results.get('model_type') == 'random_forest':
#             try:
#                 classifier = DeepfakeClassifier(model_type='random_forest')
#                 classifier.load_model(results.get('model_path', 'models/classifier.pkl'))
#                 importance = classifier.get_feature_importance()
#                 if importance:
#                     plot_feature_importance(importance, top_n=15, save_path='feature_importance.png')
#             except Exception as e:
#                 print(f"Could not plot feature importance: {e}")
        
#         # ROC Curve (if AUC available)
#         if results.get('auc_score', 0) > 0:
#             try:
#                 classifier = DeepfakeClassifier()
#                 classifier.load_model(results.get('model_path', 'models/classifier.pkl'))
#                 X = classifier.prepare_features(features_list)
#                 X_scaled = classifier.scaler.transform(X)
#                 y_pred_proba = classifier.model.predict_proba(X_scaled)[:, 1]
                
#                 fpr, tpr, _ = roc_curve(labels, y_pred_proba)
#                 plot_roc_curve(fpr, tpr, results['auc_score'], 'roc_curve.png')
#             except Exception as e:
#                 print(f"Could not plot ROC curve: {e}")
        
#         print("✅ Visualizations saved!")
        
#     except Exception as e:
#         print(f"⚠️  Error creating visualizations: {e}")

# def main():
#     parser = argparse.ArgumentParser(description='Train Deepfake Detection Model')
#     parser.add_argument('--real-dir', type=str, required=True,
#                        help='Directory containing real videos')
#     parser.add_argument('--fake-dir', type=str, required=True,
#                        help='Directory containing fake videos')
#     parser.add_argument('--model-path', type=str, default='models/classifier.pkl',
#                        help='Path to save the trained model')
#     parser.add_argument('--model-type', type=str, default='random_forest',
#                        choices=['random_forest', 'svm', 'logistic_regression'],
#                        help='Type of classifier to use')
#     parser.add_argument('--no-visualizations', action='store_true',
#                        help='Skip creating visualizations')
#     parser.add_argument('--output-report', type=str, default='training_report.json',
#                        help='Path to save training report')
    
#     args = parser.parse_args()
    
#     try:
#         print("🚀 Starting Deepfake Detection Model Training")
#         print("=" * 60)
        
#         # Step 1: Validate dataset
#         real_videos, fake_videos = validate_dataset(args.real_dir, args.fake_dir)
        
#         # Step 2: Prepare data
#         all_videos = real_videos + fake_videos
#         all_labels = [0] * len(real_videos) + [1] * len(fake_videos)  # 0=Real, 1=Fake
        
#         # Step 3: Extract features
#         features_list, valid_labels = extract_features_from_videos(all_videos, all_labels)
        
#         if len(features_list) < 2:
#             print("❌ Error: Need at least 2 videos for training")
#             sys.exit(1)
        
#         # Check if we have both classes
#         unique_labels = set(valid_labels)
#         if len(unique_labels) < 2:
#             print("❌ Error: Need videos from both classes (real and fake)")
#             sys.exit(1)
        
#         # Step 4: Analyze features
#         analysis = analyze_features(features_list, valid_labels)
        
#         # Step 5: Train model
#         results = train_and_evaluate_model(
#             features_list, valid_labels, args.model_type, args.model_path
#         )
        
#         # Step 6: Save report
#         save_training_report(results, analysis, args.output_report)
        
#         # Step 7: Create visualizations
#         if not args.no_visualizations:
#             plot_training_results(results, features_list, valid_labels)
        
#         # Final results
#         print("\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
#         print("=" * 60)
#         print(f"🎯 Model Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
#         print(f"📊 Cross-validation: {results['cv_mean']:.4f} ± {results['cv_std']:.4f}")
#         if results.get('auc_score', 0) > 0:
#             print(f"📈 AUC Score: {results['auc_score']:.4f}")
#         print(f"⏱️  Training Time: {results['training_time']:.2f} seconds")
#         print(f"💾 Model saved: {args.model_path}")
#         print(f"📄 Report saved: {args.output_report}")
        
#         print(f"\n🔥 Ready to predict! Use:")
#         print(f"   python predict.py --video your_video.mp4 --model {args.model_path}")
        
#     except Exception as e:
#         print(f"❌ Training failed: {e}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

#new update
#!/usr/bin/env python3
"""
train.py  —  Deepfake Detection: Training Script
─────────────────────────────────────────────────
Usage:
  python train.py --real-dir data/real --fake-dir data/fake
  python train.py --real-dir data/real --fake-dir data/fake --model-type gradient_boosting
  python train.py --real-dir data/real --fake-dir data/fake --model-type xgboost

Fixes vs original train.py:
  1. Imports used "from src.X" with sys.path.append — inconsistent; unified to sys.path.insert + plain imports
  2. "from utils.visualization import ..." — that module may not exist, wrapped in try/except with graceful fallback
  3. model-type choices were ['random_forest','svm','logistic_regression'] — updated to match new classifier.py
  4. train_and_evaluate_model called classifier.scaler.transform(X) directly — but scaler also needs imputer first; fixed
  5. confusion_matrix was referenced in results dict but classifier.train() never returns it — fixed by computing it here
  6. plot_training_results referenced results['confusion_matrix'] as np.array but it wasn't stored — fixed
  7. os.makedirs(os.path.dirname(save_path)) crashes when dirname is '' — added guard
"""

import os
import sys
import argparse
import json
import time
import warnings
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
# Only add SRC_DIR — adding BASE_DIR causes circular imports because Python
# finds modules by the same name at project root before finding them in src/
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from feature_extractor import FeatureExtractor
from classifier import DeepfakeClassifier

# Optional visualisation helpers — graceful fallback if utils/ doesn't exist
try:
    from utils.visualization import plot_confusion_matrix, plot_feature_importance, plot_roc_curve
    VIZ_AVAILABLE = True
except ImportError:
    VIZ_AVAILABLE = False

# sklearn metrics used for the evaluation block
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    confusion_matrix as sk_confusion_matrix,
    classification_report,
)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — VALIDATE DATASET
# ─────────────────────────────────────────────────────────────────────────────

def validate_dataset(real_dir: str, fake_dir: str) -> Tuple[List[str], List[str]]:
    """Check directories exist and list all video files."""
    print("🔍 Validating dataset...")

    for label, path in [("real", real_dir), ("fake", fake_dir)]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{label.capitalize()} videos directory not found: {path}")

    video_exts = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"}

    real_videos = sorted(
        os.path.join(real_dir, f) for f in os.listdir(real_dir)
        if os.path.splitext(f)[1].lower() in video_exts
    )
    fake_videos = sorted(
        os.path.join(fake_dir, f) for f in os.listdir(fake_dir)
        if os.path.splitext(f)[1].lower() in video_exts
    )

    print(f"\n📊 Dataset Summary:")
    print(f"   Real videos : {len(real_videos)}")
    print(f"   Fake videos : {len(fake_videos)}")
    print(f"   Total       : {len(real_videos) + len(fake_videos)}")

    if len(real_videos) == 0:
        raise ValueError("No real videos found in: " + real_dir)
    if len(fake_videos) == 0:
        raise ValueError("No fake videos found in: " + fake_dir)
    if len(real_videos) < 5 or len(fake_videos) < 5:
        print("⚠  Warning: <5 videos per class. Use at least 10-20 for reliable training.")

    return real_videos, fake_videos


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — EXTRACT FEATURES
# ─────────────────────────────────────────────────────────────────────────────

# Bump this whenever feature_extractor.py changes so old caches are auto-invalidated.
_CACHE_VERSION = "v3_ear_fixed_facial_dynamics"

def extract_features_from_videos(
    video_paths:  List[str],
    labels:       List[int],
    cache_dir:    str  = "features",
    clear_cache:  bool = False,
) -> Tuple[List[Dict], List[int]]:
    """
    Extract features from all videos with versioned .npz caching.

    Cache version: {_CACHE_VERSION}
    If a cached file was saved with a different version it is re-extracted
    automatically — no need to manually delete the features/ folder.

    clear_cache=True  → delete ALL .npz files before starting (same as
                        running:  Remove-Item -Recurse -Force features\\)
    """
    print(f"\n🔧 Extracting features  (cache_version={_CACHE_VERSION})...")
    os.makedirs(cache_dir, exist_ok=True)

    # ── Optional: wipe entire cache ───────────────────────────────
    if clear_cache:
        removed = 0
        for f in os.listdir(cache_dir):
            if f.endswith(".npz"):
                os.remove(os.path.join(cache_dir, f))
                removed += 1
        print(f"  🗑  Cleared {removed} cached file(s) from {cache_dir}/")

    extractor     = FeatureExtractor()
    features_list = []
    valid_labels  = []
    failed        = []
    total         = len(video_paths)

    for i, (video_path, label) in enumerate(zip(video_paths, labels), 1):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        cache_file = os.path.join(cache_dir, f"{video_name}.npz")
        print(f"[{i}/{total}] {os.path.basename(video_path)}")

        try:
            features = None

            # ── Try loading cache ─────────────────────────────────
            if os.path.exists(cache_file):
                try:
                    data           = np.load(cache_file, allow_pickle=True)
                    cached_version = str(data.get("cache_version", b"unknown"))
                    if cached_version == _CACHE_VERSION:
                        features = data["features"].item()
                        print(f"  ✔ Cache hit  (version OK)")
                    else:
                        print(f"  ♻  Cache stale (was {cached_version}, "
                              f"need {_CACHE_VERSION}) — re-extracting...")
                except Exception as ce:
                    print(f"  ⚠  Cache unreadable ({ce}) — re-extracting...")

            # ── Extract if not loaded from cache ──────────────────
            if features is None:
                t0       = time.time()
                features = extractor.extract_video_features(video_path)
                np.savez_compressed(
                    cache_file,
                    features      = features,
                    cache_version = _CACHE_VERSION,   # ← stamp version
                )
                elapsed = time.time() - t0
                print(f"  ➡ Extracted ({elapsed:.1f}s) — "
                      f"frames:{features.get('total_frames',0)}  "
                      f"dur:{features.get('video_duration',0):.1f}s  "
                      f"avg_ear:{features.get('avg_avg_ear',0):.4f}  "
                      f"blink_rate:{features.get('avg_blink_rate',0):.4f}")

            if features.get("total_frames", 0) == 0:
                print(f"  ⚠  Skipped — no valid frames detected")
                failed.append(video_path)
                continue

            features_list.append(features)
            valid_labels.append(label)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback; traceback.print_exc()
            failed.append(video_path)

    print(f"\n📈 Extraction Summary:")
    print(f"   Processed : {len(features_list)}")
    print(f"   Failed    : {len(failed)}")
    if failed:
        print(f"   Failed files: {[os.path.basename(f) for f in failed]}")

    if not features_list:
        raise ValueError("No features extracted. Check your video files.")

    return features_list, valid_labels


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — ANALYSE FEATURES
# ─────────────────────────────────────────────────────────────────────────────

def analyze_features(features_list: List[Dict], labels: List[int]) -> Dict:
    """Print per-class feature stats and return analysis dict."""
    print("\n📊 Analysing features...")

    df           = pd.DataFrame(features_list)
    df["label"]  = labels
    real_df      = df[df["label"] == 0]
    fake_df      = df[df["label"] == 1]

    analysis = {
        "total_samples": len(df),
        "real_samples":  len(real_df),
        "fake_samples":  len(fake_df),
        "feature_count": len(df.columns) - 1,
    }

    print(f"   Features   : {analysis['feature_count']}")
    print(f"   Real videos: {analysis['real_samples']}")
    print(f"   Fake videos: {analysis['fake_samples']}")

    key_features = [
        "avg_blink_rate", "avg_avg_blink_duration",
        "avg_avg_ear",    "video_duration",
        "dyn_sharpness_score_mean", "dyn_avg_symmetry_score_mean",
    ]

    print(f"\n🔍 Key Feature Comparison (Real vs Fake):")
    for feat in key_features:
        if feat not in df.columns:
            continue
        rm, rs = real_df[feat].mean(), real_df[feat].std()
        fm, fs = fake_df[feat].mean(), fake_df[feat].std()
        print(f"   {feat}:")
        print(f"     Real → {rm:.5f} ± {rs:.5f}")
        print(f"     Fake → {fm:.5f} ± {fs:.5f}")

    return analysis


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — TRAIN + EVALUATE
# ─────────────────────────────────────────────────────────────────────────────

def train_and_evaluate_model(
    features_list: List[Dict],
    labels: List[int],
    model_type: str = "gradient_boosting",
    save_path: str  = "models/classifier.pkl",
) -> Dict:
    """Train, evaluate, save model. Returns full results dict."""
    print(f"\n🤖 Training ({model_type})...")

    clf = DeepfakeClassifier(model_type=model_type)

    t0      = time.time()
    results = clf.train(features_list, labels)
    results["training_time"] = time.time() - t0
    results["model_type"]    = model_type
    results["model_path"]    = save_path

    # Save model
    model_dir = os.path.dirname(save_path)
    if model_dir:
        os.makedirs(model_dir, exist_ok=True)
    clf.save_model(save_path)

    # ── Additional evaluation on full training set ────────────────
    X         = clf.prepare_features(features_list)
    X_imputed = clf.imputer.transform(X)
    X_scaled  = clf.scaler.transform(X_imputed)
    if clf.feature_selector is not None:
        X_scaled = clf.feature_selector.transform(X_scaled)

    y      = np.array(labels)
    y_pred = clf.model.predict(X_scaled)
    y_prob = clf.model.predict_proba(X_scaled)[:, 1]

    # Confusion matrix stored as plain list for JSON serialisation
    cm = sk_confusion_matrix(y, y_pred)
    results["confusion_matrix"] = cm.tolist()

    # AUC
    try:
        results["auc_score"] = float(roc_auc_score(y, y_prob))
    except Exception:
        results["auc_score"] = 0.0

    # Classification report (printed only)
    print("\n📋 Classification Report:")
    print(classification_report(y, y_pred, target_names=["Real", "Fake"]))
    print(f"   AUC Score : {results['auc_score']:.4f}")
    print(f"   Train time: {results['training_time']:.1f}s")

    # Store proba for ROC plot later
    results["_y_true"] = y.tolist()
    results["_y_prob"] = y_prob.tolist()

    # Print top features
    clf.print_top_features(n=15)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — SAVE REPORT
# ─────────────────────────────────────────────────────────────────────────────

def save_training_report(results: Dict, analysis: Dict, output_file: str):
    """Write JSON training report (strips private keys starting with _)."""
    clean = {k: v for k, v in results.items() if not k.startswith("_")}
    report = {
        "timestamp":        time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_analysis": analysis,
        "training_results": clean,
    }
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n📄 Report saved: {output_file}")


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — OPTIONAL PLOTS
# ─────────────────────────────────────────────────────────────────────────────

def plot_training_results(results: Dict):
    """Create evaluation plots — only runs if utils/visualization.py exists."""
    if not VIZ_AVAILABLE:
        print("ℹ  utils/visualization.py not found — skipping plots.")
        print("   (You can still check metrics in the printed report above.)")
        return

    try:
        print("\n📈 Creating visualisation plots...")

        # Confusion matrix
        cm = np.array(results["confusion_matrix"])
        plot_confusion_matrix(cm, ["Real", "Fake"], "training_confusion_matrix.png")

        # Feature importance
        clf = DeepfakeClassifier()
        clf.load_model(results["model_path"])
        importance = clf.get_feature_importance()
        if importance:
            plot_feature_importance(importance, top_n=15, save_path="feature_importance.png")

        # ROC curve
        if results.get("auc_score", 0) > 0 and "_y_true" in results:
            fpr, tpr, _ = roc_curve(results["_y_true"], results["_y_prob"])
            plot_roc_curve(fpr, tpr, results["auc_score"], "roc_curve.png")

        print("✅ Plots saved.")
    except Exception as e:
        print(f"⚠  Could not create plots: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Train Deepfake Detection Model",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python train.py --real-dir data/real --fake-dir data/fake
  python train.py --real-dir data/real --fake-dir data/fake --model-type xgboost
  python train.py --real-dir data/real --fake-dir data/fake --no-visualizations
        """,
    )
    parser.add_argument("--real-dir",    required=True, help="Directory of real videos")
    parser.add_argument("--fake-dir",    required=True, help="Directory of fake videos")
    parser.add_argument("--model-path",  default="models/classifier.pkl",
                        help="Where to save the trained model  (default: models/classifier.pkl)")
    parser.add_argument("--cache-dir",   default="features",
                        help="Feature cache directory  (default: features/)")
    parser.add_argument(
        "--model-type",
        default="gradient_boosting",
        choices=["random_forest", "gradient_boosting", "xgboost"],  # matches classifier.py
        help="Classifier algorithm  (default: gradient_boosting)",
    )
    parser.add_argument("--no-visualizations", action="store_true",
                        help="Skip plot generation")
    parser.add_argument("--output-report", default="training_report.json",
                        help="Path for JSON training report  (default: training_report.json)")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Delete all cached .npz files before extracting. "
                             "Use this whenever feature_extractor.py changes.")

    args = parser.parse_args()

    try:
        print("\n🚀 Deepfake Detection — Training")
        print("=" * 55)

        # 1. Validate
        real_videos, fake_videos = validate_dataset(args.real_dir, args.fake_dir)

        # 2. Build combined list
        all_videos = real_videos + fake_videos
        all_labels = [0] * len(real_videos) + [1] * len(fake_videos)

        # 3. Extract / load features
        features_list, valid_labels = extract_features_from_videos(
            all_videos, all_labels, args.cache_dir,
            clear_cache=args.clear_cache,
        )

        if len(features_list) < 2:
            print("❌ Need at least 2 processable videos.")
            sys.exit(1)
        if len(set(valid_labels)) < 2:
            print("❌ Need at least 1 real AND 1 fake video.")
            sys.exit(1)

        # 4. Analyse
        analysis = analyze_features(features_list, valid_labels)

        # 5. Train + evaluate
        results = train_and_evaluate_model(
            features_list, valid_labels, args.model_type, args.model_path
        )

        # 6. Save report
        save_training_report(results, analysis, args.output_report)

        # 7. Optional plots
        if not args.no_visualizations:
            plot_training_results(results)

        # ── Final summary ────────────────────────────────────────
        print("\n🎉 TRAINING COMPLETE")
        print("=" * 55)
        print(f"   Accuracy  (train)  : {results['accuracy']:.4f}")
        print(f"   Accuracy  (CV)     : {results['cv_mean']:.4f} ± {results['cv_std']:.4f}")
        print(f"   F1        (CV)     : {results['cv_f1_mean']:.4f} ± {results['cv_f1_std']:.4f}")
        print(f"   AUC Score          : {results.get('auc_score', 0):.4f}")
        print(f"   Training time      : {results['training_time']:.1f}s")
        print(f"   Model saved        : {args.model_path}")
        print(f"\n▶  Start API server  :  python server.py")
        print(f"▶  Predict a video   :  python predict.py --video your_video.mp4")

    except Exception as e:
        import traceback
        print(f"\n❌ Training failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()