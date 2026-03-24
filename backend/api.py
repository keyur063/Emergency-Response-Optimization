from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid

from core.ga_dispatch import GeneticAlgorithm, DispatchEnvironment
from vision.predict import predict as analyze_accident_image

app = FastAPI(
    title="Intelligent Dispatch API",
    description="API for optimizing emergency ambulance routing using ML, Genetic Algorithms, and CNN Vision.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,        
    allow_methods=["*"],           
    allow_headers=["*"],           
)

class DispatchRequest(BaseModel):
    case_severity: int 

@app.post("/optimize")
async def optimize_dispatch(request: DispatchRequest):
    env = DispatchEnvironment(force_rewrite=False)
    env.state["case_severity"] = request.case_severity
    
    ga = GeneticAlgorithm(env=env, population_size=40, epochs=50, mutation_rate=0.1, early_stop_patience=10)
    best_chromosome = ga.run()
    
    ambulance = env.ambulances[best_chromosome.ambulance_index]
    hospital = env.hospitals[best_chromosome.hospital_index]
    
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

@app.post("/optimize-with-vision")
async def optimize_dispatch_vision(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No valid file name detected in upload.")
        
        os.makedirs("uploads", exist_ok=True)
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"crash_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join("uploads", unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        cnn_result = analyze_accident_image(image_input=file_path, verbose=False)
        
        if not cnn_result["is_accident"]:
            return {
                "status": "rejected",
                "message": f"No accident detected. (Confidence: {cnn_result['accident_conf']*100:.1f}%)"
            }
            
        ga_severity = cnn_result["severity_index"]
        
        env = DispatchEnvironment(force_rewrite=False)
        env.state["case_severity"] = ga_severity
        
        ga = GeneticAlgorithm(env=env, population_size=40, epochs=50, mutation_rate=0.1, early_stop_patience=10)
        best_chromosome = ga.run()
        
        ambulance = env.ambulances[best_chromosome.ambulance_index]
        hospital = env.hospitals[best_chromosome.hospital_index]
        
        return {
            "status": "success",
            "vision_analysis": {
                "severity_level": cnn_result["severity_index"],
                "confidence": round(cnn_result["severity_conf"] * 100, 2) if cnn_result["severity_conf"] else 0
            },
            "dispatch_details": {
                "ambulance_id": ambulance["id"],
                "hospital_id": hospital["id"],
                "route_index": best_chromosome.route_index,
                "fitness_score": round(best_chromosome.fitness_score, 4)
            },
            "environment_context": env.state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))