import time
import subprocess
import os
import sys
from os.path import exists
from os.path import basename

NUM_LIGANDS = 10
MODEL = 'basic'
FORCEFIELD = 'ad4'
TYPE = 'vina_module'
receptor = '1iep_receptor'

def benchmark(start_time, end_time, num_ligands, model, forcefield):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Type: {TYPE} ' + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Forcefield: {forcefield}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n")
    benchmark_file.close()

def process_results():
    subprocess.run([f"cat *results* >> results_merged.txt"], shell=True)
    INPUTFILE = f'results_merged.txt'
    OUTPUTFILE = 'final_results_processed.txt'
    
    result = []

    with open(INPUTFILE) as data:
        while line := data.readline():
            filename = basename(line.split()[-1])
            v = data.readline().split()[0]
            result.append(f'{v} {filename}\n')

    with open(OUTPUTFILE, 'w') as data:
        data.writelines(sorted(result, key=lambda x: float(x.split()[1])))

    subprocess.run(["rm results*; mv *map* *.gpf ./output/maps"], shell=True)
    
def prep_maps():
    if exists('{receptor}.gpf'):
        subprocess.run([f"rm {receptor}.gpf"], shell=True)
    subprocess.run([f"python3 write-gpf.py --box config.config {receptor}.pdbqt"], shell=True)
    subprocess.run([f"autogrid4 -p {receptor}.gpf"], shell=True)

def run_trial():
    start_time = time.time()
    prep_maps()
    subprocess.run(["ibrun -n 16 python ad4_module_vina.py"], shell=True)
    end_time = time.time()
    benchmark(start_time, end_time, NUM_LIGANDS, MODEL, FORCEFIELD)
    process_results()


run_trial()
