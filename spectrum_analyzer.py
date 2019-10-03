import PySimpleGUI as gui

layout = [[gui.Button('Start')],[gui.Exit()]]

window = gui.Window('spectrum analyzer', layout)

while True:
    event, values = window.Read()
    print(event, values)
    if event in (None, 'Exit'):
        break

window.close()