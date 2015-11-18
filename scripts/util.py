from __future__ import division
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scikits.audiolab import Sndfile

def read_wav(name):

    from scikits.audiolab import Sndfile

    sf = Sndfile(name)
    return sf.read_frames(sf.nframes)

def spectrum(x):
    f = np.fft.rfftfreq(x.shape[0])
    X = 20*np.log10(np.abs(np.fft.rfft(x)/np.sqrt(x.shape[0])))
    plt.plot(f, X)

