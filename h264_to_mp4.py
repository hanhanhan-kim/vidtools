#!/usr/bin/env python3

"""
Batch convert .h264 files to .mp4.
Can output an additional monochrome .mp4. 
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
    parser.add_argument("-m", "--mono", action="store_true",
        help="Convert to monochrome")
    args = parser.parse_args()

    root = expanduser(args.root)
    framerate = str(args.framerate)
    mono = args.mono
    vids = sorted(glob.glob(join(root, "*.h264")))

    for vid in vids:

        output_vid = f"{splitext(vid)[0]}.mp4"

        # Convert:
        args = ["ffmpeg", "-framerate", framerate, "-i", vid, "-c", "copy", output_vid]
        equivalent_cmd = f"ffmpeg -framerate {framerate} -i {vid} -c copy {output_vid}"

        print(f"running command {equivalent_cmd} from dir {root}")
        subprocess.run(args, cwd=root)

        if mono:
            
            # TODO: Find better way, this command tanks the vid quality: 

            mono_vid = f"{splitext(vid)[0]}_mono.mp4"

            args = ["ffmpeg", "-i", output_vid, "-vf", "hue=s=0", mono_vid]
            equivalent_cmd = f"ffmpeg -i {output_vid} -vf hue=s=0 {mono_vid}"

            print(f"running command {equivalent_cmd} from dir {root}")
            subprocess.run(args, cwd=root) 

        else:
            pass

if __name__ == "__main__":
    main()