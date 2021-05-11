from os.path import expanduser, dirname, join, basename, splitext
from os import mkdir
from pathlib import Path

import numpy as np
import cv2


def vid_to_imgs(vid, frames=[], ext="png", do_ask=False):

    """
    Convert a subset of video frames into images.

    Parameters:
    -----------
    vid (str): Path to the input video. 
    frames (iterable of ints): Specifies the frames in which to look for
        checkerboards. Accepts an iterable of ints, such as a list of ints, 
        where the ints specify the indices of the frames in the video. 
        If the length of the iterable is 0, will randomly draw 5 frames from 
        the video.
    ext (str): The desired file extension for the image output. 
    do_ask (bool): If True, will ask the user at every step to verify that 
        the extracted frames are suitable images in which to search for 
        checkerboard corners. Otherwise, will not ask the user. Default is 
        False.

    Returns:
    --------
    A folder of images. 
    """

    vid = expanduser(vid)
    imgs_dir = splitext(vid)[0]
    mkdir(imgs_dir)

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
    for f in samples:
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, img = cap.read()
        
        if do_ask:
            cv2.imshow(f"frame_{f}", img)
            cv2.waitKey(0) # wait for any key
            cv2.destroyAllWindows()# DO NOT CLOSE VIA THE X ON THE GUI IN JUPYTER!

        cv2.imwrite(join(imgs_dir, f"frame_{f:08d}.{ext}"), img)


# Formatted for click; config is a dict loaded from yaml:
def main(config):

    root = expanduser(config["vid_to_imgs"]["root"])
    ext = config["vid_to_imgs"]["ext"]
    frames = config["vid_to_imgs"]["frames"]
    do_ask = config["vid_to_imgs"]["do_ask"]

    # TODO: Support multiple extension types:
    vids = [str(path.absolute()) for path in Path(root).rglob("*.mp4")]

    if len(vids) == 0:
        raise ValueError("No videos ending with '.mp4' were found.")

    # TODO: Support dir as well as single vid files as inputs
    for vid in vids:

        print(f"Processing {vid} ...")

        # TODO: Handle if already exists (overwrites)
        # if Path(output_pkl).is_file():
        #     print(f"{basename(output_pkl)} already exists. Skipping ...")

        vid_to_imgs(vid=vid, frames=frames, ext=ext, do_ask=do_ask)