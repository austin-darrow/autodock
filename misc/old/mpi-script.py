import subprocess
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

filelist = open('filelist_test1.txt', 'r+')

for line_no, line in enumerate(filelist):
    if(line_no % size == rank):
        timings = open(f'timings_{rank}.txt', 'a+')
        start_time = time.time()
        subprocess.run([f"date >> timings_{rank}.txt; vina --receptor ./input/receptors/1iep_receptor.pdbqt --ligand ../ZINC-in-trials/2/{line.strip()} \
                        --out ./output/vina_basic/vina_out_{line.strip()} --config ./configs/1iep_receptor_vina_box.txt --exhaustiveness=32 --num_modes=1"], shell=True)
        timings.write(f"Rank: {rank} of {size} || Start time: {start_time} || End time: {time.time()} || Total time: {time.time() - start_time} || Ligand: {line.strip()}\n")

filelist.close()

x = "| sed -n '22p; 39p' | awk '{{print $2}}' >> results_{rank}.txt"
