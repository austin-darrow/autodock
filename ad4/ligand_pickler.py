import os
import pickle

ligands = {}

for filename in os.listdir('ligands'):
    f = open(f'ligands/{filename}', 'r')
    lines = f.read()
    ligands[filename] = lines

pickle.dump(ligands, open('ligands.pkl', 'wb'))
