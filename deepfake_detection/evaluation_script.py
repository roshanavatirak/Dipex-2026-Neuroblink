# #!/usr/bin/env python3
# """
# Comprehensive evaluation script for deepfake detection model
# Calculates F1, Precision, Recall, Accuracy and other advanced metrics
# """

# import os
# import sys
# import argparse
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.metrics import (
#     confusion_matrix, classification_report, accuracy_score,
#     precision_score, recall_score, f1_score, roc_auc_score,
#     roc_curve, precision_recall_curve, matthews_corrcoef
# )
# from sklearn.model_selection import cross_val_score, StratifiedKFold
# import json
# from datetime import datetime

# # Add the project root to Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from src.feature_extractor import FeatureExtractor
# from src.classifier import DeepfakeClassifier

# def load_ground_truth_labels(labels_file: str) -> dict:
#     """
#     Load ground truth labels from JSON file
#     Expected format: {"video_name.mp4": 0/1, ...} where 0=real, 1=fake
#     """
#     if os.path.exists(labels_file):
#         with open(labels_file, 'r') as f:
#             return json.load(f)
#     else:
#         print(f"Warning: Labels file {labels_file} not found")
#         return {}

# def evaluate_on_dataset(model_path: str, dataset_dir: str, labels_file: str = None,
#                        save_results: bool = True, plot_results: bool = True) -> dict:
#     """
#     Comprehensive evaluation of the model on a dataset
#     """
#     print("=" * 60)
#     print("DEEPFAKE DETECTION MODEL EVALUATION")
#     print("=" * 60)
    
#     # Load model
#     print("Loading model...")
#     classifier = DeepfakeClassifier()
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"Model file not found: {model_path}")
    
#     classifier.load_model(model_path)
    
#     # Load ground truth labels if available
#     ground_truth = {}
#     if labels_file:
#         ground_truth = load_ground_truth_labels(labels_file)
    
#     # Initialize feature extractor
#     extractor = FeatureExtractor()
    
#     # Get all video files
#     video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
#     video_files = []
    
#     if os.path.isdir(dataset_dir):
#         for file in os.listdir(dataset_dir):
#             if any(file.lower().endswith(ext) for ext in video_extensions):
#                 video_files.append(os.path.join(dataset_dir, file))
#     else:
#         # Single video file
#         video_files = [dataset_dir]
    
#     if not video_files:
#         raise ValueError(f"No video files found in {dataset_dir}")
    
#     print(f"Found {len(video_files)} video files for evaluation")
    
#     # Process videos and make predictions
#     predictions = []
#     confidences = []
#     true_labels = []
#     video_names = []
#     detailed_results = []
    
#     print("\nProcessing videos...")
#     for i, video_path in enumerate(video_files, 1):
#         video_name = os.path.basename(video_path)
#         print(f"[{i}/{len(video_files)}] Processing: {video_name}")
        
#         try:
#             # Extract features
#             features = extractor.extract_video_features(video_path)
            
#             # Make prediction
#             prediction, confidence, detailed_metrics = classifier.predict(features)
            
#             predictions.append(prediction)
#             confidences.append(confidence)
#             video_names.append(video_name)
            
#             # Get ground truth if available
#             if video_name in ground_truth:
#                 true_labels.append(ground_truth[video_name])
#             elif ground_truth:
#                 print(f"Warning: No ground truth label for {video_name}")
#                 continue
            
#             # Store detailed results
#             detailed_results.append({
#                 'video_name': video_name,
#                 'prediction': prediction,
#                 'confidence': confidence,
#                 'detailed_metrics': detailed_metrics,
#                 'features': features,
#                 'true_label': ground_truth.get(video_name, -1)
#             })
            
#         except Exception as e:
#             print(f"Error processing {video_name}: {e}")
#             continue
    
#     # Calculate comprehensive evaluation metrics
#     results = {}
    
#     if true_labels and len(true_labels) == len(predictions):
#         print(f"\nCalculating metrics for {len(true_labels)} samples...")
        
#         y_true = np.array(true_labels)
#         y_pred = np.array(predictions)
#         y_conf = np.array(confidences)
        
#         # Basic metrics
#         accuracy = accuracy_score(y_true, y_pred)
#         precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
#         recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
#         f1 = f1_score(y_true, y_pred, average='binary', zero_division=0)
        
#         # Confusion matrix
#         cm = confusion_matrix(y_true, y_pred)
#         if cm.shape == (2, 2):
#             tn, fp, fn, tp = cm.ravel()
#         else:
#             tn = fp = fn = tp = 0
        
#         # Additional metrics
#         specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
#         npv = tn / (tn + fn) if (tn + fn) > 0 else 0
#         balanced_accuracy = (recall + specificity) / 2
        
#         # Matthews Correlation Coefficient
#         mcc = matthews_corrcoef(y_true, y_pred)
        
#         # ROC AUC if we have both classes
#         roc_auc = 0.5
#         if len(np.unique(y_true)) > 1:
#             try:
#                 roc_auc = roc_auc_score(y_true, y_conf)
#             except:
#                 roc_auc = 0.5
        
#         # Store results
#         results = {
#             'evaluation_summary': {
#                 'total_samples': len(y_true),
#                 'accuracy': accuracy,
#                 'precision': precision,
#                 'recall': recall,
#                 'f1_score': f1,
#                 'specificity': specificity,
#                 'balanced_accuracy': balanced_accuracy,
#                 'roc_auc': roc_auc,
#                 'mcc': mcc,
#                 'npv': npv
#             },
#             'confusion_matrix': {
#                 'true_negatives': int(tn),
#                 'false_positives': int(fp),
#                 'false_negatives': int(fn),
#                 'true_positives': int(tp)
#             },
#             'class_distribution': {
#                 'real_videos': int(np.sum(y_true == 0)),
#                 'fake_videos': int(np.sum(y_true == 1))
#             },
#             'detailed_results': detailed_results,
#             'evaluation_timestamp': datetime.now().isoformat()
#         }
        
#         # Print comprehensive results
#         print("\n" + "=" * 60)
#         print("EVALUATION RESULTS")
#         print("=" * 60)
#         print(f"Dataset: {dataset_dir}")
#         print(f"Model: {model_path}")
#         print(f"Total Samples: {len(y_true)}")
#         print(f"Real Videos: {np.sum(y_true == 0)} ({np.sum(y_true == 0)/len(y_true)*100:.1f}%)")
#         print(f"Fake Videos: {np.sum(y_true == 1)} ({np.sum(y_true == 1)/len(y_true)*100:.1f}%)")
#         print("\nPERFORMANCE METRICS:")
#         print(f"Accuracy:          {accuracy:.4f} ({accuracy*100:.2f}%)")
#         print(f"Precision:         {precision:.4f} ({precision*100:.2f}%)")
#         print(f"Recall:            {recall:.4f} ({recall*100:.2f}%)")
#         print(f"F1-Score:          {f1:.4f} ({f1*100:.2f}%)")
#         print(f"Specificity:       {specificity:.4f} ({specificity*100:.2f}%)")
#         print(f"Balanced Accuracy: {balanced_accuracy:.4f} ({balanced_accuracy*100:.2f}%)")
#         print(f"ROC-AUC:           {roc_auc:.4f}")
#         print(f"Matthews CC:       {mcc:.4f}")
#         print(f"NPV:               {npv:.4f} ({npv*100:.2f}%)")
        
#         print("\nCONFUSION MATRIX:")
#         print(f"True Negatives:  {tn:4d} (Real correctly identified)")
#         print(f"False Positives: {fp:4d} (Real misclassified as Fake)")
#         print(f"False Negatives: {fn:4d} (Fake misclassified as Real)")
#         print(f"True Positives:  {tp:4d} (Fake correctly identified)")
        
#         # Calculate and display error analysis
#         if fp > 0 or fn > 0:
#             print(f"\nERROR ANALYSIS:")
#             print(f"Type I Error Rate (False Positive): {fp/(fp+tn)*100:.2f}%")
#             print(f"Type II Error Rate (False Negative): {fn/(fn+tp)*100:.2f}%")
        
#         # Plot results if requested
#         if plot_results:
#             create_evaluation_plots(y_true, y_pred, y_conf, results)
        
#         # Cross-validation analysis
#         if len(detailed_results) >= 10:
#             print("\nCROSS-VALIDATION ANALYSIS:")
#             perform_cross_validation_analysis(detailed_results, classifier)
    
#     else:
#         print("No ground truth labels available for evaluation")
#         results = {
#             'predictions_only': {
#                 'total_samples': len(predictions),
#                 'predicted_real': int(np.sum(np.array(predictions) == 0)),
#                 'predicted_fake': int(np.sum(np.array(predictions) == 1)),
#                 'average_confidence': float(np.mean(confidences)) if confidences else 0,
#                 'confidence_std': float(np.std(confidences)) if confidences else 0
#             },
#             'detailed_results': detailed_results,
#             'evaluation_timestamp': datetime.now().isoformat()
#         }
        
#         print(f"\nPREDICTION SUMMARY (No Ground Truth):")
#         print(f"Total Videos: {len(predictions)}")
#         print(f"Predicted Real: {np.sum(np.array(predictions) == 0)}")
#         print(f"Predicted Fake: {np.sum(np.array(predictions) == 1)}")
#         print(f"Average Confidence: {np.mean(confidences):.4f}")
    
#     # Save results
#     if save_results:
#         save_evaluation_results(results, dataset_dir)
    
#     return results

# def create_evaluation_plots(y_true, y_pred, y_conf, results):
#     """Create comprehensive evaluation plots"""
#     plt.style.use('dark_background')
#     fig, axes = plt.subplots(2, 3, figsize=(18, 12))
#     fig.suptitle('Deepfake Detection Model Evaluation', fontsize=16, fontweight='bold')
    
#     # Confusion Matrix Heatmap
#     cm = confusion_matrix(y_true, y_pred)
#     sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0,0])
#     axes[0,0].set_title('Confusion Matrix')
#     axes[0,0].set_xlabel('Predicted')
#     axes[0,0].set_ylabel('Actual')
#     axes[0,0].set_xticklabels(['Real', 'Fake'])
#     axes[0,0].set_yticklabels(['Real', 'Fake'])
    
#     # ROC Curve
#     if len(np.unique(y_true)) > 1:
#         fpr, tpr, _ = roc_curve(y_true, y_conf)
#         axes[0,1].plot(fpr, tpr, color='cyan', lw=2, label=f'ROC (AUC = {results["evaluation_summary"]["roc_auc"]:.3f})')
#         axes[0,1].plot([0, 1], [0, 1], 'r--', lw=1)
#         axes[0,1].set_xlabel('False Positive Rate')
#         axes[0,1].set_ylabel('True Positive Rate')
#         axes[0,1].set_title('ROC Curve')
#         axes[0,1].legend()
#         axes[0,1].grid(True, alpha=0.3)
    
#     # Precision-Recall Curve
#     if len(np.unique(y_true)) > 1:
#         precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_conf)
#         axes[0,2].plot(recall_curve, precision_curve, color='lime', lw=2)
#         axes[0,2].set_xlabel('Recall')
#         axes[0,2].set_ylabel('Precision')
#         axes[0,2].set_title('Precision-Recall Curve')
#         axes[0,2].grid(True, alpha=0.3)
    
#     # Confidence Distribution
#     axes[1,0].hist(y_conf[y_true == 0], bins=20, alpha=0.7, label='Real', color='green', density=True)
#     axes[1,0].hist(y_conf[y_true == 1], bins=20, alpha=0.7, label='Fake', color='red', density=True)
#     axes[1,0].set_xlabel('Confidence')
#     axes[1,0].set_ylabel('Density')
#     axes[1,0].set_title('Confidence Distribution by Class')
#     axes[1,0].legend()
#     axes[1,0].grid(True, alpha=0.3)
    
#     # Metrics Bar Plot
#     metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Specificity']
#     values = [
#         results['evaluation_summary']['accuracy'],
#         results['evaluation_summary']['precision'],
#         results['evaluation_summary']['recall'],
#         results['evaluation_summary']['f1_score'],
#         results['evaluation_summary']['specificity']
#     ]
#     bars = axes[1,1].bar(metrics, values, color=['blue', 'green', 'orange', 'red', 'purple'], alpha=0.7)
#     axes[1,1].set_ylim(0, 1)
#     axes[1,1].set_title('Performance Metrics')
#     axes[1,1].set_ylabel('Score')
#     axes[1,1].tick_params(axis='x', rotation=45)
    
#     # Add value labels on bars
#     for bar, value in zip(bars, values):
#         axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
#                       f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
#     # Prediction vs True Labels Scatter
#     jitter = np.random.normal(0, 0.05, len(y_true))
#     axes[1,2].scatter(y_true + jitter, y_pred + jitter, c=y_conf, cmap='viridis', alpha=0.6)
#     axes[1,2].set_xlabel('True Labels')
#     axes[1,2].set_ylabel('Predictions')
#     axes[1,2].set_title('Predictions vs Truth (Color = Confidence)')
#     axes[1,2].set_xticks([0, 1])
#     axes[1,2].set_yticks([0, 1])
#     axes[1,2].set_xticklabels(['Real', 'Fake'])
#     axes[1,2].set_yticklabels(['Real', 'Fake'])
    
#     plt.tight_layout()
    
#     # Save plot
#     plot_path = f"evaluation_plots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
#     plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='black')
#     print(f"\nEvaluation plots saved to: {plot_path}")
    
#     plt.show()

# def perform_cross_validation_analysis(detailed_results, classifier):
#     """Perform cross-validation analysis on the results"""
#     try:
#         # Extract features and labels
#         features_list = []
#         labels = []
        
#         for result in detailed_results:
#             if result['true_label'] != -1:  # Valid ground truth
#                 features_list.append(result['features'])
#                 labels.append(result['true_label'])
        
#         if len(features_list) < 5:
#             print("Insufficient data for cross-validation")
#             return
        
#         # Prepare features for sklearn
#         X = classifier.prepare_features(features_list)
#         y = np.array(labels)
        
#         # Stratified K-Fold Cross Validation
#         skf = StratifiedKFold(n_splits=min(5, len(set(y))), shuffle=True, random_state=42)
        
#         cv_scores = {
#             'accuracy': cross_val_score(classifier.model, X, y, cv=skf, scoring='accuracy'),
#             'precision': cross_val_score(classifier.model, X, y, cv=skf, scoring='precision'),
#             'recall': cross_val_score(classifier.model, X, y, cv=skf, scoring='recall'),
#             'f1': cross_val_score(classifier.model, X, y, cv=skf, scoring='f1')
#         }
        
#         print("Cross-Validation Results:")
#         for metric, scores in cv_scores.items():
#             print(f"{metric.capitalize()}: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
    
#     except Exception as e:
#         print(f"Cross-validation analysis failed: {e}")

# def save_evaluation_results(results, dataset_dir):
#     """Save evaluation results to JSON file"""
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     dataset_name = os.path.basename(dataset_dir.rstrip('/'))
#     filename = f"evaluation_results_{dataset_name}_{timestamp}.json"
    
#     # Create a clean version for JSON serialization
#     clean_results = results.copy()
#     if 'detailed_results' in clean_results:
#         for result in clean_results['detailed_results']:
#             # Remove large feature dictionaries to keep file size manageable
#             if 'features' in result:
#                 result['features'] = {k: v for k, v in result['features'].items() 
#                                    if k in ['avg_blink_rate', 'avg_avg_ear', 'video_quality_score', 'temporal_consistency']}
    
#     with open(filename, 'w') as f:
#         json.dump(clean_results, f, indent=2, default=str)
    
#     print(f"\nDetailed results saved to: {filename}")

# def main():
#     parser = argparse.ArgumentParser(description='Comprehensive Model Evaluation')
#     parser.add_argument('--model', type=str, required=True, help='Path to trained model')
#     parser.add_argument('--dataset', type=str, required=True, help='Path to dataset directory or single video')
#     parser.add_argument('--labels', type=str, help='Path to ground truth labels JSON file')
#     parser.add_argument('--no-plots', action='store_true', help='Skip generating plots')
#     parser.add_argument('--no-save', action='store_true', help='Skip saving results')
    
#     args = parser.parse_args()
    
#     try:
#         results = evaluate_on_dataset(
#             model_path=args.model,
#             dataset_dir=args.dataset,
#             labels_file=args.labels,
#             save_results=not args.no_save,
#             plot_results=not args.no_plots
#         )
        
#         print("\nEvaluation completed successfully!")
        
#         if 'evaluation_summary' in results:
#             print(f"Final F1-Score: {results['evaluation_summary']['f1_score']:.4f}")
#             print(f"Final Accuracy: {results['evaluation_summary']['accuracy']:.4f}")
        
#     except Exception as e:
#         print(f"Evaluation failed: {e}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

#new update
#!/usr/bin/env python3
"""
evaluate.py  —  Comprehensive Model Evaluation
───────────────────────────────────────────────
Usage:
  # With ground truth labels file
  python evaluate.py --model models/classifier.pkl --dataset data/test/ --labels labels.json

  # Without labels (prediction summary only)
  python evaluate.py --model models/classifier.pkl --dataset data/test/

  # Single video
  python evaluate.py --model models/classifier.pkl --dataset path/to/video.mp4 --labels labels.json

  # Skip plots / skip saving
  python evaluate.py --model models/classifier.pkl --dataset data/test/ --no-plots --no-save

Labels JSON format:
  {"video1.mp4": 0, "video2.mp4": 1, ...}   (0 = real, 1 = fake)

Fixes vs original:
  1. classifier.predict() returns 2 values (pred, conf) — original unpacked 3; fixed
  2. import used "from src.X" with sys.path.append — unified to sys.path.insert + plain imports
  3. perform_cross_validation_analysis passed raw X (not imputed/scaled) to cross_val_score — fixed
  4. save_evaluation_results filtered features to 4 blink keys only — now saves all dyn_*/temporal_* too
  5. No facial dynamics in printed output or plots — fully added
"""

import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless-safe; use "TkAgg" if you want plt.show()
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    matthews_corrcoef,
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
for p in (BASE_DIR, SRC_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from feature_extractor import FeatureExtractor
from classifier import DeepfakeClassifier


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def load_ground_truth_labels(labels_file: str) -> Dict[str, int]:
    """
    Load ground truth labels from a JSON file.
    Expected format: {"video_name.mp4": 0, "fake_video.mp4": 1, ...}
    """
    if not os.path.exists(labels_file):
        print(f"⚠  Labels file not found: {labels_file}")
        return {}
    with open(labels_file, "r") as f:
        data = json.load(f)
    print(f"✔ Loaded {len(data)} ground-truth labels from {labels_file}")
    return data


def _get_video_files(dataset_dir: str) -> List[str]:
    exts = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
    if os.path.isfile(dataset_dir):
        return [dataset_dir]
    return sorted(
        os.path.join(dataset_dir, f)
        for f in os.listdir(dataset_dir)
        if os.path.splitext(f)[1].lower() in exts
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_on_dataset(
    model_path:   str,
    dataset_dir:  str,
    labels_file:  Optional[str] = None,
    cache_dir:    str = "features",
    save_results: bool = True,
    plot_results: bool = True,
) -> Dict:

    print("=" * 65)
    print("  DEEPFAKE DETECTION — MODEL EVALUATION")
    print("=" * 65)

    # ── Load model ────────────────────────────────────────────────
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    clf = DeepfakeClassifier()
    clf.load_model(model_path)
    print(f"✔ Model loaded: {model_path}")

    # ── Ground truth ─────────────────────────────────────────────
    ground_truth = load_ground_truth_labels(labels_file) if labels_file else {}

    # ── Video files ───────────────────────────────────────────────
    video_files = _get_video_files(dataset_dir)
    if not video_files:
        raise ValueError(f"No video files found in: {dataset_dir}")
    print(f"✔ Found {len(video_files)} video(s) for evaluation\n")

    extractor = FeatureExtractor()
    os.makedirs(cache_dir, exist_ok=True)

    # ── Process each video ────────────────────────────────────────
    predictions:    List[int]   = []
    confidences:    List[float] = []
    true_labels:    List[int]   = []
    detailed_results: List[Dict] = []

    for i, video_path in enumerate(video_files, 1):
        video_name = os.path.basename(video_path)
        print(f"[{i}/{len(video_files)}] {video_name}")

        try:
            # Load from cache or extract
            cache_file = os.path.join(cache_dir, f"{os.path.splitext(video_name)[0]}.npz")
            if os.path.exists(cache_file):
                data     = np.load(cache_file, allow_pickle=True)
                features = data["features"].item()
                print(f"  ✔ Cache hit")
            else:
                features = extractor.extract_video_features(video_path)
                np.savez_compressed(cache_file, features=features)

            # FIX 1: classifier.predict() returns (prediction, confidence) — NOT 3 values
            prediction, confidence = clf.predict(features)

            predictions.append(prediction)
            confidences.append(confidence)

            # Ground truth
            true_label = ground_truth.get(video_name, -1)
            if true_label != -1:
                true_labels.append(true_label)
            elif ground_truth:
                # Labels file provided but this video is missing from it
                print(f"  ⚠ No ground-truth label for {video_name} — skipping from metrics")
                continue

            detailed_results.append({
                "video_name":  video_name,
                "prediction":  prediction,
                "confidence":  confidence,
                "true_label":  true_label,
                "features":    features,
            })

            lbl_str = f"GT={true_label} → " if true_label != -1 else ""
            result  = "FAKE" if prediction == 1 else "REAL"
            correct = "✓" if true_label == prediction else "✗" if true_label != -1 else ""
            print(f"  {lbl_str}Pred={result}  conf={confidence:.3f}  {correct}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # ── Compute metrics ───────────────────────────────────────────
    results: Dict = {}

    have_gt = bool(true_labels) and len(true_labels) == len(
        [r for r in detailed_results if r["true_label"] != -1]
    )

    if have_gt:
        results = _compute_full_metrics(
            true_labels, predictions, confidences,
            detailed_results, clf,
            dataset_dir, model_path,
            plot_results,
        )
    else:
        results = _compute_prediction_summary(predictions, confidences, detailed_results)

    # ── Save JSON ─────────────────────────────────────────────────
    if save_results:
        _save_results(results, dataset_dir)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# METRICS (with ground truth)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_full_metrics(
    true_labels:      List[int],
    predictions:      List[int],
    confidences:      List[float],
    detailed_results: List[Dict],
    clf:              DeepfakeClassifier,
    dataset_dir:      str,
    model_path:       str,
    plot_results:     bool,
) -> Dict:

    y_true = np.array(true_labels)
    y_pred = np.array(predictions)
    y_conf = np.array(confidences)

    acc       = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="binary", zero_division=0)
    recall    = recall_score(y_true, y_pred,    average="binary", zero_division=0)
    f1        = f1_score(y_true, y_pred,        average="binary", zero_division=0)
    mcc       = matthews_corrcoef(y_true, y_pred)

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

    specificity       = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    npv               = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    balanced_accuracy = (recall + specificity) / 2

    roc_auc = 0.5
    if len(np.unique(y_true)) > 1:
        try:
            roc_auc = roc_auc_score(y_true, y_conf)
        except Exception:
            pass

    # ── Print results ─────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  EVALUATION RESULTS")
    print("=" * 65)
    print(f"  Dataset : {dataset_dir}")
    print(f"  Model   : {model_path}")
    print(f"  Samples : {len(y_true)}  "
          f"(real={int(np.sum(y_true==0))}, fake={int(np.sum(y_true==1))})")

    print("\n  PERFORMANCE METRICS:")
    print(f"  {'Accuracy':<22} {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  {'Precision':<22} {precision:.4f}  ({precision*100:.2f}%)")
    print(f"  {'Recall':<22} {recall:.4f}  ({recall*100:.2f}%)")
    print(f"  {'F1-Score':<22} {f1:.4f}  ({f1*100:.2f}%)")
    print(f"  {'Specificity':<22} {specificity:.4f}  ({specificity*100:.2f}%)")
    print(f"  {'Balanced Accuracy':<22} {balanced_accuracy:.4f}  ({balanced_accuracy*100:.2f}%)")
    print(f"  {'ROC-AUC':<22} {roc_auc:.4f}")
    print(f"  {'Matthews CC':<22} {mcc:.4f}")
    print(f"  {'NPV':<22} {npv:.4f}  ({npv*100:.2f}%)")

    print("\n  CONFUSION MATRIX:")
    print(f"  True Negatives  (real→real) : {int(tn):>5}")
    print(f"  False Positives (real→fake) : {int(fp):>5}")
    print(f"  False Negatives (fake→real) : {int(fn):>5}")
    print(f"  True Positives  (fake→fake) : {int(tp):>5}")

    if fp > 0 or fn > 0:
        print("\n  ERROR ANALYSIS:")
        if (fp + tn) > 0:
            print(f"  Type I  error (false positive rate) : {fp/(fp+tn)*100:.2f}%")
        if (fn + tp) > 0:
            print(f"  Type II error (false negative rate) : {fn/(fn+tp)*100:.2f}%")

    # ── Facial dynamics summary ───────────────────────────────────
    _print_facial_dynamics_summary(detailed_results)

    # ── Classification report ─────────────────────────────────────
    print("\n  CLASSIFICATION REPORT:")
    print(classification_report(y_true, y_pred,
                                target_names=["Real", "Fake"],
                                digits=4))

    # ── Plots ─────────────────────────────────────────────────────
    if plot_results:
        _create_evaluation_plots(y_true, y_pred, y_conf, {
            "evaluation_summary": {
                "accuracy": acc, "precision": precision,
                "recall": recall, "f1_score": f1,
                "specificity": specificity, "roc_auc": roc_auc,
            }
        }, detailed_results)

    # ── Cross-validation ──────────────────────────────────────────
    if len(detailed_results) >= 10:
        _cross_validation_analysis(detailed_results, clf)

    return {
        "evaluation_summary": {
            "total_samples": int(len(y_true)),
            "accuracy": float(acc),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "specificity": float(specificity),
            "balanced_accuracy": float(balanced_accuracy),
            "roc_auc": float(roc_auc),
            "mcc": float(mcc),
            "npv": float(npv),
        },
        "confusion_matrix": {
            "true_negatives":  int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives":  int(tp),
        },
        "class_distribution": {
            "real_videos": int(np.sum(y_true == 0)),
            "fake_videos": int(np.sum(y_true == 1)),
        },
        "detailed_results":      detailed_results,
        "evaluation_timestamp":  datetime.now().isoformat(),
    }


def _compute_prediction_summary(
    predictions:      List[int],
    confidences:      List[float],
    detailed_results: List[Dict],
) -> Dict:
    """Used when no ground-truth labels are provided."""
    preds = np.array(predictions)
    confs = np.array(confidences) if confidences else np.array([])

    print("\n  PREDICTION SUMMARY (no ground-truth labels)")
    print(f"  Total videos     : {len(preds)}")
    print(f"  Predicted REAL   : {int(np.sum(preds == 0))}")
    print(f"  Predicted FAKE   : {int(np.sum(preds == 1))}")
    if len(confs):
        print(f"  Avg confidence   : {confs.mean():.4f} ± {confs.std():.4f}")

    _print_facial_dynamics_summary(detailed_results)

    return {
        "predictions_only": {
            "total_samples":      int(len(preds)),
            "predicted_real":     int(np.sum(preds == 0)),
            "predicted_fake":     int(np.sum(preds == 1)),
            "average_confidence": float(confs.mean()) if len(confs) else 0.0,
            "confidence_std":     float(confs.std())  if len(confs) else 0.0,
        },
        "detailed_results":     detailed_results,
        "evaluation_timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FACIAL DYNAMICS SUMMARY  (new)
# ─────────────────────────────────────────────────────────────────────────────

def _print_facial_dynamics_summary(detailed_results: List[Dict]):
    """
    Print mean facial-dynamics feature values split by real vs fake.
    Only shown when ground-truth labels are available for at least some videos.
    """
    real_results = [r for r in detailed_results if r.get("true_label") == 0]
    fake_results = [r for r in detailed_results if r.get("true_label") == 1]

    if not real_results or not fake_results:
        return

    print("\n  FACIAL DYNAMICS — REAL vs FAKE COMPARISON:")

    # Which feature keys to display (label, feature_key)
    dyn_display = [
        # Blink
        ("Blink Rate",              "avg_blink_rate"),
        ("Avg EAR",                 "avg_avg_ear"),
        # Edge / artifact
        ("Sharpness",               "dyn_sharpness_score_mean"),
        ("High-Freq Energy",        "dyn_high_freq_energy_mean"),
        ("Edge Density",            "dyn_edge_density_high_mean"),
        ("Freq Ratio",              "dyn_freq_ratio_mean"),
        # Color / skin
        ("Hue Consistency",         "dyn_hue_consistency_mean"),
        ("Color Smoothness",        "dyn_color_smoothness_mean"),
        ("Skin Ratio",              "dyn_skin_ratio_mean"),
        # Texture
        ("LBP Entropy",             "dyn_lbp_entropy_mean"),
        ("Noise Level",             "dyn_noise_level_mean"),
        ("Texture Energy",          "dyn_texture_energy_mean"),
        # Symmetry
        ("Symmetry Score",          "dyn_avg_symmetry_score_mean"),
        ("Symmetry Std",            "dyn_std_symmetry_score_mean"),
        # Head pose
        ("Yaw",                     "dyn_yaw_mean"),
        ("Pitch",                   "dyn_pitch_mean"),
        ("Roll",                    "dyn_roll_mean"),
        ("Yaw Jitter",              "temporal_yaw_jitter"),
        ("Pitch Jitter",            "temporal_pitch_jitter"),
        # Mouth
        ("Mouth Aspect Ratio",      "dyn_mouth_aspect_ratio_mean"),
        ("Mouth Corner Asymmetry",  "dyn_mouth_corner_asymmetry_mean"),
        # Motion
        ("Global Motion",           "dyn_global_motion_mean_mean"),
        ("Eye Motion Asymmetry",    "dyn_eye_motion_asymmetry_mean"),
        # Optical flow
        ("Optical Flow Mean",       "dyn_flow_mean_mean"),
        ("Boundary Flow Ratio",     "dyn_boundary_flow_ratio_mean"),
        ("Flow Direction Entropy",  "dyn_flow_direction_entropy_mean"),
    ]

    def mean_feat(results_list: List[Dict], key: str) -> str:
        vals = [r["features"].get(key) for r in results_list if r["features"].get(key) is not None]
        if not vals:
            return "  N/A  "
        return f"{np.mean(vals):>8.4f}"

    print(f"\n  {'Feature':<28}  {'REAL':>9}  {'FAKE':>9}  {'Δ':>9}")
    print(f"  {'-'*60}")

    for label, key in dyn_display:
        r_val_str = mean_feat(real_results, key)
        f_val_str = mean_feat(fake_results, key)

        # Compute delta if both available
        r_vals = [r["features"].get(key) for r in real_results if r["features"].get(key) is not None]
        f_vals = [r["features"].get(key) for r in fake_results if r["features"].get(key) is not None]
        if r_vals and f_vals:
            delta = np.mean(f_vals) - np.mean(r_vals)
            delta_str = f"{delta:>+9.4f}"
        else:
            delta_str = "       —"

        print(f"  {label:<28} {r_val_str}  {f_val_str}  {delta_str}")


# ─────────────────────────────────────────────────────────────────────────────
# PLOTS  (updated with facial dynamics panel)
# ─────────────────────────────────────────────────────────────────────────────

def _create_evaluation_plots(
    y_true:           np.ndarray,
    y_pred:           np.ndarray,
    y_conf:           np.ndarray,
    results:          Dict,
    detailed_results: List[Dict],
):
    """
    Create 3×3 evaluation plot grid:
      Row 1: Confusion matrix | ROC curve | Precision-Recall curve
      Row 2: Confidence distribution | Metrics bar | Scatter pred vs truth
      Row 3: Facial dynamics comparison (real vs fake) — NEW
    """
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 3, figsize=(20, 18))
    fig.suptitle("Deepfake Detection — Model Evaluation",
                 fontsize=17, fontweight="bold", y=0.98)

    summary = results.get("evaluation_summary", {})

    # ── [0,0] Confusion matrix heatmap ───────────────────────────
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[0, 0],
                xticklabels=["Real", "Fake"],
                yticklabels=["Real", "Fake"])
    axes[0, 0].set_title("Confusion Matrix")
    axes[0, 0].set_xlabel("Predicted"); axes[0, 0].set_ylabel("Actual")

    # ── [0,1] ROC curve ──────────────────────────────────────────
    if len(np.unique(y_true)) > 1:
        fpr, tpr, _ = roc_curve(y_true, y_conf)
        auc = summary.get("roc_auc", 0)
        axes[0, 1].plot(fpr, tpr, color="cyan", lw=2, label=f"AUC = {auc:.3f}")
        axes[0, 1].plot([0, 1], [0, 1], "r--", lw=1)
        axes[0, 1].set(xlabel="False Positive Rate", ylabel="True Positive Rate",
                       title="ROC Curve")
        axes[0, 1].legend(); axes[0, 1].grid(True, alpha=0.3)

    # ── [0,2] Precision-Recall curve ─────────────────────────────
    if len(np.unique(y_true)) > 1:
        prec_c, rec_c, _ = precision_recall_curve(y_true, y_conf)
        axes[0, 2].plot(rec_c, prec_c, color="lime", lw=2)
        axes[0, 2].set(xlabel="Recall", ylabel="Precision",
                       title="Precision-Recall Curve")
        axes[0, 2].grid(True, alpha=0.3)

    # ── [1,0] Confidence distribution ────────────────────────────
    axes[1, 0].hist(y_conf[y_true == 0], bins=20, alpha=0.7,
                    label="Real",  color="green", density=True)
    axes[1, 0].hist(y_conf[y_true == 1], bins=20, alpha=0.7,
                    label="Fake",  color="red",   density=True)
    axes[1, 0].set(xlabel="Confidence", ylabel="Density",
                   title="Confidence Distribution by Class")
    axes[1, 0].legend(); axes[1, 0].grid(True, alpha=0.3)

    # ── [1,1] Metrics bar ────────────────────────────────────────
    metric_names  = ["Accuracy", "Precision", "Recall", "F1", "Specificity"]
    metric_values = [
        summary.get("accuracy",    0),
        summary.get("precision",   0),
        summary.get("recall",      0),
        summary.get("f1_score",    0),
        summary.get("specificity", 0),
    ]
    colors = ["#4f8ef7", "#4ade80", "#f59e0b", "#f87171", "#a78bfa"]
    bars = axes[1, 1].bar(metric_names, metric_values, color=colors, alpha=0.85)
    axes[1, 1].set_ylim(0, 1.1)
    axes[1, 1].set(title="Performance Metrics", ylabel="Score")
    axes[1, 1].tick_params(axis="x", rotation=30)
    for bar, val in zip(bars, metric_values):
        axes[1, 1].text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.02,
                        f"{val:.3f}", ha="center", va="bottom",
                        fontweight="bold", fontsize=9)

    # ── [1,2] Prediction scatter ──────────────────────────────────
    jitter = np.random.normal(0, 0.05, len(y_true))
    sc = axes[1, 2].scatter(y_true + jitter, y_pred + jitter,
                            c=y_conf, cmap="viridis", alpha=0.6)
    plt.colorbar(sc, ax=axes[1, 2], label="Confidence")
    axes[1, 2].set(xlabel="True Label", ylabel="Predicted",
                   title="Predictions vs Truth (colour = confidence)")
    axes[1, 2].set_xticks([0, 1]); axes[1, 2].set_yticks([0, 1])
    axes[1, 2].set_xticklabels(["Real", "Fake"])
    axes[1, 2].set_yticklabels(["Real", "Fake"])

    # ── [2,0] Facial dynamics comparison bar (NEW) ───────────────
    dyn_keys = [
        ("Sharpness",       "dyn_sharpness_score_mean"),
        ("Symmetry",        "dyn_avg_symmetry_score_mean"),
        ("LBP Entropy",     "dyn_lbp_entropy_mean"),
        ("Noise Level",     "dyn_noise_level_mean"),
        ("Opt Flow",        "dyn_flow_mean_mean"),
        ("Hue Consist.",    "dyn_hue_consistency_mean"),
        ("Skin Ratio",      "dyn_skin_ratio_mean"),
        ("Mouth AR",        "dyn_mouth_aspect_ratio_mean"),
    ]
    real_r = [r for r in detailed_results if r.get("true_label") == 0]
    fake_r = [r for r in detailed_results if r.get("true_label") == 1]

    if real_r and fake_r:
        labels_dyn   = [d[0] for d in dyn_keys]
        real_means = []
        fake_means = []
        for _, key in dyn_keys:
            rv = [r["features"].get(key, 0) for r in real_r]
            fv = [r["features"].get(key, 0) for r in fake_r]
            real_means.append(float(np.mean(rv)) if rv else 0)
            fake_means.append(float(np.mean(fv)) if fv else 0)

        # Normalise each feature 0-1 for visual comparison
        all_means = np.array([real_means, fake_means])
        max_vals  = all_means.max(axis=0)
        max_vals[max_vals == 0] = 1
        real_norm = all_means[0] / max_vals
        fake_norm = all_means[1] / max_vals

        x = np.arange(len(labels_dyn))
        w = 0.35
        axes[2, 0].bar(x - w/2, real_norm, w, label="Real", color="#4ade80", alpha=0.8)
        axes[2, 0].bar(x + w/2, fake_norm, w, label="Fake", color="#f87171", alpha=0.8)
        axes[2, 0].set_xticks(x)
        axes[2, 0].set_xticklabels(labels_dyn, rotation=35, ha="right", fontsize=8)
        axes[2, 0].set(title="Facial Dynamics — Real vs Fake (normalised)",
                       ylabel="Relative Mean Value")
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.2)
    else:
        axes[2, 0].text(0.5, 0.5, "Need ground-truth labels\nfor dynamics comparison",
                        ha="center", va="center", transform=axes[2, 0].transAxes,
                        color="#94a3b8", fontsize=11)
        axes[2, 0].set_title("Facial Dynamics Comparison")

    # ── [2,1] Head pose jitter distribution (NEW) ────────────────
    yaw_real  = [r["features"].get("temporal_yaw_jitter",   0) for r in real_r]
    yaw_fake  = [r["features"].get("temporal_yaw_jitter",   0) for r in fake_r]
    pit_real  = [r["features"].get("temporal_pitch_jitter", 0) for r in real_r]
    pit_fake  = [r["features"].get("temporal_pitch_jitter", 0) for r in fake_r]

    if yaw_real or yaw_fake:
        if yaw_real:
            axes[2, 1].scatter([0]*len(yaw_real),  yaw_real,  alpha=0.6,
                               color="green", label="Real — Yaw")
        if yaw_fake:
            axes[2, 1].scatter([1]*len(yaw_fake),  yaw_fake,  alpha=0.6,
                               color="red",   label="Fake — Yaw",  marker="x")
        if pit_real:
            axes[2, 1].scatter([0]*len(pit_real), pit_real, alpha=0.4,
                               color="lime",  label="Real — Pitch", marker="^")
        if pit_fake:
            axes[2, 1].scatter([1]*len(pit_fake), pit_fake, alpha=0.4,
                               color="orange",label="Fake — Pitch", marker="^")
        axes[2, 1].set_xticks([0, 1])
        axes[2, 1].set_xticklabels(["Real", "Fake"])
        axes[2, 1].set(title="Head Pose Jitter (Yaw & Pitch)",
                       ylabel="Jitter Value")
        axes[2, 1].legend(fontsize=7)
        axes[2, 1].grid(True, alpha=0.2)
    else:
        axes[2, 1].text(0.5, 0.5, "No pose jitter data", ha="center", va="center",
                        transform=axes[2, 1].transAxes, color="#94a3b8")
        axes[2, 1].set_title("Head Pose Jitter")

    # ── [2,2] Texture entropy vs symmetry scatter (NEW) ──────────
    all_tex = [r["features"].get("dyn_lbp_entropy_mean", 0)         for r in detailed_results]
    all_sym = [r["features"].get("dyn_avg_symmetry_score_mean", 0)   for r in detailed_results]
    all_lbl = [r.get("true_label", -1)                               for r in detailed_results]

    colors_scatter = ["green" if l == 0 else "red" if l == 1 else "grey"
                      for l in all_lbl]
    axes[2, 2].scatter(all_tex, all_sym, c=colors_scatter, alpha=0.7, s=40)
    axes[2, 2].set(xlabel="LBP Texture Entropy",
                   ylabel="Symmetry Score",
                   title="Texture Entropy vs Symmetry")
    # Legend patches
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="green", label="Real"),
        Patch(facecolor="red",   label="Fake"),
    ]
    axes[2, 2].legend(handles=legend_elements)
    axes[2, 2].grid(True, alpha=0.2)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plot_path = f"evaluation_plots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="#0f1117")
    print(f"\n📊 Evaluation plots saved: {plot_path}")
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-VALIDATION  (fixed: now goes through full pipeline)
# ─────────────────────────────────────────────────────────────────────────────

def _cross_validation_analysis(detailed_results: List[Dict], clf: DeepfakeClassifier):
    """
    FIX 3: Original passed raw X directly to cross_val_score without
    going through imputer → scaler → feature_selector pipeline first.
    We now build a proper sklearn Pipeline for CV.
    """
    from sklearn.pipeline import Pipeline

    valid = [r for r in detailed_results if r.get("true_label", -1) != -1]
    if len(valid) < 5:
        print("\n⚠  Cross-validation skipped — need at least 5 labelled samples")
        return

    features_list = [r["features"] for r in valid]
    y             = np.array([r["true_label"] for r in valid])

    X = clf.prepare_features(features_list)

    # Build pipeline that mirrors clf's preprocessing
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import RobustScaler
    import copy

    steps = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  RobustScaler()),
    ]
    if clf.feature_selector is not None:
        steps.append(("selector", copy.deepcopy(clf.feature_selector)))
    steps.append(("model", copy.deepcopy(clf.model)))

    pipe = Pipeline(steps)
    skf  = StratifiedKFold(n_splits=min(5, len(set(y))), shuffle=True, random_state=42)

    print("\n  CROSS-VALIDATION (on evaluation set):")
    for metric in ("accuracy", "precision", "recall", "f1"):
        try:
            scores = cross_val_score(pipe, X, y, cv=skf, scoring=metric, n_jobs=-1)
            print(f"  {metric.capitalize():<12} {scores.mean():.4f} ± {scores.std()*2:.4f}")
        except Exception as e:
            print(f"  {metric.capitalize():<12} failed ({e})")


# ─────────────────────────────────────────────────────────────────────────────
# SAVE RESULTS  (fixed: retains all dyn_* and temporal_* keys)
# ─────────────────────────────────────────────────────────────────────────────

def _save_results(results: Dict, dataset_dir: str):
    """
    FIX 4: Original kept only 4 blink features in the JSON.
    Now saves a meaningful subset of ALL feature groups.
    """
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = os.path.basename(dataset_dir.rstrip("/\\")) or "dataset"
    filename     = f"evaluation_results_{dataset_name}_{timestamp}.json"

    # Keys to retain per video in detailed_results (keeps file size reasonable)
    KEEP_KEYS = {
        # Blink
        "avg_blink_rate", "avg_avg_ear", "avg_avg_blink_duration",
        "video_duration", "total_frames", "fps",
        # Edge / artifact
        "dyn_sharpness_score_mean", "dyn_high_freq_energy_mean",
        "dyn_freq_ratio_mean", "dyn_edge_density_high_mean",
        # Color / skin
        "dyn_hue_consistency_mean", "dyn_skin_ratio_mean",
        "dyn_color_smoothness_mean",
        # Texture
        "dyn_lbp_entropy_mean", "dyn_noise_level_mean", "dyn_texture_energy_mean",
        # Symmetry
        "dyn_avg_symmetry_score_mean", "dyn_std_symmetry_score_mean",
        # Pose
        "dyn_yaw_mean", "dyn_pitch_mean", "dyn_roll_mean",
        "temporal_yaw_jitter", "temporal_pitch_jitter", "temporal_roll_jitter",
        # Mouth
        "dyn_mouth_aspect_ratio_mean", "dyn_mouth_corner_asymmetry_mean",
        # Motion
        "dyn_global_motion_mean_mean", "dyn_eye_motion_asymmetry_mean",
        # Optical flow
        "dyn_flow_mean_mean", "dyn_boundary_flow_ratio_mean",
        "dyn_flow_direction_entropy_mean",
    }

    clean = {k: v for k, v in results.items() if k != "detailed_results"}
    clean["detailed_results"] = []

    for r in results.get("detailed_results", []):
        entry = {
            "video_name":  r.get("video_name"),
            "prediction":  r.get("prediction"),
            "confidence":  r.get("confidence"),
            "true_label":  r.get("true_label"),
            "features":    {k: v for k, v in r.get("features", {}).items()
                            if k in KEEP_KEYS},
        }
        clean["detailed_results"].append(entry)

    with open(filename, "w") as f:
        json.dump(clean, f, indent=2, default=str)
    print(f"\n💾 Results saved: {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Deepfake Detection Evaluation",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python evaluate.py --model models/classifier.pkl --dataset data/test/ --labels labels.json
  python evaluate.py --model models/classifier.pkl --dataset data/test/
  python evaluate.py --model models/classifier.pkl --dataset video.mp4 --no-plots
        """,
    )
    parser.add_argument("--model",    required=True, help="Path to trained model (.pkl)")
    parser.add_argument("--dataset",  required=True, help="Dataset directory or single video path")
    parser.add_argument("--labels",   default=None,  help="Ground-truth labels JSON file (optional)")
    parser.add_argument("--cache-dir",default="features", help="Feature cache dir (default: features/)")
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")
    parser.add_argument("--no-save",  action="store_true", help="Skip saving results JSON")

    args = parser.parse_args()

    try:
        results = evaluate_on_dataset(
            model_path   = args.model,
            dataset_dir  = args.dataset,
            labels_file  = args.labels,
            cache_dir    = args.cache_dir,
            save_results = not args.no_save,
            plot_results = not args.no_plots,
        )

        print("\n✅ Evaluation complete!")
        if "evaluation_summary" in results:
            s = results["evaluation_summary"]
            print(f"   Accuracy  : {s['accuracy']:.4f}")
            print(f"   F1-Score  : {s['f1_score']:.4f}")
            print(f"   ROC-AUC   : {s['roc_auc']:.4f}")

    except Exception as e:
        import traceback
        print(f"\n❌ Evaluation failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()