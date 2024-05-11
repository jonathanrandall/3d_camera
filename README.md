# 3d_camera
3d_camera code and data

## Direcotry and Files Description:
- __frames_out__ : this directory contains the raw stereo images and the left and right stereo images that have been split up and trimmed so the size matches the time of flight training data.
- __autoencoder_v3.ipynb__: this file is the file I used to implement the convoluitonal neural network, that takes as input stereo pairs and outputs a disparity image.
- __extract_frames.ipynb__: extracts frames from video data.
- __prep_process.ipynb__: looking at the impact of medial filters on the time of flight data which is noisy.
- __my_model__*: This are the keras models, which I can load into the notebook if I don't want to retraing the model.
- __recored_video.pyy__: This is the pythong code that runs on the raspberry pi for capturing the stereo pair and ground truth time of flight images
- __requirements.txt__: these are the requirements for my environment.
