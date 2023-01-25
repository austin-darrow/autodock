from vina import Vina
from mpi4py import MPI
import subprocess
import pickle

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

v = Vina(sf_name='ad4')
ligands = pickle.load(open('ligands.pkl', 'rb'))
v.load_maps(map_prefix_filename='1iep_receptor')

def vina_dock(ligand, v, filename):
    v.set_ligand_from_string(ligand)
    v.dock()
    v.write_poses(f'output/ad4_out/ad4_out_{filename}', n_poses=1, overwrite=True)

def main():
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        if(index % size == rank):
            vina_dock(ligand, v, filename)
            subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' output/ad4_out/ad4_out_{filename} \
                            | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                            >> results_{rank}.txt"], shell=True)

main()
