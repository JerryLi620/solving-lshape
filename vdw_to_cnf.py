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

def vdw_to_cnf(n, r, k, write = False, repetition_clause = False, reflection_clause = False, rotation_clause = False, filename="vdw.cnf"):
    """
    Encode Van der Waerden number into a CNF file.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors.
        k (int): Length of arithmetic progression to avoid.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = []
    m = n//(k-1) # defined by Heule
    if r == 1 or k <= 2:
        print("Trivial case.") 
    else:
        # Covering clause: \{x_{i,1},x_{i,2},...,x_{i,r}\} 
        # Ensures that every integer at least belongs to one color class
        for i in range(1, n + 1):
            clause = [var(i, j, r) for j in range(1, r + 1)]
            clauses.append(" ".join(map(str, clause)) + " 0")

        # Disjoint clause: \{¬x_{i,s},¬x_{i,t}\} for 1 ≤ i ≤ n and 1 ≤ s < t ≤ r 
        # Ensure that each integer belongs to at most one color class
        for i in range(1, n + 1):
            for s in range(1, r):
                for t in range(s + 1, r + 1):
                    clause = [-var(i, s, r), -var(i, t, r)]
                    clauses.append(" ".join(map(str, clause)) + " 0")
                    
        # Prevention of Arithmetic Progression: \{¬x_{a,j},¬x_{a+d,j},…,¬x_{a+d(t_j−1),j}\} 
        # for 1 ≤ j ≤ r and 1 ≤ a ≤ n−k+1 and 1 ≤ d ≤ \lfloor(n-a)/(k - 1))\rfloor
        # ensure that there is no arithmetic progression of length k with common difference d for color Cj.
        for j in range(1, r + 1):
            for a in range(1, n - k + 2):
                for d in range(1, (n - a) // (k - 1) + 1):
                    clause = [-var(a + (i - 1) * d, j, r) for i in range(1, k + 1)]
                    clauses.append(" ".join(map(str, clause)) + " 0")
    # Addion of repetition clause: (¬x_{i,s} ∨ x_{i+m,s}) ∧ (x{i,s} ∨ ¬x{i+m,s})
    # From Heule's paper, this is inspired from the observation that most extreme certificates and 
    # the best known lower bounds of W(k,l) show a repetition of l − 1 times the same pattern
    if repetition_clause:
        for i in range(1, m*k-m+1):
            for s in range(1, r+1):
                clause1 = [-var(i, s, r), var(i+m, s, r)]      
                clause2 = [var(i, s, r), -var(i+m, s, r)]
                clauses.append(" ".join(map(str, clause1)) + " 0")    
                clauses.append(" ".join(map(str, clause2)) + " 0")  

    # Addition of reflection clause: (¬x_{i,s} ∨ x_{m-i,r+1-s}) ∧ (x{i,s} ∨ ¬x{m-i,r+1-s})
    # From Heule's paper, this is helps insured the symmetry of the visualization of the certificate
    if reflection_clause:
        for i in range(1, m//2+1):
            for s in range(1, r+1):
                clause1 = [-var(i, s, r), var(m-i, r+1-s, r)]
                clause2 = [var(i, s, r), -var(m-i, r+1-s, r)]
                clauses.append(" ".join(map(str, clause1)) + " 0")    
                clauses.append(" ".join(map(str, clause2)) + " 0") 

    # Addition of rotation clause: (¬x_{i,s} ∨ x_{i+p_m,s(mod r)+1}) ∧ (x{i,s} ∨ ¬x{i+p_m,s(mod r)+1})
    # From Huele's paper, he observed that this rotation was the result of zipping, and all the visualization
    # of the certificates were rotated by 360/r degrees
    if rotation_clause:
        p_m = maxPrimeFactor(m)
        for i in range(1, m-p_m+1):
            for s in range(1, r+1):
                clause1 = [-var(i, s, r), var(i+p_m, s%r+1, r)]
                clause2 = [var(i, s, r), -var(i+p_m, s%r+1, r)]
                clauses.append(" ".join(map(str, clause1)) + " 0")    
                clauses.append(" ".join(map(str, clause2)) + " 0") 
    
    if write:
        with open(filename, "w") as f:
            f.write(f"p cnf {n} {len(clauses)}\n")
            for clause in clauses:
                f.write(clause + "\n")
        print("Successfully created cnf file")
    return clauses

# Experiment
n=75
r=4
k=3
vdw_to_cnf(n, r, k, write = True, filename=f"vdw_{n}_{r}_{k}.cnf") 