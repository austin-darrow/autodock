import os
import pickle

ligands = {}
path_10 = '../../Enamine-PC/10_set'
path_50 = '../../ZINC-in-trials/2'
path_200 = '../../Enamine-PC/200_set'
path_10k = '../../Enamine-PC/1'

for filename in os.listdir(path_10):
    f = open(f'{path_10}/{filename}', 'r')
    lines = f.read()
    ligands[filename] = lines

pickle.dump(ligands, open('ligands_10.pkl', 'wb'))
