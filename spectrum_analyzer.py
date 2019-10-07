import pyaudio 
import wave
import sys #so we can utilize argv

if len(sys.argv) < 2:
    print("Plays an audio file. \n\nUsage: python %s filename.[file_extension]"
        % sys.argv[0])
    sys.exit(-1)

sound_file = wave.open(sys.argv[1], 'r')
# import PySimpleGUI as gui

# layout = [[gui.Button('Start')],[gui.Exit()]]

# window = gui.Window('spectrum analyzer', layout)

# while True:
#     event, values = window.Read()
#     print(event, values)
#     if event in (None, 'Exit'):
#         break

# window.close()