from vina import Vina
from mpi4py import MPI
import subprocess
import pickle
import blosc
import os
from os.path import exists
from os.path import basename

# Setup
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
 
receptor='1fpu_receptor'
receptor_path = f'/scratch/09252/adarrow/autodock/input/receptors/{receptor}'
docking_type = 'vina'
ligand_library = '/scratch/09252/adarrow/autodock/scripts/Enamine-PC-Pickled'
config_path = '/.configs/config.config'
user_configs = {'center_x': '15.190', 'center_y': '53.903', \
                'center_z': '16.917', 'size_x': '20.0', \
                'size_y': '20.0', 'size_z': '20.0'}

def prep_config():
    with open(config_path, 'w+') as f:
        for config, value in user_configs:
            f.write(f'{config} = {value}\n')
    f.close()

def prep_maps():
    if docking_type == 'ad4':
        if exists(f'{receptor}.gpf'):
            subprocess.run([f"rm {receptor}.gpf"], shell=True)
        subprocess.run([f"python3 ./scripts/write-gpf.py --box {config_path} {receptor_path}.pdbqt"], shell=True)
        subprocess.run([f"./scripts/autogrid4 -p {receptor}.gpf"], shell=True)

def prep_receptor():
    if exists(f'{receptor_path}H.pdb'):
        subprocess.run([f'./scripts/prepare_receptor -r {receptor_path}H.pdb -o {receptor_path}.pdbqt'], shell=True)

def prep_ligands():
    # Returns a list where each item is the path to a pickled and compressed text file containing multiple ligand strings
    ligand_paths = []
    for dirpath, dirnames, filenames in os.walk(ligand_library):
        for filename in filenames:
            ligand_paths.append(f'{dirpath}/{filename}')
    return ligand_paths

def run_docking(ligands, v):
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        v.set_ligand_from_string(ligand)
        v.dock()
        v.write_poses(f'./output/{docking_type}/output_{filename}', n_poses=1, overwrite=True)
        subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' ./output/{docking_type}/output_{filename} \
                        | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                        >> results_{rank}.txt"], shell=True)

def unpickle_and_decompress(path_to_file):
    with open(path_to_file, 'rb') as f:
        compressed_pickle = f.read()
    depressed_pickle = blosc.decompress(compressed_pickle)
    dictionary_of_ligands = pickle.loads(depressed_pickle)
    return dictionary_of_ligands

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

def main():
    if rank == 0:
        # Pre-Processing
        prep_config()
        prep_receptor()
        prep_maps()
        ligands = prep_ligands()
        # Let other ranks know pre-processing is finished; they can now ask for work
        for i in range(size):
            comm.send('', dest=i)

        # Until all ligands have been docked, send more work to worker ranks
        while ligands:
            worker_task = comm.recv(source=MPI.ANY_SOURCE)
            comm.send(ligands.pop(), dest=worker_task)

        # When all ligands have been sent, let worker ranks know they can stop
        for i in range(size):
            comm.send('done', dest=i)

        # Post-Processing
        sort()
    else: # All ranks besides rank 0
        comm.recv(source=0) # Wait for rank 0 to finish pre-processing
        
        # Initialize Vina or AD4 configurations
        if docking_type == 'vina':
            v = Vina(sf_name='vina', cpu=1, verbosity=0)
            v.set_receptor(f'{receptor_path}.pdbqt')
            uc = user_configs
            v.compute_vina_maps(center=[uc[center_x], uc[center_y], uc[center_z]], box_size=[uc[size_x], uc[size_y], uc[size_z]])
        elif docking_type == 'ad4':
            v = Vina(sf_name='ad4', cpu=1, verbosity=0)
            v.load_maps(map_prefix_filename = receptor)
        
        # Ask rank 0 for ligands and dock until rank 0 says done
        while True:
            comm.send(rank,dest=0) # Ask rank 0 for another set of ligands
            ligand_set_path = comm.recv(source=0) # Wait for a response
            if ligand_set_path == 'done':
                break
            # Pickle load and de-compress ligand set
            ligands = unpickle_and_decompress(ligand_set_path)
            # Dock each ligand in the set
            run_docking(ligands, v)




main()
