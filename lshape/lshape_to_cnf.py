import itertools
from sympy.combinatorics import Permutation, PermutationGroup

# A helper: get the Dimacs CNF variable number for the variable v {r,c,v} 
# encoding the fact that the cell at (r,c) has the value v
def var(r, c, v, N, C):
    assert(1 <= r <= N and 1 <= c <= N and 1 <= v <= C) 
    return (r - 1) * N * C + (c - 1) * C + (v - 1) + 1

def lshape_to_cnf(N, C, filename="lshape.cnf"):
    """
    Encode L-shape avoidance into a CNF file.

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

                # 3. No L-shapes in the grid
                if c > r:
                    for i in range(1, N - c + 1):
                        for v in range(1, C + 1):
                            no_lshape_clause = [-var(r, c, v, N, C), -var(r + i, c, v, N, C), -var(r + i, c + i, v, N, C)]
                            f.write(" ".join(map(str, no_lshape_clause)) + " 0\n")
                            num_clauses += 1
                else:
                    for i in range(1, N - r + 1):
                        for v in range(1, C + 1):
                            no_lshape_clause = [-var(r, c, v, N, C), -var(r + i, c, v, N, C), -var(r + i, c + i, v, N, C)]
                            f.write(" ".join(map(str, no_lshape_clause)) + " 0\n")
                            num_clauses += 1

    # Write CNF header (at the beginning of the file)
    with open(filename, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"p cnf {num_variables} {num_clauses}\n" + content)

def generate_lshape_constraints(N, C):
    """
    Generate the initial L-shape constraints as a list of clauses.

    Parameters:
        N (int): The dimension of the grid.
        C (int): Number of possible values per cell.

    Returns:
        list of lists: List of clauses for initial constraints.
    """
    clauses = []

    for r in range(1, N + 1):
        for c in range(1, N + 1):
            # 1. The cell at (r, c) has at least one value
            at_least_one_clause = [var(r, c, v, N, C) for v in range(1, C + 1)]
            clauses.append(at_least_one_clause)

            # 2. The cell at (r, c) has at most one value (no two values can be true simultaneously)
            for v in range(1, C + 1):
                for w in range(v + 1, C + 1):
                    at_most_one_clause = [-var(r, c, v, N, C), -var(r, c, w, N, C)]
                    clauses.append(at_most_one_clause)

            # 3. No L-shapes in the grid
            if c > r:
                for i in range(1, N - c + 1):
                    for v in range(1, C + 1):
                        no_lshape_clause = [-var(r, c, v, N, C), -var(r + i, c, v, N, C), -var(r + i, c + i, v, N, C)]
                        clauses.append(no_lshape_clause)
            else:
                for i in range(1, N - r + 1):
                    for v in range(1, C + 1):
                        no_lshape_clause = [-var(r, c, v, N, C), -var(r + i, c, v, N, C), -var(r + i, c + i, v, N, C)]
                        clauses.append(no_lshape_clause)

    return clauses
    
def get_non_isomorphic_clauses(solution, N, C):
    """
    Generate clauses to prevent isomorphic solutions by row, column, and color permutations.

    Parameters:
        solution (str): The encoded solution string (space-separated literals).
        N (int): The dimension of the grid.
        C (int): The number of possible values per cell (colors).

    Returns:
        list: A list of clauses to prevent isomorphic solutions.
    """
    # Decode the solution into a grid
    solution_literals = list(map(int, solution.split()))
    grid = [[0 for _ in range(N)] for _ in range(N)]
    
    for literal in solution_literals:
        if literal > 0: 
            # Decode to get (r, c, v)
            r = (literal - 1) // (N * C) + 1
            c = ((literal - 1) % (N * C)) // C + 1
            v = ((literal - 1) % C) + 1
            grid[r - 1][c - 1] = v

    # Define row and column permutation groups
    row_group = PermutationGroup(*[Permutation(p) for p in itertools.permutations(range(N))])
    col_group = PermutationGroup(*[Permutation(p) for p in itertools.permutations(range(N))])
    color_group = PermutationGroup(*[Permutation(p) for p in itertools.permutations(range(C))])  

    clauses = []

    # Iterate over unique row, column, and color permutations
    for row_perm in row_group.generate():
        for col_perm in col_group.generate():
            for color_perm in color_group.generate():
                permuted_clauses = []
                for r in range(N):
                    for c in range(N):
                        original_val = grid[r][c]
                        perm_val = color_perm(original_val - 1) + 1  # Adjust for 0-based indexing in Permutation
                        perm_r = row_perm(r)
                        perm_c = col_perm(c)
                        permuted_literal = var(perm_r + 1, perm_c + 1, perm_val, N, C)
                        permuted_clauses.append(-permuted_literal)
                clauses.append(permuted_clauses)

    return clauses



def add_non_isomorphic_constraints(filename, solution, N, C):
    """
    Add non-isomorphic constraints to an existing CNF file.

    Parameters:
        filename (str): The CNF file to which the non-isomorphic clauses will be added.
        solution (str): The encoded solution string.
        N (int): The dimension of the grid.
        C (int): The number of possible values per cell.
    """
    non_isomorphic_clauses = get_non_isomorphic_clauses(solution, N, C)

    with open(filename, "a") as f:
        for clause in non_isomorphic_clauses:
            clause_str = " ".join(map(str, clause)) + " 0\n"
            f.write(clause_str)
    
    print("Added non-isomorphic clauses.")
    