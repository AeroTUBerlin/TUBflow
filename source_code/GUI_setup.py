import os
from PIL import Image
import io
import PySimpleGUI as sg 

# Theme
sg.theme('LightBrown13')
sg.set_options(font = ("Segoe UI",10))

# cwd = os.getcwd()
# logo_path = os.path.join(os.path.dirname(cwd), "other", "Aero_Logo_long.png")
# berlin_logo_path = os.path.join(os.path.dirname(cwd), "other", "TU-Berlin-Logo.svg.png")
logo_path = 'other/Aero_Logo_long.png'
berlin_logo_path = 'other/TU-Berlin-Logo.svg.png'

# Load the images using Pillow
logo = Image.open(logo_path)
berlin_logo = Image.open(berlin_logo_path)

# Define the window size (modify this according to your needs)
window_width = 600
window_height = 600
window_size = (window_width, window_height)

# Resize the Aero logo to the width of the window while maintaining the aspect ratio
img_width, img_height = logo.size
aspect_ratio = img_height / img_width
new_width = window_width - 100  # Subtract some padding for the window borders
new_height = int(new_width * aspect_ratio)
img_resized = logo.resize((new_width, new_height), Image.LANCZOS)

# Resize the TU Berlin logo to a smaller size
berlin_img_width, berlin_img_height = berlin_logo.size
berlin_aspect_ratio = berlin_img_height / berlin_img_width
berlin_new_width = int(new_width / 10)  # Adjust this value to control the width of the Berlin logo
berlin_new_height = int(berlin_new_width * berlin_aspect_ratio)
berlin_img_resized = berlin_logo.resize((berlin_new_width, berlin_new_height), Image.LANCZOS)

# Convert the images to a format suitable for PySimpleGUI
bio_logo = io.BytesIO()
img_resized.save(bio_logo, format="PNG")
img_data_logo = bio_logo.getvalue()

bio_berlin_logo = io.BytesIO()
berlin_img_resized.save(bio_berlin_logo, format="PNG")
img_data_berlin_logo = bio_berlin_logo.getvalue()
