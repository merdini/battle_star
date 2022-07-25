import cvzone
import cv2
import pandas as pd

from region import Region
from count_nonzero_pixels import apply_adaptive_threshold
from player import Player

counter = 0
current_frame = None
players_list = []


def main(source):
  global current_frame, players_list
  try:
      df = pd.read_csv(f"region_positions.csv")
      region_list = df[["region_no", "x1", "y1", "x2", "y2"]].values.tolist()
  except:
      print("run region.py before this")

  for region in region_list:
      players_list.append(Player(Region(region[1:])))

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
    if frame_no % 5 != 0:
      frame_no += 1
      continue
    current_frame = img.copy()
    img_dilated = apply_adaptive_threshold(img, "", write_img=False)
    for player in players_list:
      player.check_targets(img_dilated, img)
      cvzone.putTextRect(img, f'{player}: {player.shot_this_session}', (player.region.x1, 50), scale=3,
                      thickness=5, offset=20, colorR=(0,200,0))
    
    pick_winner(players_list, img)
    cv2.imshow("Title of Popup Window", img)
    frame_no += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break


def renew_session(event, x, y, flags, param):
    global counter, players_list, current_frame
    counter += 1
    if flags == cv2.EVENT_FLAG_RBUTTON + cv2.EVENT_FLAG_SHIFTKEY:
      for player in players_list:
        print('resetting session', counter)
        cvzone.putTextRect(current_frame, 'Session is Renewed', (600, 700), scale=5,
                          thickness=5, offset=20, colorR=(0,0,255))
        cv2.imshow("Title of Popup Window", current_frame)
        cv2.waitKey(500)
        player.reset_shot_this_session()
      

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
  else:
    winner = "Tie between Player 1, Player 2 and Player 3"
  
  cvzone.putTextRect(img, f'Winner: {winner}', (100, 1000), scale=3,
                        thickness=5, offset=20, colorR=(0,200,0))
  return winner


if __name__ == "__main__":
    main(source=1)