"""
Make a timelapse image from a grayscale video.
"""

from os.path import expanduser, splitext, basename, dirname
from pathlib import Path

import numpy as np
import cv2
from tqdm import tqdm, trange


def get_timelapse(vid, density, is_dark_on_light=True):

    """
    """

    if density > 1 or density < 0:
        raise ValueError(f"The density, {density}, must be between 0 and 1.")

    cap = cv2.VideoCapture(vid)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    used_frames = density * frame_count

    step = int(frame_count / used_frames)
    if frame_count < used_frames: step = 0

    samples = []
    pbar = trange(0, frame_count, step)
    for f in pbar:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        _, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        samples.append(gray)
        pbar.set_description(f"Getting frames for computing timelapse image ...")

    print(f"Computing timelapse image ...")
    stack = np.stack(samples)

    # OpenCV img elements must be uint8
    if is_dark_on_light:
        timelapse = np.min(stack, axis=0).astype(np.uint8)
    else:
        timelapse = np.max(stack, axis=0).astype(np.uint8)

    return timelapse


def main(config):
    
    root = expanduser(config["make_timelapse"]["root"])
    vid_ending = '*' + config["make_timelapse"]["vid_ending"]
    density = config["make_timelapse"]["density"]
    is_dark_on_light = config["make_timelapse"]["is_dark_on_light"]

    if Path(root).is_dir():

        vids = [str(path.absolute()) for path in Path(root).rglob(vid_ending)]

        if len(vids) == 0:
            raise ValueError(f"\nNo videos ending with {vid_ending} were found.")

        for vid in vids:

            output_img = f"{splitext(vid)[0]}_timelapse.png"

            if Path(output_img).exists():
                print(f"\n{output_img} already exists. Skipping ...")
                continue

            timelapse = get_timelapse(vid, density)
            print(f"Computed timelapse image from {basename(vid)}")

            cv2.imwrite(output_img, timelapse)
            print(f"Saved timelapse image in {dirname(output_img)}")

    elif Path(root).is_file():

        output_img = f"{splitext(root)[0]}_timelapse.png"

        if Path(output_img).exists():
            print(f"\n{output_img} already exists. Skipping ...")
        
        else:
            timelapse = get_timelapse(root, density, is_dark_on_light)
            print(f"Computed timelapse image from {basename(root)}")

            cv2.imwrite(output_img, timelapse)
            print(f"Saved timelapse image in {dirname(output_img)}")
