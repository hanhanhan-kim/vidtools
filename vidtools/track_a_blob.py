from os.path import expanduser
from pathlib import Path

import cv2
import numpy as np


def init_blob_detector(min_threshold=1, max_threshold=255, 
                       min_area=None, max_area=None,
                       min_circularity=None, max_circularity=None,
                       min_convexity=None, max_convexity=None,
                       min_inertia_ratio=None, max_inertia_ratio=None):

    """
    Initialize OpenCV's simple blob detector, with parameters. 
    See https://docs.opencv.org/4.5.0/d8/da7/structcv_1_1SimpleBlobDetector_1_1Params.html

    Parameters:
    -----------
    min_threshold (float): The threshold pixel value from which the threshold increments start. 
    max_threshold (float): The threshold pixel value at which the threshold increments end. 
    min_area (float or None): The minimum pixel area that a blob can have. 
    max_area (float or None): The maximum pixel area that a blob can have.
    min_circularity (float or None): The minimum circularity that a blob can have. E.g. a 
        regular hexagon is more circular than a regular pentagon. Must be between 0 and 1. 
    max_circularity (float or None): The maximum circularity that a blob can have. E.g. a 
        regular hexagon is more circular than a regular pentagon. Must be between 0 and 1. 
    min_convexity (float or None): The minimum convexity that a blob can have. Convexity is the
        area of the blob divided by the blob's convex hull. Must be between 0 and 1. 
    max_convexity (float or None): The maximum convexity that a blob can have. Convexity is the
        area of the blob divided by the blob's convex hull. Must be between 0 and 1. 
    min_inertia_ratio (float or None): The minimum 'elongatedness' that a blob can have, where 
        the lowest value is a line, and the high value is a circle. Must be between 0 and 1. 
    max_inertia_ratio (float or None): The maximum 'elongatedness' that a blob can have, where 
        the lowest value is a line, and the high value is a circle. Must be between 0 and 1. 

    Returns:
    --------
    A paramterized OpenCV SimpleBlobDetector object.
    """

    params = cv2.SimpleBlobDetector_Params()

    # Not really sure how the resulting binary images are used here ...
    params.minThreshold = min_threshold
    params.maxThreshold = max_threshold

    if min_area==None and max_area==None:
        params.filterByArea = False
    elif min_area==None:
        params.filterByArea = True
        params.maxArea = max_area
    elif max_area==None:
        params.filterByArea = True
        params.minArea = min_area  # 0.1

    if min_circularity==None and max_circularity==None:
        params.filterByCircularity = False
    elif min_circularity==None:
        params.filterByCircularity = True
        params.maxCircularity = max_circularity
    elif max_circularity==None:
        params.filterByCircularity = True
        params.minCircularity = min_circularity  # 0.1

    if min_convexity==None and max_convexity==None:
        params.filterByConvexity = False
    elif min_convexity==None:
        params.filterByConvexity = True
        params.maxConvexity = max_convexity
    elif max_convexity==None:
        params.filterByConvexity = True
        params.minConvexity = min_convexity # 0.87

    if min_inertia_ratio==None and max_inertia_ratio==None:
        params.filterByInertia = False
    elif min_inertia_ratio==None:
        params.filterByInertia = True
        params.maxInertiaRatio = max_inertia_ratio
    elif max_inertia_ratio==None:
        params.filterByInertia = True
        params.minInertiaRatio = min_inertia_ratio  # 0.5

    detector = cv2.SimpleBlobDetector_create(params)
    
    return detector 


def detect_blob(img, blob_params):

    """
    Detect blobs in an image. 

    Parameters:
    -----------
    img (str): Path to the input image. 
    blob_params (dict): A dictionary of parameters for `init_blob_detector()`. 

    Returns:
    --------
    A dictionary of dictionaries, where the outer keys are integers denoting the blob indexes,
    and the inner keys are 'x', 'y', and 'd', for which the values are the x,y pixel 
    coordinates of that blob's centroid, and the diameter of that blob. 
    In addition, shows tracked blobs and their bounding boxes. 
    """

    g_img = cv2.imread(img, cv2.IMREAD_GRAYSCALE) 
    detector = init_blob_detector(**blob_params)
    keypoints = detector.detect(g_img)

    print(f"{len(keypoints)} blob(s) detected ..." )

    # Get keypoint (centroid) coordinates of blobs: 
    blobs = {}
    for i in range(len(keypoints)):

        # The first index refers to the blob number:
        x = keypoints[i].pt[0] 
        y = keypoints[i].pt[1]
        d = keypoints[i].size # dia

        print(f"blob: {i}, x: {x}, y: {y}, d: {d}")
        blobs[i] = {"x":x, "y":y, "d":d}

    # Draw detected blobs as red circles:
    im_with_keypoints = cv2.drawKeypoints(g_img, keypoints, np.array([]), (0,0,255), 
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) # checks that blobs and circle sizes correspond

    im_with_bboxes = im_with_keypoints
    for k,v in blobs.items():
        
        scalar = 2 # adjust bbox size
        top_left = (int(v["x"] - v["d"]/2 * scalar), int(v["y"] + v["d"]/2 * scalar))
        bottom_right = (int(v["x"] + v["d"]/2 * scalar), int(v["y"] - v["d"]/2 * scalar))

        im_with_bboxes = cv2.rectangle(im_with_bboxes, top_left, bottom_right, (0,255,0), 1) 

    cv2.imshow("Keypoints", im_with_bboxes)
    cv2.waitKey(0)
    
    return blobs


def main(config):

    root = expanduser(config["track_a_blob"]["root"])
    all_params = config["track_a_blob"]
    blob_params = {k:v for (k,v) in all_params.items() if k not in set(["root"])}

    # TODO: Rework for video rather than images ... 

    # TODO: Add in a do_ask flag that draws a random sample of images from video and asks users if
    # they want to proceed. 

    if Path(root).is_dir():

        imgs = [str(path.absolute()) for path in Path(root).rglob("*.png")]

        if len(imgs) == 0:
            raise ValueError("No videos ending with '.png' were found.")

        for img in imgs:
            print(f"\nDetecting blob(s) in {img} ...")
            detect_blob(img, blob_params)

    elif Path(root).is_file():
        detect_blob(root, blob_params)
        

    # TODO: Implement tracking!!! 