import pandas as pd
import random
import os

NUM_SAMPLES = 5000
data = []

for _ in range(NUM_SAMPLES):
    eta = random.randint(3, 20)
    equipment = random.choice([0, 1])
    trauma_center = random.choice([0, 1])
    icu_beds = random.randint(0, 15)
    traffic_level = random.uniform(0, 1)
    weather_severity = random.uniform(0, 1)
    distance_km = random.uniform(1, 25)
    hospital_load = random.uniform(0, 1)
    case_severity = random.choice([0, 1, 2])

    # Increased baseline weight for time and distance
    time_penalty = (eta * 2.5) * (1 + traffic_level) 
    distance_penalty = distance_km * (1 + weather_severity) 
    load_penalty = (hospital_load ** 2) * 20
    bed_bonus = icu_beds * 1.5

    score = time_penalty + distance_penalty + load_penalty - bed_bonus

    # Dynamic scoring based on severity
    if case_severity == 1:
        # Exponential penalty for high ETA in severe cases (The Golden Hour rule)
        score += (eta ** 1.5) 

        if trauma_center == 0:
            score += 50  
        else:
            score -= 25  

        if equipment == 0:
            score += 35  
    else:
        # For non-critical cases, lightly penalize using a trauma center to save resources
        if trauma_center == 1:
            score += 15  

    # Add realistic noise
    score += random.uniform(-5, 5)

    data.append([
        eta, equipment, trauma_center, icu_beds,
        traffic_level, weather_severity,
        distance_km, hospital_load,
        case_severity, score
    ])

columns = [
    "eta", "equipment", "trauma_center", "icu_beds",
    "traffic_level", "weather_severity",
    "distance_km", "hospital_load",
    "case_severity", "dispatch_score"
]

os.makedirs("data", exist_ok=True)
pd.DataFrame(data, columns=columns).to_csv("data/synthetic_data.csv", index=False)

print("Optimized synthetic data generated successfully.")