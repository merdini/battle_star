from asyncio.streams import FlowControlMixin
import cv2
import pandas as pd
import numpy as np
from params import cam_pos
from params import width, height




def apply_adaptive_threshold(img, pos, write_img=True):
    # img = cv2.resize(img,(0,0), img, 1.2, 1.2)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_threshold = cv2.adaptiveThreshold(img_blur, 255, 
                                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 
                                            3, 5)
    img_median = cv2.medianBlur(img_threshold, 1)
    kernel = np.ones((3, 3), np.uint8)
    img_dilate = cv2.dilate(img_median, kernel, iterations=1)
    if write_img:
        cv2.imwrite(f"dilated_targets_{pos}.jpg", img_dilate)
        cv2.imwrite(f"img_median_{pos}.jpg", img_median)
        cv2.imwrite(f"img_threshold_targets_{pos}.jpg", img_threshold)
    return img_dilate


def create_target_position_df(position_list):
    box_list = []
    for c, *pos in position_list:
        x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
        box_list.append([c, x1, y1, x2, y2])

    df = pd.DataFrame(columns=["box_num", "x1", "y1", "x2", "y2"], data=box_list)
    return df

def img_nonzero_pixels(img, df, new_col_name):
    nonzero_list = []
    for idx, rows in df.iterrows():
        x1, y1, x2, y2 = rows[["x1", "y1", "x2", "y2"]]
        nonzero = count_nonzero_pixels(img, x1, y1, x2, y2)
        if column_name == "up_nonzero_cnt":
            df.loc[idx, new_col_name] = nonzero if nonzero < df.loc[idx, new_col_name] else df.loc[idx, new_col_name]
        elif column_name == "down_nonzero_cnt":
            df.loc[idx, new_col_name] = nonzero if nonzero > df.loc[idx, new_col_name] else df.loc[idx, new_col_name]

def count_nonzero_pixels(img, x1,y1,x2,y2):
    img_crop = img[y1:y2, x1:x2]
    num_nonzero = cv2.countNonZero(img_crop)
    return num_nonzero


def count_zero_pixels(img, x1,y1,x2,y2):
    img_crop = img[y1:y2, x1:x2]
    totaL_pixels = np.size(img_crop)
    num_nonzero = cv2.countNonZero(img_crop)
    zero_pix = totaL_pixels - num_nonzero
    return zero_pix


def get_nonzero_pixel_thresholds(df, img, column_name):
    

    img_dilated = apply_adaptive_threshold(img, "up", True)
    
    img_nonzero_pixels(img_dilated, df, column_name)


    # df["diff"] = df["up_nonzero_cnt"] - df["down_nonzero_cnt"]
    df["box_num"] = range(1, df.shape[0]+1)
    



if __name__ == "__main__":
    df = pd.read_csv(f"vid_target_positions.csv", dtype='Int16')
    df["up_nonzero_cnt"] = float('Inf')
    df["down_nonzero_cnt"] = float('-Inf')
    last_frame_no = 100
    cap = cv2.VideoCapture('output.mp4')
    total_frames = (cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_no = 0
    while True:
        _, img = cap.read()
        frame_no += 1
        print(frame_no)
        if frame_no < 100:
            cv2.imwrite(f'targets_up.jpg', img)
        elif frame_no > total_frames - 100:
            cv2.imwrite(f'targets_down.jpg', img)
        
        if frame_no < 10:
            column_name = "up_nonzero_cnt"
        elif 1720 < frame_no < 1780:
            column_name = "down_nonzero_cnt"
        elif frame_no > 1780:
            break
        else:
            continue
        img = cv2.resize(img, (width, height))
        get_nonzero_pixel_thresholds(df, img, column_name)

    df["diff"] = df["up_nonzero_cnt"] - df["down_nonzero_cnt"]
    df["box_num"] = range(1, df.shape[0]+1)
    df["is_down"] = False
    df["abs_diff"] = abs(df["diff"])
    df.sort_values('abs_diff', inplace=True)
    df.to_csv(f"vid_target_positions.csv", index=False)