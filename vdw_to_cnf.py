def var(i, j, r):
    """Returns the variable number for integer i in color class Cj."""
    return (i - 1) * r + j

def vdw_to_cnf(n, r, k, filename="vdw.cnf"):
    """
    Encode Van der Waerden number into a CNF file.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors.
        k (int): Length of arithmetic progression to avoid.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = []
    if r == 1 or k <= 2:
        print("Trivial case.") 

    if r == 2:
        # Clauses to prevent arithmetic progression in C1 \{¬x_a,¬x_{a+d},…,¬x_{a+d(t_1−1)}\}
        for a in range(1, n - k + 2):  # Ensure a + d(k-1) <= n
            for d in range(1, (n - a) // (k - 1) + 1):
                # Add clause {¬xa, ¬xa+d, ..., ¬xa+d(k−1)}
                clause = [-((a + (i - 1) * d)) for i in range(1, k + 1)]
                clauses.append(" ".join(map(str, clause)) + " 0")

        # Clauses to prevent arithmetic progression in C2 \{x_a,x_{a+d},…,x_{a+d(t_2−1)}\}
        for a in range(1, n - k + 2):
            for d in range(1, (n - a) // (k - 1) + 1):
                # Add clause {xa, xa+d, ..., xa+d(k−1)}
                clause = [(a + (i - 1) * d) for i in range(1, k + 1)]
                clauses.append(" ".join(map(str, clause)) + " 0")

    if r > 2:
        # Covering clause: \{x_{i,1},x_{i,2},...,x_{i,r}\} 
        # Ensures that every integer at least belongs to one color class
        for i in range(1, n + 1):
            clause = [var(i, j) for j in range(1, r + 1)]
            clauses.append(" ".join(map(str, clause)) + " 0")

        # Disjoint clause: \{¬x_{i,s},¬x_{i,t}\} for 1 ≤ i ≤ n and 1 ≤ s < t ≤ r 
        # Ensure that each integer belongs to at most one color class
        for i in range(1, n + 1):
            for s in range(1, r):
                for t in range(s + 1, r + 1):
                    clause = [-var(i, s), -var(i, t)]
                    clauses.append(" ".join(map(str, clause)) + " 0")
                    
        # Prevention of Arithmetic Progression: \{¬x_{a,j},¬x_{a+d,j},…,¬x_{a+d(t_j−1),j}\} 
        # for 1 ≤ j ≤ r and 1 ≤ a ≤ n−k+1 and 1 ≤ d ≤ \lfloor(n-a)/(k - 1))\rfloor
        # ensure that there is no arithmetic progression of length k with common difference d for color Cj.
        for j in range(1, r + 1):
            for a in range(1, n - k + 2):
                for d in range(1, (n - a) // (k - 1) + 1):
                    clause = [-var(a + (i - 1) * d, j) for i in range(1, k + 1)]
                    clauses.append(" ".join(map(str, clause)) + " 0")
                    
    with open(filename, "w") as f:
        f.write(f"p cnf {n} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")

vdw_to_cnf(n=5, r=2, k=3, filename="vdw_2_3.cnf") 
vdw_to_cnf(n=5, r=3, k=3, filename="vdw_3_3.cnf") 