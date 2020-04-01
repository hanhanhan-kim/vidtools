#!/usr/bin/env python3

"""
Convert raw .fmf videos to compressed and viewable .avi or .mp4 video files.
The .fmf video is converted to an uncompressed directory of .tiff files, \
before being compressed to the .avi or .mp4. 
"""

import skimage.io 
import tqdm
import os
import shutil
import glob
import sys
import argparse

import motmot.FlyMovieFormat.FlyMovieFormat as FMF
from ffmpy import FFmpeg


def mkdirs4tiffs (names):
    '''
    Makes an empty directory for each .fmf video. 
    
    Parameters:
    names (list): a list of the .fmf files to be converted
    
    Returns:
    Empty directories for each .fmf video. Can undo in terminal by navigating to `vid_path` and executing `rm -r */` 
    '''
    # Each directory will have the same name as the .fmf video:
    folders = []
    for name in names:
        folders.append(name.replace('.fmf',''))

    # Make the directories:
    for folder in folders:
        # Check if the directory exists already:
        isDir = os.path.isdir(folder)
        if not isDir:
            os.mkdir(os.path.join(folder))
        else:
            print("Directory already exists")
            continue


def get_FrameRate_TimeLength (names):
    '''
    Get the frame rate and length of video (secs) from a list of .fmf videos.
    
    Parameters:
    names (list): a list of the .fmf files to be converted
    
    Returns:
    Empty directories for each .fmf video. Can undo in terminal by navigating to `vid_path` and executing `rm -r */` 
    '''
    fmfs = []
    
    for name in names:
        
        # Make a list of fmf objects:
        fmfs.append(FMF.FlyMovie(name))
        
        # Get an fmf from the fmfs
        fmf = fmfs[names.index(name)]
    
        vidSize = fmf.get_n_frames()
        tmStmps = fmf.get_all_timestamps()

        timeLen = tmStmps[-1] - tmStmps[0]

        #frameRate in frames per second
        frameRate = vidSize/timeLen
    
        print(str(frameRate)+ ' is frame rate and ' + str(timeLen) + ' is length of video (s)')


def fmf2tiff (names):
    
    '''
    Converts a list of .fmf files to .tiff files so they can be converted to mp4s. Can batch process multiple .fmf videos into multiple 
    
    Parameters:
    names (list): a list of the .fmf files to be converted
    
    Returns:
    A directory of .tiff files, where each directory corresponds to an .fmf object. Can undo in terminal by navigating to `vid_path` and executing `rm -r */`
    
    '''
    
    fmfs = []
    
    for name in names:
        
        # Make a list of fmf objects:
        fmfs.append(FMF.FlyMovie(name))
        
        # Get an fmf from the fmfs:
        fmf = fmfs[names.index(name)]
        # For each fmf, convert it to a series of .tiffs and store the series in its respective directory:
        print("Converting .fmf video to .tiff files ...")
        i = 0
        for im in tqdm.tqdm(range(len(fmf.get_all_timestamps()))):
            skimage.io.imsave(arr=fmf.get_frame(i)[0], fname=name.replace('.fmf','') + '/' +
                          str(format(i, '08d')) + '.tiff')
            i += 1


def tiff2mp4 (names, save_tiffs, crf):
    
    '''
    Converts .tiffs located in a directory into an .mp4 file. Can batch process multiple directories of .tiffs into multiple respective .mp4 files.
    
    Paramters:
    names (list): a list of the .fmf files to be converted.
    save_tiffs (str): a flag to delete directories containing the input tiff files, after conversion
    crf (int): the constant rate factor for video compression, ranging from 0, the least compressed, to 51, the most compressed. 
    
    Returns:
    .mp4 files in the same directory as the .fmf files. Can undo in terminal by navigating to `vid_path` and executing `rm *.!(fmf)` 
    
    '''
    
    in_paths = []
    out_paths = []
    
    fmfs = []
    
    for name in names:
        
        # Compute the exact frame rate of each video to input into the FFmpeg conversions
        fmfs.append(FMF.FlyMovie(name))
        fmf = fmfs[names.index(name)]
        vidSize = fmf.get_n_frames()
        tmStmps = fmf.get_all_timestamps()
        timeLen = tmStmps[-1] - tmStmps[0]
        frameRate = vidSize/timeLen
        
        # FFmpeg conversions
        in_paths.append(name.replace('.fmf','/%08d.tiff'))
        out_paths.append(name.replace('.fmf','.mp4'))
        
        ff = FFmpeg(
            inputs={in_paths[names.index(name)]: '-r '+ str(frameRate)+' -f image2'},
            outputs={out_paths[names.index(name)]: '-crf ' + str(crf) + ' -pix_fmt yuv420p'} # crf 0 is most lossless compression, 51 is opposite
        )
        ff.run()

        # Remove folders containing tiffs, based on flag:
        if save_tiffs == "false":

            os.chdir(name.replace(".fmf",""))

            if all (glob.glob(name.replace(".fmf",".tiff"))) is True:
                shutil.rmtree(name.replace(".fmf",""))
                os.chdir("..")
            else:
                print("No .tiff files in this directory")
        
        else:
            print("Save .tiffs flag is true")
            continue


def tiff2avi (names, save_tiffs, crf):
    
    '''
    Converts .tiffs located in a directory into an .avi file. Can batch process multiple directories of .tiffs into multiple respective .avi files.
    
    Paramters:
    names (list): a list of the .fmf files to be converted.
    save_tiffs (str): a flag to delete directories containing the input tiff files, after conversion
    crf (int): the constant rate factor for video compression, ranging from 0, the least compressed, to 51, the most compressed. 
    
    Returns:
    .avi files in the same directory as the .fmf files. Can undo in terminal by navigating to `vid_path` and executing `rm *.!(fmf)` 
    
    '''
    
    assert (0 <= crf <= 51), "crf is not an int between 0 and 51."

    in_paths = []
    out_paths = []
    
    fmfs = []
    
    for name in names:
        
        # Compute the exact frame rate of each video to input into the FFmpeg conversions
        fmfs.append(FMF.FlyMovie(name))
        fmf = fmfs[names.index(name)]
        vidSize = fmf.get_n_frames()
        tmStmps = fmf.get_all_timestamps()
        timeLen = tmStmps[-1] - tmStmps[0]
        frameRate = vidSize/timeLen
        
        # FFmpeg conversions
        in_paths.append(name.replace('.fmf','/%08d.tiff'))
        out_paths.append(name.replace('.fmf','.avi'))
        
        ff = FFmpeg(
            inputs={in_paths[names.index(name)]: '-r '+ str(frameRate)+' -f image2'},
            outputs={out_paths[names.index(name)]: '-c:v libx264 -crf ' + str(crf) + ' -pix_fmt yuv420p'} # crf 0 is most lossless compression, 51 is opposite
        )
        ff.run()

        # Remove folders containing tiffs, based on flag:
        if save_tiffs == "false":

            os.chdir(name.replace(".fmf",""))

            if all (glob.glob(name.replace(".fmf",".tiff"))) is True:
                shutil.rmtree(name.replace(".fmf",""))
                os.chdir("..")
            else:
                print("No .tiff files in this directory")
        
        else:
            print("Remove .tiffs flag is false")
            continue


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vid_path",
        help="Absolute path to the directory that houses the .fmf videos\
            E.g.'/mnt/2TB/data_in/vids/'")
    parser.add_argument("output_type", nargs="?", default="avi",
        help="The compressed video output type. Accepts either 'avi' or 'mp4'.\
            Default is 'avi'")
    parser.add_argument("crf", nargs="?", type=int, default=0,
        help="The 'constant rate factor' for the FFmpeg conversion from uncompressed\
             .tiffs to compressed .avi or .mp4. Ranges from 0 to 51, where 0 is most\
             lossless and 51 is most compressed. Default is 0.")
    parser.add_argument("-t","--tiffs", action="store_true", default=False,
        help="If enabled, a directory of uncompressed .tiffs from\
            the .fmf file is retained. Default is false.")
    args = parser.parse_args()

    vid_path = args.vid_path
    output_type = args.output_type
    crf = args.crf
    save_tiffs = args.tiffs

    # vid_path = sys.argv[1]
    # # If all arguments are specified, use them:
    # if len(sys.argv) >= 5:

    #     # Specify save_tiffs flag and output type:
    #     save_tiffs = sys.argv[2].lower()
    #     output_type = sys.argv[3].lower()
    #     crf = str(sys.argv[4])
    
    # # If not all arguments are specified, use these defaults:
    # else:
    #     save_tiffs = "false"
    #     output_type = "avi"
    #     crf = 0
        
    # Get the list of .fmf files to be converted:
    if vid_path.endswith("/"):
        names = sorted(glob.glob(vid_path + "*.fmf"))
    else:
        names = sorted(glob.glob(vid_path + "/*.fmf"))

    assert (names), \
        f"The directory, {vid_path}, is empty. Are you sure you specified a directory?"

    # Convert:
    mkdirs4tiffs(names)
    get_FrameRate_TimeLength(names)
    fmf2tiff(names)

    # Convert to either .mp4 or .avi:
    if output_type == "mp4":
        tiff2mp4(names, save_tiffs, crf)
    elif output_type == "avi":
        tiff2avi(names, save_tiffs, crf)


if __name__ == "__main__":
    main()