from vina import Vina
from mpi4py import MPI
import subprocess
import pickle # For unpickling ligand files
import os
import blosc # For decompressing compressed ligand files
from os.path import exists
from os.path import basename # Used in the sorting function
import argparse # To accept user inputs as command line arguments

# Setup base MPI declarations
# In this MPI implementation, rank 0 acts as the director that all other ranks work for. Rank 0 first completes all pre-processing. As a final step, it creates a list containing full filepaths to all ligand files in the ligand library. Then it accepts messages from worker ranks saying they are ready for more work. It sends work for as long as there are ligand files left. Then rank 0 waits to hear from all ranks that they have finished processing, then proceeds to do the post-processing work. 
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


# Assign user inputs
receptor='1fpu_receptor'
flex_receptor=f'{receptor}_flex'
receptor_path = f'/scratch/09252/adarrow/autodock/input/receptors'
flexible = False
sidechains = ['THR315']
docking_type = 'vina'
ligand_library = '/scratch/09252/adarrow/autodock/scripts/Enamine-PC'
config_path = './configs/config.config'
user_configs = {'center_x': '15.190', 'center_y': '53.903', \
                'center_z': '16.917', 'size_x': '20.0', \
                'size_y': '20.0', 'size_z': '20.0'}


def prep_config():
# Write user inputted configurations (grid center and box size) to a config file for AutoDock Vina to use
    with open(config_path, 'w+') as f:
        for config, value in user_configs.items():
            f.write(f'{config} = {value}\n')
    f.close()


def prep_maps():
# Generate affinity maps using write-gpf.py and AFDRSuite's autogrid4. Generates maps for all possible ligand atom types for a given receptor
    if docking_type == 'ad4':
        if exists(f'{receptor}.gpf'):
            subprocess.run([f"rm {receptor}.gpf"], shell=True)
        subprocess.run([f"python3 ./scripts/write-gpf.py --box {config_path} {receptor_path}/{receptor}.pdbqt"], shell=True)
        subprocess.run([f"./scripts/autogrid4 -p {receptor}.gpf"], shell=True)


def prep_receptor():
# Converts a PDB receptor to a PDBQT, if needed. If the user has specified flexible docking, also prepares the rigid receptor and user-chosen flexible sidechains.
    if exists(f'{receptor_path}/{receptor}H.pdb'):
        subprocess.run([f'./scripts/prepare_receptor -r {receptor_path}/{receptor}H.pdb -o {receptor_path}/{receptor}.pdbqt'], shell=True)
    if flexible == True:
        subprocess.run([f"./scripts/pythonsh ./scripts/prepare_flexreceptor.py -g {receptor}.pdbqt -r {receptor_path}/{receptor}.pdbqt -s {'_'.join(sidechains)}"], shell=True)
        subprocess.run([f"mv *receptor* {receptor_path}"], shell=True)


def prep_ligands():
    # Returns a list where each item is the path to a pickled and compressed text file containing multiple ligand strings
    ligand_paths = []
    for dirpath, dirnames, filenames in os.walk(ligand_library):
        for filename in filenames:
            ligand_paths.append(f'{dirpath}/{filename}')
    return ligand_paths


def run_docking(ligands, v):
    # Runs AutoDock on each ligand in the given set; outputs a .pdbqt file showing the pose and all scores; appends the ligand name (filename) and it's best pose/score to a temporary results file
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        v.set_ligand_from_string(ligand)
        v.dock()
        v.write_poses(f'./output/pdbqt/output_{filename}', n_poses=1, overwrite=True)
        subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' ./output/pdbqt/output_{filename} \
                        | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                        >> results_{rank}.txt"], shell=True)


def unpickle_and_decompress(path_to_file):
    # Given a filepath, decompresses and unpickles the file. Returns the contents of the file as a dictionary where keys are ligand filenames and values are the actual ligand strings
    with open(path_to_file, 'rb') as f:
        compressed_pickle = f.read()
    depressed_pickle = blosc.decompress(compressed_pickle)
    dictionary_of_ligands = pickle.loads(depressed_pickle)
    return dictionary_of_ligands


def pre_processing():
    # Helper function to reduce clutter in main()
    prep_config()
    prep_receptor()
    prep_maps()
    ligands = prep_ligands()
    return ligands


def processing():
    # Long method; difficult to de-couple any one part without breaking many things

    # Initialize docking configurations
    # Note: Internal benchmarks showed that on a given node with 128 cores, setting ibrun -np to 32 and, below, setting CPU=4 granted the fastest docking. Verbosity set to 0 to increase speeds, as stdout cannot be captured from Vina's Python module.
    if docking_type == 'vina':
        v = Vina(sf_name='vina', cpu=4, verbosity=0)
        if flexible == True:
            v.set_receptor(f'{receptor_path}/{receptor}.pdbqt', f'{receptor_path}/{flex_receptor}.pdbqt')
        else:
            v.set_receptor(f'{receptor_path}/{receptor}.pdbqt')
        uc = user_configs
        v.compute_vina_maps(center=[float(uc['center_x']), float(uc['center_y']), float(uc['center_z'])], \
                            box_size=[float(uc['size_x']), float(uc['size_y']), float(uc['size_z'])])
    elif docking_type == 'ad4':
        v = Vina(sf_name='ad4', cpu=4, verbosity=0)
        v.load_maps(map_prefix_filename = receptor)
        
    # Ask rank 0 for ligands and dock until rank 0 says done
    while True:
        comm.send(rank,dest=0) # Ask rank 0 for another set of ligands
        ligand_set_path = comm.recv(source=0) # Wait for a response
        if ligand_set_path == 'no more ligands':
            comm.send('message received--proceed to post-processing',dest=0)
            break
        ligands = unpickle_and_decompress(ligand_set_path)
        run_docking(ligands, v)



def sort():
    # Cats all results files into one, arranges each line to read: (ligand, top score), then sorts by score so that highest scoring ligands are on top; prints these sorted results are written to processed_results.txt; finally cleans up the directory
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
        ligands = pre_processing()
        # Let other ranks know pre-processing is finished; they can now ask for work
        for i in range(size):
            comm.sendrecv('pre-processing finished; ask for work', dest=i)

        # Until all ligands have been docked, send more work to worker ranks
        while ligands:
            source = comm.recv(source=MPI.ANY_SOURCE)
            comm.send(ligands.pop(), dest=source)

        # When all ligands have been sent, let worker ranks know they can stop
        for i in range(size):
            comm.send('no more ligands', dest=i)
            comm.recv(source=i)

        # Post-Processing
        sort()
    else: # All ranks besides rank 0
        comm.recv(source=0) # Wait for rank 0 to finish pre-processing
        comm.send(rank, dest=0)
        processing()    
        


main()
