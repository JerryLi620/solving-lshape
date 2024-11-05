#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project

eval "$(conda shell.bash hook)"
conda activate thesis

cd /home/DAVIDSON/mili/Senior-Thesis
./parkissat -c=31 -simp -shr-sleep=500000 -shr-lit=1500 $1 -initshuffle

# glucose/parallel/glucose-syrup lshape_19_3.cnf  > lshape_19_3_result.txt
