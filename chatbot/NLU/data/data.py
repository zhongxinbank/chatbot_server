import torch
from torch.autograd import Variable
import pickle
import os

def prepare_sequence(seq, to_ix):
    idxs = list(map(lambda w: to_ix[w] if w in to_ix.keys() else to_ix["<UNK>"], seq))
    tensor = Variable(torch.LongTensor(idxs))
    return tensor

def preprocessing(file_path):
    try:
        word2index, tag2index, intent2index = pickle.load(open(file_path, "rb"))
        return word2index, tag2index, intent2index
    except Exception:
        return [None] * 3