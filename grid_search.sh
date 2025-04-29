#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project
#SBATCH --output=grid_search_%j.out
#SBATCH --cpus-per-task=8

eval "$(conda shell.bash hook)"
conda activate thesis


cd /home/DAVIDSON/mili/Senior-Thesis
python grid_search.py 