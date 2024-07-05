# =============================================================================
# Buttons
# =============================================================================

# general
Select = "Select"

# flow tab
mask_create = "Create Mask"
mask_preview = "Preview Mask"
mask_delete = "Delete Mask"
mask_save = "Save Mask"
flow_set = "Flow Settings"
flow_run = "Calculate Flow"
flow_save = "Save Vector field"
hsv_preview = "Preview HSV Image"
hsv_save = "Save HSV Image"
mean_show = "Preview mean"
mean_save = "Save mean"

# plot tab
transfer_flow = "Use Calculated Flow"
load_flow = "Load Flow"
plot_set = "Plot Settings"
plot_set_default = "Use Default Plot Settings"
plot_preview = "Preview Plot"
plot_save = "Save Plot"
plot_run = "Create Streamplot"


# =============================================================================
# File Types
# =============================================================================
videos = [
    ("MP4 (*.MP4)", "*.MP4"),
    ("AVI (*.AVI)", "*.AVI")
]

npy_files = [
    ("NPY (*.NPY)", "*.NPY")
]

# =============================================================================
# Dictionaries
# =============================================================================

Video_Settings = {
    "Input_Type":'',
    "Src_Path": '',
    "Mask_path": '',
    "Mask": [],
    "Mask_area": '',
    "Optical_Flow_Method": '',
    "Flow_Settings_Path": '',
    "Flow_Settings": [],
    "Plot_Settings_Path": '',
    "Plot_Settings": [],
    "Dst_Path": '',
    "FileName": '',
    "Dst_FilePath": '', 
}

Default_Flow_Settings={
    "Start_Frame":1,
    "End_Frame":-1,
    "Frame_frequence":1,
    "resize_Factor":40,
    "pyr_scale": 0.5,
    "levels":3,
    "winsize":15,
    "iterations":3,
    "poly_n":5,
    "poly_sigma":1.1,
    "flags":0,
}

Default_Plot_Settings={
    "Stream_density":2,
    "Stream_arrowstyle":'-',
    "Stream_minlength":0.1,
    "Stream_linewidth":0.3,
    "Stream_color":(0,0,0),
    "Stream_ShowSpeed":False,
    "Plot_dpi":300,
    "broken_streamlines":False
    }

CalculatedFlow={
    "Vector field":[],
    "Path":'',
    "Flow_Settings":[]
}

PlottedFlow={
    "Vector field":[],
    "Path":'',
    'Flow_Settings':[]
}

HSV={
    "Image":[],
    "Legend":[]
}

Properties={}

img = None