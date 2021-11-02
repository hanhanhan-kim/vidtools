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
   pip install -e .
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

This command batch converts `.h264` videos to `.mp4` videos. It can output the `.mp4` videos in monochrome. 

Its `.yaml` parameters are:

- `root` (string): Path to the root directory; the directory that houses the target `.h264` videos. Is recursive.

- `framerate` (integer): The framerate, in Hz, of the target `.h264` videos. Assumes that all the videos in the `root` directory and its recursive subdirectories have the same framerate. 

- `do_mono` (boolean): If true, will also convert the videos to monochrome, with OpenCV. If false, will convert the videos, without recolouring, with FFmpeg. The OpenCV-based conversion **generates a higher quality output**, but takes longer. 

This command returns converted `.mp4` videos, in the same directory as the input `.h264` videos. 
</details>


#### `vid-to-imgs`

<details><summary> Click for details. </summary>
<br>

This command converts a subset of video frames into images. It can either convert a single `.mp4` video, or batch convert a directory of `.mp4` videos. 

Its `.yaml` parameters are:

- `root` (string): Path to the root video or directory. If the latter, the directory that houses the target `.mp4` videos, and is recursive.

- `vid_ending` (string): The file ending of the videos to be analyzed. For example, `.mp4` or `_undistorted.mp4`. Videos without the specified file ending will be skipped. This command supports only `.mp4` video files.

- `ext` (string): The desired file extension for the output images. 

- `frames` (iterable of integers): Specifies the frames for converting into images. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `.mp4` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 

- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable for converting to images. In addition, will give the user access to a keystroke-based 'GUI', where hitting 'q' exits the `vid-to-imgs` command, 'd' takes the user to the adjacent next frame, 'a' takes the user to the adjacent previous frame, and 's' explicitly saves the current frame. Pressing any other key will take the user to the next frame specified in the `frames` parameter of the `.yaml` file. If no frames are explicitly saved with the 's' key, then only the frames specified in the `.yaml` file will be saved. Otherwise, only the explicitly saved frames will be saved. 

- `do_overwrite` (boolean): If true, will overwrite the output folder of images, if it already exists. 

This command returns a subdirectory of images, in the same directory as the input `.mp4` video or videos. 
</details>


#### `undistort`

<details><summary> Click for details. </summary>
<br>

This command undistorts videos by calibrating a checkerboard `.mp4` video or a folder of checkerboard `.jpg` images. This command can take a long time, if a lot of checkerboards are found. For this reason, if you wish to cut on compute time, I recommend inputting a folder of a few checkerboard `.jpg` images, rather than a whole checkerboard `.mp4` video. The number of internal corners on the checkerboard's rows and columns are interchangeable. 

Its `.yaml` parameters are:

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

This command converts pixel measurements to physical lengths, by calibrating with an *undistorted* `.mp4` video of checkerboards. 

Its `.yaml` parameters are:

- `real_board_squre_len`: The actual real-world length of an edge of a checkerboard square, e.g. in mm. 

- `undistorted_board` (string): Path to an _undistorted_ video of the checkerboard. Will be the output of the `undistort` command, where `do_crop` is true. 

- `framerate` (integer): Framerate of `undistorted_board` video in Hz. 

- `m_corners` (integer): Number of internal corners along the rows of the checkerboard.

- `n_corners` (integer): Number of internal corners along the columns of the checkerboard.

- `frames` (iterable of integers): Specifies the frames in which to look for checkerboards. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the `undistorted_board` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 

- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for checkerboard corners. 

This command returns the ratio of pixels to real-world units in a `pxls_to_mm.pkl` file saved in the same directory as the `undistorted_board` video. 
</details>


#### `circular-mask-crop`

<details><summary> Click for details. </summary>
<br>

This command uses a [Hough Circle Transform](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d) to find a _single_ mean circle for each undistorted video, in a directory of undistorted `.mp4` videos. The command then uses that circle to generate a mask, so that only those things inside the circle are visible. The command will also crop the video into a square, whose edge lengths are just slightly larger than the diameter of the identified circle. The typical use case is for identifying the boundaries of a circular arena from a behaviour video. The masking and cropping that is generated from the identified circle is useful for making clean videos for presentations, reducing input noise for various object trackers, and for accelerating the training of neural networks (e.g. object detection classifiers, etc.). 

Its `.yaml` parameters are:

- `root` (string): Path to the root directory; the directory that houses the target `.mp4` videos. Is recursive.

- `vid_ending` (string): The file ending of the videos to be analyzed. For example, `.mp4` or `_undistorted.mp4`. Videos without the specified file ending will be skipped. This command supports only `.mp4` video files.

- `dp` (integer): The image resolution over the accumulator resolution. See the OpenCV docs for details.

- `param1` (integer): The highest threshold of the two passed to the Canny edge detector. See OpenCV docs for details.

- `param2` (integer): The accumulator threshold for the circle centres at the detection stage. The smaller it is, the more false circles that may be detected. See OpenCV docs for details.

- `minDist` (integer): Minimum distance between the centres of the detected circles, in pixels. If the parameter is too small, multiple neighbour circles may be falsely detected, in addition to the true one. See OpenCV docs for details. 

- `minRadius` (integer): Minimum circle radius, in pixels. See OpenCV docs for details.

- `maxRadius` (integer): Maximum circle radius, in pixels. See OpenCV docs for details. 

- `frames` (iterable of integers): Specifies the frames in which to look for circles. Accepts an iterable of integers, such as a list of integers, where the integers specify the indexes of the frames in the undistorted `.mp4` video. If the length of the iterable is 0, the command will randomly draw 5 frames from the video. The default value of `frames` is `[]` (a list of length 0). 

- `do_ask` (boolean): If true, will ask the user at every step to verify that the extracted frames are suitable images in which to search for circles. 

This command returns a `.pkl` file that ends in `_circle.pkl`, for each `.mp4` video. The `.pkl` file contains the Cartesian pixel coordinates of the mean circle's center and the pixel radius of the mean circle. The command also returns videos that are both masked and cropped, based on each video's identified circle. These videos end in the `_masked.mp4` suffix.
</details>


#### `make-timelapse`

<details><summary> Click for details. </summary>
<br>

This command generates a timelapse image from a video, for one or more videos. It assumes a fixed camera position. Its `.yaml` parameters are:

- `root` (string): Path to the root video or directory. If the latter, the directory that houses the target `.mp4` videos, and is recursive.

- `vid_ending` (string): The file ending of the videos to be analyzed. For example, `.mp4` or `_undistorted.mp4`. Videos without the specified file ending will be skipped. This command supports only `.mp4` video files.

- `density` (float): Specifies the percentage of frames from which to generate the timelapse image. Must be a value between 0 and 1, where 1 selects all frames. 

- `is_dark_on_light` (boolean): Specifies whether the moving objects of interest are dark against a light background, or light against a dark background. 

This command returns an image suffixed with `_timelapse.png`, for each video.
</details>


#### `track-blobs`

<details><summary> Click for details. </summary>
<br>

This command uses OpenCV's [simple blob detector](https://docs.opencv.org/3.4/d0/d7a/classcv_1_1SimpleBlobDetector.html) and Alex Bewley's [SORT tracker](https://github.com/abewley/sort) to detect and track blobs in an undistorted video. The typical use case is for identifying the coordinate positions of a single animal in a backlit arena. This detection algorithm does poorly under complex lighting conditions, or if tracking multiple *interacting* blobs. The quality of the tracker depends highly on the quality of the detector. The tracked blob IDs may prove unnecessary, depending on your use case. 

The algorithm used for this command merits a brief explanation. First, it computes a background image, by taking the median of each pixel across ~30 frames. Then, the code draws 10 random frames from the video, and then background subtracts, and then inverts, each of the 10 sample images. The code then uses OpenCV's simple blob detector with the passed in user parameters, and a minimum threshold of 1 and a maximum threshold of 255, to identify blobs. The resulting detected blobs are not ideal, but are still fairly accurate. For this reason, the code then grabs these blobs' bounding boxes, and computes the Otsu threshold *from each of these bounding boxes*, and then calculates the mean of the Otsu thresholds; the histogram of pixel intensities within each bounding box will be very bimodal. Now that the algorithm has derived the ideal threshold value from the 10 sample images, it moves onto all the frames of the video. For each frame, it background subtracts, inverts, and then thresholds the image. It then median blurs the image to get rid of all salt and pepper noise. The blurred image is the final processed image, and is passed into the SORT tracker. 

This command's `.yaml` parameters mostly derive from OpenCV's [blob detector parameters](https://docs.opencv.org/4.5.0/d8/da7/structcv_1_1SimpleBlobDetector_1_1Params.html#addd6c9f61049769bcc301005daf21637) and Alex Bewley's [SORT tracker parameters](https://github.com/abewley/sort/blob/master/sort.py#L261-L267). 

This command's `.yaml` parameters are:

- `root` (string): Path to the root video or directory. If the latter, the directory that houses the target `_undistorted.mp4` videos, and is recursive.

- `vid_ending` (string): The file ending of the videos to be analyzed. For example, `.mp4` or `_undistorted.mp4`. Videos without the specified file ending will be skipped. This command supports only `.mp4` video files.

- `framerate` (integer): Framerate of the target video(s), in Hz.

- `do_show` (boolean): If true, will display the labelled video output stream. The blob tracking will run slower if this value is true. 

Detector parameters:

- `min_area` (float or `None`): The minimum pixel area that a blob can have. Recall that `null` in a `.yaml` file denotes `None`. 

- `max_area` (float or `None`): The maximum pixel area that a blob can have. Recall that `null` in a `.yaml` file denotes `None`. 

- `min_circularity` (float or `None`): The minimum circularity that a blob can have. E.g. a regular hexagon is more circular than a regular pentagon. Must be between 0 and 1.  Recall that `null` in a `.yaml` file denotes `None`. 

- `max_circularity` (float or `None`): The maximum circularity that a blob can have. E.g. a regular hexagon is more circular than a regular pentagon. Must be between 0 and 1.  Recall that `null` in a `.yaml` file denotes `None`. 

- `min_convexity` (float or `None`): The minimum convexity that a blob can have. Convexity is the
area of the blob divided by the blob's convex hull. Must be between 0 and 1. Recall that `null` in a `.yaml` file denotes `None`. 

- `max_convexity` (float or `None`): The maximum convexity that a blob can have. Convexity is the
area of the blob divided by the blob's convex hull. Must be between 0 and 1.  Recall that `null` in a `.yaml` file denotes `None`. 

- `min_inertia_ratio` (float or `None`): The minimum 'non-elongatedness' that a blob can have, where 
the lowest value is a line, and the highest value is a circle. Must be between 0 and 1. Recall that `null` in a `.yaml` file denotes `None`. 

- `max_inertia_ratio` (float or `None`): The maximum 'non-elongatedness' that a blob can have, where 
the lowest value is a line, and the highest value is a circle. Must be between 0 and 1.  Recall that `null` in a `.yaml` file denotes `None`. 

Tracker parameters:

- `max_age` (int): Maximum number of frames to keep a track alive, without associated detections. 

- `min_hits` (int): Minimum number of associated detections, before initializing a track. 

- `iou_thresh` (float): Minimum IOU (intersection over union) value for defining a match between the predicted and actual bounding box. 

This command returns a video of the tracked blobs, where the bounding box and ID of the blobs are labelled. The output videos are suffixed with `_blobbed.mp4`. It also returns a csv file of each blob's data for each frame. The output csv files are suffixed with `_blobbed.csv`.
</details>