#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project 

eval "$(conda shell.bash hook)"
conda activate thesis

cd /home/DAVIDSON/mili/Senior-Thesis
glucose/parallel/glucose-syrup -verb=0 -model vdw_paintover_100_5_3.cnf  > vdw_paintover_100_5_3_result.txt