import pandas as pd
import cv2
import cvzone
from params import cam_pos

position_list = []
counter = 1 

def get_all_targets():
    # idx_list = []
    df = pd.read_csv("vid_target_positions.csv")
    return df


def draw_regions_with_drag(event, x, y,flags, param):
    global ix, iy, counter, position_list
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        position_list.append((counter, ix, iy, x, y))
        counter += 1
    
    elif event == cv2.EVENT_RBUTTONDOWN:
            for i, pos, in enumerate(position_list):
                _, x1, y1, x2, y2 = pos
                if x1 < x < x2 and y1 < y < y2:
                    position_list.pop(i)
                    counter -= 1

    df = pd.DataFrame(columns=["region_no", "x1", "y1", "x2", "y2"], data=position_list)
    df.sort_values(by='x1', inplace=True)
    df["region_no"] = range(1, df.shape[0]+1)
    df.to_csv("region_positions.csv", index=False)


class Region:
    def __init__(self, box) -> None:
        self.x1 = box[0]
        self.y1 = box[1]
        self.x2 = box[2]
        self.y2 = box[3]

    
    def get_target_coordinates_in_region(self):
        idx_list = []
        df = get_all_targets()
        for idx, rows in df.iterrows():
            x1, y1, x2, y2 = rows[["x1", "y1", "x2", "y2"]]
            if self.x1 < x1 < self.x2:
                idx_list.append(idx)
        return df.loc[idx_list]

def draw_regions(position_list, draw_regions_with_drag):
    cv2.namedWindow(winname= "Title of Popup Window")
    cv2.setMouseCallback("Title of Popup Window", draw_regions_with_drag)
    while True:
        img = cv2.imread(f'targets_up.jpg')
        for c, *pos in position_list:
                x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
                cv2.rectangle(img, (pos[0], pos[1]), (pos[2], pos[3]) , (0, 0, 255), 1)
                cvzone.putTextRect(img, str(c), (pos[0], pos[1] - 3), scale=1.7,
                            thickness=3, offset=0, colorR=(0, 200,0))
        
        cv2.imshow("Title of Popup Window", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        df = pd.read_csv(f"region_positions.csv")
        position_list = df[["region_no", "x1", "y1", "x2", "y2"]].values.tolist()
        counter = df.index[-1] + 2
    except:
        position_list = []
    draw_regions(position_list, draw_regions_with_drag)