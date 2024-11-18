from pysat.solvers import Glucose3
from .lshape_to_cnf import *
import itertools
from sympy import Matrix
from tqdm import tqdm

def solve_L_shape(N, C):
    solution_set = []
    iteration = 1
    clauses = []

    # Generate initial L-shape constraints and add them to clauses
    clauses.extend(generate_lshape_constraints(N, C))

    # Initialize progress bar
    with tqdm(desc="Solving L-shape", unit="solution", dynamic_ncols=True) as pbar:
        while True:
            solver = Glucose3()

            for clause in clauses:
                solver.add_clause(clause)

            if solver.solve():
                new_solution = solver.get_model()
                # Decode the solution into a grid format
                decoded_solution = decode_solution(new_solution, N, C)

                # Check if the solution is isomorphic to any previous one
                if all(not is_isomorphic(decoded_solution, sol, N) for sol in solution_set):
                    solution_set.append(decoded_solution)
                    pbar.update(1)

                    # Add non-isomorphic constraints to clauses for the next iteration
                    non_isomorphic_clauses = get_non_isomorphic_clauses(" ".join(map(str, new_solution)), N, C)
                    clauses.extend(non_isomorphic_clauses)
            else:
                pbar.close()
                print("No more solutions found.")
                break
            
            iteration += 1

    print(f"All {len(solution_set)} non-isomorphic solutions found.")
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

def is_sat(matrix, N, C):
    """
    Check if a given matrix satisfies the constraints (including no L-shape) using a SAT solver.

    Parameters:
        matrix: 2D list representing the N x N grid solution.
        N: Size of the grid.
        C: Number of possible values per cell (colors).

    Returns:
        bool: True if the matrix satisfies the constraints, False otherwise.
    """
    clauses = []

    # Add general L-shape constraints
    clauses.extend(generate_lshape_constraints(N, C))

    # Add fixed value constraints (unit clauses)
    for r in range(N):
        for c in range(N):
            v = matrix[r][c]
            fixed_clause = [int(var(r + 1, c + 1, v, N, C))]
            clauses.append(fixed_clause)

    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    is_satisfiable = solver.solve()
    solver.delete() 
    return is_satisfiable


def generate_isomorphic_solutions(matrix, N, C):
    """
    Generate all isomorphic permutations of a matrix (SAT solution) that are also SAT.

    Parameters:
        matrix: 2D list representing the N x N grid solution.
        N: Size of the grid.
        C: Number of possible values per cell (colors).

    Returns:
        list of 2D lists: All SAT solutions in the same isomorphic group.
    """
    grid = Matrix(matrix)
    row_perms = list(itertools.permutations(range(N)))
    col_perms = list(itertools.permutations(range(N)))

    isomorphic_solutions = []

    # Generate all row and column permutations
    for row_perm in row_perms:
        for col_perm in col_perms:
            # Apply the row and column permutations
            permuted_grid = grid.permute_rows(row_perm)
            permuted_grid = permuted_grid.permute_cols(col_perm)

            permuted_matrix = [[int(x) for x in permuted_grid.row(i)] for i in range(N)]
            
            # Check if the permuted solution satisfies the l shape
            if is_sat(permuted_matrix, N, C):
                if permuted_matrix not in isomorphic_solutions:
                    isomorphic_solutions.append(permuted_matrix)
    print(f"All {len(isomorphic_solutions)} isomorphic solutions found.")
    return isomorphic_solutions


# solutions = solve_L_shape(4, 2)
# print(len(solutions))
