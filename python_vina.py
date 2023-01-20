import subprocess
import sys
import os
import time
from os.path import basename
from vina import Vina

NUM_LIGANDS = '10'
#MODEL = sys.argv[1]
#FORCEFIELD = sys.argv[2]

def benchmark(start_time, end_time, num_ligands, model, forcefield):
    benchmark_file = open("benchmarks.txt", 'a+')
    benchmark_file.write("\n" + f'Ligands: {num_ligands}' + "\n" + f'Model: {model}' + "\n" + f'Forcefield: {forcefield}'+ "\n")
    benchmark_file.write("Start: " + str(start_time) + " || End: " + str(end_time) + f' || Total time: {end_time - start_time}' + "\n") 
    benchmark_file.close()

def dock_ligands(model='basic', forcefield='vina'):
    if not os.path.exists('output'):
        os.makedirs('output')
    
    for file in os.listdir('/work/09252/adarrow/ls6/autodock/input/ligands'):
        if model=='basic' and forcefield=='vina':
            subprocess.run([f"vina --receptor ./input/receptors/1iep_receptor.pdbqt --ligand ./input/ligands/{file} \
                            --config ./configs/1iep_receptor_vina_box.txt --exhaustiveness=32 \
                            --out ./output/vina_basic/VINA_OUT_{file} | sed -n '22p; 39p' | awk '{{print $2}}' >> results_vina_basic.txt"], shell=True)
        elif model=='flex' and forcefield=='vina':
            subprocess.run([f"vina --receptor ./input/receptors/1fpu_receptor_rigid.pdbqt --flex ./input/receptors/1fpu_receptor_flex.pdbqt \
                            --ligand  ./input/ligands/{file} --config ./configs/1fpu_receptor_rigid_vina_box.txt \
                            --exhaustiveness 32 --out ./output/vina_flex/VINA_OUT_{file} \
                            | sed -n '23p; 40p' |awk '{{print $2}}' >> results_vina_flex.txt"], shell=True)
        elif model=='basic' and forcefield=='ad4':
            subprocess.run([f"vina --ligand ./input/ligands/{file} --maps ./input/maps/1iep_receptor --scoring ad4 \
                            --exhaustiveness 32 --out ./output/ad4_basic/AD4_OUT_{file} \
                            | sed -n '21p; 36p' | awk '{{print $2}}' >> results_ad4_basic.txt"], shell=True)
        elif model=='flex' and forcefield=='ad4':
            subprocess.run([f"vina --flex ./input/receptors/1fpu_receptor_flex.pdbqt --ligand ./input/ligands/{file} \
                            --maps ./input/maps/1fpu_receptor_rigid --scoring ad4 --exhaustiveness 32 --out \
                            ./output/ad4_flex/AD4_OUT_{file} | sed -n '22p; 37p' | awk '{{print $2}}' >> results_ad4_flex.txt"], shell=True)

def vina_dock(ligand):
    v = Vina(sf_name='vina')
    v.set_receptor('./input/receptors/1iep_receptor.pdbqt')
    v.set_ligand_from_file(ligand)
    v.compute_vina_maps(center=[15.190, 53.903, 16.917], box_size=[20, 20, 20])
    
    # Score the current pose
    energy = v.score()
    print('Score before minimization: %.3f (kcal/mol)' % energy[0])

    # Minimized locally the current pose
    energy_minimized = v.optimize()
    print('Score after minimization : %.3f (kcal/mol)' % energy_minimized[0])
    v.write_pose(f'./output/vina_python/{ligand}_minimized.pdbqt', overwrite=True)
    
    # Dock the ligand
    v.dock(exhaustiveness=32, n_poses=20)
    v.write_poses(f'./output/vina_python/{ligand}_vina_out.pdbqt', n_poses=5, overwrite=True)

def vina_dock_multiple():
    for filename in os.listdir('./input/ligands'):
        vina_dock(filename)


def sort():
    INPUTFILE = f'results_{FORCEFIELD}_{MODEL}.txt'
    OUTPUTFILE = 'parsed_results.txt'

    result = []

    with open(INPUTFILE) as data:
        while line := data.readline():
            filename = basename(line.split()[-1])
            v = data.readline().split()[0]
            result.append(f'{v} {filename}\n')


    with open(OUTPUTFILE, 'w') as data:
        data.writelines(sorted(result, key=lambda x: float(x.split()[0])))

def run_trial():
   # start_time = time.time()
    dock_ligands(MODEL, FORCEFIELD)
   # end_time = time.time()
   # benchmark(start_time, end_time, NUM_LIGANDS, MODEL, FORCEFIELD)
   # sort()
   

#run_trial()
vina_dock_multiple()
