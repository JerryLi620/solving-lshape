#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project 

eval "$(conda shell.bash hook)"
conda activate thesis

cd /home/DAVIDSON/mili/Senior-Thesis
glucose/parallel/glucose-syrup vdw_75_4_3.cnf vdw_75_4_3_results_2.txt