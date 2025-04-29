#!/bin/bash
#SBATCH --partition=mcs-project
#SBATCH --account=projects
#SBATCH --qos=project
#SBATCH --mem 128G

eval "$(conda shell.bash hook)"
conda activate thesis

cd /home/DAVIDSON/mili/Senior-Thesis
python -m lshape.find_all_cert