from itertools import combinations
from tqdm import tqdm
from pysat.solvers import Glucose3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def var(r, c, N):
    """
    Map grid cell (r, c) (with 1-based indexing) to a unique DIMACS variable number.
    """
    assert 1 <= r <= N and 1 <= c <= N
    return (r - 1) * N + c

def generate_single_color_clauses(N, write = False, filename="single_color.cnf"):
    """
    Generate a DIMACS CNF file for a one-color assignment on an N x N grid.
    
    Assumptions:
      - N is even (so that every cell belongs to a unique quadruple under 90° rotations).
      - A cell variable is True when that cell is colored.
      
    Constraints added:
      1. **Quadruple constraints:**  
         Every cell is in an orbit of four cells under 90° rotations.  
         In each orbit, exactly one cell is colored.  
         This is encoded as:
           - One clause: (v1 ∨ v2 ∨ v3 ∨ v4)
           - And for each pair (vi, vj) in the orbit, a clause: (¬vi ∨ ¬vj)
           
      2. **L-shape avoidance constraints:**  
         For every L‑shape of three cells with equal leg length, add a clause
         that forbids all three from being colored simultaneously.
         
         Four orientations are encoded:
           - Orientation 1 (0° rotation): cells (r, c), (r+i, c), (r+i, c+i)
           - Orientation 2 (90° rotation): cells (r, c), (r+i, c), (r+i, c−i)
           - Orientation 3 (180° rotation): cells (r, c), (r−i, c), (r−i, c−i)
           - Orientation 4 (270° rotation): cells (r, c), (r, c+i), (r−i, c+i)
         For each valid triple, the clause is: (¬v(A) ∨ ¬v(B) ∨ ¬v(C))
    
    After solving the CNF for the one-color assignment, one can produce a full
    four-color assignment by rotating the solution by 90°, 180° and 270°.
    
    Parameters:
       N (int): The grid dimension (must be even).
       filename (str): The name of the output DIMACS CNF file.
    """
    num_variables = N * N  # one variable per cell
    clauses = []
    clause_count = 0

    # --- 1. Quadruple Constraints ---
    #
    # Each cell belongs to a unique orbit (quadruple) under the 90° rotation group.
    # For a cell (r, c), its orbit is:
    #    (r, c)
    #    (c, N+1-r)
    #    (N+1-r, N+1-c)
    #    (N+1-c, r)
    #
    # We only add the constraint once per orbit (using a seen set).
    seen = set()
    for r in tqdm(range(1, N + 1), desc="Processing quadruple orbits"):
        for c in range(1, N + 1):
            if (r, c) in seen:
                continue
            # Compute the orbit (quadruple) of (r, c)
            cell1 = (r, c)
            cell2 = (c, N + 1 - r)
            cell3 = (N + 1 - r, N + 1 - c)
            cell4 = (N + 1 - c, r)
            orbit = {cell1, cell2, cell3, cell4}
            for pos in orbit:
                seen.add(pos)
            # Constraint: Exactly one cell in the orbit is colored.
            # At least one is colored:
            clause = [var(pos[0], pos[1], N) for pos in orbit]
            clauses.append(clause)
            clause_count += 1
            # At most one: for every pair in the orbit, add a clause that not both are colored.
            for a, b in combinations(orbit, 2):
                clause = [-var(a[0], a[1], N), -var(b[0], b[1], N)]
                clauses.append(clause)
                clause_count += 1

    # --- 2. L-shape Avoidance Constraints ---
    #
    # For each of the four orientations, we add a clause to forbid an L-shape
    # triple from all being colored.
    
    # Orientation 1: cells (r, c), (r+i, c), (r+i, c+i)
    for r in tqdm(range(1, N + 1), desc="L-shape orientation 1"):
        for c in range(1, N + 1):
            max_i = min(N - r, N - c)
            for i in range(1, max_i + 1):
                clause = [
                    -var(r, c, N),
                    -var(r + i, c, N),
                    -var(r + i, c + i, N)
                ]
                clauses.append(clause)
                clause_count += 1

    # Orientation 2: cells (r, c), (r, c-i), (r+i, c-i)
    for r in tqdm(range(1, N + 1), desc="L-shape orientation 2"):
        for c in range(1, N + 1):
            max_i = min(N - r, c - 1)
            for i in range(1, max_i + 1):
                clause = [
                    -var(r, c, N),
                    -var(r, c - 1, N),
                    -var(r + i, c - i, N)
                ]
                clauses.append(clause)
                clause_count += 1

    # Orientation 3: cells (r, c), (r-i, c), (r-i, c-i)
    for r in tqdm(range(1, N + 1), desc="L-shape orientation 3"):
        for c in range(1, N + 1):
            max_i = min(r - 1, c - 1)
            for i in range(1, max_i + 1):
                clause = [
                    -var(r, c, N),
                    -var(r - i, c, N),
                    -var(r - i, c - i, N)
                ]
                clauses.append(clause)
                clause_count += 1

    # Orientation 4: cells (r, c), (r, c+i), (r-i, c+i)
    for r in tqdm(range(1, N + 1), desc="L-shape orientation 4"):
        for c in range(1, N + 1):
            max_i = min(r - 1, N - c)
            for i in range(1, max_i + 1):
                clause = [
                    -var(r, c, N),
                    -var(r, c + i, N),
                    -var(r - i, c + i, N)
                ]
                clauses.append(clause)
                clause_count += 1
    if write:
        with open(filename, "w") as f:
            f.seek(0, 0)
            f.write(f"p cnf {num_variables} {clause_count}\n")
            for c in clauses:
                f.write(" ".join(map(str, c)) + " 0\n")
    return clauses


def visualize_solution(sat_output, N, C):
    """
    Visualizes the SAT solver output for the L-shape avoidance problem as a color grid.
    
    Each grid cell is assigned a value from 1 to C. The solver's output is assumed to be a
    string of space-separated integers corresponding to the DIMACS variable numbering for the
    encoding where a variable is True if the cell (r, c) takes the value v. This function decodes
    the positive literals and fills in an N x N grid with the corresponding values.
    
    Parameters:
        sat_output_str (str): SAT solver output as a string of space-separated literals.
        N (int): Dimension of the grid (N x N).
        C (int): Number of possible values (colors) per cell.
    """
    grid = np.zeros((N, N), dtype=int)
    
    for v in sat_output:
        if v > 0:
            r = (v-1) // N 
            c = (v-1) % N 
            grid[r][c] = 1

    # cmap = mcolors.ListedColormap(['black', 'blue', 'red', 'green', 'yellow'])
    cmap = mcolors.ListedColormap(['black', 'blue'])
    print(grid)
    plt.figure(figsize=(8, 8))
    plt.imshow(grid, cmap=cmap, origin='upper', vmin=-0.5, vmax=1.5)
    plt.axis('off')
    plt.title("Single Coloring Grid")
    plt.savefig(f"cyclic_{N}.jpg", bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # N must be even.
    N = 20
    # Generate clauses for a one-color assignment.
    clauses = generate_single_color_clauses(N, write = True)
    # solver = Glucose3()
    # for clause in clauses:
    #     solver.add_clause(clause)

    # if solver.solve():
    #     model = solver.get_model()
    #     print(model)
    #     visualize_solution(model, N, 1)
    # else:
    #     print("No solution found.")


