import cv2 as cv
import mediapipe as mp
import random
import csv

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands



def write_to_databse(data):
    with open('database.csv',mode='a',newline='') as database:
        Rock = data['Rock']
        Paper = data['Paper']
        Scissors = data['Scissors']
        csv_writer = csv.writer(database, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([Rock,Paper,Scissors])

data = {"Rock": 0,
        "Paper": 0,
        "Scissors": 0}
def get_hand_marks(hand_landmarks):
    landmarks = hand_landmarks.landmark
    if all([landmarks[i].y < landmarks[i+3].y for i in range(5,20,4)]):
        data["Rock"]+=1
        write_to_databse(data)
        return "Rock"
    elif landmarks[13].y < landmarks[16].y and landmarks[9].y>landmarks[12].y and landmarks[5].y>landmarks[8].y:
          data["Scissors"]+=1
          write_to_databse(data)
          return "Scissors"
    else:
        data["Paper"]+=1
        write_to_databse(data)
        return "Paper"
    


vid = cv.VideoCapture(0,cv.CAP_DSHOW)
vid.set(cv.CAP_PROP_FRAME_WIDTH, 1080)
vid.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

clock = 0

p1_move = p2_move = None
game_text = ""
success = True
NPC_list = ['Scissors','Paper','Rock']


with mp_hands.Hands(model_complexity=0,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = vid.read()
        if not ret or frame is None: break
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(frame)

        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame,
                                          hand_landmarks,
                                          mp_hands.HAND_CONNECTIONS,
                                          mp_drawing_styles.get_default_hand_landmarks_style(),
                                          mp_drawing_styles.get_default_hand_connections_style())
        frame = cv.flip(frame,1)

        if 0 <= clock<20:
            success = True
            game_text = "Ready?"
        elif clock < 30: game_text = "3..."
        elif clock < 40: game_text = "2..."
        elif clock < 50: game_text = "1..."
        elif clock < 65: game_text = "GO!"
        elif clock == 65:
            hls = results.multi_hand_landmarks
            if hls:
                print(hls)
                p1_move = get_hand_marks(hls[0])
                p2_move = random.choice(NPC_list)
            else:
                success = False
        elif clock < 100:
            if success:
                game_text = f"Player 1 showed {p1_move}. Computer showed {p2_move}."
                if p1_move == "Paper" and p2_move=="Rock":
                    game_text = f"{game_text} Player 1 wins"
                elif p1_move == "Rock" and p2_move=="Scissors":
                    game_text = f"{game_text} Player 1 wins" 
                elif p1_move == "Scissors" and p2_move=="Paper":
                    game_text = f"{game_text} Player 1 wins"
                elif p1_move == p2_move:
                    game_text = f"{game_text} Game Tied"
                else:
                    game_text = f"{game_text} Computer wins"

            else:
                game_text = 'Didn\'t play properly!'

        cv.putText(frame, f'Clock: {clock}',(50,50),cv.FONT_HERSHEY_PLAIN, 2,(0,255,255), 2, cv.LINE_AA)
        cv.putText(frame, game_text,(50,80),cv.FONT_HERSHEY_PLAIN, 2,(0,255,255), 2, cv.LINE_AA)
        clock = (clock + 1) % 100
        if p2_move:
            icon = cv.imread(f"{p2_move}.png")
            icon = cv.resize(icon, (400, 400))
            frame[100:500, 100:500] = icon

        cv.imshow('frame',frame)

        if cv.waitKey(1) & 0xFF == ord('q'): break
vid.release()
cv.destroyAllWindows


