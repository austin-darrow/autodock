import subprocess
import os
import time

# RECEPTOR = open('./1iep_receptor.pdbqt', 'r')
"""
MODEL='basic' #Once we have portal up, change, this to accept an input
FORCEFIELD='vina'
EXHAUSTIVENESS=32

def create_config():
    with open('receptor_vina_box.txt', 'w') as c:
        # Get inputted coordinates from user input
        # Write them to config file
"""
NUM_LIGANDS = '10'
MODEL = 'basic'
FORCEFIELD = 'vina'

def benchmark(start_time, end_time, num_ligands, model, forcefield):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Forcefield: {forcefield}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n") 
    benchmark_file.close()

def dock_ligands(model='basic', forcefield='vina'):
    if not os.path.exists('output'):
        os.makedirs('output')

    #results = open("results.txt", 'a+')
    for file in os.listdir('/work/09252/adarrow/ls6/autodock/input'):
        #if model=='basic' and forcefield=='vina':
        result = subprocess.run(["vina", '--receptor', '1iep_receptor.pdbqt', '--ligand', f'./input/{file}', '--config', \
                                 "1iep_receptor_vina_box.txt", "--exhaustiveness=32", '--dir', 'output', \
                                 '--out', f'./output/{file}_vina_out.pdbqt', '|', 'sed', '-n', '22p; 39p'], shell=True)
        #results.write(result.stdout)
    #results.close()

def main():
    start_time = time.time()
    dock_ligands('basic', 'vina')
    end_time = time.time()
    benchmark(start_time, end_time, NUM_LIGANDS, MODEL, FORCEFIELD)

main()
