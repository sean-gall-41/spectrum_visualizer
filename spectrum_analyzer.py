import pyaudio 
import wave
import sys #so we can utilize argv

CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

if len(sys.argv) < 2:
    print("Plays an audio file. \n\nUsage: python %s filename.[file_extension]"
        % sys.argv[0])
    sys.exit(-1)

f = wave.open(sys.argv[1], 'r')

p = pyaudio.PyAudio()

stream = p.open(
    format=p.get_format_from_width(f.getsampwidth()),
    channels=f.getnchannels(),
    rate=f.getframerate(),
    output=True
)

data = f.readframes(CHUNK)

while data != '':
    stream.write(data)
    data = f.readframes(CHUNK)

stream.close()
p.terminate()
# import PySimpleGUI as gui

# layout = [[gui.Button('Start')],[gui.Exit()]]

# window = gui.Window('spectrum analyzer', layout)

# while True:
#     event, values = window.Read()
#     print(event, values)
#     if event in (None, 'Exit'):
#         break

# window.close()