#!/home/hank-x299/anaconda3/envs/cinema/bin/python

# Written by Will Dickson

from __future__ import print_function
import os
import sys
import cv2
import numpy as np


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
    framerate = get_framerate(index_list) 
    vid = None
    with open(bias_moviefile,'rb') as f:
        for i, index_item in enumerate(index_list):
            # Extract frame from file
            print('frame: {}, timestap: {:1.2f}'.format(index_item['frame'],index_item['timestamp'])) 
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
            

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    indexfile = sys.argv[1]
    moviefile = sys.argv[2]
    if len(sys.argv) >= 4:
        scale = float(sys.argv[3])
    else:
        scale = 1.0
    basename, extname = os.path.splitext(moviefile)
    outfile = '{}_converted.{}'.format(basename, 'avi')
    convert_bias_mjpg(indexfile, moviefile, outfile, scale=scale)


