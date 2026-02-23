# Intelligent Emergency Dispatch Optimization System 🚑⚡

An advanced, AI-driven backend API that optimizes emergency medical dispatch routing. This project utilizes a hybrid approach, combining **Machine Learning (Random Forest Regressor)** for complex multi-variable fitness evaluation and a **Genetic Algorithm (GA)** for rapid search space optimization.

By evaluating real-time variables such as traffic, weather, hospital trauma capabilities, and the "Golden Hour" constraint for critical patients, the system efficiently matches available ambulances to the optimal hospital and route.

## 🚀 Key Features

* **Hybrid AI Architecture:** Uses a trained Random Forest model as the fitness function within a Genetic Algorithm.
* **RESTful API Endpoint:** Built with **FastAPI** to serve real-time dispatch optimizations to any frontend dashboard.
* **Clinical Triage Logic:** Dynamically weights travel time (ETA) against case severity, ensuring critical patients are routed to trauma centers while non-critical cases preserve specialized resources.
* **Rapid Convergence:** Hyperparameter-tuned Genetic Algorithm capable of finding the global optimum in fractions of a second.
* **CORS Ready:** Pre-configured for seamless integration with modern frontend frameworks (React, Vue, Vite).

## 📁 Project Structure

```text
Emergency-Response-Optimization/
│
├── backend/
│   ├── core/
│   │   └── ga_dispatch.py       # Core Genetic Algorithm logic
│   │
│   ├── ml_pipeline/
│   │   ├── generate_data.py     # Generates synthetic dispatch scenarios
│   │   └── train_model.py       # Trains the Random Forest fitness evaluator
│   │
│   ├── artifacts/           # Contains saved_model.pkl and metric charts
│   ├── data/                    # Generated CSVs (ambulances, hospitals)
│   ├── logs/                    # Audit logs of optimal GA runs
│   │
│   ├── api.py                   # FastAPI server entry point
│   ├── main.py                  # CLI runner (Alternative to API)
│   └── requirements.txt         # Pinned dependencies
│
├── .gitignore
└── README.md
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/username/Emergency-Response-Optimization.git](https://github.com/username/Emergency-Response-Optimization.git)
   cd Emergency-Response-Optimization/backend
   ```

2. **Create and activate a virtual environment:**
   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **Mac/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚦 How to Run the System

Ensure your terminal is inside the `backend/` directory and your virtual environment is activated.

### Phase 1: Data Generation & Training (Run Once)
```bash
python ml_pipeline/generate_data.py
python ml_pipeline/train_model.py
```

### Phase 2: Start the API Server
To spin up the live backend server, run:
```bash
uvicorn api:app --reload
```
The API will start running at `http://127.0.0.1:8000`.

## 📡 API Usage & Documentation

FastAPI automatically generates an interactive UI to test your endpoints. 
Once the server is running, navigate to: **`http://127.0.0.1:8000/docs`**

You can test the `/optimize` endpoint directly from your browser by sending a JSON payload:
```json
{
  "case_severity": 1
}
```
The server will return the optimal `ambulance_id`, `hospital_id`, and route index in milliseconds while printing the GA epoch progress directly to your terminal.