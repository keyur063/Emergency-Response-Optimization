from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.ga_dispatch import GeneticAlgorithm, DispatchEnvironment

# Initialize FastAPI App
app = FastAPI(
    title="Intelligent Dispatch API",
    description="API for optimizing emergency ambulance routing using ML and Genetic Algorithms.",
    version="1.0.0"
)

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=True,        
    allow_methods=["*"],           
    allow_headers=["*"],           
)

# SCHEMAS
class DispatchRequest(BaseModel):
    case_severity: int  # 0 for minor, 1 for critical

# API ROUTES
@app.post("/optimize")
async def optimize_dispatch(request: DispatchRequest):
    print(f"\n[API] Received dispatch request. Case Severity: {request.case_severity}")
    
    # Initialize environment safely without rewriting CSVs
    env = DispatchEnvironment(force_rewrite=False)
    
    # Inject the specific API request parameters into the environment
    env.state["case_severity"] = request.case_severity
    
    # Initialize and run the Genetic Algorithm
    ga = GeneticAlgorithm(
        env=env,
        population_size=40,
        epochs=50,
        mutation_rate=0.1,
        early_stop_patience=10
    )
    
    best_chromosome = ga.run()
    
    # Extract final route info
    ambulance = env.ambulances[best_chromosome.ambulance_index]
    hospital = env.hospitals[best_chromosome.hospital_index]
    
    print("\n[API] Optimization complete. Returning JSON response.")
    
    return {
        "status": "success",
        "dispatch_details": {
            "ambulance_id": ambulance["id"],
            "hospital_id": hospital["id"],
            "route_index": best_chromosome.route_index,
            "fitness_score": round(best_chromosome.fitness_score, 4)
        },
        "environment_context": env.state
    }

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Dispatch optimization server is running."}