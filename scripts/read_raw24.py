
from numpy import dtype , fromfile
import numpy as np

def load_raw24(filename):

    d = fromfile(filename,dtype='>u1')

    d = np.reshape(d, (-1,3))

    d = np.concatenate((np.zeros((d.shape[0],1), dtype='>u1'), d), axis=1)

    d.dtype = '>u4'

    return d
