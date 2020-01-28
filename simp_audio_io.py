"""
This file is purely for debugging audio_visualizer.py.
"""
import sys
import numpy as np
# from scipy.io import wavfile
import wave
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.fftpack import fft

CHUNK = 1024

try:
    filename = sys.argv[1]
except IndexError:
    print('no argument entered in position 1. Exiting...')
    sys.exit(1)
else:
    wf = wave.open(filename, 'rb')
    t_data = np.arange(0, wf.getnchannels()*CHUNK, 1)
    t_data = t_data / wf.getframerate()
    t_data = 1000 * t_data
    n_unique_pts = int(math.ceil((CHUNK+1) / 2.))
    # obtain f data in Hz
    f_data = np.arange(0, n_unique_pts, 1.) * \
        (wf.getframerate() / CHUNK)

    # Simple loop to see how histogram data changes with each chunk 
    # passed in from our WAV file. 
    # FIXME: extremely large first bin "drowns out" the rest of the data.
    #        Need to find a fix, such as a cutoff so that data is presentable.
    while True:
        raw_wave_data = wf.readframes(CHUNK)
        wave_data = np.frombuffer(raw_wave_data, dtype=np.int16)
        wave_data = wave_data / 2.**15

        amp_data = np.abs(fft(wave_data)[0:n_unique_pts])
        amp_data = (2 / CHUNK) * amp_data
        # plt.plot(np.log10(f_data), amp_data)
        # bin_data, bins = np.histogram(amp_data, bins=np.linspace(0, n_unique_pts, 64))
        plt.hist(amp_data[20:], bins=128)
        plt.show()
