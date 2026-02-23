import random
import joblib
import pandas as pd
import os
import time
import csv

# Load model once
model = joblib.load("artifacts/saved_model.pkl")
model.n_jobs = 1

NUM_ROUTES = 5

class DispatchEnvironment:
    """Encapsulates the state so it isn't executed on import."""
    def __init__(self, force_rewrite=True):
        self.ambulances, self.hospitals = self._generate_and_store_resources(force_rewrite)
        self.state = {
            "traffic_level": random.uniform(0.2, 0.9),
            "weather_severity": random.uniform(0.1, 0.8),
            "distance_km": random.randint(5, 20),
            "hospital_load": random.uniform(0.3, 0.9),
            "case_severity": random.choice([0, 1])
        }

    def _generate_and_store_resources(self, force_rewrite):
        os.makedirs("data", exist_ok=True)
        ambulance_path = "data/ambulances.csv"
        hospital_path = "data/hospitals.csv"

        if not force_rewrite and os.path.exists(ambulance_path) and os.path.exists(hospital_path):
            ambulances = pd.read_csv(ambulance_path).to_dict(orient="records")
            hospitals = pd.read_csv(hospital_path).to_dict(orient="records")
            return ambulances, hospitals

        ambulances = [{"id": f"A{i}", "eta": random.randint(3, 15), "equipment": random.randint(0, 1)} for i in range(20)]
        hospitals = [{"id": f"H{i}", "trauma_center": random.randint(0, 1), "icu_beds": random.randint(1, 20)} for i in range(15)]

        pd.DataFrame(ambulances).to_csv(ambulance_path, index=False, mode="w")
        pd.DataFrame(hospitals).to_csv(hospital_path, index=False, mode="w")

        return ambulances, hospitals


class Chromosome:
    def __init__(self, num_ambulances, num_hospitals):
        self.ambulance_index = random.randrange(num_ambulances)
        self.hospital_index = random.randrange(num_hospitals)
        self.route_index = random.randrange(NUM_ROUTES)
        self.fitness_score = float("inf")


class GeneticAlgorithm:
    def __init__(self, env: DispatchEnvironment, population_size=30, epochs=100,
                 mutation_rate=0.2, early_stop_patience=8):
        self.env = env
        self.population_size = population_size
        self.epochs = epochs
        self.base_mutation_rate = mutation_rate
        self.mutation_rate = mutation_rate
        self.early_stop_patience = early_stop_patience

    def initialize(self):
        num_amb = len(self.env.ambulances)
        num_hosp = len(self.env.hospitals)
        return [Chromosome(num_amb, num_hosp) for _ in range(self.population_size)]

    def evaluate_population(self, population):
        """Evaluates the entire population in a single batch prediction."""
        rows = []
        for chrom in population:
            amb = self.env.ambulances[chrom.ambulance_index]
            hosp = self.env.hospitals[chrom.hospital_index]
            
            route_multiplier = 1 + (chrom.route_index * self.env.state["traffic_level"])
            adjusted_eta = amb["eta"] * route_multiplier

            rows.append([
                adjusted_eta, amb["equipment"], hosp["trauma_center"], hosp["icu_beds"],
                self.env.state["traffic_level"], self.env.state["weather_severity"],
                self.env.state["distance_km"], self.env.state["hospital_load"],
                self.env.state["case_severity"]
            ])

        columns = [
            "eta", "equipment", "trauma_center", "icu_beds",
            "traffic_level", "weather_severity",
            "distance_km", "hospital_load", "case_severity"
        ]
        
        # Batch prediction is significantly faster
        batch_df = pd.DataFrame(rows, columns=columns)
        predictions = model.predict(batch_df)

        for i, chrom in enumerate(population):
            chrom.fitness_score = predictions[i]

        population.sort(key=lambda c: c.fitness_score)

    def select_parent(self, population):
        tournament = random.sample(population, 2)
        # tournament is already small, but min() is slightly faster than sorting
        return min(tournament, key=lambda c: c.fitness_score)

    def evolve(self, population):
        new_population = population[:1] # Elitism
        num_amb = len(self.env.ambulances)
        num_hosp = len(self.env.hospitals)

        while len(new_population) < self.population_size:
            p1 = self.select_parent(population)
            p2 = self.select_parent(population)

            child = Chromosome(num_amb, num_hosp)
            child.ambulance_index = random.choice([p1.ambulance_index, p2.ambulance_index])
            child.hospital_index = random.choice([p1.hospital_index, p2.hospital_index])
            child.route_index = random.choice([p1.route_index, p2.route_index])

            if random.random() < self.mutation_rate:
                child.ambulance_index = random.randrange(num_amb)
            if random.random() < self.mutation_rate:
                child.hospital_index = random.randrange(num_hosp)
            if random.random() < self.mutation_rate:
                child.route_index = random.randrange(NUM_ROUTES)

            new_population.append(child)

        return new_population

    def run(self):
        start_time = time.time()
        population = self.initialize()
        self.evaluate_population(population)

        best = population[0]
        no_improvement_counter = 0

        print("\nGENETIC ALGORITHM PROGRESS")
        print("-" * 53)

        for epoch in range(self.epochs):
            population = self.evolve(population)
            self.evaluate_population(population)

            current_best = population[0]
            diversity = len(set((c.ambulance_index, c.hospital_index, c.route_index) for c in population))

            if diversity < 6:
                self.mutation_rate = min(0.5, self.base_mutation_rate * 2)
            else:
                self.mutation_rate = self.base_mutation_rate

            if current_best.fitness_score < best.fitness_score:
                best = current_best
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1

            print(f"Epoch {epoch+1:3d} | Fitness: {best.fitness_score:8.2f} | Diversity: {diversity} | Mutation: {self.mutation_rate:.2f}", flush=True)

            if no_improvement_counter >= self.early_stop_patience:
                print("\nEarly stopping triggered.")
                break

        execution_time = round(time.time() - start_time, 3)
        self.log_run(best, execution_time)
        return best

    def log_run(self, best, execution_time):
        os.makedirs("logs", exist_ok=True)
        log_path = "logs/ga_runs.csv"
        
        file_exists = os.path.exists(log_path)
        
        # Standard CSV writing is faster and lighter than Pandas for appending single rows
        with open(log_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["fitness", "ambulance", "hospital", "route", "execution_time", "traffic_level", "weather_severity"])
                
            writer.writerow([
                best.fitness_score,
                self.env.ambulances[best.ambulance_index]["id"],
                self.env.hospitals[best.hospital_index]["id"],
                best.route_index,
                execution_time,
                self.env.state["traffic_level"],
                self.env.state["weather_severity"]
            ])