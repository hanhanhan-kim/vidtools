"""
Use Hough Circle Transform to find a single mean circle from a dir of videos. 
Typical use case is for identifying the boundaries of a circular arena. 
"""

from os.path import expanduser, splitext, basename
from pathlib import Path
import pickle
from pprint import pprint

import numpy as np
import cv2

from vidtools.common import ask_yes_no


def find_circle(vid, dp=2, param1=80, param2=200, minDist=140, 
                minRadius=400, maxRadius=0, frames=[], do_ask=False):
    
    """
    From a subset of frames from a video, finds a circle in each frame.
    
    Parameters:
    -----------
    vid (str): Path to the input video. 
    dp (int): The image resolution over the accumulator resolution. See 
        the OpenCV docs for details. 
    param1 (int): The highest threshold of the two passed to the Canny 
        edge detector. See OpenCV docs for details. 
    param2 (int): The accumualtor threshold for the circle centers at the
        detection stage. The smaller it is, the more false circles that 
        may be detected. See OpenCV docs for details.
    minDist (int): Minimum distance between the centers of the detected
        circles, in pixels. If the parameter is too small, multiple 
        neighbour circles may be falsely detected, in addition to the true 
        one. See OpenCV docs for details. 
    minRadius (int): Minimum circle radius, in pixels. See OpenCV docs for
        details.
    maxRadius (int): Maximum circle radius, in pixels. See OpenCV docs for 
        details.
    frames (iterable of ints): Specifies the frames in which to look for
        checkerboards. Accepts an iterable of ints, such as a list of ints, 
        where the ints specify the indices of the frames in the video. 
        If the length of the iterable is 0, will randomly draw 5 frames from 
        the video.
    do_ask (bool): If True, will ask the user at every step to verify that 
        the extracted frames are suitable images in which to search for 
        checkerboard corners. Otherwise, will not ask the user. Default is 
        False. 
    
    Returns:
    --------
    A list of dictionaries, where each dictionary stores the frame that the 
    circle was found, the (x,y) coordinate of the circle's center, and the 
    circle's radius. Only 1 circle is found per frame, or else an error is 
    raised.
    """
    
    # 1. DRAW FRAMES FROM VIDEO:
    
    cap = cv2.VideoCapture(vid)
    
    # Option 1: Draw random number of images from video:
    if len(frames) == 0:
        num_chosen = 5
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        samples = np.random.choice(frame_count, num_chosen)
    
    # Option 2: Draw specified frames from video:
    else:
        samples = frames
    
    samples = sorted(samples)
    imgs = []
    for f in samples:
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.medianBlur(gray, 5)
        imgs.append(blurred) # save imgs
        
        if do_ask:
            cv2.imshow(f"frame_{f}", gray)
            cv2.waitKey(0) # wait for any key
            cv2.destroyAllWindows()# DO NOT CLOSE VIA THE X ON THE GUI IN JUPYTER!
    
    # 2. DETECT CIRCLES:
    
    if do_ask:
        q = "Do you want to find circles from these frames?"
        a = ask_yes_no(q)
    else:
        a = True
        
    if a:
        
        all_circles =[]
        for i, img in enumerate(imgs):
            
            circles = cv2.HoughCircles(img, 
                                       method=cv2.HOUGH_GRADIENT, 
                                       dp=dp, 
                                       minDist=minDist, 
                                       param1=param1, 
                                       param2=param2, # the higher, the fewer false circles detected
                                       minRadius=minRadius, 
                                       maxRadius=0)
            
            try:
                circles = np.uint16(np.around(circles))
            except TypeError as e:
                raise Exception("No circles were found. Try adjusting the circle finding parameters, " 
                                "like `param1` and `param2`.") from e

            print(f"frame {samples[i]}: [x, y, radius] {np.squeeze(circles)}")
            
            # Recolor:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            # Draw circles:
            for c in circles[0,:]:
                # Draw the outer circle
                cv2.circle(img,(c[0],c[1]),c[2],(0,255,0),2)
                # Draw the center of the circle
                cv2.circle(img,(c[0],c[1]),2,(0,0,255), 3)
            
            cv2.imshow('detected circles', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            circles = np.squeeze(circles)

            if circles.ndim > 1 or len(circles) > 3:
                raise ValueError("More than 1 circle was detected. Change parameters so that only 1 circle is detected.")
            
            f = samples[i]
            x = circles[0]
            y = circles[1]
            r = circles[2]
            
            data = {"frame": f, "x (pxls)": x, "y (pxls)":y, "radius (pxls)":r}
            all_circles.append(data)
                
        return all_circles
            
    else:
        exit("\nPlease re-run the script. Exiting ...")

    cap.release()


def get_mean_circle_info(circle_info):
    
    """Get mean values from the output of `find_circle()`"""
    
    for circle in circle_info:
        xs, ys, rs = [], [], []
        for k,v in circle.items():
            xs.append(circle["x (pxls)"])
            ys.append(circle["y (pxls)"])
            rs.append(circle["radius (pxls)"]) 
        
    return {"x (pxls)":np.mean(xs), 
            "y (pxls)":np.mean(ys), 
            "r (pxls)":np.mean(rs)}


def mask_and_crop(vid, mean_circle_info, framerate):

    """
    Mask a video with a circle, and then crop the video around the circle. 
    
    Parameters:
    -----------
    vid (str): Path to the input video
    mean_circle_info (dict): The output of `get_mean_circle_info()`.
    framerate: The video framerate.

    Returns:
    --------
    The new circle centre coordinates and radius (radius will be same as before). 
    In addition, saves the masked and cropped video. 
    """

    output_vid = f"{splitext(vid)[0]}_masked.mp4"

    cap = cv2.VideoCapture(vid)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x = int(mean_circle_info["x (pxls)"])
    y = int(mean_circle_info["y (pxls)"])
    r = int(mean_circle_info["r (pxls)"])

    spacing = 5
    target_edge = 2 * (r + spacing)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v") 
    out = cv2.VideoWriter(filename=output_vid, 
                            apiPreference=0, 
                            fourcc=fourcc, 
                            fps=int(framerate), 
                            frameSize=(int(target_edge), int(target_edge)), 
                            params=None)

    while cap.isOpened():

        ret, frame = cap.read()
        
        if ret:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Mask:
            mask = np.zeros((height, width), dtype="uint8")
            cv2.circle(mask, (x,y), r, 255, -1)
            masked = cv2.bitwise_and(gray, gray, mask=mask)

            # Crop (centred about circle centre): 
            roi = masked[y-r-spacing : y+r+spacing, x-r-spacing : x+r+spacing]

            # In OpenCV, images saved to video file must be three channels:
            re_bgr = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)

            # # Inspect the location of the new circle centre:
            # x_after_crop = int(roi.shape[1]/2)
            # y_after_crop = int(roi.shape[0]/2)
            # test = cv2.circle(roi, (x_after_crop, y_after_crop), 5, (0,0,255), -1)
            # re_bgr = cv2.cvtColor(test, cv2.COLOR_GRAY2BGR)

            out.write(re_bgr)
            cv2.imshow("masked", re_bgr)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    out.release()

    x_after_crop = int(roi.shape[1]/2)
    y_after_crop = int(roi.shape[0]/2)

    return {"x (pxls)": x_after_crop, 
            "y (pxls)": y_after_crop,
            "r (pxls)": r}


# Formatted for click; config is a dict loaded from yaml:
def main(config):

    root = expanduser(config["find_circle"]["root"])
    vid_ending = '*' + config["find_circle"]["vid_ending"]
    framerate = int(config["find_circle"]["framerate"])
    dp = int(config["find_circle"]["dp"])
    param1 = int(config["find_circle"]["param1"])
    param2 = int(config["find_circle"]["param2"])
    minDist = int(config["find_circle"]["minDist"])
    minRadius = int(config["find_circle"]["minRadius"])
    maxRadius = int(config["find_circle"]["maxRadius"])
    frames = config["find_circle"]["frames"]
    do_ask = config["find_circle"]["do_ask"]
    
    vids = [str(path.absolute()) for path in Path(root).rglob(vid_ending) 
            if ".mp4" in str(path.absolute())]

    if len(vids) == 0:
        raise ValueError(f"No .mp4 videos ending with '{vid_ending}' were found.")

    for vid in vids:
        
        print(f"Processing {vid} ...")
        output_pkl = f"{splitext(vid)[0]}_circle.pkl"

        if Path(output_pkl).is_file():
            print(f"{basename(output_pkl)} already exists. Skipping ...")

        else:
            all_circles = find_circle(vid=vid, 
                                      dp=dp, 
                                      minDist=minDist, 
                                      param1=param1, 
                                      param2=param2, 
                                      minRadius=minRadius, 
                                      maxRadius=maxRadius, 
                                      frames=frames, 
                                      do_ask=do_ask)

            results = get_mean_circle_info(all_circles)

            # Mask and crop video, then save:
            results_after_cropping = mask_and_crop(vid, results, framerate)

            print("mean circle:")
            pprint(results)
            pickle.dump(results_after_cropping, open(output_pkl, "wb"))
            print(f"The mean circle has been saved to {output_pkl} .")