import cv2
import cvzone
import numpy as np
import pandas as pd
import csv

from count_nonzero_pixels import apply_adaptive_threshold
from count_nonzero_pixels import count_nonzero_pixels


# variables
ix = -1
iy = -1
drawing = False
position_list = []
counter = 1 

def check_targets(dilated_img, img, up_cnt, down_cnt, x1, y1, x2, y2, draw=True):
        img_crop = dilated_img[y1:y2, x1:x2]
        nonzero_count = cv2.countNonZero(img_crop)

        threshold = (up_cnt + down_cnt) // 2
        if up_cnt > down_cnt:
            sign = '>'
        else:
            sign = '<'

        if eval(f'{nonzero_count} {sign} {threshold}'):
            color = (0, 255, 0)
            thickness = 1
        else:
            color = (0, 0, 255)
            thickness = 1

        if draw:
          cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
          cvzone.putTextRect(img, str(nonzero_count), (x1, y1 - 3), scale=0.8, thickness=thickness, offset=0, colorR=color)


def count_nonzero_pixels(img, x1,y1,x2,y2):
    img_crop = img[y1:y2, x1:x2]
    num_nonzero = cv2.countNonZero(img_crop)
    return num_nonzero


def draw_reactangle_with_drag(event, x, y, flags, param):
    global ix, iy, img, counter
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y


    # elif event == cv2.EVENT_MOUSEMOVE:
    #     if drawing == True:
    #         cv2.rectangle(img, pt1=(ix,iy), pt2=(x, y),color=(255,0,0),thickness=-1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        position_list.append([counter, ix, iy, x, y])
        counter += 1
        
        # cv2.rectangle(img, pt1=(ix,iy), pt2=(x, y),color=(0,0,255),thickness=2)
    
    elif event == cv2.EVENT_RBUTTONDOWN:
            for i, pos, in enumerate(position_list):
                _, x1, y1, x2, y2 = pos
                if x1 < x < x2 and y1 < y < y2:
                    position_list.pop(i)
                    counter -= 1


    with open(f'vid_target_positions.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["box_num", "x1", "y1", "x2", "y2"])
        position_list.sort(key=lambda x: x[1])
        idx = 0
        for pos in position_list:
            idx += 1
            pos[0] = idx
        csvwriter.writerows(position_list)




    

def draw_images(position_list, img_up, img_down, img_up_thresh, img_down_thresh):
    for c, *pos in position_list:
            x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
            up_cnt = count_nonzero_pixels(img_up_thresh, x1, y1, x2, y2)
            down_cnt = count_nonzero_pixels(img_down_thresh, x1, y1, x2, y2)

            # cv2.rectangle(img_up, (pos[0], pos[1]), (pos[2], pos[3]) , (255, 255, 255), 1)
            # cvzone.putTextRect(img_up, str(c), (pos[0], pos[1] - 3), scale=0.7,
            #                 thickness=1, offset=0, colorR=(0, 200,0))

            # cv2.rectangle(img_down, (pos[0], pos[1]), (pos[2], pos[3]) , (255, 255, 255), 1)
            # cvzone.putTextRect(img_down, str(c), (pos[0], pos[1] - 3), scale=0.7,
            #                 thickness=1, offset=0, colorR=(0, 200,0))

            check_targets(img_up_thresh, img_up, up_cnt, down_cnt, x1, y1, x2, y2, draw=True)
            check_targets(img_down_thresh, img_down, up_cnt, down_cnt, x1, y1, x2, y2, draw=True)

            cv2.rectangle(img_up_thresh, (pos[0], pos[1]), (pos[2], pos[3]) , (255, 255, 255), 1)
            cvzone.putTextRect(img_up_thresh, str(c), (pos[0], pos[1] - 3), scale=0.7,
                            thickness=1, offset=0, colorR=(0, 200,0))

            cv2.rectangle(img_down_thresh, (pos[0], pos[1]), (pos[2], pos[3]) , (255, 255, 255), 1)
            cvzone.putTextRect(img_down_thresh, str(c), (pos[0], pos[1] - 3), scale=0.7,
                            thickness=1, offset=0, colorR=(0, 200,0))

if __name__ == "__main__":
    try:
        df = pd.read_csv(f"bounding_box.csv")
        position_list = df[["box_num", "x1", "y1", "x2", "y2"]].values.tolist()
        counter = df.index[-1] + 2
    except:
        position_list = []

    cv2.namedWindow(winname= "Targets up")
    cv2.setMouseCallback("Targets up", draw_reactangle_with_drag)

    while True:
        img_up = cv2.imread(f'bounding_box.jpg')
        # img_up = apply_adaptive_threshold(img_up, "", write_img=False)
        img_down = cv2.imread(f'targets_down.jpg')
        img_up_thresh = apply_adaptive_threshold(img_up, "", write_img=False)
        img_down_thresh = apply_adaptive_threshold(img_down, "", write_img=False)
        draw_images(position_list, img_up, img_down, img_up_thresh, img_down_thresh)
        
        cv2.imshow("Targets up", img_up)
        cv2.imshow("Targets Down", img_down)
        cv2.imshow("Targets up threshold", img_up_thresh)
        cv2.imshow("Targets Down threshold", img_down_thresh)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()
