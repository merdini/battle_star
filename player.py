import cvzone
import cv2
import pandas as pd
import time

from region import Region
from count_nonzero_pixels import apply_adaptive_threshold


class Player:
  counter = 0
  def __init__(self, region) -> None:
      self.region = region
      self.targets = self.region.get_target_coordinates_in_region()
      self.region_mid_point = self.mid_point()

      self.shot_this_session = 0
      self.up_targets_this_frame = 0
      self.down_targets_this_frame = 0
      self.completed_times = 0
      Player.counter += 1
      self.no = Player.counter
      self.is_all_down = False
      self.completed_times = 0 
      self.start_time = None
      self.end_time = None
      self.pause = False
    
  
  def update_is_down_status(self):
    self.targets['is_down'] = False
    
  def reset_shot_this_session(self):
    self.completed_times = 0
    self.targets["is_down"] = False
    self.start_time = None
    self.end_time = None
  
  def update_shot_this_session(self):
    self.shot_this_session = self.completed_times * 30 + self.targets["is_down"].sum()

  def update_completed_times(self):
    self.completed_times += 1
  
  def mid_point(self):
    min_x = self.targets['x1'].min()
    max_x = self.targets['x2'].min()

    return (min_x + max_x) // 2

  def __repr__(self) -> str:
      return f'Player {self.no}'

  def count_up_targets(self, dilated_img):
          self.up_targets_this_frame = 0
          for idx, rows in self.targets.iterrows():
              x1, y1, x2, y2, up_cnt, down_cnt = rows[["x1", "y1", "x2", "y2", "up_nonzero_cnt", "down_nonzero_cnt"]]
              img_crop = dilated_img[y1:y2, x1:x2]
              nonzero_count = cv2.countNonZero(img_crop)
              threshold = (up_cnt + down_cnt) // 2 
              if up_cnt > down_cnt:
                  sign = '>'
                  threshold -= 10
              else:
                  sign = '<'
                  threshold += 10

              if eval(f'{nonzero_count} {sign} {threshold}'):
                  self.up_targets_this_frame += 1


  def check_targets(self, dilated_img, img, draw=True):
    self.up_targets_this_frame = 0
    self.down_targets_this_frame = 0
    if self.pause and self.tick < 200:
      self.tick += 1
      return
    if not self.is_all_down:  
      for idx, rows in self.targets.iterrows():
        x1, y1, x2, y2, up_cnt, down_cnt = rows[["x1", "y1", "x2", "y2", "up_nonzero_cnt", "down_nonzero_cnt"]]
        img_crop = dilated_img[y1:y2, x1:x2]
        nonzero_count = cv2.countNonZero(img_crop)
        
        if not rows["is_down"]:
          threshold = (up_cnt + down_cnt) // 2 - 10
          if up_cnt > down_cnt:
              sign = '>'
              threshold -= 10
          else:
              sign = '<'
              threshold += 10

          if eval(f'{nonzero_count} {sign} {threshold}'):
            self.up_targets_this_frame += 1
            color = (0, 255, 0)
            thickness = 1
          else:
            self.down_targets_this_frame += 1
            self.targets.at[idx, "is_down"] = True
            color = (0, 0, 255)
            thickness = 1

            if self.start_time:
              self.end_time = time.time()

          self.update_shot_this_session()
          if not self.start_time and self.shot_this_session == 1:
            self.start_time = time.time()
          if self.targets["is_down"].sum() > 0 and self.targets["is_down"].sum() % 30 == 0:
            self.is_all_down = True
            
            self.update_completed_times()
        else:
          color = (0, 0, 255)
          thickness = 1 

        if draw:
          cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
          cvzone.putTextRect(img, str(nonzero_count), (x1, y1 - 3), scale=0.8, thickness=thickness, offset=0, colorR=color)

          # cvzone.putTextRect(img, f'{self}: {self.shot_this_session}', (self.region.x1, 50), scale=3,
          #             thickness=5, offset=20, colorR=(0,200,0))
    else:
      self.count_up_targets(dilated_img)
    # TODO: repalce value 20 with 30
    if self.is_all_down and self.up_targets_this_frame == 30:  
      self.is_all_down = False
      self.targets["is_down"] = False
      self.pause = True
      self.tick = 0
    
    


if __name__ == "__main__":
    try:
          df = pd.read_csv(f"region_positions.csv")
          region_list = df[["region_no", "x1", "y1", "x2", "y2"]].values.tolist()
    except:
          print("run region.py before this")
    
    players_list = []
    for region in region_list:
      players_list.append(Player(Region(region[1:])))

    cap = cv2.VideoCapture('output.mp4')
    
    if (cap.isOpened()== False): 
      print("Error opening video stream or file")

    cv2.namedWindow(winname= "Title of Popup Window")
    cv2.setMouseCallback("Title of Popup Window", renew_session)

    frame_no = 1
    while True:
      # print(frame_no)
      # if frame_no > 790:
      #   print()
      if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
      success, img = cap.read()
      if frame_no % 10 != 0:
        frame_no += 1
        continue
      img_dilated = apply_adaptive_threshold(img, "", write_img=False)
      for player in players_list:
          player.check_targets(img_dilated, img)
      
      pick_winner(players_list)

      cv2.imshow("Title of Popup Window", img)
      frame_no += 1
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

