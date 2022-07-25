0. Set all targets up and run sample_videos.py. wait 5 seconds and start shooting to targets. once all targets are down wait anohter 5 seconds and press ctrl+c to stop the program. This script will produce samle video called, output.mp4

1. run sample_frames.py to get targets_down and targets_up frames
    you may need to pay with frame number to get down positions

2. run bbox.py to draw bounding boxes around targets
    For standing targets only

3. call count_nonzero_pixels.py to set threshold for white pixels for every bbox when targets are up and down
    Note: this will require paying wiht the size of window in adaptiveThreshold (second to the last parameter) and medianBlur and kernel size of dilate functions
    always rerun count_non_zero_pixels.py each time you modified bounding boxes

4. run region.py and draw bounding boxes around platform that contain targets

5. run main.py



