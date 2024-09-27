from tqdm import tqdm
import numpy as np
def var(i, j, r):
    """
    Returns the variable number for integer i in color class Cj.

    Parameters:
        i (int): Position of block.
        j (int): Color class.
        r (int): Number of colors.
    """
    return (i - 1) * r + j
  
# A function to find largest prime factor 
def maxPrimeFactor(n):
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n /= d
        d = d + 1

    return max(factors)

def write_array_to_file(f, array):
    # For each row in the array, append "0" and write to file
    np.savetxt(f, np.column_stack((array, np.zeros(array.shape[0], dtype=int))), fmt='%d', delimiter=' ')

def vdw_to_cnf_paintover(old_n, new_n, r, k, write = True, filename="vdw.cnf"):
    """
    Encode Van der Waerden number into a CNF file.

    Parameters:
        old_n (int): Previous number of blocks.
        new_n (int): Updated number of blocks.
        r (int): Number of colors.
        k (int): Length of arithmetic progression to avoid.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = []
    m = n/(k-1) # defined by Heule
    if r == 1 or k <= 2:
        print("Trivial case.") 
    else:
        # Covering clause: \{x_{i,1},x_{i,2},...,x_{i,r}\} 
        # Ensures that every integer at least belongs to one color class
        for i in range(old_n+1, new_n + 1):
            clause = [var(i, j, r) for j in range(1, r + 1)]
            clauses.append(" ".join(map(str, clause)) + " 0")
                    
        # Prevention of Arithmetic Progression: \{¬x_{a,j},¬x_{a+d,j},…,¬x_{a+d(t_j−1),j}\} 
        # for 1 ≤ j ≤ r and 1 ≤ a ≤ n−k+1 and 1 ≤ d ≤ \lfloor(n-a)/(k - 1))\rfloor
        # ensure that there is no arithmetic progression of length k with common difference d for color Cj.
        for j in range(1, r + 1):
            for a in range(old_n + 1, new_n - k + 1):
                for d in range(1, (new_n - a) // (k - 1) + 1):
                    clause = [-var(a + (i - 1) * d, j, r) for i in range(1, k + 1)]
                    clauses.append(" ".join(map(str, clause)) + " 0")
    if write:
        with open(filename, "w") as f:
            f.write(f"p cnf {n} {len(clauses)}\n")
            for clause in clauses:
                f.write(clause + "\n")
    return clauses

def vdw_to_cnf(n, r, k, write=False, repetition_clause=False, reflection_clause=False, rotation_clause=False, filename="vdw.cnf", batch_size=10000):
    """
    Encode Van der Waerden number into a CNF file.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors.
        k (int): Length of arithmetic progression to avoid.
        filename (str): The name of the file to output the CNF formula.
    """
    m = n//(k-1) # defined by Heule
    if r == 1 or k <= 2:
        print("Trivial case.") 
        return
    
    print("Start generating")

    num_clauses = 0
    num_clauses += n  # Covering clauses
    num_disjoint_clauses = sum(1 for s in range(1, r) for t in range(s + 1, r + 1))
    num_clauses += n * num_disjoint_clauses  # Disjoint clauses
    for j in range(1, r + 1):
        for a in range(1, n - k + 2):
            for d in range(1, (n - a) // (k - 1) + 1):
                num_clauses += 1 # Progression clauses

    with open(filename, "w") as f:
        f.write(f"p cnf {n * r} {num_clauses}\n")
        # Batch buffer
        clause_batch = []

        # Covering clause: \{x_{i,1},x_{i,2},...,x_{i,r}\} 
        # Ensures that every integer at least belongs to one color class
        for i in tqdm(range(1, n + 1), desc="Covering Clause Progress"):
            clause = [var(i, j, r) for j in range(1, r + 1)]
            clause_batch.append(" ".join(map(str, clause)) + " 0")
            if len(clause_batch) >= batch_size:
                f.write("\n".join(clause_batch) + "\n")
                clause_batch = []

        print("Finished covering clause")

        # Disjoint clause: \{¬x_{i,s},¬x_{i,t}\} for 1 ≤ i ≤ n and 1 ≤ s < t ≤ r 
        # Ensure that each integer belongs to at most one color class
        for i in tqdm(range(1, n + 1), desc="Disjoint Clause Progress"):
            for s in range(1, r):
                for t in range(s + 1, r + 1):
                    clause = [-var(i, s, r), -var(i, t, r)]
                    clause_batch.append(" ".join(map(str, clause)) + " 0")
                    if len(clause_batch) >= batch_size:
                        f.write("\n".join(clause_batch) + "\n")
                        clause_batch = []

        print("Finished disjoint clause")            
        # Prevention of Arithmetic Progression: \{¬x_{a,j},¬x_{a+d,j},…,¬x_{a+d(t_j−1),j}\} 
        # for 1 ≤ j ≤ r and 1 ≤ a ≤ n−k+1 and 1 ≤ d ≤ \lfloor(n-a)/(k - 1))\rfloor
        # ensure that there is no arithmetic progression of length k with common difference d for color Cj.
        for j in tqdm(range(1, r + 1), desc="Progression Clauses Progress"):
            for a in tqdm(range(1, n - k + 1), desc="Progression Clauses Progress2"):
                for d in range(1, (n - a) // (k - 1) + 1):
                    clause = [-var(a + (i - 1) * d, j, r) for i in range(1, k + 1)]
                    clause_batch.append(" ".join(map(str, clause)) + " 0")
                    if len(clause_batch) >= batch_size:
                        f.write("\n".join(clause_batch) + "\n")
                        clause_batch = []
        print("Finished Progression clause")      
            
        # Addion of repetition clause: (¬x_{i,s} ∨ x_{i+m,s}) ∧ (x{i,s} ∨ ¬x{i+m,s})
        # From Heule's paper, this is inspired from the observation that most extreme certificates and 
        # the best known lower bounds of W(k,l) show a repetition of l − 1 times the same pattern
        if repetition_clause:
            for i in tqdm(range(1, m * k - m + 1), desc="Repetition Clauses"):
                for s in range(1, r + 1):
                    clause1 = [-var(i, s, r), var(i + m, s, r)]
                    clause2 = [var(i, s, r), -var(i + m, s, r)]
                    clause_batch.append(" ".join(map(str, clause1)) + " 0")
                    clause_batch.append(" ".join(map(str, clause2)) + " 0")
                    
                    # Write to file in batches
                    if len(clause_batch) >= batch_size:
                        f.write("\n".join(clause_batch) + "\n")
                        clause_batch = []

            print("Finished repetition clauses") 

        # Addition of reflection clause: (¬x_{i,s} ∨ x_{m-i,r+1-s}) ∧ (x{i,s} ∨ ¬x{m-i,r+1-s})
        # From Heule's paper, this is helps insured the symmetry of the visualization of the certificate
        if reflection_clause:
            for i in tqdm(range(1, m // 2 + 1), desc="Reflection Clauses"):
                for s in range(1, r + 1):
                    clause1 = [-var(i, s, r), var(m - i, r + 1 - s, r)]
                    clause2 = [var(i, s, r), -var(m - i, r + 1 - s, r)]
                    clause_batch.append(" ".join(map(str, clause1)) + " 0")
                    clause_batch.append(" ".join(map(str, clause2)) + " 0")

                    # Write to file in batches
                    if len(clause_batch) >= batch_size:
                        f.write("\n".join(clause_batch) + "\n")
                        clause_batch = []
            print("Finished reflection clauses")   

        # Addition of rotation clause: (¬x_{i,s} ∨ x_{i+p_m,s(mod r)+1}) ∧ (x{i,s} ∨ ¬x{i+p_m,s(mod r)+1})
        # From Huele's paper, he observed that this rotation was the result of zipping, and all the visualization
        # of the certificates were rotated by 360/r degrees
        if rotation_clause:
            p_m = maxPrimeFactor(m)
            for i in tqdm(range(1, m - p_m + 1), desc="Rotation Clauses"):
                for s in range(1, r + 1):
                    clause1 = [-var(i, s, r), var(i + p_m, s % r + 1, r)]
                    clause2 = [var(i, s, r), -var(i + p_m, s % r + 1, r)]
                    clause_batch.append(" ".join(map(str, clause1)) + " 0")
                    clause_batch.append(" ".join(map(str, clause2)) + " 0")

                    # Write to file in batches
                    if len(clause_batch) >= batch_size:
                        f.write("\n".join(clause_batch) + "\n")
                        clause_batch = []

        print("Finished rotation clauses")
        # Write remaining clauses
        if clause_batch:
            f.write("\n".join(clause_batch) + "\n")
    print("Successfully created CNF file")
# Experiment
n=75
r=4
k=3
vdw_to_cnf(n, r, k, write = True, filename=f"vdw_{n}_{r}_{k}.cnf") 