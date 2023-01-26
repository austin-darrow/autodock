import pickle

ligands = pickle.load(open('ligands.pkl', 'rb'))
with open('test_ligand.pdbqt', 'w+') as test:
    test.write(ligands[0])
