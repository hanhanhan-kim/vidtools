import motmot.FlyMovieFormat.FlyMovieFormat as FMF
import skimage.io 
import tqdm
import os
import glob
from ffmpy import FFmpeg

# Specify the absolute path that has the .fmf files:
vid_path = '/data2/HK20190516/top/'

# Get the list of .fmf files to be converted:
names = sorted(glob.glob(vid_path + '*.fmf'))


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
        os.mkdir(os.path.join(folder))


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
        i = 0
        for im in tqdm.tqdm_notebook(range(len(fmf.get_all_timestamps()))):
            skimage.io.imsave(arr=fmf.get_frame(i)[0], fname=name.replace('.fmf','') + '/' +
                          str(format(i, '08d')) + '.tiff')
            i += 1


def tiff2mp4 (names):
    '''
    Converts .tiffs located in a directory into an .mp4 file. Can batch process multiple directories of .tiffs into multiple respective .mp4 files.
    
    Paramters:
    names (list): a list of the .fmf files to be converted.
    
    Returns:
    .mp4 files in the same directory as the .fmf files. Can undo in terminal by navigating to `vid_path` and executing `rm *.!(fmf)` 
    
    '''
    
    inPaths = []
    outPaths = []
    
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
        inPaths.append(name.replace('.fmf','/%08d.tiff'))
        outPaths.append(name.replace('.fmf','.mp4'))
        
        ff = FFmpeg(
            inputs={inPaths[names.index(name)]: '-r '+ str(frameRate)+' -f image2'},
            outputs={outPaths[names.index(name)]: '-crf 25 -pix_fmt yuv420p'}
        )
        ff.run()

