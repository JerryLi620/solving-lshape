def decode_var(v, r):
    """Returns the integer and color class for variable v."""
    i = (v - 1) // r + 1
    j = v - (i - 1) * r
    return i, j

def decode_result(result, r):
    """
    Decode the result of a SAT solver into a list of clauses.

    Parameters:
        result (str): The result of a SAT solver.
        r (int): Number of colors.

    Returns:
        list: A list of clauses.
    """
    clauses = []
    for line in result.split(" "):
        if int(line) > 0:
            clause = decode_var(int(line), r)
            clauses.append(clause)
    return clauses