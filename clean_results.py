import os
import shutil

folders_to_clean = ["metrics", "results"]

print("This will delete all generated metrics and results.")
response = input("Continue? (y/n): ")

if response.lower() != 'y':
    print("Cancelled.")
    exit(0)

for folder in folders_to_clean:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"Deleted {folder}/")

print("\nCleaned. Run generate_metrics.py or run_multiload_experiments.py to regenerate.")
