# vidtools

Tools for working with machine vision camera videos. Geared towards preprocessing animal behaviour videos.

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

Doing so will bring up the menu of possible options and commands. To execute a command, specify the command of interest after `vidtools`. For example, to run the `print-config` command:

```bash
vidtools print-config
```
### The `.yaml` file 

The successful execution of a command requires filling out a single `.yaml` configuration file. The configuration file provides the arguments for all of `vidtools`' commands. By default, `vidtools` will look for a file called **`config.yaml`** in the directory from which you run a `vidtools` command. For this reason, I suggest that you name your `.yaml` file  `config.yaml`. Otherwise, you can specify a particular `.yaml` file like so:

```
vidtools --config <path/to/config.yaml> <command>
```

For example, if the `.yaml` file you want to use has the path `~/tmp/my_weird_config.yaml`, and you want to run the `undistort` command, you'd input:

```bash
vidtools --config ~/tmp/my_weird_config.yaml undistort
```

Each key in the `.yaml` configuration file refers to a `vidtools` command. The value of each of these keys is a dictionary that specifies the parameters for that `vidtools` command. Make sure you do not have any trailing spaces in the `.yaml` file. An example `config.yaml` file is provided in the repository. 

### Commands

The outputs of `vidtools`' commands never overwrite existing files, without first asking for user confirmation. `vidtools`' commands and their respective `.yaml` file arguments are documented below:

#### `print-config`

<details><summary> Click for details. </summary>
<br>

This command prints the contents of the `.yaml` configuration file. It does not have any `.yaml` parameters.
</details>

#### `h264-to-mp4`

<details><summary> Click for details. </summary>
<br>

This command batch converts `.h264` videos to `.mp4` videos. It can output the `.mp4` videos in monochrome. Its `.yaml` parameters are:

- `root` (string): Path to the root directory; the directory that houses the target `.h264` videos. Is recursive.
- `framerate` (integer): The framerate, in Hz, of the target `.h264` videos. Assumes that all the videos in the `root` directory and its recursive subdirectories have the same framerate. 
- `do_mono` (boolean): If true, will also convert the videos to monochrome, with OpenCV. If false, will convert the videos, without recolouring, with FFmpeg. The OpenCV-based conversion **generates a higher quality output**, but takes longer. 

This command returns converted `.mp4` videos, in the same directory as the input `.h264` videos. 
</details>

#### `vid-to-imgs`

<details><summary> Click for details. </summary>
<br>

This command converts a subset of video frames into images. It can either convert a single `.mp4` video, or batch convert a directory of `.mp4` videos. Its `.yaml` parameters are:

- `root` (string): Path to the root video or directory. If the latter, the directory that houses the target `.mp4` videos, and is recursive.
- `ext` (string): The desired file extension for the output images. 
- `frames` (iterable of ints): Specifies the frames for converting into images. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `.mp4` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 
- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable for converting to images.

This command returns a subdirectory of images, in the same directory as the input `.mp4` video or videos. 
</details>

#### `undistort`

<details><summary> Click for details. </summary>
<br>

This command undistorts videos by calibrating a checkerboard `.mp4` video or a folder of checkerboard `.jpg` images. This command can take a long time, if a lot of checkerboards are found. For this reason, if you wish to cut on compute time, I recommend inputting a folder of a few checkerboard `.jpg` images, rather than a whole checkerboard `.mp4` video. The number of internal corners on the checkerboard's rows and columns are interchangeable. Its `.yaml` parameters are:

- `board` (string): Path to the input calibration video of the checkerboard. Must _not_ be called `checkerboards`. Must be an `.mp4` file or a folder of `.jpg`s. If a `.pkl` file for the calibration already exists, it should be in the same directory that the `board_vid` video is in.
- `framerate` (integer): Framerate of `board_vid` video and `target` videos, in Hz. If `board_vid` is a path to a directory of `.jpg`s, then `framerate` applies only to the videos specified by `target`. The fact that this argument accepts only a single integer means that both the `board_vid` and `target` videos must have the same framerate. 
- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.
- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.
- `target` (string):  Path to the target video or directory of target videos to undistort. Videos must be `.mp4`. If a path to a directory of target videos is specified, the command will _not_ undistort videos with the substrings "checkerboard" or "undistorted". In other words, it won't undistort the (distorted) video of labeled checkerboards, and videos that have already been undistorted. Is recursive, if a path to a directory is specified. 
- `do_debug` (boolean): If true, will show a live feed of the labeled checkerboards, and will save a directory of the labeled checkerboards as `.jpg`s.  
- `do_crop` (boolean): If true, will crop the dead pixels out of the undistorted video outputs. **_Must be true if the output video is to be used as the `undistorted_board` argument in the `pxls_to_mm` command_**. 

This command returns a fanciful video of the (still distorted) checkerboard video with labeled detected checkerboard corners, the undistorted target `.mp4` videos, and a `.pkl` file of the camera calibration matrix that was used to undistort the target videos. Additional outputs will be returned if `do_debug` is true. 
</details>

#### `pxls-to-real`

<details><summary> Click for details. </summary>
<br>

This command converts pixel measurements to physical lengths, by calibrating with an *undistorted* `.mp4` video of checkerboards. Its `.yaml` parameters are:

- `real_board_squre_len`: The actual real-world length of an edge of a checkerboard square, e.g. in mm. 
- `undistorted_board` (string): Path to an _undistorted_ video of the checkerboard. Will be the output of the `undistort` command, where `do_crop` is true. 
- `framerate` (integer): Framerate of `undistorted_board` video in Hz. 
- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.
- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.
- `frames` (iterable of ints): Specifies the frames in which to look for checkerboards. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `undistorted_board` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 
- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for checkerboard corners. 

This command returns the ratio of pixels to real-world units in a `pxls_to_mm.pkl` file saved in the same directory as the `undistorted_board` video. 
</details>

#### `find-circle`

<details><summary> Click for details. </summary>
<br>

This command uses a [Hough Circle Transform](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d) to find a _single_ mean circle for each undistorted video, in a directory of undistorted `.mp4` videos. The typical use case is for identifying the boundaries of a circular arena from a behaviour video. Its `.yaml` parameters are:

- `root` (string): Path to the root directory; the directory that houses the target `_undistorted.mp4` videos. i.e. videos with the suffix `_undistorted.mp4`. Is recursive.
- `dp` (integer): The image resolution over the accumulator resolution. See the OpenCV docs for details.
- `param1` (integer): The highest threshold of the two passed to the Canny edge detector. See OpenCV docs for details.
- `param2` (integer): The accumulator threshold for the circle centres at the detection stage. The smaller it is, the more false circles that may be detected. See OpenCV docs for details.
- `minDist` (integer): Minimum distance between the centres of the detected circles, in pixels. If the parameter is too small, multiple neighbour circles may be falsely detected, in addition to the true one. See OpenCV docs for details. 
- `minRadius` (integer): Minimum circle radius, in pixels. See OpenCV docs for details.
- `maxRadius` (integer): Maximum circle radius, in pixels. See OpenCV docs for details. 
- `frames` (iterable of ints): Specifies the frames in which to look for circles. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the undistorted `.mp4` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 
- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for circles. 

This command returns a `.pkl` file that ends in `_circle.pkl`, for each `.mp4` video. The `.pkl` file contains the Cartesian pixel coordinates of the mean circle's center and the pixel radius of the mean circle. 
</details>



TODO: Reformat the remaining scripts to click-style commands and update docs here