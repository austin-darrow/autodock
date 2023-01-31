import os
import os.path
import pickle
import blosc
import copy

MAX_LIGANDS_PER_SET = 1000
path = '../../Enamine-PC'
ligands = {}

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

def pickle_and_compress(chunked_list_of_dicts):
    for index, dictionary in enumerate(chunked_list_of_dicts):
        pickled_dict = pickle.dumps(dictionary)
        compressed_pickle = blosc.compress(pickled_dict)
        with open(f'./Enamine-PC-Pickled/ligands_{index}.dat', 'wb') as f:
            f.write(compressed_pickle)

def main():
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in [f for f in filenames]:    
            ligand = open(f'{dirpath}/{filename}', 'r')
            ligands[filename] = ligand.read()

    chunked_list_of_dicts = split_dict_to_multiple(ligands, MAX_LIGANDS_PER_SET)
    pickle_and_compress(chunked_list_of_dicts)





main()
