import cv2
import cvzone
import numpy as np
import pandas as pd
from params import width, height


def get_target_up_and_down_frames():
    cap = cv2.VideoCapture(f'output.mp4')
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    total_frames = (cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        frame = cv2.resize(frame, (width, height))
        print(frame_no)
        if ret:
            if frame_no == 50:
                cv2.imwrite(f'targets_up.jpg', frame)
            elif frame_no == total_frames - 20:
                cv2.imwrite(f'targets_down.jpg', frame)
            # Press Q on keyboard to  exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
              break
        # Break the loop
        else: 
            break


    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == "__main__":
    get_target_up_and_down_frames()