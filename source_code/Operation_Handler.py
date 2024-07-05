"""

This File Contains the functions which will be called by the app.
The main purpose of this code it to read a settings dict and apply those 
settings to the given file (path)

Public Functions:
    
    -Image_Analysis(SrcPath,DstPath,Settigs)
    -Optical_Flow_Extraction(SrcPath,DstPath,Settings,Mask)

"""

# =============================================================================
# General Includes
# =============================================================================
import numpy as np
import math
import time

# from windrose import WindroseAxes

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from matplotlib import cm

import cv2 as cv
import time
import PySimpleGUI as sg
import os

# =============================================================================
# Custom Includes
# =============================================================================
from VideoAnalysisClass import VideoAnalysis
from mask_operation import *
from image_preview import *

"""
SingleFrameOperation:
    This function is called before each flow analysis
"""

def SingleFrameOperation(frame,Video_Settings,dim,maskList,MaskOutside):
    if len(Video_Settings['Mask']) > 0:
        frame, _ = ApplyMask(frame,maskList,MaskOutside=MaskOutside)
        if MaskOutside:
            # in this case the image can be additionally cropped outside
            frame,_ = crop_with_mask(frame,maskList)

    #resize the frame
    frame = cv.resize(frame, dim, interpolation = cv.INTER_AREA)
    #print('resize zeit =',danach-davor)

    #and a grayscale is required for the optical flow
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    return frame

"""
Optical_Flow_Extraction:
    This Funktion uses an optical flow extraction to analyse the average flow
    in a video. This flow, which is optained in the form of a 2D array of 2D
    vectors, are then visualised with the help of pyplot. Before the optical
    flow analysis, each frame of the video capture is preprocessed by the 
    "SingleFrameOperation" helper Funktion defined above. The visualisation 
    is handled by the "VectorField_Visualisation" helper Funktion. 
    
    In order to give the user of this funktion a feedback of the process a
    progress bar will be opend. This progress bar only provides feedback of 
    the progress of the analysis of the 2D flow vectors. The visualisation 
    process will take aditional time. A full resolution frame can take up to 
    two mins to be visualized.
    
    The input arguments are :
        -SrcPath:
            A string which contains the path to the saved video
            ("./videoname.mp4")
        -DstPath:
            A string which contains the desired path in which the resulting
            visualisation should be saved   ("./flow.jpg")
        -Settings:
            A dict containing the required settings of the flow extraction 
            and visualisation
        -Mask:
            A array of points which marks the edges of the mask to be used
    
    Settings:
        A full settings dict would look like this
        
        Settings={
            "Start_Frame":200,
            "End_Frame":300,
            "resize_Factor":50,
            "samplerate": 1,
            "Stream_density":4,
            "Stream_arrowstyle":'-',
            "Stream_minlength":0.1,
            "Stream_linewidth":1,
            "Stream_color":(0,0,0),
            "Stream_ShowSpeed":False,
            "Plot_dpi":300,
            "pyr_scale": 0.5,
            "levels":3,
            "winsize":15,
            "iterations":3,
            "poly_n":5,
            "poly_sigma":1.2,
            "flags":0
            }
"""

def Optical_Flow_Extraction(Video_Settings,img):
    start_time = time.time()
    VA = VideoAnalysis()

    Flow_Settings = Video_Settings['Flow_Settings']

    # Initialize
    Output = {}
    SumFlow = []
    flow = None
    mask = None
    
    #Set frame counter 
    CurrentFrame = Flow_Settings['Start_Frame']

    # frame counter counts the amounts of frames used and is not to be mixed up with frame_number
    FrameCounter = 1

    history = []
    maskList = []

    MaskOutside = Video_Settings['Mask_area'] == 'out'

    # single frame operation preparations
    if len(Video_Settings['Mask']) > 0:
        for maskelement in Video_Settings['Mask']:
            maskList.append(maskelement.points_list)
        #if a mask exists it will be applied
        #MaskOutside = maskelement.Mask_area_Type
        img,mask = ApplyMask(img,maskList,MaskOutside=MaskOutside)
        if MaskOutside:
            # in this case the image can be additionally cropped outside
            img,_ = crop_with_mask(img,maskList)
            mask,_ = crop_with_mask(mask,maskList)
            
        mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
        
    width = int(img.shape[1] * Flow_Settings['resize_Factor'] / 100)
    height = int(img.shape[0] * Flow_Settings['resize_Factor'] / 100)
    new_dims = (width, height)
    if mask is not None:
        mask = cv.resize(mask, new_dims, interpolation = cv.INTER_AREA)
        
    # initialize DIS Optical Flow object
    if Video_Settings['Optical_Flow_Method'] == 'dis':
        dis = cv.DISOpticalFlow_create(cv.DISOpticalFlow_PRESET_MEDIUM)

    # optical flow loop
    if Video_Settings['Input_Type'] == 'video':
        #read video file
        cap = cv.VideoCapture(Video_Settings['Src_Path'])
        # set that the first frame to be read is the start frame (default would be first frame of .mp4)
        cap.set(cv.CAP_PROP_POS_FRAMES, Flow_Settings['Start_Frame']-1)
        
        #get some global data
        Output['Capture_FPS'] = cap.get(cv.CAP_PROP_FPS)
        Output['frame_count'] = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        Output['Capture_duration'] = Output['frame_count']/Output['Capture_FPS']
        Output['Capture_width']  = cap.get(3)  # float `width`
        Output['Capture_height'] = cap.get(4)  # float `height`

        if Flow_Settings["End_Frame"] == -1:
            Flow_Settings["End_Frame"] = Output['frame_count']

        # frame number is the exact number of the current frame
        frame_number = Flow_Settings['Start_Frame']

        Output['FrameAmount'] = calculate_n(Flow_Settings['Start_Frame'],Flow_Settings['End_Frame'],Flow_Settings['Frame_frequence'])

        while True:
            # Beim ersten Frame
            ret, frame = cap.read()

            if CurrentFrame == Flow_Settings['Start_Frame']:
                frame_1 = SingleFrameOperation(frame,Video_Settings,new_dims,maskList,MaskOutside)
                CurrentAverageFlow = None
                flow = None
                CurrentFrame += Flow_Settings["Frame_frequence"]
                # mask = np.ma.masked_equal(frame_1, 0).mask

            # Bei allen anderen Frames
            elif CurrentFrame == frame_number:
                frame_2 = SingleFrameOperation(frame,Video_Settings,new_dims,maskList,MaskOutside)
                #print('single time =',t-r)
                sg.one_line_progress_meter(
                'Progress Meter', FrameCounter, Output['FrameAmount']-1,
                'Optical Flow Operations',no_button=True
                )

                # optical flow
                if Video_Settings['Optical_Flow_Method'] == 'gf':
                    flow = VA.ApplyFarnebackOpticalFlow(frame_1,frame_2, initial_flow=None,Set=Flow_Settings)
                elif Video_Settings['Optical_Flow_Method'] == 'hs':
                    flow = VA.ApplyHornSchunckOpticalFlow(frame_1,frame_2,initial_flow=None)
                elif Video_Settings['Optical_Flow_Method'] == 'dis':
                    flow = VA.ApplyDisOpticalFlow(dis,frame_1,frame_2,initial_flow=None)

                # redefine previous frame
                frame_1 = frame_2 

                if CurrentAverageFlow is None:
                    SumFlow = flow
                else:
                    SumFlow += flow
                CurrentAverageFlow = SumFlow / FrameCounter

                history = live_tracking(history,CurrentAverageFlow,flow,FrameCounter)
                
                # update current frame and amount of used frames
                CurrentFrame += Flow_Settings["Frame_frequence"]
                FrameCounter += 1

            frame_number += 1

            # End loop if the current next frame exceeds the last frame who was set
            if CurrentFrame > Flow_Settings['End_Frame']:
                print(f'loop interrupted, last frame would have been passed.\nA total of {FrameCounter-1} were used.')
                break

    elif Video_Settings['Input_Type'] == 'series':
        # Get the list of files in the folder
        frame_files = sorted(os.listdir(Video_Settings['Src_Path']))
        Output['frame_count'] = len(frame_files)
        if Flow_Settings["End_Frame"] == -1:
            Flow_Settings["End_Frame"] = Output['frame_count']
        
        Output['FrameAmount'] = calculate_n(Flow_Settings['Start_Frame'],Flow_Settings['End_Frame'],Flow_Settings['Frame_frequence'])

        while True:
            # Beim ersten Frame
            if CurrentFrame == Flow_Settings["Start_Frame"]:
                file_name = frame_files[CurrentFrame-1]
                # Construct the file path for the current frame
                frame = cv.imread(os.path.join(Video_Settings['Src_Path'], file_name))

                frame_1 = SingleFrameOperation(frame,Video_Settings,new_dims,maskList,MaskOutside)
                CurrentAverageFlow = None
                # mask = np.ma.masked_equal(frame_1, 0).mask

            # Bei allen anderen Frames
            elif CurrentFrame > Flow_Settings["Start_Frame"]:
                file_name = frame_files[CurrentFrame-1]
                # Construct the file path for the current frame
                frame = cv.imread(os.path.join(Video_Settings['Src_Path'], file_name))

                frame_2 = SingleFrameOperation(frame,Video_Settings,new_dims,maskList,MaskOutside)


                sg.one_line_progress_meter(
                'Progress Meter', FrameCounter-1, Output['FrameAmount']-1,
                'Optical Flow Operations',no_button=True
                )

                # optical flow
                if Video_Settings['Optical_Flow_Method'] == 'gf':
                    flow = VA.ApplyFarnebackOpticalFlow(frame_1,frame_2, initial_flow=None,Set=Flow_Settings)
                elif Video_Settings['Optical_Flow_Method'] == 'hs':
                    flow = VA.ApplyHornSchunckOpticalFlow(frame_1,frame_2,initial_flow=None)
                elif Video_Settings['Optical_Flow_Method'] == 'dis':
                    flow = VA.ApplyDisOpticalFlow(dis,frame_1,frame_2,initial_flow=None)

                # redefine previous frame
                frame_1 = frame_2

                if CurrentAverageFlow is None:
                    SumFlow = flow

                else:
                    SumFlow += flow

                # betrag der flow matrix berechnen
                CurrentAverageFlow = SumFlow / FrameCounter

                history = live_tracking(history,CurrentAverageFlow,flow,FrameCounter)


            # increase CurrentFrame according to the chosen frame frequence
            CurrentFrame += Flow_Settings["Frame_frequence"]

            #increase Frame Counter
            FrameCounter += 1
            
            # End loop if 
            if CurrentFrame > Flow_Settings['End_Frame']:
                print(f'loop interrupted, last frame would have been passed.\nA total of {FrameCounter-1} were used.')
                break
    end_time = time.time()

    #The average flow can now be calculated
    Average_Flow = SumFlow / Output["FrameAmount"]
    Output['History'] = history
    Output['Elapsed_Time'] = end_time-start_time
    Output['Frames_per_second'] = FrameCounter/(end_time-start_time)
    Output['last_frame'] = frame_2
    Output['mask'] = mask
    if mask is not None:
        Average_Flow = np.ma.array(Average_Flow, mask=np.dstack([mask]*2))

    return Output, Average_Flow

def Mean_plot(Output):
    plt.figure(0)
    x_values = [i['frame'] for i in Output['History']]
    y_values = [i['rms_current'] for i in Output['History']]
    err_values = [i['std_average'] for i in Output['History']]
    plt.errorbar(x_values, y_values, err_values,
                 errorevery=10, ecolor='r')
    # plt.hlines(y_values[-1] + err_values[-1], x_values[0], x_values[-1], 'k', '--')
    plt.vlines(x_values[np.argmax(y_values)], min(y_values), max(y_values), 'k', '--')
    plt.hlines(y_values[-1], x_values[0], x_values[-1], 'k', '--')
    plt.xlabel('Frame')
    plt.ylabel('Mean Deviation Current Flow')
    plt.savefig('mean_deviation.png',dpi=300)
    plt.clf()


def live_tracking(history,CurrentAverageFlow,flow,FrameCounter):
    mean_average = np.mean(CurrentAverageFlow)
    mean_current = np.mean(flow)
    min_average = np.min(CurrentAverageFlow)
    min_current = np.min(flow)
    max_average = np.max(CurrentAverageFlow)
    max_current = np.max(flow)
    meanabs_average = np.mean(np.abs(CurrentAverageFlow))
    meanabs_current = np.mean(np.abs(flow))
    std_average = np.std(CurrentAverageFlow)
    std_current = np.std(flow)
    rms_current = np.sqrt(np.mean(flow**2))
    rms_average = np.sqrt(np.mean(CurrentAverageFlow**2))

    results = {
        "current_flow": flow,
        "average_flow": CurrentAverageFlow,
        "frame": FrameCounter,
        "mean_average": mean_average,
        "mean_current": mean_current,
        "meanabs_average": meanabs_average,
        "meanabs_current": meanabs_current,
        "min_average": min_average,
        "min_current": min_current,
        "max_average": max_average,
        "max_current": max_current,
        "std_average": std_average,
        "std_current": std_current,
        "rms_current": rms_current,
        "rms_average": rms_average
    }
    history.append(results)

    return history



"""
VectorField_Visualisation:
    
"""

def VectorField_Visualisation(AverageFlow,Settings):
    t = time.time()
    try:
        mask = AverageFlow.mask.astype(np.uint8)
    except:
        mask = np.ones_like(AverageFlow)

    Visualisation_Settings = Settings
    Settings_List = list(Settings)
    for Var in Settings_List:
        if Var in Settings:
          Visualisation_Settings[Var] = Settings[Var]

    shape_orig = AverageFlow.shape

    dim = (int(100 * shape_orig[1]/shape_orig[0]),100)

    AverageFlow = cv.resize(AverageFlow, dim, shape_orig[2], interpolation=cv.INTER_AREA)
    mask = cv.resize(mask, dim, shape_orig[2], interpolation=cv.INTER_AREA)

    #make grid
    shape_new = AverageFlow.shape
    y = np.arange(0, shape_new[0])
    x = np.arange(0, shape_new[1])
    X, Y = np.meshgrid(x, y)
    U,V = np.ma.array(AverageFlow, mask=np.logical_not(mask)).T
    #define the figure

    fig, ax = plt.subplots(figsize=(6 * shape_new[1] / shape_new[0], 6))

    #Compute the Streamplot
    speed = np.sqrt(U**2 + V**2)

    lw = Visualisation_Settings["Stream_linewidth"]
    if Visualisation_Settings["Stream_ShowSpeed"]:
        lw = 5*speed /speed.max()
    streams = plt.streamplot(X, Y, U.T, V.T,
                             density=Visualisation_Settings["Stream_density"],
                             arrowstyle=Visualisation_Settings["Stream_arrowstyle"],
                             minlength=Visualisation_Settings["Stream_minlength"],
                             linewidth=lw,color=Visualisation_Settings["Stream_color"],
                             broken_streamlines=Visualisation_Settings["broken_streamlines"])

    #Compose the Figure
    ax.add_collection(streams.lines)
    ax.axis('off')
    ax.axis('equal')
    plt.box(False)    
    fig.gca().invert_yaxis()
    plt.tight_layout()
    fig.savefig('plot.png', dpi=Visualisation_Settings["Plot_dpi"])
    # reset
    fig.clf
    elapsed = time.time() - t
    return elapsed

def HSV_Visualisation(vector_Map,expo = 1):
    height = len(vector_Map)
    width = len(vector_Map[0])
    image_rgb = np.zeros((height,width,3), np.uint8)
    frame_hsv = cv.cvtColor(image_rgb,cv.COLOR_RGB2HSV)
    r, phi = cv.cartToPolar(vector_Map[..., 0], vector_Map[..., 1])
    frame_hsv[..., 0] = phi*180/np.pi/2
    frame_hsv[..., 1] = 255
    frame_hsv[..., 2] = cv.normalize(r, None, 0, 255, cv.NORM_MINMAX)
    return cv.cvtColor(frame_hsv, cv.COLOR_HSV2BGR)

def hsv_legend(image):
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # black & dark pixels are faking the legend
    brightness_threshold = 20
    brightness_mask = hsv_image[:,:,2] >= brightness_threshold

    hue_values = hsv_image[:,:,0][brightness_mask]

    # Define the number of angle segments
    num_segments = 36  # You can adjust this value, here I took 10 degrees segments

    # Calculate the histogram of hue values
    hist_hue, _ = np.histogram(hue_values, bins=num_segments, range=(0, 180))

    # Calculate the angles for each segment
    segment_angles = np.linspace(0, 360, num_segments + 1)

    # Calculate the average hue value for each angle segment 
    average_hues = [(segment_angles[i] + segment_angles[i + 1]) / 2 for i in range(num_segments)]

    # Normalize the histogram values
    hist_hue_normalized = hist_hue / hist_hue.max()

    # Create the windrose plot
    plt.figure(figsize=(4, 4))
    ax = plt.subplot(111, projection='polar')

    # Plot the bars for each angle segment with colors based on average hue values 
    for i in range(num_segments):
        angle_start = np.deg2rad(segment_angles[i])
        angle_end = np.deg2rad(segment_angles[i + 1])
        bar_length = hist_hue_normalized[i]
        average_hue = average_hues[i]
        color = plt.cm.hsv(average_hue / 360)  # Use average hue for color
        ax.bar(
            angle_start,
            bar_length,
            width=angle_end - angle_start,  # Correctly calculate bar width
            bottom=0.0,
            alpha=0.7,
            color=color
        )

    # Customize the windrose plot
    ax.set_theta_direction(-1)  # Clockwise direction
    ax.set_theta_zero_location("E")  # North as starting point ax.set_title("Windrose Plot")

    
    # Show the windrose plot

    return plt.gca().figure

def calculate_n(start, end, frequency):
    n = math.floor((end - start) / frequency) + 1
    return n
