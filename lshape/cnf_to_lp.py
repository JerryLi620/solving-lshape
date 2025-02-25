from gurobipy import Model, GRB

def cnf_to_lp(cnf_file, lp_file):
    """
    Convert a CNF file in DIMACS format to an equivalent Linear Programming (LP)
    formulation that can be solved by Gurobi.
    
    1. **Variable Creation**:
       - Each Boolean variable x_i in the CNF is mapped to a binary variable in the LP

    2. **Clause Translation**:
       - For a positive literal x_i, we directly use x_i.
       - For a negative literal -x_i, we use (1 - x_i) so that if x_i = 0 (i.e., False), 
         (1 - x_i) equals 1 (i.e., True).
       - Each clause, which is a disjunction (logical OR) of literals, is translated into 
         a linear inequality. For example, the clause:
         
             x1 OR ¬x2 OR x3
         
         is converted to:
         
             x1 + (1 - x2) + x3 >= 1
         
         This constraint ensures that at least one literal in the clause is True.
    """
    with open(cnf_file, 'r') as f:
        lines = f.readlines()

    model = Model("SAT_to_LP")

    variables = set()
    constraints = []

    # Parse the CNF file
    for line in lines:
        line = line.strip()
        if line.startswith('p cnf'):
            _, _, num_vars, _ = line.split()
            num_vars = int(num_vars)
            continue
        if line.startswith('c') or line == "":
            continue  # Skip comments and empty lines

        # Parse clauses (space-separated literals, ending with '0')
        literals = list(map(int, line.split()))[:-1]  # Remove trailing 0
        clause_terms = []

        for lit in literals:
            var = abs(lit)
            variables.add(var)
            
            if lit > 0:
                clause_terms.append(f"x{var}")
            else:
                clause_terms.append(f"(1 - x{var})")

        constraints.append(" + ".join(clause_terms) + " >= 1")

    # Define variables in Gurobi as binary
    x = {i: model.addVar(vtype=GRB.BINARY, name=f"x{i}") for i in variables}
    model.update()  # Ensure variables are recognized

    # Add constraints properly
    for c in constraints:
        # Remove the trailing ' >= 1'
        clause_str = c.replace(" >= 1", "")
        terms = clause_str.split(" + ")
        lhs = 0  # Left-hand side of inequality
        
        for term in terms:
            if term.startswith("(1 - x"):
                var_index = int(term.split("x")[1].split(")")[0])
                lhs += (1 - x[var_index])
            else:
                var_index = int(term.replace("x", ""))
                lhs += x[var_index]
        
        model.addConstr(lhs >= 1)

    # Write to LP file
    model.update()
    model.write(lp_file)
    print(f"LP file saved: {lp_file}")

cnf_to_lp("single_color.cnf", "single_color.lp")

