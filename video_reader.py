import cv2
import cvzone
import numpy as np
import pandas as pd
from count_nonzero_pixels import apply_adaptive_threshold

cam_pos = 'mid'

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(f'output_{cam_pos}.mp4')

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

frame_no = 0
# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  print(frame_no)
  if ret:
    # Display the resulting frame
    # cv2.imshow('Frame',frame)
    if frame_no == 10:
      cv2.imwrite(f'targets_up_{cam_pos}.jpg', frame)
    elif frame_no == 840:
      cv2.imwrite(f'targets_down_{cam_pos}.jpg', frame)
    # Press Q on keyboard to  exit
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #   break

  # Break the loop
  else: 
    break
  frame_no += 1

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()