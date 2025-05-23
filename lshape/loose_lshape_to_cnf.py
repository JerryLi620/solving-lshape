# A helper: get the Dimacs CNF variable number for the variable v {r, c, v} 
# encoding the fact that the cell at (r, c) has the value v
def var(r, c, v, N, C):
    assert(1 <= r <= N and 1 <= c <= N and 1 <= v <= C) 
    return (r - 1) * N * C + (c - 1) * C + (v - 1) + 1

def lshape_to_cnf(N, C, filename="lshape_loose.cnf"):
    """
    Encode L-shape avoidance with different side lengths into a CNF file.

    Parameters:
        N (int): The dimension of the grid.
        C (int): The number of possible values per cell (e.g., colors or labels).
        filename (str): The name of the file to output the CNF formula.
    """
    # Total variables in the CNF: N * N * C (number of cells * number of possible values)
    num_variables = N * N * C
    num_clauses = 0  # Count the number of clauses

    with open(filename, "w") as f:
        # Iterate over the grid cells
        for r in range(1, N + 1): 
            for c in range(1, N + 1):
                # 1. The cell at (r, c) has at least one value
                at_least_one_clause = [var(r, c, v, N, C) for v in range(1, C + 1)]
                f.write(" ".join(map(str, at_least_one_clause)) + " 0\n")
                num_clauses += 1

                # 2. The cell at (r, c) has at most one value (no two values can be true simultaneously)
                for v in range(1, C + 1):
                    for w in range(v + 1, C + 1):
                        at_most_one_clause = [-var(r, c, v, N, C), -var(r, c, w, N, C)]
                        f.write(" ".join(map(str, at_most_one_clause)) + " 0\n")
                        num_clauses += 1

                # 3. No L-shapes in the grid(can have different side length)
                for dr in range(1, N - r + 1):
                    for dc in range(1, N - c + 1):
                        for v in range(1, C + 1):
                            # Avoid L-shape with vertical side of length dr and horizontal side of length dc
                            no_lshape_clause1 = [
                                -var(r, c, v, N, C),
                                -var(r + dr, c, v, N, C),
                                -var(r + dr, c + dc, v, N, C)
                            ]
                            f.write(" ".join(map(str, no_lshape_clause1)) + " 0\n")
                            num_clauses += 1

                            # Avoid L-shape with horizontal side of length dc and vertical side of length dr
                            no_lshape_clause2 = [
                                -var(r, c, v, N, C),
                                -var(r, c + dc, v, N, C),
                                -var(r + dr, c + dc, v, N, C)
                            ]
                            f.write(" ".join(map(str, no_lshape_clause2)) + " 0\n")
                            num_clauses += 1

    # Write CNF header (at the beginning of the file)
    with open(filename, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"p cnf {num_variables} {num_clauses}\n" + content)

# Experiment
N=6
C=3
lshape_to_cnf(N, C, filename=f"loose_lshape_{N}_{C}.cnf")