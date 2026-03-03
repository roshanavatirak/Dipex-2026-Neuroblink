🧠 DOA-NET: Spatio-Temporal Deepfake Detection using Eye Blink Patterns

Dynamic Ocular Analysis Network (DOA-NET) is a spatio-temporal deepfake detection system that leverages periocular physiological cues, specifically eye blinking dynamics, to detect high-quality deepfake videos.

This project addresses the limitations of spatial-only deepfake detectors by integrating CNN-based spatial analysis with LSTM-based temporal modeling of Eye Aspect Ratio (EAR) signals.

📌 Key Highlights

✅ Hybrid CNN + LSTM architecture


👁️ Physiological signal-based detection (Eye Blinking)

⏱️ Spatio-temporal feature fusion

🔍 Grad-CAM explainability for forensic analysis

🌍 Cross-dataset generalization

⚡ Real-time inference support

Video Input
   ↓
Frame Extraction
   ↓
Face & Eye Landmark Detection (MediaPipe)
   ↓
Eye Region Cropping
   ↓
┌───────────────┬────────────────┐
│ Spatial Path  │ Temporal Path   │
│ (CNN)         │ (EAR → LSTM)    │
└───────────────┴────────────────┘
        ↓ Feature Fusion
        ↓
   Binary Classification
        ↓
   Real / Fake Output
        ↓
   Grad-CAM Visualization


🛠️ Tech Stack

Language: Python 3.8+

Deep Learning: TensorFlow / Keras

Computer Vision: OpenCV, MediaPipe

ML Utilities: NumPy, Pandas, Scikit-learn

Visualization: Matplotlib, Seaborn

Backend API: FastAPI

Frontend: React (Vite)

Deployment: Uvicorn

📂 Project Structure
deepfake_detection/
│
├── data/
│   ├── real_videos/
│   └── fake_videos/
│
├── models/
│   └── classifier.pkl
│
├── reports/
│   └── prediction_reports/
│
├── src/
│   ├── preprocessing/
│   ├── feature_extraction/
│   ├── model/
│   └── utils/
│
├── train.py
├── predict.py
├── main.py
├── requirements.txt
└── README.md

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/roshanavatirak/NeuroBlink---Deepfake-Video-Detection-by-using-Eye-Blink-Pattern.git
cd NeuroBlink

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Initialize MediaPipe
python -c "import mediapipe as mp; mp.solutions.face_mesh.FaceMesh()"

🧠 Training the Model
Basic Training
python train.py --real-dir data/real_videos --fake-dir data/fake_videos

Advanced Options

Train with SVM classifier

python train.py --real-dir data/real_videos --fake-dir data/fake_videos --model-type svm


Custom model save path

python train.py --real-dir data/real_videos --fake-dir data/fake_videos --model-path models/my_classifier.pkl


Skip visualizations (faster training)

python train.py --real-dir data/real_videos --fake-dir data/fake_videos --no-visualizations

🔍 Making Predictions
Single Video
python predict.py --video test_video.mp4

With HTML Report
python predict.py --video test_video.mp4 --save-report

Real-Time Visualization
python predict.py --video test_video.mp4 --visualize

All Options Combined
python predict.py --video test_video.mp4 --save-report --visualize --model models/classifier.pkl

Batch Prediction
python predict.py --batch-dir test_videos/ --output batch_results.json

🚀 Running the Backend (FastAPI)
venv\Scripts\activate
uvicorn main:app --reload


Backend available at:

http://127.0.0.1:8000

🎨 Running the Frontend
npm install
npm run dev

📊 Performance Summary
Dataset	Accuracy	AUC
FaceForensics++	99.1%	0.998
Celeb-DF (v2)	97.6%	0.991
DFDC	91.2%	0.953
🧪 Core Insight

Deepfake models struggle to replicate the natural variability and spontaneity of human eye blinking.
DOA-NET exploits this physiological limitation using spatio-temporal modeling.

🔮 Future Scope

Multimodal fusion (audio + head pose)

Compression-robust detection

Diffusion-based deepfake adaptation

LLM-assisted forensic explanation

Real-time deployment optimization

👨‍🔬 Authors

Dr. Nikita Mohod

Dr. Amar Sable

Shravani Balapure

Roshan Avatirak

Anand Tayde

Nishchay Sahu

Pratik Girnare

Department of Computer Science & Engineering
Sipna College of Engineering and Technology, Amravati, India
