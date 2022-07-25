import cv2
import cvzone
import numpy as np
import pandas as pd
import csv


# variables
ix = -1
iy = -1
drawing = False
position_list = []
counter = 1 


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


    # df = pd.DataFrame(columns=["box_num", "x1", "y1", "x2", "y2"], data=position_list)
    # df.to_csv("vid_target_positions.csv", index=False)

    with open(f'vid_target_positions.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(["box_num", "x1", "y1", "x2", "y2"])
        position_list.sort(key=lambda x: x[1])
        idx = 0
        for pos in position_list:
            idx += 1
            pos[0] = idx
        csvwriter.writerows(position_list)




if __name__ == "__main__":
    try:
        df = pd.read_csv(f"vid_target_positions.csv")
        position_list = df[["box_num", "x1", "y1", "x2", "y2"]].values.tolist()
        counter = df.index[-1] + 2
    except:
        position_list = []

    cv2.namedWindow(winname= "Title of Popup Window")
    cv2.setMouseCallback("Title of Popup Window", draw_reactangle_with_drag)

    # img = cv2.imread('targets_up.jpg')
    while True:
        img = cv2.imread(f'targets_up.jpg')
        for c, *pos in position_list:
                x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
                cv2.rectangle(img, (pos[0], pos[1]), (pos[2], pos[3]) , (0, 0, 255), 1)
                cvzone.putTextRect(img, str(c), (pos[0], pos[1] - 3), scale=0.7,
                            thickness=1, offset=0, colorR=(0, 200,0))
        
        cv2.imshow("Title of Popup Window", img)
        if cv2.waitKey(10) == 27:
            # df = pd.DataFrame(columns=["box_num", "x1", "y1", "x2", "y2"], data=position_list)
            # df.to_csv("vid_target_positions.csv", index=False)
            break
    cv2.destroyAllWindows()
