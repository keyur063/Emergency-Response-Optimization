from core.ga_dispatch import GeneticAlgorithm, DispatchEnvironment

if __name__ == "__main__":
    print("\nStarting Intelligent Dispatch Optimization...\n")

    # Initialize the environment safely here
    env = DispatchEnvironment(force_rewrite=True)

    ga = GeneticAlgorithm(
        env=env,
        population_size=40,    
        epochs=50,             
        mutation_rate=0.1,     
        early_stop_patience=10 
    )

    best = ga.run()

    ambulance = env.ambulances[best.ambulance_index]
    hospital = env.hospitals[best.hospital_index]

    print("\nFINAL OPTIMAL DISPATCH")
    print("-" * 53)
    print(f"Ambulance ID : {ambulance['id']}")
    print(f"Hospital ID  : {hospital['id']}")
    print(f"Route Index  : {best.route_index}")
    print(f"Fitness Score: {best.fitness_score:.4f}")
    print("-" * 53)

    print("\nRun successfully logged to logs/ga_runs.csv\n")