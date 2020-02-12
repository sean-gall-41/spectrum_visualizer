import sys
import os.path
import pyaudio
import wave
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import argparse
import math
import struct


def generate_sin_wave_file(freq=440., amp=2.**16, duration=1., frate=22050,
                           nchannels=1, sampwidth=2, comptype="NONE",
                           compname="not compressed"):

    data_points = int(duration * frate)
    fname = 'Sine_{f}Hz_{a}Amp_{s}s.wav'.format(f=freq, a=amp, s=duration)

    # Check if file already exists. Saves some time if it already does
    if not os.path.isfile(fname):
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
        self.win = pg.GraphicsWindow(title="Music Visualizer")
        self.win.resize(1280, 720)
        self.spectrum = self.win.addPlot(row=1, col=1)
        self.spectrum.hideAxis('bottom')
        self.spectrum.hideAxis('left')
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
            # testing different total numbers of unique points
            self.n_unique_pts = int(math.ceil((self.CHUNK+1) / 8.))
            # obtain f data in Hz
            self.f_data = np.arange(0, self.n_unique_pts, 1.) * \
                (self.wf.getframerate() / self.CHUNK)

    # Starts Qt event loop unless running in interactive mode or using pyside.
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, dataset_x, dataset_y):
        if name in self.traces:
            self.traces[name].setOpts(height=dataset_y)
        else:
            self.traces[name] = pg.BarGraphItem(x=dataset_x,
                                                height=dataset_y,
                                                width=1.5, brush='g')
            self.spectrum.addItem(self.traces[name])

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
        # take fft, find magn of result, and select pos freq components
        self.amp_data = np.abs(fft(self.wav_data)[0:self.n_unique_pts])
        # 'Normalization' and intensity correction for taking half total signal
        self.amp_data = (2. / self.CHUNK) * self.amp_data
        self.set_plotdata("spectrum", self.f_data, self.amp_data)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(15)
        self.start()

    def terminate_audio_processes(self):
        self.sstream.close()
        self.p.terminate()


# TODO: Clean up this code. reimplement arg parser and error checking
# if you want to go the extra mile: do some unit tests on input
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Displays a visualization "
                                     "of the spectrum of a generated signal "
                                     "or a specified file.")

    parser.add_argument("-f", "--file", help="include file to be analyzed and "
                        "played. Accepted formats are: *.wav")

    subparsers = parser.add_subparsers()

    generateparser = subparsers.add_parser("generate", help="command to "
                                           "generate a sine wave")
    generateparser.add_argument("-fr", "--frequency", type=float, default=440.,
                                help="frequency (in Hz) of generated sine "
                                "wave")
    generateparser.add_argument("-d", "--duration", type=float, default=1.,
                                help="duration (in seconds) of the generated "
                                "sine wave")
    args = parser.parse_args()

    if args.file is not None:
        filename = args.file
        if os.path.isfile(filename):
            if not filename.endswith('.wav'):
                print('invalid file format. Exiting...')
                sys.exit(1)
        else:
            print("file not recognized. Exiting...")
            sys.exit(2)
    else:
        print("generate the wave")
        filename = generate_sin_wave_file(freq=args.frequency,
                                          duration=args.duration)

    plt = Plot2D(filename)
    plt.animation()
