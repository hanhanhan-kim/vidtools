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

    See https://docs.opencv.org/4.5.0/d8/da7/structcv_1_1SimpleBlobDetector_1_1Params.html

    Parameters:
    -----------


    Returns:
    --------
    
    """

    params = cv2.SimpleBlobDetector_Params()

    # Not really sure how the resulting binary images are used here ...
    params.minThreshold = min_threshold
    params.maxThreshold = max_threshold
    
    # TODO: This needs to be on for this shit to work ...
    #-------------
    params.filterByArea = True
    params.minArea = min_area

    params.filterByCircularity = False

    params.filterByConvexity = False

    params.filterByInertia = True
    params.maxInertiaRatio = max_inertia_ratio
    # -------------

    # # TODO: BROKEN
    # if min_area==None and max_area==None:
    #     params.filterByArea = False
    # elif min_area==None:
    #     params.filterByArea = True
    #     params.maxArea = float(max_area)
    # elif max_area==None:
    #     params.filterByArea = True
    #     params.minArea = float(min_area)

    # print(params.minArea)

    # if min_circularity==None and max_circularity==None:
    #     params.filterByCircularity = False
    # elif min_circularity==None:
    #     params.filterByCircularity = True
    #     params.maxCircularity = float(max_circularity)
    # elif max_circularity==None:
    #     params.filterByCircularity = True
    #     params.minCircularity = float(min_circularity)  # 0.1

    # if min_convexity==None and max_convexity==None:
    #     params.filterByConvexity = False
    # elif min_convexity==None:
    #     params.filterByConvexity = True
    #     params.maxConvexity = float(max_convexity)
    # elif max_convexity==None:
    #     params.filterByConvexity = True
    #     params.minConvexity = float(min_convexity)  # 0.87

    # if min_inertia_ratio==None and max_inertia_ratio==None:
    #     params.filterByInertia = False
    # elif min_inertia_ratio==None:
    #     params.filterByInertia = True
    #     params.maxInertiaRatio = float(max_inertia_ratio)
    # elif max_inertia_ratio==None:
    #     params.filterByInertia = True
    #     params.minInertiaRatio = float(min_inertia_ratio)  # 0.5

    print(params.maxInertiaRatio)

    detector = cv2.SimpleBlobDetector_create(params)
    
    return detector 


def detect_blob(img, blob_params):

    """
    
    Parameters:
    -----------

    Returns:
    --------


    """

    g_img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    detector = init_blob_detector(**blob_params)
    keypoints = detector.detect(g_img)

    # TODO: Check that only ONE blob is detected; this is the way to do:
    print(len(keypoints))

    # Draw detected blobs as red circles:
    # The DRAW_MATCHES... flag ensures the size of the circle corresponds to the size of the blob
    im_with_keypoints = cv2.drawKeypoints(g_img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Keypoints", im_with_keypoints)
    cv2.waitKey(0)


def main(config):

    root = expanduser(config["track_a_blob"]["root"])

    all_params = config["track_a_blob"]
    blob_params = {k:v for (k,v) in all_params.items() if k not in set(["root"])}

    if Path(root).is_dir():

        imgs = [str(path.absolute()) for path in Path(root).rglob("*.png")]

        if len(imgs) == 0:
            raise ValueError("No videos ending with '.png' were found.")

        for img in imgs:
            print(f"Detecting blob in {img} ...")
            detect_blob(img, blob_params)

    elif Path(root).is_file():
        detect_blob(root, blob_params)