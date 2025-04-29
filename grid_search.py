from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import subprocess
import os
import pandas as pd
import numpy as np
import re
from tqdm import tqdm

param_grid = {
    '--ands': [1, 0],
    '--bumpreasonsrate': [10, 1],
    '--chrono': [1, 0],
    '--eliminateint': [500, 50],
    '--eliminateocclim': [2000, 20],
    '--forwardeffort': [100, 200],
    '--ifthenelse': [1, 0],
    '--probeint': [100, 10],
    '--rephaseint': [1000, 100],
    '--stable': [1, 0],
    '--substituteeffort': [10, 20],
    '--subsumeocclim': [1000, 10],
    '--vivifyeffort': [100, 200]
}

keys = list(param_grid.keys())
combinations = list(itertools.product(*(param_grid[key] for key in keys)))

input_cnf = "lshape_20_3.cnf"
time_limit = 500
num_workers = 8
print(f"Number of workers: {num_workers}")

def run_kissat(combo):
    params = dict(zip(keys, combo))
    param_str = " ".join(f"{key}={value}" for key, value in params.items())
    command = f"kissat/build/kissat --time={time_limit} {param_str} {input_cnf}"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        stdout = result.stdout + result.stderr
        match = re.search(r"process-time:.*?([0-9.]+)\s+seconds", stdout)
        runtime = float(match.group(1)) if match else None
        print(f"Runtime: {runtime}, Return code: {result.returncode}")
        return {**params, 'runtime': runtime, 'return_code': result.returncode}
    except Exception as e:
        return {**params, 'runtime': None, 'return_code': -1}

# Parallel execution with progress bar
results = []
with ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = [executor.submit(run_kissat, combo) for combo in combinations]
    for f in tqdm(as_completed(futures), total=len(futures), desc="Parallel grid search"):
        results.append(f.result())

# Save results
df = pd.DataFrame(results)
df.to_csv("runtime_grid_search_20.csv", index=False)
np.save("runtime_grid_search_20.npy", df.to_numpy())
print("Saved runtime results")

