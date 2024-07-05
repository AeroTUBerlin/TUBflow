import PySimpleGUI as sg
import json

from check_functions import *
from filesaver import *


#set = np.load("C:/Users/leoha/Documents/GitHub/Leo_Bachelor/MainBuild/settings/preset_1.npy",allow_pickle=True).item()

def settings_window_gui(settings_dict,method):
    
    input_settings = settings_dict.copy()
    
    
    #Layout Header 
    settings_layout = [
            
        ]

    #Autocomplete layout
    settings_List = list(settings_dict)
    for setting_element_key in settings_List:
        if setting_element_key == 'Start_Frame':
            settings_layout.append([sg.Text('General Flow Settings')])
        elif setting_element_key == 'pyr_scale' and method == 'gf':
            settings_layout.append([sg.Text('Farnebäck Settings')])
        elif setting_element_key == 'pyr_scale' and method != 'gf':
            break
        settings_layout.append([sg.Text(setting_element_key),sg.Input(default_text=settings_dict[setting_element_key])])
    
    #Layout Footer 
    settings_layout.append([sg.Button("apply"),sg.Button('reset changes'),sg.Button("Save_Settings")])
    
    #Lauch page
    settings_window = sg.Window("New Window", settings_layout,modal=True,enable_close_attempted_event=True)
    
    #Wait for Completion
    while True:
        new_event, new_values = settings_window.read()
    
        if new_event == "apply":
            for i in range(len(new_values)):
                Value = new_values[i]
                settings_dict[settings_List[i]] = Value
            
            settings_dict = dectVarCorrection(input_settings,settings_dict)
            break

        elif new_event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            pass
        
        elif new_event == "Save_Settings":
            for i in range(len(new_values)):
                Value = new_values[i]
                settings_dict[settings_List[i]] = Value
            
            settings_dict = dectVarCorrection(input_settings,settings_dict)
            folder,filename = popup_saver()
            try:
                json_path = folder + '/' + filename + '.json'
                with open(json_path,'w') as f:
                    json.dump(settings_dict,f, indent=4)
                sg.popup_ok('Datei erfolgreich gespeichert.')
            except:
                sg.popup_ok('Fehler beim Speichern. Erneut versuchen')

        elif new_event == 'reset changes':
            for i in range(len(settings_List)):
                settings_window[i].update(input_settings[settings_List[i]])

    settings_window.close()

    return settings_dict

def dectVarCorrection(Paragon,Target):
    Key_List = list(Paragon)
    for Key in Key_List:
        Var = Paragon[Key]
        if isinstance(Var, str):
            Target[Key] = str(Target[Key])
        elif isinstance(Var, int):
            Target[Key] = int(Target[Key])
        elif isinstance(Var, float):
            Target[Key] = float(Target[Key])
        elif isinstance(Var, tuple) and not isinstance(Target[Key], tuple):
            Target[Key] = replaceList(['(',')',' ','[',']'],'',Target[Key])
            Target[Key] = tuple(map(float,Target[Key].split(',')))
    return Target 
            
            
def replaceList(Src_List,Dst,Target):
    for element in Src_List:
        Target = Target.replace(element,Dst)
    return Target

#new_set = settings_window_gui(set)