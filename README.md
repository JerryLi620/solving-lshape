# L-Shape Graph Coloring via SAT Solvers

This repository contains the work from Mingyang Li’s independent study during Spring 2025 at Davidson College. The project focuses on using SAT solvers and related techniques to explore heuristics and find solutions for the *L-shape graph coloring problem*.

## How to Get Started
1. **Generate the CNF File**  
   The main functions are located in [`lshape_to_cnf.py`](https://github.com/JerryLi620/solving-lshape/blob/main/lshape/lshape_to_cnf.py).  
   These functions generate a CNF file encoding the L-shape coloring constraints. Alternative function are all int the same folder. See the comments of each functions.

2. **Solve the CNF File**  
   - Open [`solve.sh`](https://github.com/JerryLi620/solving-lshape/blob/main/solve.sh).
   - Enter the name of the generated CNF file.
   - Use your desired SAT solver (e.g., Kissat, CaDiCaL) to solve the problem.
  
3. **Generate permutation class of a single lshape problem
   - Open [`visualize.ipynb`](https://github.com/JerryLi620/solving-lshape/blob/main/visualize.ipynb)
   - Follow the instruction inside
   - Currently we can only generate all permutation classes of 4*4 matrices with 2 colors. Others may take long time and may be better to do it in slurm job.

4. Tuning hyperparamaters of Kissat solver
   - Code for tuning and the parameter space is in [`grid_search.py`](https://github.com/JerryLi620/solving-lshape/blob/main/grid_search.py)
   - To run it submit the [`grid_search.sh`](https://github.com/JerryLi620/solving-lshape/blob/main/grid_search.sh) job.
   - You can check top parameters setting and common setting in [`grid_search.ipynb`](https://github.com/JerryLi620/solving-lshape/blob/main/grid_search.ipynb)
  
## Possible Future Work
1. Check the distribution of parameter settings and see if we can figure out better parameter space.
2. Use Reinforcement learning or other techniques to learn from simpler case and solve 21*21 grid.

## Notes
- This project emphasizes experimentation with solver heuristics and search for solutions.
- Additional scripts and utilities for preprocessing and postprocessing are included in the repository.
