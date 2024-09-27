from vdw_to_cnf import *
from tqdm import tqdm
from decode_result import *
def read_value(file_path):
    """
    Reads a glucose output file and returns the line that starts with 'v' as a string.

    Parameters:
        file_path (str): The path to the text file.

    Returns:
        str: The line starting with 'v' or an empty string if no such line is found.
    """
    v_line = ""
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v'):
                v_line = line[1:].strip() 
                break 
    return v_line

def paint_over(old_n, new_n, old_r, new_r, k, prior_result_path, filename="vdw_paintover.cnf"):
    """
    Implement the paint-over algorithm for improving the Van der Waerden number.

    Parameters:
        n (int): Number of blocks.
        r (int): Number of colors, r is the latest added color.
        k (int): Length of arithmetic progression to avoid.
        prior_result_path (file): a txt file represents fixed cnf clause after previous case solved by SAT solver.
        filename (str): The name of the file to output the CNF formula.
    """
    clauses = vdw_to_cnf_paintover(old_n, new_n, new_r, k, write = False)
    prior_result_string = read_value(prior_result_path)
    print("Prior result: ", prior_result_string)
    decoded_result = decode_result(prior_result_string, old_r)
    print("Decoded_results: ", decoded_result)

    # Prevention of Arithmetic Progression: \{¬x_{a,j},¬x_{a+d,j},…,¬x_{a+d(k−1),j}\} 
    # for 1 ≤ j ≤ r and 1 ≤ a ≤ n−k+1 and 1 ≤ d ≤ \lfloor(n-a)/(k - 1))\rfloor
    # ensure that there is no arithmetic progression of length k with common difference d for color Cj
    # for progression includes the newly added blocks.
    for j in tqdm(range(1, new_r + 1), desc="Progression Clauses Progress"):
        for a in tqdm(range(new_n, old_n, -1), desc="Progression Clauses Progress2"):
            for d in range(1, a // (k - 1)):
                clause = [-var(a - (i - 1) * d, j, new_r) for i in range(1, k + 1)]
                clauses.append(" ".join(map(str, clause)) + " 0")

    for i in decoded_result:
        #can be painted as original color or paint over with new color
        clause = [var(i[0], i[1], new_r), var(i[0], new_r, new_r)]
        clauses.append(" ".join(map(str, clause)) + " 0")

    with open(filename, "w") as f:
        f.write(f"p cnf {n} {len(clauses)}\n")
        for clause in clauses:
            f.write(clause + "\n")
    print('Successfully created paint over CNF file')
    return clauses

old_n = 75
new_n = 100
old_r = 4
new_r = 5
k = 3
paint_over(old_n, new_n, old_r, new_r, k, "vdw_75_4_3_results_1.txt", filename=f"vdw_paintover_{new_n}_{new_r}_{k}.cnf")