#!/usr/bin/env python3

"""
Record monochrome .h264 vids with raspivid on Raspberry Pi. 
Can record timestamps.  
"""

import subprocess   
import argparse
from datetime import datetime


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", 
        help="Name of output file. If outputting multiple file types, only the extension will differ.")
    parser.add_argument("secs", 
        help="Duration of recorded video in seconds.")
    parser.add_argument("-ts", "--timestamp", action="store_true",
        help="Outputs a text file of the timestamps and frame numbers") 
    args = parser.parse_args()
    
    name = args.name + f"_{datetime.now().strftime('%Y-%m-%d')}"
    millisecs = float(args.secs) * 1000 # Raspivid takes ms 
    timestamp= args.timestamp

    # Convert:
    if timestamp:

        args = ["raspivid", "-o", f"{name}.h264", "-t", f"{millisecs}", "-cfx", "128:128", "-pts", f"{name}.txt"] 
        equivalent_cmd = " ".join(args)
        print(f"running command: {equivalent_cmd}")     
        subprocess.run(args) 

    else:   

        args = ["raspivid", "-o", f"{name}.h264", "-t", f"{millisecs}", "-cfx", "128:128"] 
        equivalent_cmd = " ".join(args)
        print(f"running command: {equivalent_cmd}")
        subprocess.run(args) 


if __name__ == "__main__":
    main()