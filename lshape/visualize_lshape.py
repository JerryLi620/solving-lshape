import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def visualize_sat_output(sat_output_str, N, C):
    """
    Visualizes the SAT solver output for the L-shape avoidance problem as a color grid
    using blue, red, and green colors, without gridlines and axis.

    Parameters:
        sat_output_str (str): Output from the SAT solver as a string of space-separated literals.
        N (int): The dimension of the grid.
        C (int): The number of possible values per cell.
    """
    # Convert the string into a list of integers
    sat_output = list(map(int, sat_output_str.split()))
    grid = np.zeros((N, N), dtype=int)
    
    # Parse the SAT output
    for literal in sat_output:
        if literal > 0:  # Only consider positive literals (those assigned True)
            # Decode the variable number into (r, c, v)
            literal -= 1  # Adjust to 0-indexed
            v = literal % C + 1  # Value in the cell (1 to C)
            literal //= C
            c = literal % N + 1  # Column index (1 to N)
            literal //= N
            r = literal + 1  # Row index (1 to N)
            
            # Fill in the grid with the value
            grid[r - 1, c - 1] = v

    colors = ['blue', 'red', 'green']
    cmap = mcolors.ListedColormap(colors[:C])
    plt.figure(figsize=(8, 8))
    plt.imshow(grid, cmap=cmap, origin='upper')
    plt.axis('off')
    
    plt.savefig(f"grid_{N}_{C}.jpg")

def visualize_color_grids(grids):
    """
    Visualizes a list of 2D grids with color coding for cell values.

    Parameters:
        grids (list of nested lists): List of 2D grids representing the solutions.
        Each cell contains an integer value.
    """
    n = len(grids)
    cols = min(4, n)  # Number of columns per row
    rows = (n + cols - 1) // cols  # Calculate required rows

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))

    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for i, grid in enumerate(grids):
        grid = np.array(grid)
        N, C = grid.shape[0], np.max(grid)
        colors = ['blue', 'red', 'green']
        cmap = mcolors.ListedColormap(colors[:C])

        axes[i].imshow(grid, cmap=cmap, origin='upper')
        axes[i].axis('off')
        axes[i].set_title(f"Grid {i+1}")
        
    if n > 1:
        for j in range(len(grids), len(axes)):
            axes[j].axis('off')

    plt.tight_layout()
    plt.show()




def visualize_snake_path(sat_output_str, N, C):
    """
    Visualizes the SAT solver output using the snake path method with arrows starting horizontally to the left
    and saves the plot to a file.
    
    Parameters:
        sat_output_str (str): Output from the SAT solver as a string of space-separated literals.
        N (int): The dimension of the grid.
        C (int): The number of color classes.
    """
    sat_output = list(map(int, sat_output_str.split()))

    directions = [(-1, 0)]  # C1 moves left (horizontal to the left)
    # Assign directions to each color class based on rotation
    for s in range(1, C):
        angle = (180 - 360 * s/ C) % 360
        angle_rad = np.radians(angle)  
        directions.append((round(np.cos(angle_rad), 2), round(np.sin(angle_rad), 2))) 
    current_pos = np.array([0, 0])
    scale_factor = 1/N

    plt.figure(figsize=(8, 8))
    plt.xlim(-N, N)
    plt.ylim(-N, N)
    
    colors = ['blue', 'red', 'green']
    
    # Parse the SAT output and draw arrows
    previous_pos = current_pos.copy()
    for literal in sat_output:
        if literal > 0:  # Only process positive literals (those assigned True)
            v = (literal - 1) % C  # Determine which color class it belongs to
            # Get the direction for this color class
            direction = np.array(directions[v])  
            direction = direction * scale_factor
            
            # Compute the next position based on the direction
            current_pos = previous_pos + direction

            # Draw a line from previous_pos to current_pos 
            plt.plot([previous_pos[0], current_pos[0]], [previous_pos[1], current_pos[1]], 
                     color=colors[v % len(colors)], linewidth=0.5)
            # Update previous position to the current position
            previous_pos = current_pos.copy()

    plt.axis('off')

    plt.savefig(f"snake_path_{N}_{C}.jpg", dpi = 1000)


