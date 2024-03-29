from os.path import expanduser, splitext, basename
from pathlib import Path
import atexit
import csv

import cv2
import numpy as np
from tqdm import tqdm, trange

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
    An array of shape (rows, 5), where each row is a detected blob, and the 5 columns are the 
    bottom left corner's x coord, the bottom left corner's y coord, the top right corner's 
    x coord, the top right corner's y coord, and a perfect dummy score of 1.0.
    """

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    detector = init_blob_detector(**blob_params)
    keypoints = detector.detect(frame)

    # Get keypoint (centroid) coordinates and size of blobs: 
    dets = []
    for i in range(len(keypoints)):

        # The first index refers to the blob number:
        x = keypoints[i].pt[0] 
        y = keypoints[i].pt[1]
        d = keypoints[i].size # dia

        # Make bounding boxes from centroid data:
        scalar = 2 # adjust bbox size
        x1 = float(x - d/2 * scalar) 
        y1 = float(y - d/2 * scalar)
        y2 = float(y + d/2 * scalar)
        x2 = float(x + d/2 * scalar)

        # print(f"is x1 < x2: {x1 < x2}")
        # p rint(f"is y1 < y2: {y1 < y2}")

        # Format into a np array that has in it the format [[x1,y1,x2,y2,score],[x1,y1,x2,y2,score],...]
        # where 1 is the bottom left corner coords and 2 is the top right corner coords of the bbox.
        # Format this way for the SORT tracker:
        det = [x1, y1, x2, y2, 1.0, x, y, d] # provide a perfect dummy score of 1.0; last 3 elements are NOT for SORT
        dets.append(det)

    dets = np.array(dets)

    return dets 


def get_bkgd(vid):

    """ 
    Compute the background image from a video, by taking the median of each pixel
    from a sample of 30 evenly spaced frames. 

    Parameters:
    -----------
    vid (str): Path to input .mp4 video. 

    Returns:
    --------
    The background image as an array of uint8s. 
    """

    cap = cv2.VideoCapture(vid)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    step = int(frame_count / 30)
    if frame_count < 30: step = 0

    samples = []
    pbar = trange(0, frame_count, step)
    for f in pbar:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        samples.append(gray)
        pbar.set_description(f"Getting frames for computing background image")

    stack = np.stack(samples)
    bkgd = np.median(stack, axis=0).astype(np.uint8) # OpenCV img elements must be uint8

    return bkgd


def get_thresh_from_sample_blobs(vid, bkgd, blob_params):

    """
    Computes the threshold with which to binarize the image, so that the blobs are
    black on a white background. Randomly samples 10 frames from the input video,
    then uses OpenCV's SimpleBlobDetector (via `detect_blobs()`) to get approximate 
    ROIs of the blobs from the **raw image**. Then runs Otsu thresholding to get 
    the thresholds for each ROI. Returns the mean threshold from the ROIs. 

    Parameters:
    -----------
    vid (str): Path to input .mp4 video. 
    bkgd (array of uint8s): The background image. 
    blob_params (dict): A dictionary of parameters for `init_blob_detector()`. 
    

    Returns:
    --------
    The mean threshold value (uint8) from the blob ROIs.
    """

    cap = cv2.VideoCapture(vid)

    # Draw random number of images from video:
    num_chosen = 10
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    samples = sorted(np.random.choice(frame_count, num_chosen))
    
    print("\nComputing threshold to use from blob samples ...")

    thresholds = []
    for f in samples:
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

         # Background subrtact:
        frgd = cv2.absdiff(gray, bkgd) 
        # Invert the image:
        b_on_w = cv2.bitwise_not(frgd)

        # Recall that detection here is with min_threshold=1, max_threshold=255
        dets = detect_blobs(b_on_w, blob_params)
        if len(dets) == 0:
            continue

        # For each detected bounding box, use Otsu to get a threshold:
        for det in dets:

            x1 = int(det[0])
            y1 = int(det[1])
            x2 = int(det[2])
            y2 = int(det[3])
            
            bbox = b_on_w[y1:y2,x1:x2]
            thresh,_ = cv2.threshold(bbox,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            # Put threshold vals for all objs into a list, even if those objs are diff types:
            thresholds.append(thresh)

    mean_thresh = np.mean(thresholds).astype(np.uint8) 
    print(f"Computed threshold to use: {mean_thresh}")

    return mean_thresh


def track_blobs(vid, framerate, max_age, min_hits, iou_thresh, bkgd, blob_params, do_show=False):

    """
    Detects and tracks blobs across a video. 

    Parameters:
    -----------
    vid (str): Path to input .mp4 video.
    framerate (int): Framerate with which `vid` was recorded.
    max_age (int): Maximum number of frames to keep a track alive without associated detections.
    min_hits (int): Minimum number of associated detections before track is initialized.
    iou_thresh (float): Minimum IOU (Intersection over Union) for match. 
    bkgd (array of uint8s): The background image. 
    blob_params (dict): A dictionary of parameters for `init_blob_detector()`. 

    Returns:
    --------
    Void; saves a video and a csv of the detected blobs.
    """

    csv_path = f"{splitext(vid)[0]}_blobbed.csv"
    csv_file_handle = open(csv_path, "w", newline="")
    atexit.register(csv_file_handle.close)
    col_names = ["frame", "blob_id", 
                 "centroid_x", "centroid_y", "dia",
                 "rect_x1", "rect_y1", 
                 "rect_x2", "rect_y2"] 
    csv_writer = csv.DictWriter(csv_file_handle, fieldnames=col_names)
    csv_writer.writeheader()

    cap = cv2.VideoCapture(vid)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = trange(frame_count)
    output_vid = f"{splitext(vid)[0]}_blobbed.mp4"

    # Get the threshold to apply across the whole image:
    thresh = get_thresh_from_sample_blobs(vid, bkgd, blob_params)
    # Change the min threshold of blob params here so OpenCV's blob detector
    # starts its thresholding on the whole image right below the Otsu threshold, which 
    # we got from the line right above; keep max_threshold at 255:
    blob_params["min_threshold"] = float(thresh - 20)

    # Initialize the SORT object:
    mot_tracker = Sort(max_age, min_hits, iou_thresh)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v") 
    out = cv2.VideoWriter(filename=output_vid, 
                            apiPreference=0, 
                            fourcc=fourcc, 
                            fps=int(framerate), 
                            frameSize=(int(cap.get(3)), int(cap.get(4))), 
                            params=None)

    count = 0
    only_empties_so_far = True
    for f,_ in enumerate(pbar):

        _, frame = cap.read()
            
        # Keep track of the frame we're on, so we can manipulate if we want:
        count += 1

        # # Always skip first 10 frames, because of artifacts:
        # if count <= 10:
        #     # For recording data, return NaN 
        #     csv_writer.writerow({col_name:np.nan for col_name in col_names})
        #     continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Background subrtact:
        frgd = cv2.absdiff(gray, bkgd) 
        # Invert the image:
        b_on_w = cv2.bitwise_not(frgd) 

        # Binarize:
        _, binarized = cv2.threshold(b_on_w, thresh, 255, cv2.THRESH_BINARY)

        # Get rid of salt and pepper noise with med filter:
        med_filtered = cv2.medianBlur(binarized, 7) # kernel size must be positive odd int

        # Detect on filtered binarized image and SORT-track:
        orig_dets = detect_blobs(med_filtered, blob_params)
        dets = orig_dets[...,:-3] # the last 3 cols aren't for SORT 
        if len(dets) == 0:
            dets = np.empty((0,5))
        trackers = mot_tracker.update(dets)

        if len(trackers) > 0:
            only_empties_so_far = False
        
        if only_empties_so_far:
            # For recording data, return NaN
            csv_writer.writerow({col_name:np.nan for col_name in col_names})
            print("Only empty tracks so far ...")
            continue

        # Draw and save data:
        # med_filtered = cv2.cvtColor(med_filtered, cv2.COLOR_GRAY2BGR) # draw on frame or processed?
        im_with_bboxes = frame
        for orig_det, tracker in zip(orig_dets, trackers): # trackers: [[x1, y1, x2, y2, ID], [x1, y1, x2, y2, ID], ...]

            x1 = int(tracker[0])
            y1 = int(tracker[1])
            x2 = int(tracker[2])
            y2 = int(tracker[3])

            # Save to csv:
            csv_writer.writerow({col_names[0]: count,             # frame
                                 col_names[1]: int(tracker[-1]),  # blob_id
                                 col_names[2]: int(orig_det[-3]), # centroid_x
                                 col_names[3]: int(orig_det[-2]), # centroid_y
                                 col_names[4]: int(orig_det[-1]), # dia
                                 col_names[5]: x1,                # rect_x1
                                 col_names[6]: y1,                # rect_y1
                                 col_names[7]: x2,                # rect_x2
                                 col_names[8]: y2})               # rect_y2
            
            # Draw on video:
            top_left = (x1, y1) 
            bottom_right = (x2, y2) 
            # Format: img mtx, box top left corner, bbox bottom right corner, colour, thickness
            im_with_bboxes = cv2.rectangle(im_with_bboxes, top_left, bottom_right, (165, 194, 102), 2)
            # # Format: img mtx, text, posn, font type, font size, colour, thickness
            # im_with_txt = cv2.putText(im_with_bboxes, f"ID: {int(tracker[-1])}", top_left, cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 1) 
        
        if do_show:
            
            cv2.imshow("tracked objects ...", im_with_bboxes) 
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        # out.write(im_with_txt)
        out.write(im_with_bboxes) # don't save text in the video
        pbar.set_description(f"Detecting {len(dets)} blob(s) from frame {f+1}/{frame_count}")

    csv_file_handle.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def main(config):

    root = expanduser(config["track_blobs"]["root"])
    vid_ending = '*' + config["track_blobs"]["vid_ending"]
    framerate = config["track_blobs"]["framerate"]
    do_show = config["track_blobs"]["do_show"]

    max_age = config["track_blobs"]["max_age"]
    min_hits = config["track_blobs"]["min_hits"]
    iou_thresh = config["track_blobs"]["iou_thresh"]

    non_blob_params = set(["root", "vid_ending", "framerate", "do_show", 
                           "max_age", "min_hits", "iou_thresh"])
    all_params = config["track_blobs"]
    blob_params = {k:v for (k,v) in all_params.items() if k not in non_blob_params}

    # TODO: Add in a do_ask flag that draws a random sample of images from video and asks users if
    # they want to proceed; show the binarized filtered image. 

    if Path(root).is_dir():

        vids = sorted([str(path.absolute()) for path in Path(root).rglob(vid_ending) 
                      if "_blobbed" not in str(path.absolute())])

        if len(vids) == 0:
            raise ValueError("\nNo untracked videos ending with '.mp4' were found.")

        for vid in vids:
            
            output_vid = f"{splitext(vid)[0]}_blobbed.mp4"

            if Path(output_vid).exists():
                print(f"\n{output_vid} already exists. Skipping ...")
                continue
            
            print("\nComputing background image ...")
            bkgd = get_bkgd(vid)
            print("Computed background image.")

            print(f"Detecting blob(s) in {basename(vid)} ...")
            track_blobs(vid, framerate, max_age, min_hits, iou_thresh, bkgd, blob_params, do_show)
            print(f"Finished detecting blob(s) in {basename(vid)}" )

    elif Path(root).is_file():
        bkgd = get_bkgd(root)
        track_blobs(root, framerate, max_age, min_hits, iou_thresh, bkgd, blob_params, do_show)