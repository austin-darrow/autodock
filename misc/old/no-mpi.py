import os
from vina import Vina
import subprocess
import pickle

filelist = open('filelist-module.txt', 'r+')

v = Vina(sf_name='vina')
v.set_receptor('./input/receptors/1iep_receptor.pdbqt')
v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])

def vina_dock(ligand, v):
    v.set_ligand_from_string(pickle.load(open('ligands.pkl', 'rb')))
    v.dock()
    v.write_poses(f'./output/vina_python/vina_out_{ligand}', n_poses=1, overwrite=True)

for line_no, line in enumerate(filelist):
    vina_dock(line.strip(), v)
    subprocess.run([f"grep -i -m 1 'REMARK VINA RESULT:' output/vina_python/vina_out_{line.strip()} | awk '{{print $4}}' >> results.txt; echo {line.strip()} >> results.txt"], shell=True)

filelist.close()
