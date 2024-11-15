from pysat.solvers import Glucose3
from lshape_to_cnf import *
import itertools
from sympy import Matrix

def solve_L_shape(N, C):
    solution_set = []
    iteration = 1

    # List to hold all clauses
    clauses = []

    # Generate initial L-shape constraints and add them to clauses
    clauses.extend(generate_lshape_constraints(N, C))

    while True:
        solver = Glucose3()

        # Load all clauses into the SAT solver
        for clause in clauses:
            solver.add_clause(clause)

        # Solve the CNF problem
        if solver.solve():
            new_solution = solver.get_model()
            # Decode the solution into a grid format
            decoded_solution = decode_solution(new_solution, N, C)

            # Check if the solution is isomorphic to any previous one
            if all(not is_isomorphic(decoded_solution, sol, N) for sol in solution_set):
                solution_set.append(decoded_solution)
                print(f"Found unique solution #{len(solution_set)}:")
                for row in decoded_solution:
                    print(row)

                # Add non-isomorphic constraints to clauses for the next iteration
                non_isomorphic_clauses = get_non_isomorphic_clauses(" ".join(map(str, new_solution)), N, C)
                clauses.extend(non_isomorphic_clauses)
        else:
            print("No more solutions found.")
            break
        
        iteration += 1

    print("All non-isomorphic solutions found.")
    return solution_set

def decode_solution(solution, N, C):
    """
    Decode a SAT solution into a grid format.

    Parameters:
        solution (list): List of SAT solution literals.
        N (int): The grid dimension.
        C (int): Number of possible values per cell.

    Returns:
        list of lists: Decoded grid.
    """
    grid = [[0 for _ in range(N)] for _ in range(N)]
    for literal in solution:
        if literal > 0:
            r = (literal - 1) // (N * C) + 1
            c = ((literal - 1) % (N * C)) // C + 1
            v = ((literal - 1) % C) + 1
            grid[r - 1][c - 1] = v
    return grid

def is_isomorphic(solution1, solution2, N):
    """
    Check if two solutions (grids) are isomorphic by row and column permutations.

    Parameters:
        solution1, solution2: 2D lists representing the N x N grids
        N: size of the grid

    Returns:
        True if solution1 and solution2 are isomorphic; False otherwise.
    """
    grid1 = Matrix(solution1)
    grid2 = Matrix(solution2)

    row_perms = list(itertools.permutations(range(N)))
    col_perms = list(itertools.permutations(range(N)))

    for row_perm in row_perms:
        for col_perm in col_perms:
            # Apply the row and column permutations
            permuted_grid = grid1.permute_rows(row_perm)
            permuted_grid = permuted_grid.permute_cols(col_perm)

            # Check if the permuted grid is equal to the target grid
            if permuted_grid == grid2:
                return True

    return False

# Run the solver with the specified parameters
solutions = solve_L_shape(4, 2)
print(len(solutions))
