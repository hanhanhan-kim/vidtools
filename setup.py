from setuptools import setup, find_packages

with open("README.md","r") as fh:
    long_description = fh.read()

setup(
    name="vidtools",
    version="0.0.0",
    author="Han Kim",
    author_email="hankim@caltech.edu",
    description="Scripts for pre-processing videos from machine vision cameras.",
    long_description=long_description,
    url="https://github.com/hanhanhan-kim/vidtools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    entry_points={
        "console_scripts": ["vidtools=vidtools.vidtools:cli"]
    },
    install_requires=[
        "numpy",
        "scikit-image",
        "pyyaml",
        "tqdm",
        "click",
        "motmot.FlyMovieFormat",
        "ffmpy" # TODO: replace with ffmpeg-python
    ]

)