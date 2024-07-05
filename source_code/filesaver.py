import PySimpleGUI as sg
from check_functions import *

def popup_saver():
    layout_folder = [
        [sg.Text('Zielordner auswählen')],
        [sg.FolderBrowse('Auswahl'),sg.Input(key='-destfolder-', enable_events=True)],
        [sg.Text('Name eintippen')],
        [sg.Input(key='-filename-',enable_events=True)],
        [sg.Button('Speichern',disabled=True),sg.Button('Abbrechen')],
    ]
    saver_gui = sg.Window('saver',layout=layout_folder,size=(300,200),modal=True)
    folder = None
    filename = None

    while True:
        event,values=saver_gui.read()
        if event == '-destfolder-' and path_check(values['-destfolder-']):
            folder = values['-destfolder-']
        elif event == '-filename-':
            filename = values['-filename-']
        elif event == 'Abbrechen' or event == sg.WIN_CLOSED:
            break
        elif event == 'Speichern':
            break
        try:
            saver_gui['Speichern'].update(disabled=not (path_check(folder) and check_string(filename)))
        except:
            None
    saver_gui.close()
    return folder,filename