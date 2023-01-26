import time
import subprocess
import os
import sys
from os.path import exists
from os.path import basename

NUM_LIGANDS = 100
MODEL = 'basic'
FORCEFIELD = 'vina'
TYPE = 'subprocess'

def filegen(directory):
    if exists('filelist.txt'):
        subprocess.run([f"rm filelist.txt"], shell=True)
    f = open('filelist.txt', 'a+')
    for filename in os.listdir(directory):
        f.write(filename + "\n")
    f.close()

def benchmark(start_time, end_time, num_ligands, model, forcefield):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Type: {TYPE} ' + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Forcefield: {forcefield}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n")
    benchmark_file.close()

def sort():
    subprocess.run([f"cat *results* >> results_merged.txt"], shell=True)
    INPUTFILE = f'results_merged.txt'
    OUTPUTFILE = 'results_processed.txt'
    
    result = []

    with open(INPUTFILE) as data:
        while line := data.readline():
            filename = basename(line.split()[-1])
            v = data.readline().split()[0]
            result.append(f'{v} {filename}\n')

    with open(OUTPUTFILE, 'w') as data:
        data.writelines(sorted(result, key=lambda x: float(x.split()[1])))
    

def run_trial():
    filegen('/scratch/09252/adarrow/ZINC-in-trials/2')
    #start_time = time.time()
    subprocess.run(["ibrun -np 100 python mpi-script-test.py"], shell=True)
    #end_time = time.time()
    #benchmark(start_time, end_time, NUM_LIGANDS, MODEL, FORCEFIELD)
    #sort()


run_trial()
