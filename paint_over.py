from vdw_to_cnf import *
from decode_result import *
def paint_over(n, r, k, prior_result, filename="vdw_paintover.cnf"):
    """
    Implement the paint-over algorithm for improving the Van der Waerden number.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors, r is the latest added color.
        k (int): Length of arithmetic progression to avoid.
        prior_result (string): a list represents fixed cnf clause after previous case solved by SAT solver.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = vdw_to_cnf(n, r, k, write = False)
    decoded_result = decode_result(prior_result, r)
    print("Decoded_results: ", decoded_result)
    for i in decoded_result:
        #can be painted as original color or paint over with new color
        clause = [var(i[0], i[1], r), var(i[0], r, r)]
        clauses.append(" ".join(map(str, clause)) + " 0")

    with open(filename, "w") as f:
        f.write(f"p cnf {n} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")
    return clauses

paint_over(20, 3, 3, '1 -2 -3 4 5 -6 -7 8 -9 10 11 -12 -13 14 15 -16 0', filename="vdw_paintover.cnf")