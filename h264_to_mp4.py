#!/usr/bin/env python3

"""
Batch convert .h264 files to .mp4.
Can output the .mp4 file in monochrome.  
"""

import subprocess
import argparse
from os.path import splitext, expanduser, basename
from pathlib import Path

import cv2


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", 
        help="Path to the root directory.")
    parser.add_argument("framerate", nargs="?", default=30,
        help="Framerate (int)")
    parser.add_argument("-m","--mono", action="store_true",
        help="Convert colour videos to monochrome with OpenCV")
    args = parser.parse_args()

    root = expanduser(args.root)
    framerate = str(args.framerate)
    mono = args.mono
    vids = [str(path.absolute()) for path in Path(root).rglob("*.h264")]

    for vid in vids:
        
        print(f"Processing {vid} ...")
        output_vid = f"{splitext(vid)[0]}.mp4"

        if Path(output_vid).is_file():

            print(f"{basename(output_vid)} already exists. Skipping ...")

        else:

            if not mono:
                    
                # Convert:
                args = ["ffmpeg", "-framerate", framerate, "-i", vid, "-c", "copy", output_vid]
                equivalent_cmd = " ".join(args)

                print(f"running command {equivalent_cmd} from {root}")
                subprocess.run(args, cwd=root)
            
            else:

                cap = cv2.VideoCapture(vid)

                # Define the codec and create VideoWriter object
                fourcc = cv2.VideoWriter_fourcc(*"mp4v") 
                out = cv2.VideoWriter(filename=output_vid, 
                                      apiPreference=0, 
                                      fourcc=fourcc, 
                                      fps=int(framerate), 
                                      frameSize=(1920,1080), # TODO: make this a kwarg?
                                      params=None)

                while (cap.isOpened()):

                    ret, frame = cap.read()

                    if ret == True:

                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # In OpenCV, images saved to video file must be three channels:
                        re_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                        # Save:
                        out.write(re_bgr)
                        # Provide live stream:
                        cv2.imshow(f"converting {basename(output_vid)} to monochrome ...", re_bgr)

                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                    
                    else:
                        break
                
                cap.release()
                out.release()
                cv2.destroyAllWindows()

    print("Conversions complete!")            

            
if __name__ == "__main__":
    main()