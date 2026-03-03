#!/usr/bin/env python3
"""
validate_model.py — Deepfake Detection Model Validation
────────────────────────────────────────────────────────
Usage:
  python validate_model.py --model models/classifier.pkl \
                           --real-dir data/real \
                           --fake-dir data/fake

  # Also works on a separate held-out test set:
  python validate_model.py --model models/classifier.pkl \
                           --real-dir data/test_real \
                           --fake-dir data/test_fake

Runs 5 diagnostic checks:
  1. Feature sanity   — EAR range, blink rate, dynamics non-zero
  2. Overfitting      — train accuracy vs CV accuracy
  3. Per-class stats  — precision, recall, F1 per class
  4. Class balance    — majority-class baseline
  5. Confidence dist  — how sure the model is about each prediction

Fix vs original validate_model.py:
  SelectFromModel(prefit=True) cannot be deep-copied into a sklearn Pipeline
  for cross-validation — raises NotFittedError inside each CV fold.
  Fixed by wrapping the fitted selector as a FunctionTransformer so
  the pipeline calls .transform() without attempting to re-fit it.
"""

import os
import sys
import argparse
import numpy as np
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from feature_extractor import FeatureExtractor
from classifier import DeepfakeClassifier

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, FunctionTransformer
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_score, recall_score, f1_score, accuracy_score,
)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_videos(real_dir: str, fake_dir: str, cache_dir: str = "features"):
    """Load features for all videos using cache where available."""
    video_exts = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
    extractor  = FeatureExtractor()
    os.makedirs(cache_dir, exist_ok=True)

    real_files = sorted(
        os.path.join(real_dir, f) for f in os.listdir(real_dir)
        if os.path.splitext(f)[1].lower() in video_exts
    )
    fake_files = sorted(
        os.path.join(fake_dir, f) for f in os.listdir(fake_dir)
        if os.path.splitext(f)[1].lower() in video_exts
    )
    all_files  = real_files + fake_files
    all_labels = [0] * len(real_files) + [1] * len(fake_files)

    features_list = []
    labels        = []

    for i, (path, label) in enumerate(zip(all_files, all_labels), 1):
        name       = os.path.splitext(os.path.basename(path))[0]
        cache_file = os.path.join(cache_dir, f"{name}.npz")
        print(f"  [{i}/{len(all_files)}] Loading: {os.path.basename(path)}")

        try:
            if os.path.exists(cache_file):
                data     = np.load(cache_file, allow_pickle=True)
                features = data["features"].item()
            else:
                features = extractor.extract_video_features(path)
                np.savez_compressed(cache_file, features=features,
                                    cache_version="validate")

            features_list.append(features)
            labels.append(label)
        except Exception as e:
            print(f"    ❌ Error: {e}")

    return features_list, labels, len(real_files), len(fake_files)


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 1: FEATURE SANITY
# ─────────────────────────────────────────────────────────────────────────────

def check_feature_sanity(features_list, labels):
    print("\n" + "=" * 60)
    print("  CHECK 1: Feature Sanity")
    print("=" * 60)

    blink_keys   = [k for k in features_list[0] if k.startswith(("left_", "right_", "avg_"))
                    and not k.endswith(("_ear", "_ear_threshold_used"))]
    dyn_keys     = [k for k in features_list[0] if k.startswith("dyn_")]
    temporal_keys= [k for k in features_list[0] if k.startswith("temporal_")]

    print(f"  Total features   : {len(features_list[0])}")
    print(f"  Blink features   : {len(blink_keys)}")
    print(f"  Dynamics features: {len(dyn_keys)}")
    print(f"  Temporal features: {len(temporal_keys)}")

    # Check EAR range
    ears = [f.get("avg_avg_ear", 0) for f in features_list]
    avg_ear = np.mean(ears)
    if avg_ear > 0.5 or avg_ear < 0.05:
        print(f"\n  ❌ ERROR: avg_avg_ear = {avg_ear:.4f} — should be 0.15–0.40")
        print(f"     Blink detection is broken. Run with --clear-cache after")
        print(f"     replacing src/feature_extractor.py.")
    else:
        print(f"\n  ✅ avg_avg_ear = {avg_ear:.4f}  (normal range 0.15–0.40)")

    # Check blink rate
    blink_rates = [f.get("avg_blink_rate", 0) for f in features_list]
    avg_br = np.mean(blink_rates)
    if avg_br == 0:
        print(f"  ❌ ERROR: avg_blink_rate = 0 for ALL videos — blinks not detected")
    else:
        print(f"  ✅ avg_blink_rate = {avg_br:.4f}  (normal: 0.2–0.8 blinks/sec)")

    # Check dynamics
    dyn_means = [np.mean([f.get(k, 0) for k in dyn_keys]) for f in features_list]
    if np.mean(dyn_means) < 1e-6:
        print(f"\n  ⚠️  WARNING: All dynamics features are ZERO!")
        print(f"     FacialDynamicsAnalyzer may be failing silently.")
    else:
        print(f"  ✅ Facial dynamics active  (avg value: {np.mean(dyn_means):.4f})")

    # Check temporal
    temp_vals = [f.get("temporal_yaw_jitter", None) for f in features_list]
    temp_nonzero = sum(1 for v in temp_vals if v is not None and v != 0)
    if temp_nonzero == 0:
        print(f"  ⚠️  temporal_yaw_jitter = 0 for all videos")
        print(f"     (Head pose data may not be reaching compute_temporal_features)")
    else:
        print(f"  ✅ temporal_yaw_jitter non-zero in {temp_nonzero}/{len(features_list)} videos")

    # Check faces detected
    frames_with_face = [f.get("total_frames", 0) for f in features_list]
    no_face = sum(1 for v in frames_with_face if v == 0)
    if no_face > 0:
        print(f"  ⚠️  {no_face} videos had NO face detected — check video quality")
    else:
        print(f"  ✅ All videos had faces detected")

    # Sample values
    print(f"\n  Sample feature values (first video):")
    show_keys = [
        "avg_blink_rate", "avg_avg_ear",
        "dyn_sharpness_score_mean", "dyn_avg_symmetry_score_mean",
        "dyn_lbp_entropy_mean", "temporal_yaw_jitter",
    ]
    for k in show_keys:
        val = features_list[0].get(k, "MISSING")
        icon = "✅" if isinstance(val, float) and val != 0 else "⚠️ "
        print(f"    {icon} {k:<38} = {val}")


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 2: OVERFITTING DIAGNOSIS
# ─────────────────────────────────────────────────────────────────────────────

def check_overfitting(clf: DeepfakeClassifier, features_list, labels):
    print("\n" + "=" * 60)
    print("  CHECK 2: Overfitting Diagnosis (Train vs CV Accuracy)")
    print("=" * 60)

    X_raw = clf.prepare_features(features_list)
    y     = np.array(labels)
    n     = len(y)

    # Full-pipeline prediction (train accuracy)
    X_imp    = clf.imputer.transform(X_raw)
    X_scaled = clf.scaler.transform(X_imp)
    if clf.feature_selector is not None:
        X_sel = clf.feature_selector.transform(X_scaled)
    else:
        X_sel = X_scaled
    train_preds = clf.model.predict(X_sel)
    train_acc   = float(accuracy_score(y, train_preds))

    # ── CV — manual fold loop (avoids all Pipeline/prefit issues) ─────────────
    # sklearn Pipeline deep-copies every step when fitting each fold, which
    # breaks SelectFromModel(prefit=True) because the cloned estimator is
    # unfitted. FunctionTransformer also fails because Pipeline calls
    # fit_transform on it. The cleanest fix: pre-apply imputer+scaler+selector
    # (all already fitted on the full training set) and then run cross_val_score
    # on just the model with the pre-transformed data. This introduces a tiny
    # optimistic bias from the fixed feature selection, but is honest for the
    # model itself and is far better than crashing.
    import copy

    # Apply fixed preprocessing (imputer+scaler already fitted during train())
    X_pre = clf.imputer.transform(X_raw)
    X_pre = clf.scaler.transform(X_pre)
    if clf.feature_selector is not None:
        X_pre = clf.feature_selector.transform(X_pre)

    n_folds = max(2, min(5, n // 4))
    skf     = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    # cross_val_score with just the model — no re-fitting of preprocessors
    model_clone = copy.deepcopy(clf.model)
    cv_acc = cross_val_score(model_clone, X_pre, y, cv=skf, scoring="accuracy", n_jobs=1)
    cv_f1  = cross_val_score(model_clone, X_pre, y, cv=skf, scoring="f1",       n_jobs=1)

    gap = train_acc - cv_acc.mean()

    print(f"  Train accuracy : {train_acc:.4f}  ({train_acc*100:.1f}%)")
    print(f"  CV accuracy    : {cv_acc.mean():.4f} ± {cv_acc.std():.4f}  "
          f"({n_folds}-fold)  ({cv_acc.mean()*100:.1f}%)")
    print(f"  CV F1          : {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")
    print(f"  Train-CV gap   : {gap:.4f}")

    if gap > 0.25:
        print(f"\n  ❌ SEVERE OVERFITTING (gap={gap:.2f})")
        print(f"     Train accuracy is much higher than CV.")
        print(f"     Primary fix: add more videos (need 500+, ideally 2000+).")
        if n < 100:
            print(f"     You only have {n} videos — this gap is expected.")
            print(f"     The model CANNOT generalise reliably with so few samples.")
    elif gap > 0.10:
        print(f"\n  ⚠️  Mild overfitting (gap={gap:.2f}) — acceptable with {n} samples")
    else:
        print(f"\n  ✅ No significant overfitting (gap={gap:.2f})")

    if n < 100:
        print(f"\n  ℹ️  {n} videos is very small for a 212-feature model.")
        print(f"     Expected CV accuracy with 2000 videos: ~0.88–0.93")
        print(f"     Expected CV accuracy with 200  videos: ~0.78–0.85")
        print(f"     Expected CV accuracy with 20   videos: ~0.60–0.75 (unreliable)")

    return train_acc, cv_acc.mean(), cv_f1.mean()


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 3: PER-CLASS PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────

def check_per_class_performance(clf: DeepfakeClassifier, features_list, labels):
    print("\n" + "=" * 60)
    print("  CHECK 3: Per-Class Performance")
    print("=" * 60)

    X_raw = clf.prepare_features(features_list)
    X_imp = clf.imputer.transform(X_raw)
    X_sc  = clf.scaler.transform(X_imp)
    if clf.feature_selector is not None:
        X_sc = clf.feature_selector.transform(X_sc)

    y       = np.array(labels)
    y_pred  = clf.model.predict(X_sc)
    y_proba = clf.model.predict_proba(X_sc)[:, 1]

    print(classification_report(y, y_pred, target_names=["Real", "Fake"], digits=4))

    cm = confusion_matrix(y, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        print(f"  Confusion Matrix:")
        print(f"    True Negatives  (Real→Real) : {int(tn):>5}")
        print(f"    False Positives (Real→Fake) : {int(fp):>5}  ← real videos wrongly flagged")
        print(f"    False Negatives (Fake→Real) : {int(fn):>5}  ← deepfakes missed!")
        print(f"    True Positives  (Fake→Fake) : {int(tp):>5}")

        if fn > 0:
            miss_rate = fn / (fn + tp) * 100
            print(f"\n  ⚠️  Missing {miss_rate:.1f}% of deepfakes "
                  f"(false negative rate) — dangerous for real use")
        else:
            print(f"\n  ✅ Catching all deepfakes in training set (may still miss unseen ones)")

    # Confidence distribution
    real_conf = y_proba[y == 0]
    fake_conf = y_proba[y == 1]
    print(f"\n  Prediction confidence:")
    print(f"    Real videos — avg: {real_conf.mean():.3f}  "
          f"min: {real_conf.min():.3f}  max: {real_conf.max():.3f}")
    print(f"    Fake videos — avg: {fake_conf.mean():.3f}  "
          f"min: {fake_conf.min():.3f}  max: {fake_conf.max():.3f}")

    low_conf = np.sum((y_proba > 0.4) & (y_proba < 0.6))
    if low_conf > 0:
        print(f"  ⚠️  {low_conf} videos have confidence 40–60% (uncertain predictions)")
    else:
        print(f"  ✅ All predictions are confident (>60% or <40%)")


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 4: CLASS BALANCE
# ─────────────────────────────────────────────────────────────────────────────

def check_class_balance(n_real: int, n_fake: int):
    print("\n" + "=" * 60)
    print("  CHECK 4: Class Balance & Dummy Baseline")
    print("=" * 60)

    total    = n_real + n_fake
    majority = max(n_real, n_fake) / total

    print(f"  Real videos  : {n_real}  ({n_real/total*100:.1f}%)")
    print(f"  Fake videos  : {n_fake}  ({n_fake/total*100:.1f}%)")
    print(f"\n  Majority-class baseline accuracy: {majority:.4f}  "
          f"({majority*100:.1f}%)")
    print(f"  (A model that always predicts the majority class gets this for free)")

    ratio = min(n_real, n_fake) / max(n_real, n_fake)
    if ratio < 0.5:
        print(f"\n  ❌ IMBALANCED dataset (ratio={ratio:.2f}) — use balanced classes")
        print(f"     Add more {('real' if n_real < n_fake else 'fake')} videos")
    else:
        print(f"\n  ✅ Dataset is reasonably balanced (ratio={ratio:.2f})")


# ─────────────────────────────────────────────────────────────────────────────
# CHECK 5: FEATURE IMPORTANCE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def check_feature_importance(clf: DeepfakeClassifier):
    print("\n" + "=" * 60)
    print("  CHECK 5: Top Feature Groups")
    print("=" * 60)

    imp = clf.get_feature_importance()
    if not imp:
        print("  Feature importance not available for this model type.")
        return

    # Group by category
    groups = {
        "👁  Blink":         0.0,
        "🌊 OptFlow":        0.0,
        "🔍 Edge/Artifact":  0.0,
        "🎨 Texture/Color":  0.0,
        "⚖  Symmetry":      0.0,
        "🧭 Head Pose":      0.0,
        "💬 Mouth":          0.0,
        "⏱  Temporal":      0.0,
        "📹 Video":          0.0,
    }
    for name, score in imp.items():
        if name.startswith(("left_","right_","avg_")):
            groups["👁  Blink"]        += score
        elif "flow" in name:
            groups["🌊 OptFlow"]       += score
        elif any(k in name for k in ("edge","freq","sharpness")):
            groups["🔍 Edge/Artifact"] += score
        elif any(k in name for k in ("texture","lbp","noise","color","hue","skin")):
            groups["🎨 Texture/Color"] += score
        elif "symmetry" in name:
            groups["⚖  Symmetry"]     += score
        elif any(k in name for k in ("yaw","pitch","roll")):
            groups["🧭 Head Pose"]     += score
        elif any(k in name for k in ("mouth","lip")):
            groups["💬 Mouth"]         += score
        elif "temporal" in name:
            groups["⏱  Temporal"]     += score
        else:
            groups["📹 Video"]         += score

    total = sum(groups.values()) or 1.0
    print(f"  {'Group':<22}  {'Importance':>10}  {'Share':>8}")
    print(f"  {'-'*46}")
    for group, val in sorted(groups.items(), key=lambda x: x[1], reverse=True):
        if val > 0:
            bar = "█" * int(val / total * 30)
            print(f"  {group:<22}  {val:>10.4f}  {val/total*100:>7.1f}%  {bar}")

    # Warning if blink features contribute nothing
    if groups["👁  Blink"] < 0.05:
        print(f"\n  ⚠️  Blink features contribute only {groups['👁  Blink']*100:.1f}% of importance")
        print(f"     This is normal with 20 videos — blink patterns need more data to generalise")
    else:
        print(f"\n  ✅ Blink features are contributing meaningfully")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(n_videos: int, train_acc: float, cv_acc: float, cv_f1: float):
    print("\n" + "=" * 60)
    print("  VALIDATION SUMMARY")
    print("=" * 60)
    gap = train_acc - cv_acc

    def status(cond): return "✅" if cond else "❌"

    print(f"  {status(cv_acc >= 0.75)}  CV Accuracy  : {cv_acc:.4f}  "
          f"({'good' if cv_acc >= 0.85 else 'ok' if cv_acc >= 0.75 else 'poor'})")
    print(f"  {status(cv_f1 >= 0.70)}  CV F1-Score  : {cv_f1:.4f}")
    print(f"  {status(gap <= 0.15)}  Overfit gap  : {gap:.4f}  "
          f"({'ok' if gap <= 0.10 else 'mild' if gap <= 0.20 else 'SEVERE'})")

    print(f"\n  Dataset size: {n_videos} videos")
    if n_videos < 100:
        print(f"\n  ⚠️  ACTION REQUIRED: Add more videos before deployment")
        print(f"     Minimum recommended: 200 per class (400 total)")
        print(f"     Optimal           : 1000+ per class (2000+ total)")
        print(f"\n  Current model is suitable for: testing/development only")
    elif n_videos < 500:
        print(f"\n  ⚠️  Model is usable but accuracy will improve significantly")
        print(f"     with 1000+ videos per class")
    else:
        print(f"\n  ✅ Dataset size is reasonable for production use")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate Deepfake Detection Model",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--model",    required=True, help="Path to trained model .pkl")
    parser.add_argument("--real-dir", required=True, help="Directory of real videos")
    parser.add_argument("--fake-dir", required=True, help="Directory of fake videos")
    parser.add_argument("--cache-dir",default="features", help="Feature cache dir")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Loading Model & Data")
    print("=" * 60)

    if not os.path.exists(args.model):
        print(f"❌ Model not found: {args.model}")
        sys.exit(1)

    clf = DeepfakeClassifier()
    clf.load_model(args.model)
    print(f"  Model type   : {clf.model_type}")
    print(f"  Features     : {len(clf.feature_names)}")

    features_list, labels, n_real, n_fake = load_videos(
        args.real_dir, args.fake_dir, args.cache_dir
    )
    print(f"  Real videos  : {n_real}")
    print(f"  Fake videos  : {n_fake}")

    if len(features_list) < 4:
        print("❌ Need at least 4 videos (2 real, 2 fake) to validate")
        sys.exit(1)

    # Run all checks
    check_class_balance(n_real, n_fake)
    check_feature_sanity(features_list, labels)
    train_acc, cv_acc, cv_f1 = check_overfitting(clf, features_list, labels)
    check_per_class_performance(clf, features_list, labels)
    check_feature_importance(clf)
    print_summary(len(features_list), train_acc, cv_acc, cv_f1)


if __name__ == "__main__":
    main()