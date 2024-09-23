#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project 

eval "$(conda shell.bash hook)"
conda activate thesis

cd /home/DAVIDSON/mili/Senior-Thesis
python vdw_to_cnf.py