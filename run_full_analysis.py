import subprocess
import sys

print("\n" + "="*70)
print("COMPLETE TRAFFIC SIMULATION ANALYSIS")
print("="*70)

steps = [
    ("1. Generating baseline metrics", "python3 generate_metrics.py"),
    ("2. Analyzing baseline results", "python3 compare_results.py"),
    ("3. Running multi-load experiments", "python3 run_multiload_experiments.py"),
    ("4. Analyzing multi-load results", "python3 analyze_multiload.py"),
]

print("\nThis will run the complete analysis pipeline:")
for i, (desc, _) in enumerate(steps, 1):
    print(f"  {desc}")

print("\nEstimated time: ~8 minutes")
response = input("\nContinue? (y/n): ")

if response.lower() != 'y':
    print("Cancelled.")
    sys.exit(0)

print("\n" + "="*70)

for i, (desc, cmd) in enumerate(steps, 1):
    print(f"\n[{i}/{len(steps)}] {desc}...")
    print("-" * 70)
    result = subprocess.run(cmd.split(), capture_output=False)
    if result.returncode != 0:
        print(f"\nError in step {i}. Stopping.")
        sys.exit(1)

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print("\nAll results are in:")
print("  - metrics/     (CSV data)")
print("  - results/     (plots and summaries)")
print("="*70 + "\n")
