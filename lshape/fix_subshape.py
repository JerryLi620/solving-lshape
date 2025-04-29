from pysat.solvers import Glucose3

def var(r, c, v, N, C):
    assert(1 <= r <= N and 1 <= c <= N and 1 <= v <= C) 
    return (r - 1) * N * C + (c - 1) * C + (v - 1) + 1

def reverse_var(var_id, N, C):
    id0 = var_id - 1
    r = id0 // (N * C) + 1
    c = (id0 % (N * C)) // C + 1
    v = (id0 % C) + 1
    return (r, c, v)

def lshape_to_cnf(N, C, fixed_subgrid=None, filename="lshape.cnf"):
    """
    Encode L-shape avoidance and fixed values into a CNF file.

    Parameters:
        N (int): Grid dimension (NxN).
        C (int): Number of colors/values.
        fixed_subgrid (list): List of tuples (r, c, v) for fixed values.
        filename (str): Output CNF filename.
    """
    num_variables = N * N * C
    num_clauses = 0
    clauses = []

    for r in range(1, N + 1):
        for c in range(1, N + 1):
            # Cell has at least one value
            at_least_one = [var(r, c, v, N, C) for v in range(1, C + 1)]
            clauses.append(at_least_one)
            num_clauses += 1

            # Cell has at most one value
            for v in range(1, C + 1):
                for w in range(v + 1, C + 1):
                    clauses.append([-var(r, c, v, N, C), -var(r, c, w, N, C)])
                    num_clauses += 1

            # No L-shapes
            if c > r:
                for i in range(1, N - c + 1):
                    for v in range(1, C + 1):
                        clauses.append([
                            -var(r, c, v, N, C),
                            -var(r + i, c, v, N, C),
                            -var(r + i, c + i, v, N, C)
                        ])
                        num_clauses += 1
            else:
                for i in range(1, N - r + 1):
                    for v in range(1, C + 1):
                        clauses.append([
                            -var(r, c, v, N, C),
                            -var(r + i, c, v, N, C),
                            -var(r + i, c + i, v, N, C)
                        ])
                        num_clauses += 1

    # Add fixed-value unit clauses
    if fixed_subgrid:
        for (r, c, v) in fixed_subgrid:
            assert 1 <= r <= N and 1 <= c <= N and 1 <= v <= C
            clauses.append([var(r, c, v, N, C)])
            num_clauses += 1

    # Write the CNF
    with open(filename, "w") as f:
        f.write(f"p cnf {num_variables} {num_clauses}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


def solve_lshape(N, C):
    """
    Build and solve the L-shape CNF using PySAT's Glucose3 solver.

    Parameters:
        N (int): Grid size.
        C (int): Number of values per cell.
        fixed_subgrid (list): Optional list of fixed (r, c, v) constraints.

    Returns:
        List of (r, c, v) tuples representing the solution, or None if UNSAT.
    """
    solver = Glucose3()

    # Build CNF clauses
    for r in range(1, N + 1):
        for c in range(1, N + 1):
            # At least one value per cell
            solver.add_clause([var(r, c, v, N, C) for v in range(1, C + 1)])

            # At most one value per cell
            for v in range(1, C + 1):
                for w in range(v + 1, C + 1):
                    solver.add_clause([-var(r, c, v, N, C), -var(r, c, w, N, C)])

            # Avoid L-shapes
            if c > r:
                for i in range(1, N - c + 1):
                    for v in range(1, C + 1):
                        solver.add_clause([
                            -var(r, c, v, N, C),
                            -var(r + i, c, v, N, C),
                            -var(r + i, c + i, v, N, C)
                        ])
            else:
                for i in range(1, N - r + 1):
                    for v in range(1, C + 1):
                        solver.add_clause([
                            -var(r, c, v, N, C),
                            -var(r + i, c, v, N, C),
                            -var(r + i, c + i, v, N, C)
                        ])

    if solver.solve():
        model = solver.get_model()
        assignments = [reverse_var(v, N, C) for v in model if v > 0]
        return assignments
    else:
        return None

prefix_N = 4
prefix_C = 3
N, C = 18, 3
assignments = solve_lshape(prefix_N, prefix_C)
lshape_to_cnf(N, C, fixed_subgrid=assignments, filename=f"prefix_lshape_{N}_{C}_{prefix_N}_{prefix_C}.cnf")