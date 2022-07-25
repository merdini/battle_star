# Python program to illustrate
# saving an operated video

# organize imports
import numpy as np
import cv2

def get_sample_video2():
    cap = cv2.VideoCapture(0)

    _, frame = cap.read()
    width  = int(cap.get(3)) # float
    height = int(cap.get(4)) # float

    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MP4V'))    

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('output_test2.mp4', fourcc, 20.0, (width,height))



    while(True):
        ret, frame = cap.read()
        # frame = cv2.rotate(frame, cv2.ROTATE_180)

        out.write(frame)
        # cv2.imshow('frame', frame)
        c = cv2.waitKey(1)
        if c & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def get_sample_video():
    cap = cv2.VideoCapture(0)
    _, frame = cap.read()
    width  = int(cap.get(3)) # float
    height = int(cap.get(4)) # float

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('output.mp4', fourcc, 10.0, (width,height))



    while(True):
        ret, frame = cap.read()
        # frame = cv2.rotate(frame, cv2.ROTATE_180)

        out.write(frame)
        cv2.imshow('frame', frame)
        c = cv2.waitKey(1)
        if c & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    get_sample_video()
