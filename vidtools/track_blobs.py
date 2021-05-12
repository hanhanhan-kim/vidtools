from os.path import expanduser, splitext
from pathlib import Path

import cv2
import numpy as np

from vidtools.sort import *


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


def detect_blobs(frame, blob_params):

    """
    Detect blobs in a video frame. 

    Parameters:
    -----------
    frame (str): Frame from `cv2.VideoCapture(vid).read()`, where vid is the path to input video. 
    blob_params (dict): A dictionary of parameters for `init_blob_detector()`. 

    Returns:
    --------
    1. A dictionary of dictionaries, where the outer keys are integers denoting the blob indexes,
    and the inner keys are 'x', 'y', and 'd', for which the values are the x,y pixel 
    coordinates of that blob's centroid, and the diameter of that blob. 
    2. The image matrix of the tracked blobs and their bounding boxes; can pass to `cv2.imshow()` 
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    detector = init_blob_detector(**blob_params)
    keypoints = detector.detect(gray)

    print(f"{len(keypoints)} blob(s) detected ..." )

    # Get keypoint (centroid) coordinates and size of blobs: 
    dets = []
    for i in range(len(keypoints)):

        # The first index refers to the blob number:
        x = keypoints[i].pt[0] 
        y = keypoints[i].pt[1]
        d = keypoints[i].size # dia

        print(f"blob: {i}, x: {x}, y: {y}, d: {d}")

        # Make bounding boxes from centroid data:
        scalar = 2 # adjust bbox size
        x1 = float(x - d/2 * scalar) # TODO FYI: CAST AS FLOAT FOR SORT, AND INT FOR OPENCV DRAWINGS
        y1 = float(y + d/2 * scalar)
        x2 = float(x + d/2 * scalar)
        y2 = float(y - d/2 * scalar)
        top_left = (x1, y1)
        bottom_right = (x2, y2)

        # Format into a np array in the format [[x1,y1,x2,y2,score],[x1,y1,x2,y2,score],...]
        # where 1 is the top left corner coords and 2 is the bottom right corner coords of the bbox.
        # Format this way for the SORT tracker:
        det = [x1, y1, x2, y2, 1.0] # provide a perfect dummy score of 1.0
        dets.append(det)

    dets = np.array(dets)

    # # Draw detected blobs:
    # im_with_keypoints = cv2.drawKeypoints(gray, keypoints, np.array([]), (0,0,255), 
    #                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) # checks that blobs and circle sizes correspond

    # # Draw bounding boxes
    # im_with_bboxes = im_with_keypoints
    # for k,v in blobs.items():

    #     im_with_bboxes = cv2.rectangle(im_with_bboxes, 
    #                                    top_left, 
    #                                    bottom_right, 
    #                                    (0,255,0), # colour
    #                                    1) # line thickness

    return dets #, im_with_bboxes


def detect_blobs_in_vid(vid, framerate, blob_params):
    
    """
    Detects blobs across a video. 

    Parameters:
    -----------
    vid (str): Path to input .mp4 video.
    framerate (int): Framerate with which `vid` was recorded.

    Returns:
    --------
    Void; saves a video of the detected blobs. 
    """

    cap = cv2.VideoCapture(vid)
    output_vid = f"{splitext(vid)[0]}_blobbed.mp4"

    # Initialize the SORT object:
    mot_tracker = Sort() # TODO: pass in params from args

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v") 
    out = cv2.VideoWriter(filename=output_vid, 
                            apiPreference=0, 
                            fourcc=fourcc, 
                            fps=int(framerate), 
                            frameSize=(int(cap.get(3)), int(cap.get(4))), 
                            params=None)

    while cap.isOpened():

        ret, frame = cap.read()

        if ret:
            
            dets = detect_blobs(frame, blob_params)

            if len(dets) == 0:
                dets = np.empty((0,5))

            trackers = mot_tracker.update(dets)

            print(f"dets: {dets}")
            print(f"trackers: {trackers}")

            import ipdb; ipdb.set_trace()

            # cv2.imshow("blobs and bounding boxes ...", im_with_bboxes)

            # if cv2.waitKey(1) & 0xFF == ord("q"):
            #     break

            # # In OpenCV, images saved to video file must be 3 channels; save:
            # out.write(im_with_bboxes)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def main(config):

    root = expanduser(config["track_blobs"]["root"])
    framerate = config["track_blobs"]["framerate"]
    all_params = config["track_blobs"]
    blob_params = {k:v for (k,v) in all_params.items() if k not in set(["root", "framerate"])}

    # TODO: Add in a do_ask flag that draws a random sample of images from video and asks users if
    # they want to proceed. 

    if Path(root).is_dir():

        vids = [str(path.absolute()) for path in Path(root).rglob("*.mp4")]

        if len(vids) == 0:
            raise ValueError("No videos ending with '.mp4' were found.")

        for vid in vids:
            print(f"\nDetecting blob(s) in {vid} ...")
            detect_blobs_in_vid(vid, framerate, blob_params)

    elif Path(root).is_file():
        detect_blobs_in_vid(root, framerate, blob_params)