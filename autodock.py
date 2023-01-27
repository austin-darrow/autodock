from vina import Vina
from mpi4py import MPI
import subprocess
import pickle
import time
import os
import sys
from os.path import exists
from os.path import basename

# Set variables
receptor='1iep_receptor'
docking_type = 'vina'
ligand_library = ''
num_ligands = 10000
model = 'basic'

def benchmark(start_time, end_time, num_ligands, model, docking_type):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Docking type: {docking_type}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n")
    benchmark_file.close()

def sort():
    subprocess.run(["cat results* >> results_merged.txt"], shell=True)
    INPUTFILE = 'results_merged.txt'
    OUTPUTFILE = './output/processed_results.txt'
    
    result = []

    with open(INPUTFILE) as data:
        while line := data.readline():
            filename = basename(line.split()[-1])
            v = data.readline().split()[0]
            result.append(f'{v} {filename}\n')

    with open(OUTPUTFILE, 'w') as data:
        data.writelines(sorted(result, key=lambda x: float(x.split()[1])))
    
    subprocess.run(["rm results*; mv *map* *.gpf ./output/maps"], shell=True)

def run_docking(ligand, v, filename):
    v.set_ligand_from_string(ligand)
    v.dock()
    v.write_poses(f'./output/{docking_type}/output_{filename}', n_poses=1, overwrite=True)
'''
def prep_maps(receptor):
    if exists('{receptor}.gpf'):
        subprocess.run([f"rm {receptor}.gpf"], shell=True)
    subprocess.run([f"python3 /scripts/write-gpf.py --box /configs/config.config /input/receptors/{receptor}.pdbqt"], shell=True)
    subprocess.run([f"/scripts/autogrid4 -p /input/receptors/{receptor}.gpf"], shell=True)
'''


def main():
    # Setup
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    # Pre-Processing
    start_time = time.time()
    
    receptor = '1iep_receptor'
    docking_type = 'vina'
    ligands = pickle.load(open('./input/ligands_10.pkl', 'rb'))

    # Initialize Vina or AD4 configurations
    if docking_type == 'vina':
        v = Vina(sf_name='vina', cpu=0, verbosity=0)
        v.set_receptor(f'./input/receptors/{receptor}.pdbqt')
        v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])
    elif docking_type == 'ad4':
        prep_maps(receptor)    
        v = Vina(sf_name='ad4', cpu=0, verbosity=0)
        v.load_maps(map_prefix_filename='1iep_receptor')

    # Run docking
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        if(index % size == rank):
            run_docking(ligand, v, filename)
            subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' ./output/{docking_type}/output_{filename} \
                            | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                            >> results_{rank}.txt"], shell=True)
    
    # Post-Processing
    sort()
    end_time = time.time()
    benchmark(start_time, end_time, num_ligands, model, docking_type)
main()
