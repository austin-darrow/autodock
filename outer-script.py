import time
import subprocess
import os
import sys
from os.path import exists
from os.path import basename

NUM_LIGANDS = 10000
MODEL = 'basic'
FORCEFIELD = 'vina'

def benchmark(start_time, end_time, num_ligands, model, forcefield):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Forcefield: {forcefield}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n")
    benchmark_file.close()

def sort():
    subprocess.run(["cat results* >> results_merged.txt"], shell=True)
    INPUTFILE = 'results_merged.txt'
    OUTPUTFILE = 'processed_results.txt'
    
    result = []

    with open(INPUTFILE) as data:
        while line := data.readline():
            filename = basename(line.split()[-1])
            v = data.readline().split()[0]
            result.append(f'{v} {filename}\n')

    with open(OUTPUTFILE, 'w') as data:
        data.writelines(sorted(result, key=lambda x: float(x.split()[1])))
    
    subprocess.run(["rm results*"], shell=True)

def run_trial():
    start_time = time.time()
    subprocess.run(["ibrun -n 16 python module_vina.py"], shell=True)
    end_time = time.time()
    benchmark(start_time, end_time, NUM_LIGANDS, MODEL, FORCEFIELD)
    sort()


run_trial()
