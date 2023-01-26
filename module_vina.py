from vina import Vina
from mpi4py import MPI
import subprocess
import pickle

receptor='1iep_receptor'

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

v = Vina(sf_name='vina')
v.set_receptor(f'./input/receptors/{receptor}.pdbqt')
v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])

ligands = pickle.load(open('ligands.pkl', 'rb'))

def vina_dock(ligand, v, filename):
    v.set_ligand_from_string(ligand)
    v.dock()
    v.write_poses(f'./output/vina/vina_out_{filename}', n_poses=1, overwrite=True)

def main():
    for index, filename in enumerate(ligands):
        ligand = ligands[filename]
        if(index % size == rank):
            vina_dock(ligand, v, filename)
            subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' output/vina/vina_out_{filename} \
                            | awk '{{print $4}}' >> results_{rank}.txt; echo {filename} \
                            >> results_{rank}.txt"], shell=True)

main()
