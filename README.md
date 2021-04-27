# Video scripts
Scripts for working with machine vision camera videos. 

## Installation:

TODO: wrap this in a package and use entry_points

## Dependencies:
TODO: Put this in a yaml file and write out the conda create command

Set up an Anaconda environment with the following installs:

```
conda create -n cinema python=3.8
conda install -c conda-forge opencv=4.5.0
conda install scikit-image
conda install tqdm
pip install motmot.FlyMovieFormat
pip install ffmpy
```

Tested on Ubuntu 18.04. 

## How to use

These scripts accept a path to a common  `.yaml` configuration file as their sole argument. The keys for the `.yaml` file are listed for each script:

### `undistort`

- `board_vid` (string): Path to the input calibration video of the checkerboard. Must _not_ be called `checkerboards`. Must be an `.mp4` file or a folder of `.jpg`s. If a `.pkl` file for the calibration already exists, it should be in the same directory that the `board_vid` video is in.
- `framerate` (integer): Framerate of `board_vid` video and `target` videos, in Hz. If `board_vid` is a path to a directory of `.jpg`s, then `framerate` applies only to the videos specified by `target`. The fact that this argument accepts only a single integer means that both the `board_vid` and `target` videos must have the same framerate. 
- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.

- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.
- `target` (string):  Path to the target video or directory of target videos to undistort. Videos must be `.mp4`. If a path to a directory of target videos is specified, the script will _not_ undistort videos with the substrings "checkerboard" or "undistorted". In other words, it won't undistort the (distorted) video of labeled checkerboards, and videos that have already been undistorted. 
- `do_debug` (boolean): If true, will show a live feed of the labeled checkerboards, and will save a directory of the labeled checkerboards as `.jpg`s.  
- `keep_dims` (boolean): If true, will not crop the dead pixels out of the undistorted video outputs. 

This script returns a fanciful video of the (still distorted) checkerboard video with labeled detected checkerboard corners, the undistorted target videos, and a `.pkl` file of the camera calibration matrix that was used to undistort the target videos. Additional outputs will be returned if `do_debug` is true. 

### `pxls_to_mm`

- `real_board_squre_len`: The actual real-world length of an edge of a checkerboard square, e.g. in mm. 
- `undistorted_board` (string): Path to an _undistorted_ video of the checkerboard. 

- `framerate` (integer): Framerate of `undistorted_board` video in Hz. 

- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.

- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.

- `frames` (iterable of ints): Specifies the frames in which to look for checkerboards. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `undistorted_board` video. If the length of the iterable is 0, the script will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 

- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for checkerboard corners. 

This script returns the ratio of pixels to real-world units in a `pxls_to_mm.pkl` file saved in the same directory as the `undistorted_board` video. 