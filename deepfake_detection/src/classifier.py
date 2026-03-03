# # src/classifier.py - FIXED VERSION

# import numpy as np
# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.svm import SVC  # Fixed import
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split, cross_val_score
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
# import joblib
# from typing import Dict, List, Tuple
# import os

# class DeepfakeClassifier:
#     def __init__(self, model_type: str = 'random_forest'):
#         """
#         Initialize classifier
#         model_type: 'random_forest', 'svm', or 'logistic_regression'
#         """
#         self.model_type = model_type
#         self.model = None
#         self.scaler = StandardScaler()
#         self.feature_names = None
        
#         self._initialize_model()
    
#     def _initialize_model(self):
#         """Initialize the selected model"""
#         if self.model_type == 'random_forest':
#             self.model = RandomForestClassifier(
#                 n_estimators=100,
#                 max_depth=10,
#                 random_state=42,
#                 n_jobs=-1
#             )
#         elif self.model_type == 'svm':
#             self.model = SVC(  # Fixed: was SVM, should be SVC
#                 kernel='rbf',
#                 C=1.0,
#                 gamma='scale',
#                 random_state=42,
#                 probability=True
#             )
#         elif self.model_type == 'logistic_regression':
#             self.model = LogisticRegression(
#                 random_state=42,
#                 max_iter=1000
#             )
#         else:
#             raise ValueError(f"Unsupported model type: {self.model_type}")
    
#     def prepare_features(self, features_list: List[Dict]) -> np.ndarray:
#         """Convert list of feature dictionaries to numpy array"""
#         if not features_list:
#             raise ValueError("Features list is empty")
        
#         # Get feature names from first sample
#         if self.feature_names is None:
#             self.feature_names = list(features_list[0].keys())
        
#         # Convert to DataFrame for easier handling
#         df = pd.DataFrame(features_list)
        
#         # Ensure all required features are present
#         for feature in self.feature_names:
#             if feature not in df.columns:
#                 df[feature] = 0.0
        
#         # Select only the required features in correct order
#         df = df[self.feature_names]
        
#         # Handle missing values and inf values
#         df = df.fillna(0)
#         df = df.replace([np.inf, -np.inf], 0)
        
#         return df.values
    
#     def train(self, features_list: List[Dict], labels: List[int]) -> Dict:
#         """
#         Train the classifier
#         labels: 0 for real, 1 for fake
#         """
#         print(f"Training {self.model_type} classifier...")
        
#         # Prepare features
#         X = self.prepare_features(features_list)
#         y = np.array(labels)
        
#         print(f"Training data shape: {X.shape}")
#         print(f"Class distribution - Real: {np.sum(y == 0)}, Fake: {np.sum(y == 1)}")
        
#         # Check if we have enough samples
#         if len(X) < 4:
#             raise ValueError("Need at least 4 samples for training")
        
#         # Split data
#         test_size = min(0.2, 2.0 / len(X))  # Adjust test size for small datasets
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
#         )
        
#         # Scale features
#         X_train_scaled = self.scaler.fit_transform(X_train)
#         X_test_scaled = self.scaler.transform(X_test)
        
#         # Train model
#         self.model.fit(X_train_scaled, y_train)
        
#         # Evaluate on test set
#         y_pred = self.model.predict(X_test_scaled)
#         y_pred_proba = self.model.predict_proba(X_test_scaled)
        
#         # Calculate metrics
#         accuracy = accuracy_score(y_test, y_pred)
        
#         # Cross-validation (adjust cv for small datasets)
#         cv_folds = min(5, len(X_train))
#         if cv_folds < 2:
#             cv_scores = np.array([accuracy])  # Use test accuracy if too few samples
#         else:
#             cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv_folds)
        
#         results = {
#             'accuracy': accuracy,
#             'cv_mean': cv_scores.mean(),
#             'cv_std': cv_scores.std(),
#             'classification_report': classification_report(y_test, y_pred),
#             'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
#         }
        
#         print(f"Training completed!")
#         print(f"Test Accuracy: {accuracy:.4f}")
#         print(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
#         return results
    
#     def predict(self, features: Dict) -> Tuple[int, float]:
#         """
#         Predict if video is fake or real
#         Returns: (prediction, confidence)
#         """
#         if self.model is None:
#             raise ValueError("Model not trained yet")
        
#         # Prepare features
#         X = self.prepare_features([features])
#         X_scaled = self.scaler.transform(X)
        
#         # Make prediction
#         prediction = self.model.predict(X_scaled)[0]
#         probabilities = self.model.predict_proba(X_scaled)[0]
#         confidence = np.max(probabilities)
        
#         return int(prediction), float(confidence)
    
#     def save_model(self, filepath: str):
#         """Save trained model and scaler"""
#         if self.model is None:
#             raise ValueError("No trained model to save")
        
#         model_data = {
#             'model': self.model,
#             'scaler': self.scaler,
#             'feature_names': self.feature_names,
#             'model_type': self.model_type
#         }
        
#         os.makedirs(os.path.dirname(filepath), exist_ok=True)
#         joblib.dump(model_data, filepath)
#         print(f"Model saved to {filepath}")
    
#     def load_model(self, filepath: str):
#         """Load trained model and scaler"""
#         if not os.path.exists(filepath):
#             raise FileNotFoundError(f"Model file not found: {filepath}")
        
#         model_data = joblib.load(filepath)
#         self.model = model_data['model']
#         self.scaler = model_data['scaler']
#         self.feature_names = model_data['feature_names']
#         self.model_type = model_data['model_type']
        
#         print(f"Model loaded from {filepath}")
    
#     def get_feature_importance(self) -> Dict:
#         """Get feature importance (for tree-based models)"""
#         if self.model_type == 'random_forest' and self.model is not None:
#             importance = self.model.feature_importances_
#             feature_importance = dict(zip(self.feature_names, importance))
#             return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
#         else:
#             return {}


#new updated

#!/usr/bin/env python3
"""
Updated Deepfake Classifier
Supports:
  - Random Forest (original)
  - Gradient Boosting / XGBoost (new, better for mixed feature sets)
  - Transfer-learned feature fusion
Handles large mixed feature vectors (blink + facial dynamics).
"""

import os
import pickle
import numpy as np
from typing import Dict, List, Optional, Tuple

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectFromModel
import warnings
warnings.filterwarnings("ignore")

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class DeepfakeClassifier:
    def __init__(self, model_type: str = "gradient_boosting"):
        """
        Args:
            model_type: 'random_forest' | 'gradient_boosting' | 'xgboost'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = RobustScaler()           # Robust to outliers
        self.imputer = SimpleImputer(strategy="median")
        self.feature_names: List[str] = []
        self.feature_selector = None
        self.is_trained = False
        self._build_model()

    def _build_model(self):
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=None,
                min_samples_split=4,
                min_samples_leaf=2,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=5,
                min_samples_split=4,
                min_samples_leaf=2,
                subsample=0.8,
                max_features="sqrt",
                random_state=42,
            )
        elif self.model_type == "xgboost" and XGBOOST_AVAILABLE:
            self.model = XGBClassifier(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=1,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1,
            )
        else:
            print(f"Model type '{self.model_type}' not available; falling back to gradient_boosting.")
            self.model_type = "gradient_boosting"
            self._build_model()

    # ─────────────────────────────────────────────────────────────
    # FEATURE PREPARATION
    # ─────────────────────────────────────────────────────────────

    def prepare_features(self, features_list: List[Dict]) -> np.ndarray:
        """Convert list of feature dicts to a clean numpy matrix."""
        if not features_list:
            return np.array([])

        # Determine consistent feature set (union of all keys)
        if not self.feature_names:
            all_keys = set()
            for f in features_list:
                all_keys.update(f.keys())
            self.feature_names = sorted(all_keys)

        matrix = []
        for features in features_list:
            row = [float(features.get(k, 0.0)) for k in self.feature_names]
            matrix.append(row)

        X = np.array(matrix, dtype=np.float32)

        # Replace NaN/Inf
        X = np.where(np.isfinite(X), X, 0.0)
        return X

    # ─────────────────────────────────────────────────────────────
    # TRAINING
    # ─────────────────────────────────────────────────────────────

    def train(self, features_list: List[Dict], labels: List[int]) -> Dict:
        """
        Train the classifier.
        Returns training summary dict.
        """
        print(f"Preparing feature matrix ({len(features_list)} samples)...")
        X = self.prepare_features(features_list)
        y = np.array(labels)

        print(f"Feature matrix shape: {X.shape}")
        print(f"Class distribution — Real: {(y==0).sum()}, Fake: {(y==1).sum()}")

        # Impute then scale
        X_imputed = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_imputed)

        # Optional: feature selection to reduce dimensionality for large feature sets
        if X_scaled.shape[1] > 100:
            print(f"Running feature selection ({X_scaled.shape[1]} → top features)...")
            selector_model = RandomForestClassifier(
                n_estimators=50, random_state=42, n_jobs=-1
            )
            selector_model.fit(X_scaled, y)
            self.feature_selector = SelectFromModel(
                selector_model, threshold="mean", prefit=True
            )
            X_scaled = self.feature_selector.transform(X_scaled)
            print(f"  → {X_scaled.shape[1]} features selected")

        # Train
        print(f"Training {self.model_type} classifier...")
        self.model.fit(X_scaled, y)
        self.is_trained = True

        # Training accuracy
        train_preds = self.model.predict(X_scaled)
        train_acc = float((train_preds == y).mean())

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_scaled, y,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="accuracy", n_jobs=-1
        )

        # F1 cross-validation
        f1_scores = cross_val_score(
            self.model, X_scaled, y,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring="f1", n_jobs=-1
        )

        results = {
            "accuracy": train_acc,
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "cv_f1_mean": float(f1_scores.mean()),
            "cv_f1_std": float(f1_scores.std()),
            "n_features": X_scaled.shape[1],
            "n_samples": len(y),
        }

        print(f"\n✅ Training complete:")
        print(f"   Train accuracy : {train_acc:.4f}")
        print(f"   CV accuracy    : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"   CV F1          : {f1_scores.mean():.4f} ± {f1_scores.std():.4f}")

        return results

    # ─────────────────────────────────────────────────────────────
    # PREDICTION
    # ─────────────────────────────────────────────────────────────

    def predict(self, features: Dict) -> Tuple[int, float]:
        """
        Predict single video.
        Returns (prediction: 0/1, confidence: 0-1)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() or load_model() first.")

        X = self.prepare_features([features])
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)

        if self.feature_selector is not None:
            X_scaled = self.feature_selector.transform(X_scaled)

        prediction = int(self.model.predict(X_scaled)[0])
        proba = self.model.predict_proba(X_scaled)[0]
        confidence = float(proba[prediction])

        return prediction, confidence

    def predict_batch(self, features_list: List[Dict]) -> List[Tuple[int, float]]:
        """Batch prediction."""
        if not self.is_trained:
            raise RuntimeError("Model not trained.")

        X = self.prepare_features(features_list)
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)

        if self.feature_selector is not None:
            X_scaled = self.feature_selector.transform(X_scaled)

        predictions = self.model.predict(X_scaled)
        probas = self.model.predict_proba(X_scaled)

        results = []
        for pred, proba in zip(predictions, probas):
            results.append((int(pred), float(proba[int(pred)])))
        return results

    # ─────────────────────────────────────────────────────────────
    # FEATURE IMPORTANCE
    # ─────────────────────────────────────────────────────────────

    def get_feature_importance(self) -> Dict[str, float]:
        """Return sorted feature importance dict."""
        if not self.is_trained or not hasattr(self.model, "feature_importances_"):
            return {}

        importances = self.model.feature_importances_

        # Map back to feature names (accounting for selector)
        if self.feature_selector is not None:
            selected_mask = self.feature_selector.get_support()
            selected_names = [n for n, m in zip(self.feature_names, selected_mask) if m]
        else:
            selected_names = self.feature_names

        importance_dict = {
            name: float(imp)
            for name, imp in zip(selected_names, importances)
        }
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

    def print_top_features(self, n: int = 20):
        """Print top N most important features."""
        importance = self.get_feature_importance()
        if not importance:
            print("Feature importance not available.")
            return
        print(f"\n🏆 Top {n} Most Important Features:")
        for i, (name, score) in enumerate(list(importance.items())[:n], 1):
            # Categorize feature group
            if name.startswith("left_") or name.startswith("right_") or name.startswith("avg_"):
                group = "👁  Blink"
            elif "temporal_" in name:
                group = "⏱ Temporal"
            elif "dyn_" in name:
                if "sharpness" in name or "edge" in name or "freq" in name:
                    group = "🔍 Edge/Artifact"
                elif "symmetry" in name:
                    group = "⚖  Symmetry"
                elif "texture" in name or "lbp" in name or "noise" in name:
                    group = "🎨 Texture"
                elif "yaw" in name or "pitch" in name or "roll" in name:
                    group = "🧭 Pose"
                elif "mouth" in name or "lip" in name:
                    group = "💬 Mouth"
                elif "flow" in name:
                    group = "🌊 OptFlow"
                elif "color" in name or "hue" in name or "skin" in name:
                    group = "🎨 Color"
                elif "motion" in name:
                    group = "🏃 Motion"
                else:
                    group = "📊 Dynamics"
            else:
                group = "📹 Video"
            print(f"  {i:2d}. [{group}] {name}: {score:.4f}")

    # ─────────────────────────────────────────────────────────────
    # PERSISTENCE
    # ─────────────────────────────────────────────────────────────

    def save_model(self, path: str):
        """Save model + preprocessing pipeline."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        state = {
            "model": self.model,
            "scaler": self.scaler,
            "imputer": self.imputer,
            "feature_names": self.feature_names,
            "feature_selector": self.feature_selector,
            "model_type": self.model_type,
            "is_trained": self.is_trained,
        }
        with open(path, "wb") as f:
            pickle.dump(state, f)
        print(f"✅ Model saved to: {path}")

    def load_model(self, path: str):
        """Load model + preprocessing pipeline."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        with open(path, "rb") as f:
            state = pickle.load(f)
        self.model = state["model"]
        self.scaler = state["scaler"]
        self.imputer = state["imputer"]
        self.feature_names = state["feature_names"]
        self.feature_selector = state.get("feature_selector")
        self.model_type = state.get("model_type", "unknown")
        self.is_trained = state.get("is_trained", True)
        print(f"✅ Model loaded from: {path}")
        print(f"   Type: {self.model_type} | Features: {len(self.feature_names)}")