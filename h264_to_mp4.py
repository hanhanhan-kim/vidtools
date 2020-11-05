#!/usr/bin/env python3

"""
Batch convert .h264 files to .mp4.
Can output the .mp4 file in monochrome.  
"""

import subprocess
import glob
from os.path import join, splitext, expanduser
import argparse


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", 
        help="Absolute path to the root directory.")
    parser.add_argument("framerate", nargs="?", default=30,
        help="Framerate (int)")
    args = parser.parse_args()

    root = expanduser(args.root)
    framerate = str(args.framerate)
    vids = sorted(glob.glob(join(root, "*.h264")))

    for vid in vids:

        output_vid = f"{splitext(vid)[0]}.mp4"
            
        # Convert:
        args = ["ffmpeg", "-framerate", framerate, "-i", vid, "-c", "copy", output_vid]
        equivalent_cmd = f"ffmpeg -framerate {framerate} -i {vid} -c copy {output_vid}"

        print(f"running command {equivalent_cmd} from dir {root}")
        subprocess.run(args, cwd=root)

if __name__ == "__main__":
    main()