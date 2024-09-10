from vdw_to_cnf import vdw_to_cnf 

def paint_over(n, r, k, fixed_clauses, filename="vdw_paintover.cnf"):
    """
    Implement the paint-over algorithm for improving the Van der Waerden number.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors.
        k (int): Length of arithmetic progression to avoid.
        fixed_clauses (list): a list represents fixed variables after previous case solved by SAT solver.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = vdw_to_cnf(n, r, k, filename)
    clauses.extend(fixed_clauses)
    with open(filename, "w") as f:
        f.write(f"p cnf {n} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")
    return clauses

paint_over(15, 3, 3, ['1 -2 -3 4 5 -6 -7 8 -9 10 11 -12 -13 14 15 -16 0'], filename="vdw_paintover.cnf")