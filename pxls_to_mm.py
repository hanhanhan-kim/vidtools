#!/usr/bin/env python3

"""
Converts pixel measurements into physical lengths, by 
calibrating an undistorted video of checkerboards. 
"""

import argparse
from os.path import expanduser

import numpy as np
import cv2

from common import ask_yes_no, flatten_list


def get_checkerboard_coords(vid, framerate, frames, m_corners, n_corners, do_ask=False):
    
    """
    Finds the internal corners of a checkerboard. 
    Is useful for converting objects of known real-world lengths to pixels,
    and vice-versa, provided the objects of interest do not move in the z-direction. 
    Such conversions require that `vid` be an undistorted video of checkerboards.
    
    Parameters:
    -----------
    vid (str): Path to an undistorted video of checkerboards.
    framerate (int): Framerate with which `vid` was recorded. 
    frames (iterable of ints): Specifies the frames in which to look for
        checkerboards. Accepts an iterable of ints, such as a list of ints, where 
        the ints specify the indices of the frames in the video. If the length of 
        the iterable is 0, will randomly draw 5 frames from the video. 
    m_corners (int): Number of internal corners along the rows of the checkerboard.
        Is interchangeable with `n_corners`. 
    n_corners (int): Number of internal corners along the columns of the checkerboard.
        Is interchangeable with `m_corners`. 
    do_ask (bool): If True, will ask the user at every step to verify that the extracted 
        frames are suitable images in which to search for checkerboard corners. Otherwise, 
        will not ask the user. Default is False. 
    
    Returns:
    --------
    The mean length (fl) of checkerboard edges from the specified frames. 
    Will return None if no checkerboard edges are found. 
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
    
    imgs = []
    for f in sorted(samples):
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgs.append(gray) # save imgs
        
        if do_ask:
            cv2.imshow(f"frame_{f}", gray)
            cv2.waitKey(0) # wait for any key
            cv2.destroyAllWindows()# DO NOT CLOSE VIA THE X ON THE GUI IN JUPYTER!
    
    # 2. DETECT CHECKERBOARD CORNERS:
    
    if do_ask:
        q = "Do you want to detect checkerboards from these frames?"
        a = ask_yes_no(q)
    else:
        a = True
        
    if a:
        # Termination criteria:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # Prepare object points like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0):
        obj_p = np.zeros((n_corners * m_corners, 3), np.float32)
        obj_p[:,:2] = np.mgrid[0:m_corners, 0:n_corners].T.reshape(-1,2)
        # Arrays to store object points and image points from all the images: 
        obj_points = [] # 3d point in real world space
        img_points = [] # 2d points in image plane
                                                                   
        for img in imgs:
        
            # Find the checkerboard corners:
            do_ret, corners = cv2.findChessboardCorners(img, (m_corners, n_corners), None)

            # If found, add object points, image points (after refining them):
            if do_ret:

                obj_points.append(obj_p)

                # This method increases the accuracy of the identified corners:
                better_corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                img_points.append(better_corners)

                # Draw and display the corners:
                detected = cv2.drawChessboardCorners(frame, (m_corners, n_corners), better_corners, do_ret)
                
                # Convert shape of (m*n, 1, 2) to (m*n, 2):
                return np.squeeze(better_corners)
            
            else:
                print("No checkerboard corners were found.")
                return None
            
    else:
        # TODO: Have the user pick new frames or pick randomly:
        pass

    cap.release()


def get_dist(a, b):
    return np.sqrt( ((a[0]-b[0])**2) + ((a[1]-b[1])**2) )


def get_x_dists_checkerboard(corners, m_corners, n_corners):
    
    """
    Get the distance, in pixels, of each square's row edge, in the checkerboard. 
    
    Parameters:
    -----------
    corners: A numpy array that holds the [x,y] coordinates of the checkerboard corners.
        Will have a shape of ((m*n), 2), where m and n are the number of internal corners 
        along the rows and columns of the checkerboard, respectively. Will usually be 
        shaped (42, 2). Will be the output of `get_checkerboard_coords()`. 
    m_corners (int): Number of internal corners along the rows of the checkerboard.
        Is interchangeable with `n_corners`. 
    n_corners (int): Number of internal corners along the columns of the checkerboard.
        Is interchangeable with `m_corners`. 
    
    Returns:
    --------
    A list of distances, in pixels. 
    """
    
    return [get_dist(corners[i+1], corners[i]) 
            for i,_ in enumerate(corners) 
            # Don't go past the indices and 
            # don't compute dist bw last and final cols of diff rows:
            if (i < len(corners)-1) and ((i+1) % m_corners != 0)]


def get_y_dists_checkerboard(corners, m_corners, n_corners):
    
    """
    Get the distance, in pixels, of each square's column edge, in the checkerboard. 
    
    Parameters:
    -----------
    corners: A numpy array that holds the [x,y] coordinates of the checkerboard corners.
        Will have a shape of ((m*n), 2), where m and n are the number of internal corners 
        along the rows and columns of the checkerboard, respectively. Will usually be 
        shaped (42, 2). Will be the output of `get_checkerboard_coords()`. 
    m_corners (int): Number of internal corners along the rows of the checkerboard.
        Is interchangeable with `n_corners`. 
    n_corners (int): Number of internal corners along the columns of the checkerboard.
        Is interchangeable with `m_corners`. 
    
    Returns:
    --------
    A list of distances, in pixels. 
    """
    
    all_col_edge_lens = []
    
    for i in range(m_corners):
    
        col_corners = corners[i::m_corners]

        col_edge_lens = [get_dist(col_corners[j+1], col_corners[j]) 
                         for j,_ in enumerate(col_corners) 
                         # Don't go past the indices:
                         if (j < len(col_corners)-1)]
        
        all_col_edge_lens.append(col_edge_lens)
        
    return flatten_list(all_col_edge_lens)


def get_mean_edge_len_checkerboard(corners, m_corners, n_corners):

    """
    Gets the mean edge length from an array of coordinates that specifies
    the corners of the squares from a checkerboard. 

    Parameters:
    -----------
    corners: A numpy array that holds the [x,y] coordinates of the checkerboard corners.
        Will have a shape of ((m*n), 2), where m and n are the number of internal corners 
        along the rows and columns of the checkerboard, respectively. Will usually be 
        shaped (42, 2). Will be the output of `get_checkerboard_coords()`.
    m_corners (int): Number of internal corners along the rows of the checkerboard.
        Is interchangeable with `n_corners`. 
    n_corners (int): Number of internal corners along the columns of the checkerboard.
        Is interchangeable with `m_corners`. 

    Returns:
    --------
    The mean edge length of a square from the checkerboard video. 
    """

    return np.mean(get_x_dists_checkerboard(corners, m_corners, n_corners) \
                 + get_y_dists_checkerboard(corners, m_corners, n_corners))


def main():

    # TODO: Switch to yaml or toml. 

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board_vid", 
        help="Path to an UNDISTORTED video of checkerboards.")

    # TODO: Can't accept None as an alternative ... yaml might be able to answer this.
    parser.add_argument("-f", "--frames", nargs="+", type=int, required=True,
        help="Specifies the frames in which to look for checkerboards. Accepts an "
            "iterable of ints, such as a list of ints, where the ints specify the "
            "indices of the frames in the video. If the length of the iterable is 0, "
            "will randomly draw 5 frames from the video.  This argument is REQUIRED.")

    parser.add_argument("framerate",
        help="Framerate (int) in Hz")
    parser.add_argument("m_corners",
        help="Number of internal corners along the rows of the checkerboard")
    parser.add_argument("n_corners",
        help="Number of internal corners along the columns of the checkerboard")
    parser.add_argument("-v","--verify", action="store_true", 
        help="Ask the user at every step to verify that the extracted frames \n"
        "are suitable images in which to search for checkerboard corners.")
    args = parser.parse_args()

    board_vid = expanduser(args.board_vid)

    framerate = args.framerate
    frames = args.frames
    m_corners = int(args.m_corners)
    n_corners = int(args.n_corners)
    do_ask = args.verify

    corners = get_checkerboard_coords(vid=board_vid,
                                      frames=frames,
                                      framerate=framerate,
                                      m_corners=m_corners,
                                      n_corners=n_corners,
                                      do_ask=do_ask)

    print(get_mean_edge_len_checkerboard(corners, m_corners, n_corners))
    return get_mean_edge_len_checkerboard(corners, m_corners, n_corners)


if __name__ == "__main__":
    main ()