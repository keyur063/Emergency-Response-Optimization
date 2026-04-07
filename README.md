```markdown
# 🚑 SmartDispatch: Multi-Modal AI Emergency Routing System

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688)
![AI/ML](https://img.shields.io/badge/AI%2FML-PyTorch%20%7C%20Scikit--Learn-EE4C2C)

## 📌 The Problem
During critical emergencies, dispatchers rely on subjective, panicked descriptions to gauge accident severity. Simultaneously, legacy routing systems rely on static "shortest-path" metrics, ignoring dynamic variables like traffic density and severe weather. This inefficiency severely impacts the 60-minute "Golden Hour" of trauma survival.

## 🚀 Our Solution
**SmartDispatch** is a highly decoupled, multi-modal emergency response platform. It fuses Computer Vision for objective triage with a custom Evolutionary Algorithm (Genetic Algorithm + Random Forest) to calculate the absolute optimal ambulance-hospital dispatch pairing in under a second.

### ✨ Key Features
- **👁️ Auto-Triage (Vision AI):** Upload accident scene images to instantly classify severity using a custom PyTorch MobileNetV2 CNN architecture.
- **🎛️ Dual-Mode Command Center:** Allows dispatchers to override AI with manual condition parameters (Level 0 to Level 2 Critical Trauma).
- **🧬 Intelligent Routing Engine:** Utilizes a custom Genetic Algorithm evaluating permutations against real-time traffic and weather metrics, scored by a Random Forest fitness function.
- **🗺️ MediTrak Live Map:** A seamlessly integrated Leaflet.js geographic tracker utilizing OSRM (Open Source Routing Machine) and Nominatim geocoding for real-time ambulance tracking.
- **💎 Glassmorphism UI:** A sleek, dark-themed, and responsive command center built with React.

---

## 💻 Tech Stack

### Frontend Architecture
* **Framework:** React.js powered by Vite for lightning-fast HMR.
* **Geospatial Mapping:** Leaflet.js, Leaflet Routing Machine.
* **Styling:** Custom CSS with Glassmorphism principles and dynamic flexbox/grid layouts.

### Backend Architecture (API Bridge)
* **Framework:** FastAPI (Python) for asynchronous, high-speed API endpoints.
* **Latency:** Sub-second processing (avg. 850ms turnaround for end-to-end vision and routing generation).

### Machine Learning Pipeline
* **Computer Vision:** PyTorch (MobileNetV2).
* **Optimization Algorithm:** Custom Genetic Algorithm (100 Epochs / Early Stopping).
* **Fitness Scoring:** Scikit-Learn (Random Forest Regressor).

---

## 🛠️ Installation & Setup

### Prerequisites
* Node.js (v18+)
* Python (v3.9+)
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/SmartDispatch.git](https://github.com/yourusername/SmartDispatch.git)
cd SmartDispatch
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*The React dashboard will be available at `http://localhost:5173`.*

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn main:app --reload
```
*The FastAPI backend will be available at `http://127.0.0.1:8000`.*

---
