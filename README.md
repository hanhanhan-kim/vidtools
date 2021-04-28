# vidtools

Tools for working with machine vision camera videos. 

Tested on Ubuntu 18.04. 

## Installation:

1. Clone this repository:

   ```bash
   git clone https://github.com/hanhanhan-kim/vidtools
   ```

2. Install the Anaconda environment from the repo's root directory, where `conda_env.yaml` is housed:

   ```bash
   conda env create -f conda_env.yaml
   ```

   It will create an environment called `vidtools`. 

3. Activate the environment:

   ```bash
   conda activate vidtools
   ```

4. Install the `vidtools` Python package from the repo's root directory:

   ```bash
   pip install .
   ```

## How to use

Using `vidtools` is simple! From anywhere, type the following in the command line:

```bash
vidtools
```

Doing so will bring up the menu of possible options and commands. To execute a command, specify the command of interest after `vidtools`. For example, to run `print-config`:

```bash
vidtools print-config
```

A single  `.yaml` configuration file provides the arguments for all of `vidtools`' commands. Each key in the `.yaml` file refers to a `vidtool` command. The value of each of these keys is a dictionary that specifies the parameters for that `vidtool` command. The keys for the `.yaml` file are listed below:

### `undistort`

- `board` (string): Path to the input calibration video of the checkerboard. Must _not_ be called `checkerboards`. Must be an `.mp4` file or a folder of `.jpg`s. If a `.pkl` file for the calibration already exists, it should be in the same directory that the `board_vid` video is in.
- `framerate` (integer): Framerate of `board_vid` video and `target` videos, in Hz. If `board_vid` is a path to a directory of `.jpg`s, then `framerate` applies only to the videos specified by `target`. The fact that this argument accepts only a single integer means that both the `board_vid` and `target` videos must have the same framerate. 
- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.

- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.
- `target` (string):  Path to the target video or directory of target videos to undistort. Videos must be `.mp4`. If a path to a directory of target videos is specified, the command will _not_ undistort videos with the substrings "checkerboard" or "undistorted". In other words, it won't undistort the (distorted) video of labeled checkerboards, and videos that have already been undistorted. 
- `do_debug` (boolean): If true, will show a live feed of the labeled checkerboards, and will save a directory of the labeled checkerboards as `.jpg`s.  
- `keep_dims` (boolean): If true, will not crop the dead pixels out of the undistorted video outputs. **_Must be true if the output video is to be used as the `undistorted_board` argument in the `pxls_to_mm` command_**. Otherwise, makes more sense to set this argument to false. 

This command returns a fanciful video of the (still distorted) checkerboard video with labeled detected checkerboard corners, the undistorted target videos, and a `.pkl` file of the camera calibration matrix that was used to undistort the target videos. Additional outputs will be returned if `do_debug` is true. 

### `pxls_to_real`

- `real_board_squre_len`: The actual real-world length of an edge of a checkerboard square, e.g. in mm. 
- `undistorted_board` (string): Path to an _undistorted_ video of the checkerboard. Will be the output of the `undistort` command, where `keep_dims` is false. 

- `framerate` (integer): Framerate of `undistorted_board` video in Hz. 

- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.

- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.

- `frames` (iterable of ints): Specifies the frames in which to look for checkerboards. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `undistorted_board` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 

- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for checkerboard corners. 

This command returns the ratio of pixels to real-world units in a `pxls_to_mm.pkl` file saved in the same directory as the `undistorted_board` video. 

TODO: Reformat the remaining scripts to click-style commands and update docs here