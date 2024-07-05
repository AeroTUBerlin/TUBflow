# =============================================================================
# Packages
# =============================================================================
import PySimpleGUI as sg
import numpy as np
import cv2 as cv
import os
import json
import shutil

# =============================================================================
# Includes
# =============================================================================
from Operation_Handler import *
from mask_operation import *
from vid_settings import settings_window_gui
from check_functions import *
from mask_operation import *
from filesaver import *
from image_preview import *
from dictionaries_and_buttons import *
from GUI_setup import *

# =============================================================================
# GUI
# =============================================================================

def FlowCalGui():
    global img

    tab1_layout = [
        # Source Video
        [sg.Text("1. Source Video or series of frames")],
        [sg.FileBrowse('Video',file_types=videos),sg.Input(key="-vid_input_FILE-",enable_events=True)],
        [sg.FolderBrowse('Series of frames'),sg.Input(key="-frame_input_FOLDER-",enable_events=True)],
        [sg.HorizontalSeparator()],

        # Mask
        [sg.Text("2. Mask")],
        [sg.FileBrowse(Select,file_types=npy_files,disabled=True,key='-maskbrowse-'),sg.Input(key='-Mask_FILE-', enable_events=True)],
        [sg.Button(mask_create,disabled=True),sg.Button(mask_preview,disabled=True),sg.Button(mask_delete,disabled=True)],
        [sg.Text("Mask area"),sg.Radio('outside','area',key='-out-',default=True),sg.Radio('inside','area',key='-in-')],
        [sg.Button(mask_save,disabled=True)],
        [sg.HorizontalSeparator()],

        # Flow Settings
        [sg.Text("3. Flow Settings")],
        [sg.Text("Optical Flow Method"),sg.Radio('Gunnar-Färneback','method',key='-gf-',default=True),sg.Radio('Horn-Schunck','method',key='-hs-'),sg.Radio('DisOpticalFlow','method',key='-dis-')],
        [sg.FileBrowse(Select,disabled=True,key='-flowsetbrowse-'),sg.Input(key='-flow_settings_FILE-', enable_events=True)],
        [sg.Button(flow_set,disabled=True)],
        [sg.HorizontalSeparator()],

        # Execute
        [sg.Button(flow_run,disabled=True),sg.Button(flow_save,disabled=True)],
        [sg.Button(mean_show,disabled=True),sg.Button(mean_save,disabled=True)]
    ]

    tab2_layout = [
        # Flow Selection
        [sg.Text('1. Use the previously calculated Vector field or load a new one?')],
        [sg.Button(transfer_flow,disabled=True)],
        [sg.FileBrowse(load_flow,enable_events=True,key='-load_flow_path-',file_types=npy_files)],

        # Plot Settings
        [sg.Text('2. Plot Settings.')],
        [sg.FileBrowse(Select,file_types=npy_files,disabled=True,key='-plot_set_browse-'),sg.Input(key='-plot_settings_FILE-',enable_events=True)],
        [sg.Button(plot_set,disabled=True),sg.Button(plot_set_default,disabled=True)],
        [sg.HorizontalSeparator()],

        # HSV 
        [sg.Button(hsv_preview,disabled=True),sg.Button(hsv_save,disabled=True)],
        [sg.Button(plot_run,disabled=True),sg.Button(plot_preview,disabled=True),sg.Button(plot_save,disabled=True)]
    ]

    tab_group = [
        [sg.TabGroup(
            [[
                sg.Tab('Flow', tab1_layout),
                sg.Tab('Plot', tab2_layout)
            ]],
            tab_location='centertop',
            pad=((20, 20), (0, 0)) )  # Add this line to set equal padding on left and right
        ],
    ]

    # Adding logos to the top of the window
    layout = [
        [sg.Image(data=img_data_berlin_logo, size=(berlin_new_width, berlin_new_height)), sg.Image(data=img_data_logo, size=(new_width, new_height))],  # Display the resized logos side by side
        [tab_group],
    ]

    window = sg.Window("TUBflow", layout, size=window_size)

    # =============================================================================
    # Event Loop
    # =============================================================================

    while True:
        event,values=window.read()

    # =============================================================================
    # Flow events
    # =============================================================================

        # =============================================================================
        # 1.File Selection
        # =============================================================================
        if event == '-vid_input_FILE-' and path_check(values['-vid_input_FILE-']):
            # Wenn Quellvideo ausgewählt wird
            Video_Settings['Input_Type'] = 'video'
            Video_Settings['Src_Path'] = values['-vid_input_FILE-']
            window['-frame_input_FOLDER-'].update('')
            Video_Settings['Flow_Settings'] = Default_Flow_Settings.copy()
            window['-flowsetbrowse-'].update(disabled=False)
            window['-maskbrowse-'].update(disabled=False)
        
        elif event == '-frame_input_FOLDER-' and path_check(values['-frame_input_FOLDER-']):
            # Wenn Frameordner ausgewählt wird
            Video_Settings['Input_Type'] = 'series'
            Video_Settings['Src_Path'] = values['-frame_input_FOLDER-']
            window['-vid_input_FILE-'].update('')
            Video_Settings['Flow_Settings'] = Default_Flow_Settings.copy()
            window['-flowsetbrowse-'].update(disabled=False)
            window['-maskbrowse-'].update(disabled=False)

        # =============================================================================
        # 2.Mask 
        # =============================================================================
        if img is None:
            # If input is a video
            if Video_Settings['Input_Type'] == 'video':
                try:
                    cap = cv.VideoCapture(Video_Settings['Src_Path'])
                    ret, img = cap.read()
                    cap.release()
                except:
                    sg.popup_error()
                
            # if input is a series of frames
            elif Video_Settings['Input_Type'] == 'series':
                # check if the first file of the folder is a frame
                try:
                    # Get the name of the first file in the folder
                    first_file_name = os.listdir(Video_Settings['Src_Path'])[0]

                    # Construct the full path to the first file
                    first_file_path = os.path.join(Video_Settings['Src_Path'], first_file_name)

                    # Load the first file using OpenCV
                    img = cv.imread(first_file_path)
                # display error if condition is not met
                except:
                    sg.popup_ok('The frame folder must only contain image format')

        # 2.1 Mask Selection
        if event == '-Mask_FILE-' and path_check(values['-Mask_FILE-']) == True:
            # Dateipfad einspeichern
            Video_Settings['Mask_path'] = values['-Mask_FILE-']
            # load mask
            try:
                Video_Settings['Mask'] = load_masks_from_file(Video_Settings['Mask_path'])
                for mask in Video_Settings['Mask']:
                    img_with_mask = Preview_crop(img,mask.points_list)
            except:
                sg.popup_cancel('Loading Failed')

        # 2.2 create mask
        elif event == mask_create:
            img_with_mask = img.copy()
            pts = Mask(img_with_mask)
            if len(pts.points_list) > 2:
                Video_Settings['Mask'].append(pts)
                for mask in Video_Settings['Mask']:
                    img_with_mask = Preview_crop(img,mask.points_list)
            else:
                img_with_mask = img.copy()

        # 2.3 preview mask
        elif event == mask_preview:
            image_preview(img_with_mask)

        # 2.4 delete mask
        elif event == mask_delete:
            Video_Settings['Mask'] = []
            Video_Settings['Mask_path'] = ''
            window['-Mask_FILE-'].update('')
            img = None
        
        # 2.5 save mask
        elif event == mask_save:
            folder,filename = popup_saver()
            save_mask(folder+'/'+filename+'.npy', Video_Settings['Mask'])
            sg.popup_ok("Mask(s) succesfully saved")
            


        # =============================================================================
        # 3.Settings Selection
        # =============================================================================

        # load flow_settings
        if event == '-flow_settings_FILE-' and path_check(values['-flow_settings_FILE-']) == True:
            try:
                with open(values['-flow_settings_FILE-'], 'r') as f:
                    data = json.load(f)
                if 'Flow_Settings' in data:
                    Video_Settings['Flow_Settings'] = data.get('Flow_Settings',{})
                else:
                    Video_Settings['Flow_Settings'] = data
                Video_Settings['Flow_Settings_Path'] = values['-flow_settings_FILE-']
            except:
                sg.popup_ok('An error occured.\n The default settings will be used')
        
        # edit flow settings
        elif event == flow_set:
            if values['-gf-']:
                Video_Settings['Optical_Flow_Method'] = 'gf'
            elif values['-hs-']:
                Video_Settings['Optical_Flow_Method'] = 'hs'
            elif values['-dis-']:
                Video_Settings['Optical_Flow_Method'] = 'dis'
            Video_Settings['Flow_Settings'] = settings_window_gui(Video_Settings['Flow_Settings'],Video_Settings['Optical_Flow_Method'])
        
        # =============================================================================
        # 4. Execute
        # =============================================================================
        if event == sg.WIN_CLOSED:
            try:
                # delete plot if not saved. sorry, should have saved xoxo
                os.remove('plot.png')
                os.remove('mean_deviation.png')
            except:
                None
            break

        if event == flow_run:
            if values['-gf-']:
                Video_Settings['Optical_Flow_Method'] = 'gf'
            elif values['-hs-']:
                Video_Settings['Optical_Flow_Method'] = 'hs'
            elif values['-dis-']:
                Video_Settings['Optical_Flow_Method'] = 'dis'
            if values['-out-']:
                Video_Settings['Mask_area'] = 'out'
            elif values['-in-']:
                Video_Settings['Mask_area'] = 'in'
            Output,CalculatedFlow['Vector field'] = Optical_Flow_Extraction(Video_Settings,img)
            Mean_plot(Output)
            sg.popup_ok("Flow Calculated.")
            window[flow_save].update(disabled=False)
            window[mean_show].update(disabled=False)
            window[mean_save].update(disabled=False)
        
        if event == flow_save:
            folder,filename = popup_saver()
            try:
                CalculatedFlow['Path'] = folder + '/' + filename + '.npy'
                np.save(CalculatedFlow['Path'],CalculatedFlow['Vector field'])
                Properties['Src_Path'] = Video_Settings['Src_Path']
                Properties['Flow_Settings'] = Video_Settings['Flow_Settings']
                Properties_Path = folder + '/' + filename + '.json'
                with open(Properties_Path,'w') as f:
                    json.dump(Properties,f, indent=4)
                sg.popup_ok('File successfully saved. A .json-file containing the settings was additionally saved.')
            except:
                sg.popup_ok('An error occured during the saving process.')
        
        if event == mean_save:
            folder,filename = popup_saver()
            try:
                path = folder + '/' + filename + '.png'
                shutil.move('mean_deviation.png',path)
                sg.popup_ok('File successfully saved.')
            except:
                sg.popup_ok('An error occured during the saving process.')
        # =============================================================================
        # 5. mean
        # =============================================================================

        if event == mean_show:
            av_plot = cv.imread('mean_deviation.png')
            image_preview(av_plot)

        # =============================================================================
        # Button updates
        # =============================================================================
        
        # Enable create mask Button if video path exists
        window[mask_create].update(disabled= not path_check(Video_Settings['Src_Path']))
        # Enable preview mask if mask path exists and mask contains at least 3 points 
        window[mask_preview].update(disabled = Video_Settings['Mask'] == [])
        # Enable 'delete mask' button if mask exists
        window[mask_delete].update(disabled=Video_Settings['Mask']==[])
        # enable "save mask" button if mask was created"
        window[mask_save].update(disabled = Video_Settings['Mask']==[])
        
        # enable flow settings button if video path exists
        window[flow_set].update(disabled=not path_check(Video_Settings["Src_Path"]))

        # enable execute button if video path exists
        window[flow_run].update(disabled=not path_check(Video_Settings['Src_Path']))

    # =============================================================================
    # Plot Event Loop
    # =============================================================================
        
        if event == transfer_flow:
           PlottedFlow['Vector field'] = CalculatedFlow['Vector field'].copy()
           PlottedFlow['Path'] = CalculatedFlow['Path']

        elif event == '-load_flow_path-':
            PlottedFlow['Path'] = values['-load_flow_path-']
            PlottedFlow['Vector field'] = np.load(PlottedFlow['Path'])
            try:
                json_path = PlottedFlow['Path'].replace('.npy','.json')
                with open(json_path, 'r') as f:
                    PlottedFlow['Flow_Settings'] = json.load(f)
            except:
                print('could not load json')
        
        # Plot settings
        if Video_Settings['Plot_Settings'] == []:
                Video_Settings['Plot_Settings'] = Default_Plot_Settings.copy()
        if event == '-plot_settings_FILE-' and path_check(values['-plot_settings_FILE-']) == True:
            Video_Settings['Plot_Settings_Path'] = values['-plot_settings_FILE-']
            window[plot_set_default].update(disabled=False)
            try:
                Video_Settings['Plot_Settings'] = np.load(Video_Settings['Plot_Settings_Path'],allow_pickle=True).item()
            except:
                None

            if path_check(Video_Settings['Plot_Settings_Path']) == True and Video_Settings['Plot_Settings'] == Default_Plot_Settings:
                sg.popup_ok('An error occured.\n The default settings will be used')

        elif event == plot_set:
            Video_Settings['Plot_Settings'] = settings_window_gui(Video_Settings['Plot_Settings'],method=None)
        
        # execute
        if event == plot_run:
            PlottedFlow['Visualisation_Time'] = VectorField_Visualisation(PlottedFlow['Vector field'],Video_Settings['Plot_Settings'])
            sg.popup_ok("Done. streamplot took:",PlottedFlow['Visualisation_Time'])

        elif event == plot_preview:
            plot = cv.imread('plot.png')
            image_preview(plot)

        elif event == plot_save:
            folder,filename = popup_saver()
            try:
                PlottedFlow['Plot_Path'] = folder + '/' + filename + '.png'
                shutil.move('plot.png',PlottedFlow['Plot_Path'])
                # now combine all the wanted dictionaries together
                Properties['Src_Path'] = Video_Settings['Src_Path']
                Properties['Flow_Settings'] = Video_Settings['Flow_Settings']
                Properties['Plot_Settings'] = Video_Settings['Plot_Settings']
                Properties_Path = folder + '/' + filename + '.json'
                with open(Properties_Path,'w') as f:
                    json.dump(Properties,f, indent=4)
                sg.popup_ok('File successfully saved. A json-file containing the settings was additionally saved.')
            except:
                sg.popup_ok('An error occured during the saving process.')

        # hsv
        try:
            HSV['Image'] = HSV_Visualisation(PlottedFlow['Vector field'])
        except:
            None

        if event == hsv_preview:
            HSV['Image'] = HSV_Visualisation(PlottedFlow['Vector field'])
            image_preview(HSV['Image'])
        elif event == hsv_save:
            folder,filename=popup_saver()
            try:
                HSV['Path'] = folder + '/' + filename + '.png'
                cv.imwrite(HSV['Path'],HSV['Image'])
                HSV['Legend'] = hsv_legend(HSV['Image'])
                HSV['Legend_Path'] = folder + '/' + filename + '_legend.png'
                HSV['Legend'].savefig(HSV['Legend_Path'],dpi=500)
                sg.popup_ok('File successfully saved. A legend was additionally saved.')
            except:
                sg.popup_ok('An error occured during the saving process.')

        # =============================================================================
        # Button updates
        # =============================================================================

        # Enable Transfer Flow button freischalten if flow has been calculated
        window[transfer_flow].update(disabled= len(CalculatedFlow['Vector field'])==0)

        # Enable Plot-Settings and execute button if Vectorfeld exists
        window['-plot_set_browse-'].update(disabled=False)
        window[plot_set].update(disabled=len (PlottedFlow['Vector field']) == 0)
        window[plot_run].update(disabled=len (PlottedFlow['Vector field']) == 0)
        # Enable Plot-Settings default button if Plot-Settings are not default settings
        window[plot_set_default].update(disabled=Video_Settings['Plot_Settings']==Default_Plot_Settings)

        # Enable preview and save button if preview image exists
        window[plot_preview].update(disabled=not path_check('plot.png'))
        window[plot_save].update(disabled=not path_check('plot.png'))

        # enable HSV preview and save button if Vector field exists
        window[hsv_preview].update(disabled=len (PlottedFlow['Vector field']) == 0)
        window[hsv_save].update(disabled=len (PlottedFlow['Vector field']) == 0)

    window.close()

FlowCalGui()