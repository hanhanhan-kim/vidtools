#!/usr/bin/env python3

"""
Calibrates and undistorts images from a calibration checkerboard video.
Calibration video must be called "calibration.mp4". 
The rows and corners of the checkerboard are interchangeable. 
"""

import subprocess
import argparse
from os.path import splitext, expanduser, basename, dirname
from os import path, mkdir
from pathlib import Path

import cv2
import numpy as np


def convert_vid_to_jpgs(calib_vid, 
                        framerate, 
                        backend="opencv"):

    """
    Converts a video called "calibration.mp4" into a folder of .jpgs. 
    Saves the .jpgs folder into the same directory as "calibration.mp4".

    Parameters:
    -----------
    calib_vid (str): Path to "calibration.mp4".
    framerate (int): Framerate with which "calibration.mp4" was recorded.
    backend (str): Backend with which to convert. Can be either "opencv" or "ffmpeg".
        Default is "opencv". The ffmpeg backend is much faster, but is poor quality.

    Returns:
    --------
    A folder of .jpgs.
    """

    assert("calibration.mp4" in calib_vid, f"'calibration.mp4' is not in {calib_vid}")

    calib_vid = expanduser(calib_vid)
    jpgs_dir = path.join(dirname(calib_vid), "calibration")

    if Path(jpgs_dir).is_dir():

        print(f"{basename(jpgs_dir)} already exists at '{dirname(jpgs_dir)}'. Skipping ...")

    else:
        
        mkdir(jpgs_dir)
        print("Converting 'calibration.mp4' to .jpgs")

        if backend=="opencv":

            cap = cv2.VideoCapture(calib_vid)
            
            i = 0
            while (cap.isOpened()):

                ret, frame = cap.read()

                if ret == True:

                    cv2.imwrite(path.join(jpgs_dir, f"frame_{i:08d}.jpg"), frame)
                    cv2.imshow(f"converting {basename(calib_vid)} ...", frame) 

                    i += 1

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                else:
                    break
            
            cap.release()
            cv2.destroyAllWindows()

        elif backend=="ffmpeg":

            args = ["ffmpeg", "-i", calib_vid, "-vf", f"fps={str(framerate)}", "frame_%08d.jpg"]
            equivalent_cmd = " ".join(args)

            print(f"running command {equivalent_cmd} from {jpgs_dir}")
            subprocess.run(args, cwd=jpgs_dir)

        else:
            print("backend arg must be either 'opencv' or 'ffmpeg'")


def calibrate_checkerboard(board_jpgs_path, m_corners, n_corners):

    """
    Finds internal corners of checkerboards and saves them from a folder of .jpgs.
    Generates the camera matrix from the checkerboards' internal corners. 

    Parameters:
    -----------
    board_jpgs_path (str): Path to folder where 
    m_corners (int): Number of internal corners along the 
        rows of the checkerboard
    n_corners (int): Number of internal corners along the 
        columns of the checkerboard

    Returns:
    --------

    """

    boards_dir = path.join(dirname(board_jpgs_path), "checkerboards")

    if Path(boards_dir).is_dir():
        print(f"{basename(boards_dir)} already exists at {dirname(boards_dir)}. Skipping ...")

    else:
        mkdir(boards_dir)

        images = [str(path.absolute()) for path in Path(board_jpgs_path).rglob("*.jpg")]
        
        # FIND CORNERS:

        # Termination criteria:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Prepare object points like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0):
        obj_p = np.zeros((n_corners * m_corners, 3), np.float32)
        obj_p[:,:2] = np.mgrid[0:m_corners, 0:n_corners].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images: 
        obj_points = [] # 3d point in real world space
        img_points = [] # 2d points in image plane

        i = 0
        for fname in images:

            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            # Find the chess board corners:
            ret, corners = cv2.findChessboardCorners(gray, (m_corners, n_corners),None)

            # If found, add object points, image points (after refining them):
            if ret == True:
                
                obj_points.append(obj_p)

                # This method increases the accuracy of the identified corners:
                better_corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                img_points.append(better_corners)

                # Draw and display the corners:
                img = cv2.drawChessboardCorners(img, (m_corners, n_corners), better_corners, ret)
                cv2.imwrite(path.join(boards_dir, f"checkerboard_{i:08d}.jpg"), img)
                cv2.imshow(f"checkerboard", img) # live feed slows down the code
                print(f"found checkerboard number {i}")
                cv2.waitKey(500) # can't be too low, 500 seems safe if using imshow()
                i += 1

        cv2.destroyAllWindows()

        # CALIBRATE: 
        ret, mtx, dist, r_vecs, t_vecs = cv2.calibrateCamera(obj_points, img_points, 
                                                             gray.shape[::-1], 
                                                             None, None)

        return ret, mtx, dist, r_vecs, t_vecs


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("calib_vid", 
        help="Path to the input calibration video")
    parser.add_argument("framerate",
        help="Framerate (int)")
    parser.add_argument("m_corners",
        help="Number of internal corners along the rows of the checkerboard")
    parser.add_argument("n_corners",
        help="Number of internal rows along the corners of the checkerboard")
    parser.add_argument("-ff","--ffmpeg", action="store_true",
        help="Generate .jpgs with ffmpeg instead of OpenCV") 
    args = parser.parse_args()

    calib_vid = expanduser(args.calib_vid)
    framerate = args.framerate
    is_ffmpeg = args.ffmpeg
    board_jpgs_path = path.join(dirname(calib_vid), "calibration")
    m_corners = int(args.m_corners)
    n_corners = int(args.n_corners)

    if not is_ffmpeg:
        convert_vid_to_jpgs(calib_vid, framerate)

    else:
        convert_vid_to_jpgs(calib_vid, framerate, backend="ffmpeg")

    ret, mtx, dist, r_vecs, t_vecs = calibrate_checkerboard(board_jpgs_path, m_corners, n_corners) 

            
if __name__ == "__main__":
    main()