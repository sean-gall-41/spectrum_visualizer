import sys
import os.path
import pyaudio
import wave
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import math
import struct


def generate_sin_wave_file(freq=440., amp=2.**16, frate=22050,
                           data_points=44100, nchannels=1, sampwidth=2,
                           comptype="NONE", compname="not compressed"):

    duration = data_points / frate
    fname = 'Sine_{f}Hz_{a}Amp_{s}s.wav'.format(f=freq, a=amp, s=duration)

    # Check if file already exists. Saves some time if it already does
    if os.path.isfile(fname):
        return fname
    else:
        data = [math.sin(2 * math.pi * freq * (x / frate))
                for x in range(data_points)]
        wav_file = wave.open(fname, 'wb')
        wav_file.setparams(
            (nchannels, sampwidth, frate, data_points, comptype, compname))
        for v in data:
            wav_file.writeframes(struct.pack('h', int(v * amp / 2)))
        wav_file.close()
        return fname


class Plot2D(object):
    def __init__(self, filename):
        self.filename = filename
        self.traces = dict()

        pg.setConfigOptions(antialias=True)
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title="Frequency Analyzer")
        self.win.resize(1000, 600)
        self.win.setWindowTitle('Spectrum Analysis')
        self.raw_waveform = self.win.addPlot(title='raw waveform', row=1,
                                             col=1)
        self.spectrum = self.win.addPlot(title='spectrum', row=2, col=1)

        self.CHUNK = 1024

        try:
            self.wf = wave.open(self.filename, 'rb')

        except FileNotFoundError:
            print('File not found. Exiting...')

        else:
            self.p = pyaudio.PyAudio()
            self.sstream = self.p.open(
                            format=self.p.get_format_from_width(
                                self.wf.getsampwidth()),
                            channels=self.wf.getnchannels(),
                            rate=self.wf.getframerate(),
                            output=True)

            self.t_data = np.arange(0,
                                    self.wf.getnchannels()*self.CHUNK,
                                    1)
            # obtain t data in seconds
            self.t_data = self.t_data / self.wf.getframerate()
            # scale t data to ms
            self.t_data = 1000 * self.t_data
            # find number of unique points to cut off graph at nyquist freq
            self.n_unique_pts = int(math.ceil((self.CHUNK+1) / 2.))
            # obtain f data in Hz
            self.f_data = np.arange(0, self.n_unique_pts, 1.) * \
                (self.wf.getframerate() / self.CHUNK)

    # Starts Qt event loop unless running in interactive mode or using pyside.
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    # TODO: bugfix: getting divide by zero errors in log modes
    def set_plotdata(self, name, dataset_x, dataset_y, hist=False):
        # If plot 'name' is initialized, set data
        if name in self.traces:
            self.traces[name].setData(dataset_x, dataset_y)
        # If plot 'name' is not initialized, add it to our traces dict and
        # set up that plot item.
        else:
            if name == 'raw_waveform':
                self.traces[name] = self.raw_waveform.plot(pen='b', width=3)
                # y units in arbitrary units, normalized to lie in (-1., 1,)
                self.raw_waveform.setYRange(-1, 1, padding=0)
                # x units in ms
                self.raw_waveform.setXRange(0, np.max(self.t_data),
                                            padding=0.005)

            if name == 'spectrum':
                if hist:
                    self.traces[name] = self.spectrum.plot(np.ones(2), np.ones(1), stepMode=True, brush=(0,0,255,150))
                else:
                    self.traces[name] = self.spectrum.plot(pen='b', width=3)
                self.spectrum.setXRange(0, self.wf.getframerate() / 2)
                np.seterr(divide='ignore')
                self.spectrum.setLogMode(x=True, y=False)
                # TODO: not reaching maximum value? --> max value slightly off
                # self.spectrum.setYRange(0., 1., padding=0)
                # self.spectrum.setXRange(np.log10(20), 0, padding=0.005)

    def update(self):
        # read data one chunk at a time, write each chunk to output stream
        self.raw_wav_data = self.wf.readframes(self.CHUNK)
        self.sstream.write(self.raw_wav_data)

        # Check to see if we've run out of data to read. If so, exit
        self.wav_data = np.frombuffer(self.raw_wav_data, dtype=np.int16)
        if len(self.wav_data) != self.wf.getnchannels()*self.CHUNK:
            self.terminate_audio_processes()
            sys.exit()

        # Normalize wave data to lie within range (-1, 1)
        self.wav_data = self.wav_data / 2.**15
        # take fft, find magn of result, and select (negative?) freq components
        self.amp_data = np.abs(fft(self.wav_data)[0:self.n_unique_pts])
        # 'Normalization' and intensity correction for taking half total signal
        self.amp_data = (2. / self.CHUNK) * self.amp_data

        # conversion to decibels I suppose and some data cleaning
        # self.amp_data = 20 * np.log10(self.amp_data)
        # self.amp_data[np.isinf(self.amp_data)] = 0
        
        # TODO: plot histogram data in spectrum plot item
        # testing: code to calculate frequency of sine wave input
        # freqs = fftfreq(len(self.amp_data))
        # max_freq = freqs[np.argmax(np.abs(self.amp_data))]
        # freq_Hz = abs(max_freq * self.wf.getframerate())
        # with 440 signal, getting about 431...pretty close but why off?

        self.set_plotdata(name='raw_waveform', dataset_x=self.t_data,
                          dataset_y=self.wav_data,)

        self.set_plotdata(name='spectrum', dataset_x=self.f_data,
                          dataset_y=self.amp_data,)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(15)
        self.start()

    def terminate_audio_processes(self):
        self.sstream.close()
        self.p.terminate()


if __name__ == '__main__':
    try:
        filename = sys.argv[1]

    # Checks whether any filename was entered: if not, assume user wants to
    # generate a sine wave
    except IndexError:
        # TODO: prompt user if they want different values than default
        filename = generate_sin_wave_file()

    else:
        # Checks whether filename has correct extension
        if not filename.endswith('.wav'):
            print('invalid file format. Exiting...')
            sys.exit(1)

    plt = Plot2D(filename)
    plt.animation()
