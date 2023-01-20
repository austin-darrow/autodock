import subprocess
import os
from mpi4py import MPI
from vina import Vina

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

filelist = open('filelist.txt', 'r+')

for line_no, line in enumerate(filelist):
    if(line_no % size == rank):
        print(line," ",rank)
        subprocess.run([f"vina --receptor ./input/receptors/1iep_receptor.pdbqt --ligand ./input/ligands/{line.strip()} \
                        --config ./configs/1iep_receptor_vina_box.txt --exhaustiveness=32 \
                        --out ./output/vina_basic/VINA_OUT_{line.strip()} | sed -n '22p; 39p' | awk '{{print $2}}' >> results_{rank}.txt"], shell=True)

filelist.close()
