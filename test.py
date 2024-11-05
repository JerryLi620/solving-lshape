def calculate_total_iterations(r, n, k):
    total_iterations = 0

    for j in range(1, r + 1):
        print(total_iterations)
        for a in range(1, n - k + 2):
            for d in range(1, (n - a) // (k - 1) + 1):
                    total_iterations += 1

    return total_iterations

# Example values
r = 5  # Number of colors
n = 98740 # Number of blocks
k = 5  # Length of arithmetic progression

# Calculate total iterations
total_iterations = calculate_total_iterations(r, n, k)
print(f"Total number of iterations: {total_iterations}")