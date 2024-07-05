import cv2 as cv
from target_monitor_resolution import *

def fit_image(image):

    image_width = image.shape[1]
    image_height = image.shape[0]
    screen_width, screen_height = target_monitor_resolution()[1]

    # Case 1: Both width and height are smaller than screen resolution
    if image_width <= screen_width and image_height <= screen_height:
        new_width, new_height = image_width, image_height

    # Case 2: Only one dimension is smaller than screen resolution
    elif image_width <= screen_width:
        scale_factor = screen_height / image_height
        new_width = image_width
        new_height = min(int(image_height * scale_factor), screen_height)
    
    elif image_height <= screen_height:
        scale_factor = screen_width / image_width
        new_width = min(int(image_width * scale_factor), screen_width)
        new_height = image_height

    # Case 3: Both dimensions are exceeding screen resolution
    else:
        scale_factor = min(screen_width / image_width, screen_height / image_height)
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)
    
    return new_width,new_height

def image_preview(image):
    width,height = fit_image(image)
    screen_width, screen_height = target_monitor_resolution()[1]
    window_x = (screen_width - width) // 2
    window_y = (screen_height - height) // 2
    cv.namedWindow('window', cv.WINDOW_NORMAL)
    cv.resizeWindow('window', width, height)
    cv.moveWindow('window', window_x, window_y)
    cv.imshow('window', image)
    cv.waitKey(0)
    cv.destroyAllWindows()