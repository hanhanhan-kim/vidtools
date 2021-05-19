from os.path import expanduser, join, splitext
from os import mkdir
from shutil import rmtree
from pathlib import Path

import numpy as np
import cv2


def vid_to_imgs(vid, frames=[], ext="png", do_ask=False, do_overwrite=False):

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
    do_overwrite (bool): If True, will overwrite the output folder of images,
        if it already exists. 

    Returns:
    --------
    A folder of images. 
    """

    vid = expanduser(vid)
    imgs_dir = splitext(vid)[0]
    if Path(imgs_dir).exists() and do_overwrite:
        rmtree(imgs_dir)
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
    
    # Use the OpenCV GUI to navigate through frames
    print("Press 'd' to go to adjacent next frame, 'a', to go to adjacent previous frame, "
           "and 's' to explicitly save the frame. Press any other key to go to the next frame "
           "specified in the `config.yaml` file")

    good_samples = {"idx":[], "img":[]}
    samples = sorted(samples)

    # Save state here, bc looping through samples in upcoming looop can mutate samples, 
    # if 'd' or 'a' are pressed:
    original_samples = samples.copy()
    did_explicit_save = False

    for i,f in enumerate(samples):
        
        print(f"Current frame: {f}")
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, img = cap.read()
        
        if do_ask:
            cv2.imshow(f"frame_{f}", img)
            key = cv2.waitKey(0) & 0xFF # FYI: Gotta save waitKey in its own var
            # Press "q" to quit:
            if key == ord("q"):
                print("Quitting ...")
                break
            # Press "d" to go to the next frame:
            elif key == ord("d"):
                f = f + 1
                samples.insert(i+1, f)
                cv2.destroyAllWindows()
                print("Remember to hit 's' to save.")
                continue
            # Press "a" to go to the previous frame: 
            elif key == ord("a"):
                f = f - 1
                samples.insert(i+1, f)
                cv2.destroyAllWindows()
                print("Remember to hit 's' to save.")
                continue
            # Press "s" to save this frame:
            elif key == ord("s"):
                did_explicit_save = True
                good_samples["idx"].append(f)
                good_samples["img"].append(img)
                print(f"Frame {f} has been saved.")
                samples.insert(i+1, f) # stay on current frame in imshow
                cv2.destroyAllWindows()

            # Press anything else to go to next frame in list:

            cv2.destroyAllWindows()
    
    # If no frames were explicitly saved via 's' key (e.g. if do_ask = False), 
    # just save what was specified in config.yaml:
    if not did_explicit_save:

        print("No frames were explicitly saved. Saving frames specified in `config.yaml`")

        for f in original_samples:

            cap.set(cv2.CAP_PROP_POS_FRAMES, f)
            _, img = cap.read()
            cv2.imwrite(join(imgs_dir, f"frame_{f:08d}.{ext}"), img)
    
    # Otherwise, save the images marked with 's' key to file: 
    else:
        for f, img in zip(good_samples["idx"], good_samples["img"]):
            cv2.imwrite(join(imgs_dir, f"frame_{f:08d}.{ext}"), img)


# Formatted for click; config is a dict loaded from yaml:
def main(config):

    root = expanduser(config["vid_to_imgs"]["root"])
    ext = config["vid_to_imgs"]["ext"]
    frames = config["vid_to_imgs"]["frames"]
    do_ask = config["vid_to_imgs"]["do_ask"]
    do_overwrite = config["vid_to_imgs"]["do_overwrite"]

    if Path(root).is_dir():

        vids = [str(path.absolute()) for path in Path(root).rglob("*.mp4")]

        if len(vids) == 0:
            raise ValueError("No videos ending with '.mp4' were found.")

        for vid in vids:
            print(f"Processing {vid} ...")
            vid_to_imgs(vid=vid, frames=frames, ext=ext, do_ask=do_ask, do_overwrite=do_overwrite)
    
    elif Path(root).is_file():
        vid_to_imgs(vid=root, frames=frames, ext=ext, do_ask=do_ask, do_overwrite=do_overwrite)