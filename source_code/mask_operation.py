import cv2 as cv
import numpy as np

from image_preview import *
from Operation_Handler import *


class Mask:
    points_list = []
    img = None

    def __init__(self, img, points_list=None):
        self.img = img
        if points_list is None:
            self.points_list = self.MaskSelection_Page(img)
        else:
            self.points_list = points_list

    def MaskSelection_Page(self,Src_Img):
        global points_list
        points_list = []
        width,height = fit_image(Src_Img)
        screen_width, screen_height = target_monitor_resolution()[1]
        window_x = (screen_width - width) // 2
        window_y = (screen_height - height) // 2

        cv.namedWindow("window", cv.WINDOW_NORMAL)
        cv.resizeWindow('window', width, height)
        cv.moveWindow('window', window_x, window_y)
        cv.imshow("window", Src_Img)
        cv.setMouseCallback('window', click_event,{'img': Src_Img})
        cv.waitKey(0)
        cv.destroyAllWindows()
        return points_list


def load_masks_from_file(filename):
    masks_data = np.load(filename, allow_pickle=True)
    masks = [Mask(None, points_list) for points_list in masks_data]
    return masks

def save_mask(filename,masks):
    points_lists = np.array([mask.points_list for mask in masks],dtype=object)
    # with open(filename, 'w') as f:
    #     json.dump(points_lists, f)

    np.save(filename, points_lists)


def image_crop(image,p1,p2):
    x_max = max(p1[0],p2[0])
    x_min = min(p1[0],p2[0])
    y_max = max(p1[1],p2[1])
    y_min = min(p1[1],p2[1])
    return image[y_min:y_max,x_min:x_max]


def crop_with_mask(image,points):
    # Convert points to numpy arrays
    points = [np.array(pts, dtype=np.int32) for pts in points]
    
    # Concatenate all points to find the bounding box
    all_points = np.concatenate(points, axis=0)
    
    # Find the minimum and maximum coordinates
    p1 = np.array([np.min(all_points[:, 0]), np.min(all_points[:, 1])])
    p2 = np.array([np.max(all_points[:, 0]), np.max(all_points[:, 1])])
    
    # Calculate the new points in relation to the new coordinate origin p1
    newpoints = [pts - p1 for pts in points]

    return image_crop(image,p1,p2),newpoints


def draw_line(image,points):
    for i in range(len(points)-1):
        cv.line(image,points[i],points[i+1],(0,0,255), 10)
    cv.line(image,points[0],points[len(points)-1],(0,0,255), 10)
    return image


def ApplyMask(image,points,MaskOutside = True):
    # mask defaulting to black for 3-channel and transparent for 4-channel
    # (of course replace corners with yours)
    mask_ext = np.zeros(image.shape, dtype=np.uint8)

    # fill the ROI so it doesn't get wiped out when the mask is applied
    channel_count = image.shape[2]  # i.e. 3 or 4 depending on your image
    ignore_mask_color = (255,)*channel_count

    if not MaskOutside:
        mask_ext = np.ones(image.shape, dtype=np.uint8)
        mask_ext = mask_ext * 255
        ignore_mask_color = (0,)*channel_count

    points = [np.array(pts, dtype=np.int32) for pts in points]
    cv.fillPoly(mask_ext, points, ignore_mask_color)
    
    # apply the mask
    masked_image = cv.bitwise_and(image, mask_ext)
    
    # save the result
    return masked_image, mask_ext




# =============================================================================
# These funktion will be used in the main code
# =============================================================================


def Preview_crop(image,mask):
    return draw_line(image,mask)



def click_event(event, x, y, flags, params):
    if event == cv.EVENT_LBUTTONDOWN:
        points_list.append([x,y])
        img_with_points = cv.circle(params['img'], (x, y), 5, (0, 0, 255), -1)
        cv.imshow("window", img_with_points)
    return 

