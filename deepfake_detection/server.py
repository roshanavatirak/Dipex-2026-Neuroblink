# #!/usr/bin/env python3
# """
# Simple FastAPI backend for Deepfake Detection - Fixed Version
# """

# import os
# import sys
# import uuid
# import tempfile
# import shutil
# from pathlib import Path
# from contextlib import asynccontextmanager

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # Add src to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# # Global variables
# classifier = None
# feature_extractor = None
# model_loaded = False

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     global classifier, feature_extractor, model_loaded
#     try:
#         print("Loading ML components...")
        
#         # Import here to avoid module loading issues
#         from feature_extractor import FeatureExtractor
#         from classifier import DeepfakeClassifier
        
#         feature_extractor = FeatureExtractor()
#         classifier = DeepfakeClassifier()
        
#         if os.path.exists("models/classifier.pkl"):
#             classifier.load_model("models/classifier.pkl")
#             model_loaded = True
#             print("✅ Model loaded successfully")
#         else:
#             print("❌ Model file not found: models/classifier.pkl")
            
#     except ImportError as e:
#         print(f"❌ Import error: {e}")
#         print("Make sure your ML files are in the src/ folder with correct imports")
#     except Exception as e:
#         print(f"❌ Error loading model: {e}")
    
#     yield
#     # Shutdown (if needed)
#     print("Shutting down...")

# app = FastAPI(title="Deepfake Detection API", version="1.0.0", lifespan=lifespan)

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class PredictionResponse(BaseModel):
#     success: bool
#     prediction: str
#     confidence: float
#     processing_time: float
#     video_info: dict
#     features: dict = None
#     error: str = None

# @app.get("/")
# async def root():
#     return {
#         "message": "Deepfake Detection API", 
#         "model_loaded": model_loaded,
#         "status": "running"
#     }

# @app.get("/health")
# async def health():
#     return {
#         "status": "healthy" if model_loaded else "unhealthy", 
#         "model_loaded": model_loaded
#     }

# @app.post("/predict")
# async def predict_video(file: UploadFile = File(...)):
#     if not model_loaded:
#         raise HTTPException(status_code=503, detail="Model not loaded")
    
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="No file provided")
    
#     # Create temp directory
#     temp_dir = tempfile.mkdtemp()
#     temp_path = None
    
#     try:
#         # Save file
#         file_ext = os.path.splitext(file.filename)[1]
#         temp_path = os.path.join(temp_dir, f"video{file_ext}")
        
#         with open(temp_path, "wb") as temp_file:
#             content = await file.read()
#             temp_file.write(content)
        
#         # Process video
#         import time
#         start_time = time.time()
        
#         features = feature_extractor.extract_video_features(temp_path)
#         prediction, confidence = classifier.predict(features)
        
#         processing_time = time.time() - start_time
#         result = "FAKE" if prediction == 1 else "REAL"
        
#         return PredictionResponse(
#             success=True,
#             prediction=result,
#             confidence=float(confidence),
#             processing_time=processing_time,
#             video_info={
#                 "filename": file.filename,
#                 "duration": features.get('video_duration', 0),
#                 "total_frames": features.get('total_frames', 0),
#                 "fps": features.get('fps', 0)
#             },
#             features={
#                 "blink_rate": features.get('avg_blink_rate', 0),
#                 "avg_blink_duration": features.get('avg_avg_blink_duration', 0),
#                 "avg_ear": features.get('avg_avg_ear', 0),
#                 "blink_completeness": features.get('avg_avg_blink_completeness', 0)
#             }
#         )
        
#     except Exception as e:
#         print(f"Error processing video: {e}")
#         return PredictionResponse(
#             success=False,
#             prediction="ERROR",
#             confidence=0.0,
#             processing_time=0.0,
#             video_info={},
#             error=str(e)
#         )
#     finally:
#         # Cleanup
#         try:
#             if temp_path and os.path.exists(temp_path):
#                 os.remove(temp_path)
#             if os.path.exists(temp_dir):
#                 os.rmdir(temp_dir)
#         except:
#             pass

# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 Starting Deepfake Detection API...")
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

#new update
#!/usr/bin/env python3
"""
server.py  —  Deepfake Detection REST API
─────────────────────────────────────────
Run:  python server.py
  or: uvicorn server:app --host 0.0.0.0 --port 8000 --reload

Fixes vs original api.py:
  1. uvicorn self-reference was "api:app" — changed to "server:app"
  2. sys.path pointed to nested src/src — fixed to project root + src/
  3. temp-dir cleanup used os.rmdir (fails if non-empty) — replaced with shutil.rmtree
  4. CORS hardcoded to localhost:3000 only — widened for dev; restrict in prod
  5. Missing shutil import — added
  6. MODEL_PATH env-var resolves relative to project root, not CWD
# """

# import os
# os.environ["GLOG_minloglevel"] = "2"
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# os.environ["ABSL_MIN_LOG_LEVEL"] = "3"

# import absl.logging
# absl.logging.set_verbosity(absl.logging.ERROR)
# import os
# import sys
# import time
# import shutil
# import tempfile
# from contextlib import asynccontextmanager
# from typing import Optional, Dict

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # ── Paths ─────────────────────────────────────────────────────────────────────
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # project root
# SRC_DIR  = os.path.join(BASE_DIR, "src")

# for p in (BASE_DIR, SRC_DIR):
#     if p not in sys.path:
#         sys.path.insert(0, p)

# # ── Global ML state ───────────────────────────────────────────────────────────
# classifier        = None
# feature_extractor = None
# model_loaded      = False


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global classifier, feature_extractor, model_loaded
#     try:
#         print("🔧 Loading ML components...")
#         from feature_extractor import FeatureExtractor
#         from classifier import DeepfakeClassifier

#         feature_extractor = FeatureExtractor()
#         classifier        = DeepfakeClassifier()

#         # Resolve model path relative to project root so it works from any CWD
#         model_file = os.environ.get(
#             "MODEL_PATH",
#             os.path.join(BASE_DIR, "models", "classifier.pkl")
#         )
#         if os.path.exists(model_file):
#             classifier.load_model(model_file)
#             model_loaded = True
#             print(f"✅ Model loaded: {model_file}")
#         else:
#             print(f"⚠  Model not found: {model_file}")
#             print("   Train first → python train.py --mode train --real-dir <path> --fake-dir <path>")

#     except ImportError as e:
#         print(f"❌ Import error: {e}")
#         print("   Ensure src/ contains: feature_extractor.py, classifier.py, facial_dynamics_analyzer.py")
#     except Exception as e:
#         import traceback
#         print(f"❌ Startup error: {e}")
#         traceback.print_exc()

#     yield
#     print("🛑 Server shutdown")


# # ── App ───────────────────────────────────────────────────────────────────────
# app = FastAPI(
#     title       = "Deepfake Detection API",
#     description = "Eye Blink + Facial Dynamics deepfake detector",
#     version     = "2.0.0",
#     lifespan    = lifespan,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins     = ["*"],   # lock down in production (e.g. ["https://yourapp.com"])
#     allow_credentials = True,
#     allow_methods     = ["*"],
#     allow_headers     = ["*"],
# )


# # ── Response schema ───────────────────────────────────────────────────────────
# class PredictionResponse(BaseModel):
#     success:         bool
#     prediction:      str            # "REAL" | "FAKE" | "ERROR"
#     confidence:      float
#     processing_time: float
#     video_info:      Dict
#     blink_features:  Dict
#     facial_dynamics: Dict
#     error:           Optional[str] = None


# # ── Routes ────────────────────────────────────────────────────────────────────
# @app.get("/")
# async def root():
#     return {
#         "message":      "Deepfake Detection API v2.0",
#         "model_loaded": model_loaded,
#         "status":       "ready" if model_loaded else "model_not_loaded",
#         "docs":         "/docs",
#     }


# @app.get("/health")
# async def health():
#     return {
#         "status":       "healthy" if model_loaded else "unhealthy",
#         "model_loaded": model_loaded,
#     }


# @app.post("/predict", response_model=PredictionResponse)
# async def predict_video(file: UploadFile = File(...)):
#     """
#     Upload a video (.mp4 / .avi / .mov / .mkv) → returns REAL / FAKE prediction.
#     """
#     if not model_loaded:
#         raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="No file provided.")

#     allowed = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
#     ext = os.path.splitext(file.filename)[1].lower()
#     if ext not in allowed:
#         raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {allowed}")

#     # Save to temp file
#     temp_dir  = tempfile.mkdtemp()
#     temp_path = os.path.join(temp_dir, f"upload{ext}")

#     try:
#         content = await file.read()
#         with open(temp_path, "wb") as f:
#             f.write(content)

#         start    = time.time()
#         features = feature_extractor.extract_video_features(temp_path)
#         prediction, confidence = classifier.predict(features)
#         elapsed  = time.time() - start

#         result = "FAKE" if prediction == 1 else "REAL"

#         return PredictionResponse(
#             success         = True,
#             prediction      = result,
#             confidence      = round(float(confidence), 4),
#             processing_time = round(elapsed, 3),
#             video_info = {
#                 "filename":     file.filename,
#                 "duration_sec": round(float(features.get("video_duration", 0)), 2),
#                 "total_frames": int(features.get("total_frames", 0)),
#                 "fps":          round(float(features.get("fps", 0)), 2),
#             },
#             blink_features = {
#                 "blink_rate":         round(float(features.get("avg_blink_rate", 0)), 4),
#                 "avg_blink_duration": round(float(features.get("avg_avg_blink_duration", 0)), 4),
#                 "avg_ear":            round(float(features.get("avg_avg_ear", 0)), 4),
#                 "blink_completeness": round(float(features.get("avg_avg_blink_completeness", 0)), 4),
#             },
#             facial_dynamics = {
#                 "sharpness":           round(float(features.get("dyn_sharpness_score_mean", 0)), 4),
#                 "symmetry":            round(float(features.get("dyn_avg_symmetry_score_mean", 0)), 4),
#                 "noise_level":         round(float(features.get("dyn_noise_level_mean", 0)), 4),
#                 "texture_entropy":     round(float(features.get("dyn_lbp_entropy_mean", 0)), 4),
#                 "mouth_aspect_ratio":  round(float(features.get("dyn_mouth_aspect_ratio_mean", 0)), 4),
#                 "optical_flow":        round(float(features.get("dyn_flow_mean_mean", 0)), 4),
#                 "head_yaw_jitter":     round(float(features.get("temporal_yaw_jitter", 0)), 4),
#                 "color_consistency":   round(float(features.get("dyn_hue_consistency_mean", 0)), 4),
#                 "skin_ratio":          round(float(features.get("dyn_skin_ratio_mean", 0)), 4),
#                 "boundary_flow_ratio": round(float(features.get("dyn_boundary_flow_ratio_mean", 0)), 4),
#             },
#         )

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return PredictionResponse(
#             success=False, prediction="ERROR", confidence=0.0,
#             processing_time=0.0, video_info={}, blink_features={},
#             facial_dynamics={}, error=str(e),
#         )
#     finally:
#         # shutil.rmtree safely removes non-empty temp directories
#         shutil.rmtree(temp_dir, ignore_errors=True)


# # ── Dev entry point ───────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 Deepfake Detection API  →  http://localhost:8000")
#     print("📖 Interactive docs        →  http://localhost:8000/docs")
#     uvicorn.run(
#         "server:app",          # ← must match filename (server.py)
#         host       = "0.0.0.0",
#         port       = 8000,
#         reload     = True,
#         reload_dirs= [BASE_DIR],
#     )


##new update
import os
import sys

# ── Suppress MediaPipe / TensorFlow / absl noise ─────────────────────────────
os.environ["GLOG_minloglevel"]    = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["ABSL_MIN_LOG_LEVEL"]  = "3"

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

# ── Standard library ──────────────────────────────────────────────────────────
import time
import shutil
import tempfile
from contextlib import asynccontextmanager
from typing import Optional, Dict

# ── Third-party ───────────────────────────────────────────────────────────────
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # project root
SRC_DIR  = os.path.join(BASE_DIR, "src")

for p in (BASE_DIR, SRC_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Global ML state ───────────────────────────────────────────────────────────
classifier        = None
feature_extractor = None
model_loaded      = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier, feature_extractor, model_loaded
    try:
        print("🔧 Loading ML components...")
        from feature_extractor import FeatureExtractor
        from classifier import DeepfakeClassifier

        feature_extractor = FeatureExtractor()
        classifier        = DeepfakeClassifier()

        # Resolve model path relative to project root so it works from any CWD
        model_file = os.environ.get(
            "MODEL_PATH",
            os.path.join(BASE_DIR, "models", "classifier.pkl")
        )
        if os.path.exists(model_file):
            classifier.load_model(model_file)
            model_loaded = True
            print(f"✅ Model loaded: {model_file}")
        else:
            print(f"⚠  Model not found: {model_file}")
            print("   Train first → python train.py --mode train --real-dir <path> --fake-dir <path>")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Ensure src/ contains: feature_extractor.py, classifier.py, facial_dynamics_analyzer.py")
    except Exception as e:
        import traceback
        print(f"❌ Startup error: {e}")
        traceback.print_exc()

    yield
    print("🛑 Server shutdown")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Deepfake Detection API",
    description = "Eye Blink + Facial Dynamics deepfake detector",
    version     = "2.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # lock down in production (e.g. ["https://yourapp.com"])
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ── Response schema ───────────────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    success:         bool
    prediction:      str            # "REAL" | "FAKE" | "ERROR"
    confidence:      float
    processing_time: float
    video_info:      Dict
    blink_features:  Dict
    facial_dynamics: Dict
    error:           Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message":      "Deepfake Detection API v2.0",
        "model_loaded": model_loaded,
        "status":       "ready" if model_loaded else "model_not_loaded",
        "docs":         "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status":       "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_video(file: UploadFile = File(...)):
    """
    Upload a video (.mp4 / .avi / .mov / .mkv) → returns REAL / FAKE prediction.
    """
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    allowed = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {allowed}")

    # Save to temp file
    temp_dir  = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, f"upload{ext}")

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        start    = time.time()
        features = feature_extractor.extract_video_features(temp_path)
        prediction, confidence = classifier.predict(features)
        elapsed  = time.time() - start

        result = "FAKE" if prediction == 1 else "REAL"

        return PredictionResponse(
            success         = True,
            prediction      = result,
            confidence      = round(float(confidence), 4),
            processing_time = round(elapsed, 3),
            video_info = {
                "filename":     file.filename,
                "duration_sec": round(float(features.get("video_duration", 0)), 2),
                "total_frames": int(features.get("total_frames", 0)),
                "fps":          round(float(features.get("fps", 0)), 2),
            },
            blink_features = {
                "blink_rate":         round(float(features.get("avg_blink_rate", 0)), 4),
                "avg_blink_duration": round(float(features.get("avg_avg_blink_duration", 0)), 4),
                "avg_ear":            round(float(features.get("avg_avg_ear", 0)), 4),
                "blink_completeness": round(float(features.get("avg_avg_blink_completeness", 0)), 4),
            },
            facial_dynamics = {
                "sharpness":           round(float(features.get("dyn_sharpness_score_mean", 0)), 4),
                "symmetry":            round(float(features.get("dyn_avg_symmetry_score_mean", 0)), 4),
                "noise_level":         round(float(features.get("dyn_noise_level_mean", 0)), 4),
                "texture_entropy":     round(float(features.get("dyn_lbp_entropy_mean", 0)), 4),
                "mouth_aspect_ratio":  round(float(features.get("dyn_mouth_aspect_ratio_mean", 0)), 4),
                "optical_flow":        round(float(features.get("dyn_flow_mean_mean", 0)), 4),
                "head_yaw_jitter":     round(float(features.get("temporal_yaw_jitter", 0)), 4),
                "color_consistency":   round(float(features.get("dyn_hue_consistency_mean", 0)), 4),
                "skin_ratio":          round(float(features.get("dyn_skin_ratio_mean", 0)), 4),
                "boundary_flow_ratio": round(float(features.get("dyn_boundary_flow_ratio_mean", 0)), 4),
            },
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return PredictionResponse(
            success=False, prediction="ERROR", confidence=0.0,
            processing_time=0.0, video_info={}, blink_features={},
            facial_dynamics={}, error=str(e),
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("🚀 Deepfake Detection API  →  http://localhost:8000")
    print("📖 Interactive docs        →  http://localhost:8000/docs")
    uvicorn.run(
        "server:app",
        host       = "0.0.0.0",
        port       = 8000,
        reload     = True,
        reload_dirs= [BASE_DIR],
    )