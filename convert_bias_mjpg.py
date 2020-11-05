#!/usr/bin/env python3

"""
This script was originally written by Will Dickson. 
I since modified it to enable batch processing, and for use with argparse.

Batch convert .mjpg colour videos captured in BIAS (IOrodeo) into compressed \
and viewable .avi video files. 

This script requires both the index.txt file and its corresponding .mjpg \
image stack file. The index file MUST be called 'index.txt'.

Only one index.txt file and its corresponding .mjpg image stack should be present \
in a given directory.

N.B. This script cannot convert to the true acquisition frame rate for videos \
captured at speeds greater than 65 Hz. If captured at 65+ Hz, convert the video
to a slower speed, then speed it up afterwards. An example shell script is provided
in this directory. 
"""

import cv2
import numpy as np
import argparse
import glob
import os
from os.path import join, split, splitext


def read_indexfile(indexfile):
    with open(indexfile,'r') as f:
        raw_line_list = f.readlines()
    index_list = []
    for raw_line in raw_line_list:
        tmp = raw_line.split(' ')
        item = {
                'frame': int(tmp[0]), 
                'timestamp': float(tmp[1]), 
                'start_pos': int(tmp[2]), 
                'end_pos': int(tmp[3]),
                }
        index_list.append(item)
    return index_list


def get_framerate(index_list, num_avg=10):
    """ Get framerate .. average over first 10 frames"""
    f_list= []
    num_avg = min(num_avg,len(index_list))
    for i in range(1,num_avg):
        t1 = index_list[i]['timestamp']
        t0 = index_list[i-1]['timestamp']
        dt = t1 - t0
        try:
            f = 1/dt
            f_list.append(f)
        except:
            pass
    f_array = np.array(f_list)
    f_mean = f_array.mean()
    return f_mean


def convert_bias_mjpg(bias_indexfile, bias_moviefile, outfile, scale=1.0):
    index_list = read_indexfile(bias_indexfile)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    framerate = get_framerate(index_list) # can hardcode here if greater than 65 Hz
    vid = None
    print(bias_moviefile)
    # import ipdb; ipdb.set_trace()
    with open(bias_moviefile,'rb') as f:
        for i, index_item in enumerate(index_list):
            # Extract frame from file
            print('frame: {}, timestamp: {:1.2f}'.format(index_item['frame'],index_item['timestamp'])) 
            f.seek(index_item['start_pos'])
            data = f.read(index_item['end_pos'] - index_item['start_pos']+1)
            img = cv2.imdecode(np.fromstring(data,dtype=np.uint8),-1)
            (n,m,k) = img.shape
            n_scaled = int(scale*n)
            m_scaled = int(scale*m)
            img_scaled = cv2.resize(img,(m_scaled,n_scaled))
            if vid is None:
                vid = cv2.VideoWriter(outfile, fourcc, framerate, (m_scaled,n_scaled))
            cv2.imshow('frame',img_scaled)
            vid.write(img_scaled)
            key = cv2.waitKey(1) & 0xff
            if key == ord('q'):
                break
            

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root",
        help="Absolute path to the root directory. I.e. the outermost folder\
             that houses the index.txt and .mjpg image stack file.")
    parser.add_argument("nesting", type=int,
        help="Specifies the number of folders that are nested from the root\
            directory. I.e. the number of folders between root and the subdirectory\
            that houses the index.txt and .mjpg image stack file.")
    parser.add_argument("scale", type=float, nargs="?", default=1.0,
        help="The scale of the video to be converted, relative to the raw input.\
            The default value is 1.0.")
    args = parser.parse_args()

    root = args.root
    nesting = args.nesting
    scale = args.scale

    folders = sorted(glob.glob(join(root, nesting * "*/")))
    for folder in folders:

        indexfile = glob.glob(join(folder, "index.txt"))
        moviefile = glob.glob(join(folder, "*.mjpg"))

        assert indexfile,\
            f"The folder, {folder}, has no index.txt files."
        assert len(indexfile)==1,\
            f"The folder, {folder}, must have exactly 1 index.txt file."
        assert moviefile,\
            f"The folder, {folder}, has no .mjpg image stacks."
        assert len(moviefile)==1,\
            f"The folder, {folder}, must have exactly 1 .mjpg file"

        outfile_base, _ = splitext(moviefile[0])
        outfile = f"{outfile_base}.avi"

        convert_bias_mjpg(indexfile[0], moviefile[0], outfile, scale)
        

if __name__ == '__main__':
    main()