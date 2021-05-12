"""
Batch convert .h264 files to .mp4.
Can output the .mp4 file in monochrome. 
Will not overwrite existing videos. 
"""

import subprocess
from os.path import splitext, expanduser, basename
from pathlib import Path

import cv2


# Formatted for click; config is a dict loaded from yaml:
def main(config):

    root = expanduser(config["h264_to_mp4"]["root"])
    framerate = str(config["h264_to_mp4"]["framerate"])
    do_mono = config["h264_to_mp4"]["do_mono"]

    vids = [str(path.absolute()) for path in Path(root).rglob("*.h264")]

    if len(vids) == 0:
        raise ValueError("No '.h264' videos were found.")

    for vid in vids:
        
        print(f"Processing {vid} ...")
        output_vid = f"{splitext(vid)[0]}.mp4"

        if Path(output_vid).is_file():

            print(f"{basename(output_vid)} already exists. Skipping ...")

        else:

            if not do_mono:
                    
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
                                      frameSize=(int(cap.get(3)), int(cap.get(4))), 
                                      params=None)

                while cap.isOpened():

                    ret, frame = cap.read()

                    if ret:

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