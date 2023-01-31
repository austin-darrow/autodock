import os
import os.path
import pickle

MAX_LIGANDS_PER_SET = 1000

ligands = {}
path = '../../Enamine-PC'
for dirpath, dirnames, filenames in os.walk(path):
    for filename in [f for f in filenames]:    
        ligand = open(f'{dirpath}/{filename}', 'r')
        ligands[filename] = ligand.read()

#pickle.dump(ligands, open('ligands_10.pkl', 'wb'))

import copy
def split_dict_to_multiple(input_dict, max_limit=200):
    """Splits dict into multiple dicts with given maximum size. 
    Returns a list of dictionaries."""
    chunks = []
    curr_dict ={}
    for k, v in input_dict.items():
        if len(curr_dict.keys()) < max_limit:
            curr_dict.update({k: v})
        else:
            chunks.append(copy.deepcopy(curr_dict))
            curr_dict = {k: v}
    # update last curr_dict
    chunks.append(curr_dict)
    return chunks

chunked_list_of_dicts = split_dict_to_multiple(ligands, MAX_LIGANDS_PER_SET)

def pickler(chunked_list_of_dicts):
    for index, dictionary in enumerate(chunked_list_of_dicts):
        pickle.dump(dictionary, open(f'./Enamine-PC-Pickled/ligands_{index}.pkl', 'wb'))

pickler(chunked_list_of_dicts)
