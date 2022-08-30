import cvzone
import cv2
import pandas as pd
import numpy as np
import datetime
from region import Region
from count_nonzero_pixels import apply_adaptive_threshold
from player import Player
import pyautogui
from params import width, height

screen_width, screen_height= pyautogui.size()

counter = 0
current_frame = None
players_list = []

try:
  all_time_record = pd.read_csv(f"all_time_records.csv")
  month = datetime.datetime.today().month
  monthly_records = pd.read_csv(f"{month}_monthly_records.csv")
except:
  all_time_record = pd.DataFrame(columns=['name', 'shot', 'time'])
  monthly_records = pd.DataFrame(columns=['name', 'shot', 'time'])

all_time_record.sort_values(by=['shot', 'time'], inplace=True, ascending=[False, True], ignore_index=True)
monthly_records.sort_values(by=['shot', 'time'], inplace=True, ascending=[False, True], ignore_index=True)

def main(source, dev=False):
  global current_frame, players_list
  # bg = np.zeros([screen_height, screen_width])
  # bg.fill(255)
  bg = cv2.imread('webb.jpg')
  bg = cv2.resize(bg, (screen_width, screen_height))
  try:
    df = pd.read_csv(f"region_positions.csv")
    region_list = df[["region_no", "x1", "y1", "x2", "y2"]].values.tolist()
  except:
    print("run region.py before this")


  color = (0, 0, 255)
  cvzone.putTextRect(bg, f"All time best shooters", (screen_width // 2 -300, 50), scale=3, thickness=3, offset=0, colorR=color)
  for idx, rows in all_time_record.iterrows():
    if idx > 9:
      break
    x1 = screen_width // 2 -300
    y1 = idx  *  50 + 50
    x2 = x1 + 700
    y2 = y1 + 50
    
    # cv2.rectangle(bg, (x1, y1), (x2, y2), color, 2)
    cvzone.putTextRect(bg, f"{rows['name']}: {rows['shot']} {rows['time']} sec", (x1, y2-3), scale=3, thickness=3, 
    offset=0, colorR=(0,255,0))

  cvzone.putTextRect(bg, f"This month best shooters", (screen_width//2 + 350, 50), scale=3, thickness=3, offset=0, colorR=color)
  for idx, rows in monthly_records.iterrows():
    if idx > 9:
      break
    x1 = screen_width // 2 + 350
    y1 = idx  *  50 + 50
    x2 = x1 + 700
    y2 = y1 + 50
    
    # cv2.rectangle(bg, (x1, y1), (x2, y2), color, 2)
    cvzone.putTextRect(bg, f"{rows['name']}: {rows['shot']} {rows['time']} sec", (x1, y2-3), scale=3, thickness=3, 
    offset=0, colorR=(0,255,0))

  for region in region_list:
      players_list.append(Player(Region(region[1:])))

  num_player = len(players_list) 
  if source == 0:
    cap = cv2.VideoCapture(0)
  elif source == 1:
    cap = cv2.VideoCapture('output.mp4')

  if (cap.isOpened()== False): 
    print("Error opening video stream or file")

  cv2.namedWindow(winname= "Title of Popup Window")
  cv2.setMouseCallback("Title of Popup Window", renew_session)

  frame_no = 1
  while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
      cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    _, img = cap.read()
    img = cv2.resize(img, (width, height))
    print(frame_no)
    if frame_no % 5 != 0:
      frame_no += 1
      continue
    current_frame = img.copy()
    img_dilated = apply_adaptive_threshold(img, "", write_img=False)
    for idx, player in enumerate(players_list):
      player.check_targets(img_dilated, img)
      if dev:
        frame = img
        text_region_x = player.region.x1
        text_region_y = 50
        scale = 2
        time_text_region_y = text_region_y+50
      else:
        frame = bg
        text_region_x = 0
        text_region_y = int(idx * (screen_height / num_player) + (screen_height / num_player)/2)
        time_text_region_y = text_region_y+70
        scale = 5
      if player.end_time:
        elapsed_time = (player.end_time - player.start_time)
      else:
        elapsed_time = 0
      cvzone.putTextRect(frame, f'{player}: {player.shot_this_session}', (text_region_x, text_region_y), scale=scale,
                      thickness=5, offset=20, colorR=(255,153,51))
      cvzone.putTextRect(frame, f'Time: {elapsed_time:.2f} sec', (text_region_x, time_text_region_y), scale=scale,
      thickness=5, offset=20, colorR=(255,153,51))
    
    pick_winner(players_list, img)
    if dev:
      cv2.imshow("Title of Popup Window", img)
    else:
      cv2.imshow("Title of Popup Window", bg)
    frame_no += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break


def renew_session(event, x, y, flags, param):
    global counter, players_list, current_frame
    empty_frame = np.zeros([screen_height, screen_width])
    empty_frame.fill(255)
    counter += 1
    
    if flags == cv2.EVENT_FLAG_RBUTTON + cv2.EVENT_FLAG_SHIFTKEY:
      

      for player in players_list:
        print('resetting session', counter)
        player.reset_shot_this_session()
      
      cv2.namedWindow(winname= "Renew Session")
      cvzone.putTextRect(empty_frame, 'Session is Renewed', (600, 700), scale=5,
                            thickness=5, offset=20, colorR=(0,0,255))
      cv2.imshow("Renew Session", empty_frame)
      cv2.waitKey(5000)
      cv2.destroyWindow("Renew Session")
      update_all_time_records(players_list)
      update_monthly_time_records(players_list)
      
def update_all_time_records():
  pass
  

def update_monthly_time_records():
  pass


def pick_winner(players, img):   
  if players[0].shot_this_session > players[1].shot_this_session and players[0].shot_this_session > players[1].shot_this_session:
    winner = "Player 1"
  elif players[1].shot_this_session > players[2].shot_this_session and players[1].shot_this_session > players[0].shot_this_session:
    winner = "Player 2"
  elif players[2].shot_this_session > players[0].shot_this_session and players[2].shot_this_session > players[1].shot_this_session:
    winner = "Player 3"
  elif players[0].shot_this_session == players[1].shot_this_session and players[0].shot_this_session > players[2].shot_this_session:
    winner = "Tie between Player 1 and Player 2"
  elif players[0].shot_this_session == players[2].shot_this_session and players[0].shot_this_session > players[1].shot_this_session:
    winner = "Tie between Player 1 and Player 3"
  elif players[1].shot_this_session > players[2].shot_this_session and players[1].shot_this_session > players[0].shot_this_session:
    winner = "Tie between Player 2 and Player 3"
  
  elif players[0].shot_this_session == players[1].shot_this_session == players[2].shot_this_session == 0:
    return
  else:
    winner = "Tie between Player 1, Player 2 and Player 3"
  
  cvzone.putTextRect(img, f'Winner: {winner}', (100, img.shape[0]-100), scale=2,
                        thickness=5, offset=20, colorR=(0,200,0))
  return winner


if __name__ == "__main__":
    main(source=0, dev=False)