
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.linalg import toeplitz
from scipy.io import wavfile
from scipy.signal import resample,fftconvolve

import pyroomacoustics as pra
#import TDBeamformers as tdb

# Beam pattern figure properties
freq=[800, 1600]
figsize=(1.88,2.24)
xlim=[-4,8]
ylim=[-4.9,9.4]

# Some simulation parameters
Fs = 8000
t0 = 1./(Fs*np.pi*1e-2)  # starting time function of sinc decay in RIR response
absorption = 0.90
max_order_sim = 10
sigma2_n = 1e-7

# Room 1 : Shoe box
room_dim = [4, 6]

# the good source is fixed for all 
good_source = [1, 4.5]       # good source
normal_interferer = [2.8, 4.3]   # interferer
hard_interferer = [1.5, 3]   # interferer in direct path
#normal_interferer = hard_interferer

# microphone array design parameters
mic1 = [2, 1.5]         # position
M = 8                   # number of microphones
d = 0.08                # distance between microphones
phi = 0.                # angle from horizontal
max_order_design = 2    # maximum image generation used in design
shape = 'Linear'        # array shape
Lg_t = 0.050            # Filter size in seconds
Lg = np.ceil(Lg_t*Fs)   # Filter size in samples
delay = 0.02

# define the FFT length
N = 1024

# create a microphone array
R = np.array([[25.146, 51.816, 24.13, 44.45, 64.516, 84.582],
    [33.528, 36.068, 16.002, 10.414, 10.668, 16.764]])*1e-3
R -= R.mean(axis=1, keepdims=True) - np.array([mic1]).T
mics = pra.Beamformer(R, Fs, N, Lg=Lg)


# The first signal (of interest) is singing
rate1, signal1 = wavfile.read('samples/singing_'+str(Fs)+'.wav')
signal1 = np.array(signal1, dtype=float)
signal1 = pra.normalize(signal1)
signal1 = pra.highpass(signal1, Fs)
delay1 = 0.

# the second signal (interferer) is some german speech
rate2, signal2 = wavfile.read('samples/german_speech_'+str(Fs)+'.wav')
signal2 = np.array(signal2, dtype=float)
signal2 = pra.normalize(signal2)
signal2 = pra.highpass(signal2, Fs)
delay2 = 1.

# create the room with sources and mics
room1 = pra.Room.shoeBox2D(
    [0,0],
    room_dim,
    fs=Fs,
    t0 = t0,
    max_order=max_order_sim,
    absorption=absorption,
    sigma2_awgn=sigma2_n)

# add mic and good source to room
room1.addSource(good_source, signal=signal1, delay=delay1)
room1.addMicrophoneArray(mics)

# add interferer
room1.addSource(normal_interferer, signal=signal2, delay=delay2)

# simulate the acoustic
room1.compute_RIR()
room1.simulate()

# compute beamforming filters
good_sources = room1.sources[0][:max_order_design+1]
bad_sources = room1.sources[1][:max_order_design+1]
mics.rakePerceptualFilters(good_sources, bad_sources, sigma2_n*np.eye(mics.Lg*mics.M), delay=delay)

# process the signal
output = mics.process()

# save to output file
inp = pra.normalize(pra.highpass(mics.signals[mics.M/2], Fs))
out = pra.normalize(pra.highpass(output, Fs))

wavfile.write('output_samples/input.wav', Fs, inp)
wavfile.write('output_samples/output.wav', Fs, out)

'''
Plot Stuff
'''
f_size = (3.93, 1.57)

# plot the room and beamformer
room1.plot(img_order=np.minimum(room1.max_order, max_order_design), 
        freq=freq)

# plot the beamforming weights
plt.figure()
mics.plot(FD=False)

# plot before/after processing
plt.figure()
pra.comparePlot(inp, out, Fs)

# plot angle/frequency plot
plt.figure()
mics.plot_beam_response()

plt.show()
