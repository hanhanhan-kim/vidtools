#!/usr/bin/env python3

"""
Use Hough Circle Transform to find circles in an image. 
Typical use case is for identifying the boundaries of a circular arena. 
"""

import argparse
from os.path import expanduser, dirname, join
from os import path
from pathlib import Path
import pickle

import yaml
import numpy as np
import cv2

from common import ask_yes_no

