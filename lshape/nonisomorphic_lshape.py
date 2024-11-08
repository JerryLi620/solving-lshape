import itertools
# A helper: get the Dimacs CNF variable number for the variable v {r,c,v} 
# encoding the fact that the cell at (r,c) has the value v
def var(r, c, v, N, C):
    assert(1 <= r <= N and 1 <= c <= N and 1 <= v <= C) 
    return (r - 1) * N * C + (c - 1) * C + (v - 1) + 1

class SATGridProcessor:
    def __init__(self, solution, N, C):
        self.solution = list(map(int, solution.split()))
        self.N = N  
        self.C = C 
        self.grid = self.decode_solution()
        
    def decode_solution(self):
        grid = [[0 for _ in range(self.N)] for _ in range(self.N)]
        
        for literal in self.solution:
            if literal > 0: 
                # Decode to get (r, c, v)
                r = (literal - 1) // (self.N * self.C) + 1
                c = ((literal - 1) % (self.N * self.C)) // self.C + 1
                v = ((literal - 1) % self.C) + 1
                grid[r - 1][c - 1] = v 
        
        return grid

    def generate_non_isomorphic_constraints(self):
        row_perms = list(itertools.permutations(range(self.N)))
        col_perms = list(itertools.permutations(range(self.N)))
        
        clauses = []
        
        # For each permutation pair (row_perm, col_perm), prevent isomorphic solutions
        for row_perm in row_perms:
            for col_perm in col_perms:
                permuted_clauses = []
                
                for r in range(self.N):
                    for c in range(self.N):
                        original_val = self.grid[r][c]
                        perm_r = row_perm[r]
                        perm_c = col_perm[c]
                        permuted_literal = var(perm_r + 1, perm_c + 1, original_val, self.N, self.C)
                        permuted_clauses.append(-permuted_literal)
                
                clauses.append(permuted_clauses)
        
        return clauses

    def write_non_isomorphic_cnf(self, original_filename, new_filename):
        with open(original_filename, "r") as original_file:
            original_lines = original_file.readlines()
        
        non_isomorphic_clauses = self.generate_non_isomorphic_constraints()
        
        # Count total variables and clauses for the new CNF file header
        num_vars = self.N * self.N * self.C
        original_clauses = [line for line in original_lines if not line.startswith('p') and not line.startswith('c')]
        print("Number of isomorphic clauses: ", len(non_isomorphic_clauses))
        num_clauses = len(original_clauses) + len(non_isomorphic_clauses)
        
        # Write to the new CNF file
        with open(new_filename, "w") as new_file:
            new_file.write(f"p cnf {num_vars} {num_clauses}\n")
            
            for clause in original_clauses:
                new_file.write(clause)
            
            for clause in non_isomorphic_clauses:
                clause_str = " ".join(map(str, clause)) + " 0\n"
                new_file.write(clause_str)
        
        print(f"New CNF file '{new_filename}' created with additional non-isomorphic constraints.")


solution = "1 -2 -3 4 5 -6 -7 8 -9 10 11 -12 13 -14 -15 16 -17 18 19 -20 -21 22 -23 24 25 -26 -27 28 29 -30 -31 32"

processor = SATGridProcessor(solution, N=4, C=2)

filename = "lshape_4_2.cnf"
new_filename = filename.replace(".cnf", "_non_isomorphic.cnf")
processor.write_non_isomorphic_cnf(filename, new_filename)
