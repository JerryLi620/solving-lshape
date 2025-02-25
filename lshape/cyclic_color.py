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

def generate_single_color_clauses(N, write=False, filename="single_color.cnf"):
    """
    Generate a DIMACS CNF file for a one-color assignment on an N x N grid.
    
    If N is even:
      - Every cell belongs to a unique orbit (quadruple) under 90° rotations.
    If N is odd:
      - The center cell at ((N+1)//2, (N+1)//2) is fixed to be colored.
    
    Constraints added:
      1. Quadruple constraints:
         - For each orbit (of 4 cells for even or non‑center cells for odd grids), 
           add a clause ensuring that at least one cell is colored.
         - And for every pair of cells in an orbit, add a clause forbidding both
           from being colored simultaneously.
           
      2. L‑shape avoidance constraints:
         - For each L‑shape of three cells with equal leg length (in four orientations),
           add a clause forbidding all three cells from being colored simultaneously.
    
    After solving the CNF for the one‑color assignment, one can produce a full
    four‑color assignment by rotating the solution by 90°, 180° and 270°.
    
    Parameters:
       N (int): The grid dimension.
       filename (str): The name of the output DIMACS CNF file.
    """
    num_variables = N * N  # one variable per cell
    clauses = []
    clause_count = 0
    seen = set()

    # If N is odd, fix the center cell to be colored.
    if N % 2 == 1:
        center = ((N + 1) // 2, (N + 1) // 2)
        clauses.append([var(center[0], center[1], N)])
        clause_count += 1
        seen.add(center)

    # --- 1. Quadruple Constraints ---
    #
    # Process each cell (unless already handled, e.g. the fixed center).
    for r in tqdm(range(1, N + 1), desc="Processing quadruple orbits"):
        for c in range(1, N + 1):
            if (r, c) in seen:
                continue
            # Compute the orbit (quadruple) under 90° rotations:
            cell1 = (r, c)
            cell2 = (c, N + 1 - r)
            cell3 = (N + 1 - r, N + 1 - c)
            cell4 = (N + 1 - c, r)
            orbit = {cell1, cell2, cell3, cell4}
            for pos in orbit:
                seen.add(pos)
            # At least one in the orbit is colored:
            clause = [var(pos[0], pos[1], N) for pos in orbit]
            clauses.append(clause)
            clause_count += 1
            # At most one: For every pair in the orbit, add a clause that not both are colored.
            for a, b in combinations(orbit, 2):
                clauses.append([-var(a[0], a[1], N), -var(b[0], b[1], N)])
                clause_count += 1

    # --- 2. L-shape Avoidance Constraints ---
    #
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
                    -var(r, c - i, N),
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
            f.write(f"p cnf {num_variables} {clause_count}\n")
            for c in clauses:
                f.write(" ".join(map(str, c)) + " 0\n")
    return clauses


def decode_one_color_grid(sat_output, N):
    """
    Decodes the SAT solver output into an N x N one-color grid.
    
    The SAT output is assumed to be a list (or a space‐separated string) of integers.
    The encoding is:
         variable number = (r-1)*N + c,  for 1 <= r,c <= N.
    A positive literal indicates that the corresponding cell is “colored” (set to 1).
    All other cells remain 0.
    
    Parameters:
        sat_output (list or str): SAT output as a list of integers or as a string.
        N (int): Grid dimension.
    
    Returns:
        one_color_grid (np.array): An N x N binary NumPy array.
    """
    # If sat_output is a string, convert it to a list of integers.
    if isinstance(sat_output, str):
        sat_output = list(map(int, sat_output.split()))
    
    grid = np.zeros((N, N), dtype=int)
    for v in sat_output:
        if v > 0:
            # Decode using: r = (v-1) // N, c = (v-1) % N.
            r = (v - 1) // N
            c = (v - 1) % N
            grid[r][c] = 1
    return grid

def one_color_to_four_color(one_color_grid):
    """
    Given a one-color solution grid (with 1's indicating the chosen cell in each orbit),
    this function builds a full four-color grid by “rotating” the one-color assignment.
    
    For each orbit (a quadruple of cells related by 90° rotations), the orbit is defined as:
       Position 0: (r, c)
       Position 1: (c, N-1-r)
       Position 2: (N-1-r, N-1-c)
       Position 3: (N-1-c, r)
    
    If the one-color solution marks a cell at position j (0-based) in the orbit, then we assign:
       orbit[j]         -> color 1
       orbit[(j+1)%4]   -> color 2
       orbit[(j+2)%4]   -> color 3
       orbit[(j+3)%4]   -> color 4
    
    Parameters:
        one_color_grid (np.array): A binary N x N grid.
        
    Returns:
        four_color_grid (np.array): An N x N grid with values 1..4 assigned per orbit.
    """
    N = one_color_grid.shape[0]
    four_color_grid = np.zeros((N, N), dtype=int)
    processed = np.zeros((N, N), dtype=bool)
    
    for r in range(N):
        for c in range(N):
            if processed[r, c]:
                continue
            # Compute the orbit of cell (r, c) using 0-indexing.
            orbit = [
                (r, c),
                (c, N-1-r),
                (N-1-r, N-1-c),
                (N-1-c, r)
            ]
            # Mark all positions in this orbit as processed.
            for (rr, cc) in orbit:
                processed[rr, cc] = True
            # Find which position in the orbit is "colored" (i.e. has a 1).
            colored_index = None
            for idx, (rr, cc) in enumerate(orbit):
                if one_color_grid[rr, cc] == 1:
                    colored_index = idx
                    break
            # If no cell is marked in this orbit, leave it as zeros.
            if colored_index is None:
                continue
            # Assign colors cyclically.
            for offset in range(4):
                pos = orbit[(colored_index + offset) % 4]
                # Colors will be 1, 2, 3, 4.
                four_color_grid[pos] = offset + 1
    return four_color_grid

def visualize_four_color_grid(four_color_grid):
    """
    Visualizes a four-color grid.
    
    The grid values are interpreted as:
         0 -> (should not occur, or black as background),
         1 -> blue,
         2 -> red,
         3 -> green,
         4 -> yellow.
    
    Parameters:
        four_color_grid (np.array): An N x N grid with values in {0,1,2,3,4}.
    """
    cmap = mcolors.ListedColormap(['black', 'blue', 'red', 'green', 'yellow'])
    N = four_color_grid.shape[0]
    plt.figure(figsize=(8, 8))
    # Set vmin and vmax so that each integer value gets its own color.
    plt.imshow(four_color_grid, cmap=cmap, origin='upper', vmin=-0.5, vmax=4.5)
    plt.axis('off')
    plt.title("Four-Color Grid from One-Color Solution")
    plt.savefig(f"cyclic_four_color_{N}.jpg", bbox_inches='tight')
    plt.show()

def visualize_rotated_solution(sat_output, N):
    """
    Given the SAT solver output (one-color assignment) for the L-shape avoidance problem,
    this function decodes the solution, builds a four-color grid by computing the 90°, 180°,
    and 270° rotations (via orbit decomposition), and visualizes the final grid.
    
    Parameters:
        sat_output (list or str): SAT solver output as a list of integers or a string.
        N (int): Dimension of the grid.
    """
    # Step 1: Decode the one-color grid.
    one_color_grid = decode_one_color_grid(sat_output, N)
    print("One-Color Grid:")
    print(one_color_grid)
    
    # Step 2: Convert the one-color grid into a four-color grid.
    four_color_grid = one_color_to_four_color(one_color_grid)
    print("Four-Color Grid:")
    print(four_color_grid)
    
    # Step 3: Visualize the four-color grid.
    visualize_four_color_grid(four_color_grid)


if __name__ == "__main__":
    # N must be even.
    N = 17
    # Generate clauses for a one-color assignment.
    clauses = generate_single_color_clauses(N, write = False)
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        print(model)
        visualize_rotated_solution(model, N)
    else:
        print("No solution found.")


