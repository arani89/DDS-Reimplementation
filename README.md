# DDS

## Introduction
This repository contains codes for the [paper]((https://people.cs.uchicago.edu/~junchenj/docs/DDS-Sigcomm20.pdf)) "Server-Driven Video Streaming for Deep Learning Inference", published at SIGCOMM ’20.  
DDS is a video streaming system that permits aggressive compression/pruning of pixels not relevant to achieving high DNN inference accuracy. It advocates that the video streaming protocol should be driven by real-time feedback from the server-side DNN. DDS continuously sends a low-quality video stream to the server; the server runs the DNN to determine where to re-send with higher quality to increase the inference accuracy.

## Directory Structure
```
└── input                     : input videos for DDS
|
└── media
|   ├── first_pass_input      : processed video as input for first pass of DDS
|   ├── frame_crops           : crops of frames of objects required in second pass of DDS
|   ├── processed_frames      : processed frames used to compile input video for second pass of DDS
|   ├── raw_files             : raw files of input video
|   ├── raw_frames            : raw frames of input video
|   ├── second_pass_input     : processed video as input for second pass of DDS
|
└── results                   : results of yolov5 run on processed videos
|
└── yolov5                    : yolov5 model
|
└── run.ipynb                 : DDS implementation (driver code)
```