from vina import Vina
from mpi4py import MPI
import subprocess
import pickle
from os.path import exists
from os.path import basename

# Setup
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
 
receptor='1fpu_receptor'
receptor_path = f'/scratch/09252/adarrow/autodock/input/receptors/{receptor}'
docking_type = 'vina'
ligand_library = './input/ligands_10.pkl'
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

def run_docking(ligand, v, filename):
    v.set_ligand_from_string(ligand)
    v.dock()
    v.write_poses(f'./output/{docking_type}/output_{filename}', n_poses=1, overwrite=True)

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
    # Pre-Processing (only rank 0)
    if rank == 0:
        prep_config()
        prep_receptor()
        prep_maps()
        for i in range(size):
            comm.send('', dest=i)
    else:
        comm.recv(source=0)

    # Initialize Vina or AD4 configurations
    ligands = pickle.load(open(ligand_library, 'rb'))
    
    if docking_type == 'vina':
        v = Vina(sf_name='vina', cpu=1, verbosity=0)
        v.set_receptor(f'{receptor_path}.pdbqt')
        uc = user_configs
        v.compute_vina_maps(center=[uc[center_x], uc[center_y], uc[center_z]], box_size=[uc[size_x], uc[size_y], uc[size_z]])
    elif docking_type == 'ad4':
        v = Vina(sf_name='ad4', cpu=1, verbosity=0)
        v.load_maps(map_prefix_filename = receptor)

    # Run docking
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        if(index % size == rank):
            run_docking(ligand, v, filename)
            subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' ./output/{docking_type}/output_{filename} \
                            | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                            >> results_{rank}.txt"], shell=True)
    comm.Barrier()
    # Post-Processing (only rank 0)
    if rank == 0:
        sort()

main()
