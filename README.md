# TUBFlow
We present TUBflow, an innovative open-source application for the digital postprocessing of oil film visualizations in wind tunnel tests, addressing the limitations of traditional analog techniques. The proposed method leverages modern computer vision algorithms, specifically optical flow techniques, to automate the extraction of skin friction lines from a sequence of oil-film images. The user-friendly graphical user interface (GUI) of TUBflow allows easy pre-processing of the input images and visualization of the results, while the OpenCV library enables the efficient implementation of several optical flow algorithms. 

In the accompanying paper, the versatility of the approach is demonstrated by applying it to three different wind-tunnel test cases: 
1) A subsonic half-diffuser flow,
2) An incident shock-wave/boundary-layer interaction, and
3) The suction side of a high-lift wing with distributed propulsion.
The results show that TUBflow enhances the interpretation of oil-film visualizations by effectively capturing complex flow structures across the image sequences. This makes it a promising tool to aid the digital post-processing of oil-film visualizations in ground-testing campaigns.

The publication can be found here: http://dx.doi.org/10.2514/6.2024-4283

Required Packages for SourceCode:

PySimpleGUI
os
numpy
cv2
json
shutil
PIL
io
math
matplotlib
time
screeninfo
tkinter
pyinstaller

Python Version: Python 3.11

If you like the program and want to use it for your own research, please cite our article in your publications: 
Lennart Rohlfs, Léo Hastrich, Alex Gothow and Julien Weiss. "TUBflow - An Open Source Application for Digital Postprocessing of Oil Film Visualizations in Wind Tunnels," AIAA 2024-4283. AIAA AVIATION FORUM AND ASCEND 2024 . July 2024.
