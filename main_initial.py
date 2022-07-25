import cv2
import cvzone
import numpy as np
import pandas as pd
from count_nonzero_pixels import apply_adaptive_threshold
from params import cam_pos

df = pd.read_csv(f"vid_target_positions_{cam_pos}.csv")


def check_target_status(imgPro):
    spaceCounter = 0

    for idx, rows in df.iterrows():
        x1, y1, x2, y2, up_cnt, down_cnt = rows[["x1", "y1", "x2", "y2", "up_nonzero_cnt", "down_nonzero_cnt"]]
        imgCrop = imgPro[y1:y2, x1:x2]
        # cv2.imshow(str(x1 * y1), imgCrop)
        # cv2.waitKey(10)
        nonzero_count = cv2.countNonZero(imgCrop)
        threshold = (up_cnt + down_cnt) // 2
        if up_cnt > down_cnt:
            sign = '>'
        else:
            sign = '<'

        if eval(f'{nonzero_count} {sign} {threshold}'):
            color = (0, 255, 0)
            thickness = 2
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        cvzone.putTextRect(img, str(nonzero_count), (x1, y1 - 3), scale=0.8,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{df.shape[0]}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))

def process_single_frame(checkParkingSpace):
    img = cv2.imread('base_img.jpg')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    # cv2.imwrite("predictions.jpeg", img)
    cv2.waitKey(10000)
    key = cv2.waitKey(1)
    if key == ord('q'):
        cv2.destroyAllWindows()
        exit(1)   

# process_single_frame(checkParkingSpace)

cap = cv2.VideoCapture(f'output.mp4')
if (cap.isOpened()== False): 
  print("Error opening video stream or file")
frame_no = 1
while True:
    print(frame_no, cv2.CAP_PROP_POS_FRAMES, cv2.CAP_PROP_FRAME_COUNT)
    if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) == int(cap.get(cv2.CAP_PROP_FRAME_COUNT)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    if frame_no < 700:
        frame_no += 1
        continue

    imgDilate = apply_adaptive_threshold(img, "", write_img=False)
    check_target_status(imgDilate)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    # cv2.imshow("ImageThres", imgMedian)
    cv2.waitKey(1)
    frame_no += 1
    


