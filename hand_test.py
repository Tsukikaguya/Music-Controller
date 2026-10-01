import cv2
import mediapipe as mp
import time
import math

from pycaw.pycaw import AudioUtilities
from pynput.keyboard import Controller, Key

# Model Path
MODEL_PATH = r"C:\Users\User\OneDrive\Desktop\MUSIC_G\hand_landmarker.task"

# ==========================
# Windows Control
# ==========================
devices = AudioUtilities.GetSpeakers()

volume_control = devices.EndpointVolume

keyboard = Controller()

# ==========================
# MediaPipe Setup
# ==========================
BaseOptions = mp.tasks.BaseOptions

HandLandmarker = mp.tasks.vision.HandLandmarker

HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=RunningMode.VIDEO,

    num_hands=2,

    min_hand_detection_confidence=0.6,

    min_hand_presence_confidence=0.6,

    min_tracking_confidence=0.6

)

detector = HandLandmarker.create_from_options(options)

# ==========================
# State
# ==========================
action_enabled = False
volume_enabled = False

# 防止連續觸發
last_action = ""
last_action_time = 0


# 模式切換時間
mode_change_time = 0
action_start_time = 0
volume_start_time = 0


# 音量平滑
filtered_volume = 0.5

# 左手 Swipe 記錄
previous_left_index_x = None

# ==========================
# Hand Label Stability
# ==========================
stable_labels = []
candidate_labels = []
candidate_counts = []

# ==========================
# Basic Function
# ==========================
def distance(p1,p2):

    return math.sqrt(

        (p1.x-p2.x)**2 +

        (p1.y-p2.y)**2

    )



def map_volume(d):

    min_d = 0.03
    max_d = 0.25


    d=max(

        min_d,
        min(max_d,d)

    )


    return (

        (d-min_d)

        /

        (max_d-min_d)

    )


# ==========================
# Gesture Detection
# ==========================
def detect_ok(hand):

    """
    OK gesture
    Thumb + index close
    Other fingers open
    """

    pinch = distance(

        hand[4],

        hand[8]

    )


    middle = hand[12].y < hand[10].y

    ring = hand[16].y < hand[14].y

    pinky = hand[20].y < hand[18].y

    return (

        pinch < 0.06

        and middle

        and ring

        and pinky

    )



def detect_open_palm(hand):

    count = 0

    tips=[8,12,16,20]

    joints=[6,10,14,18]


    for tip,joint in zip(tips,joints):

        if hand[tip].y < hand[joint].y:

            count += 1

    return count == 4



def detect_fist(hand):

    count = 0

    tips=[8,12,16,20]

    joints=[6,10,14,18]

    for tip,joint in zip(tips,joints):

        if hand[tip].y < hand[joint].y:

            count += 1

    return count == 0




def detect_left_swipe(hand):

    global previous_left_index_x

    current_x = hand[8].x

    action = None

    if previous_left_index_x is not None:

        dx = current_x - previous_left_index_x


        if dx > 0.20:

            action = "NEXT"

        elif dx < -0.20:

            action = "PREVIOUS"

    previous_left_index_x = current_x

    return action


def get_stable_hand_label(index, raw_label):
    """
    左右手穩定判斷：
    必須連續 3 幀判成不同的手，
    才真正切換左右手。
    """

    global stable_labels
    global candidate_labels
    global candidate_counts

    # 如果目前是第一次看到這隻手
    while len(stable_labels) <= index:
        stable_labels.append(None)
        candidate_labels.append(None)
        candidate_counts.append(0)

    # 第一次建立
    if stable_labels[index] is None:

        stable_labels[index] = raw_label
        candidate_labels[index] = raw_label
        candidate_counts[index] = 0

        return raw_label

    # 和目前穩定結果一樣
    if raw_label == stable_labels[index]:

        candidate_labels[index] = raw_label
        candidate_counts[index] = 0

        return stable_labels[index]

    # 出現不同的手
    if raw_label == candidate_labels[index]:

        candidate_counts[index] += 1

    else:

        candidate_labels[index] = raw_label
        candidate_counts[index] = 1

    # 連續 3 幀才切換
    if candidate_counts[index] >= 3:

        stable_labels[index] = raw_label

        candidate_labels[index] = raw_label

        candidate_counts[index] = 0

    return stable_labels[index]


# ==========================
# Trigger Control
# ==========================
def trigger(action):

    global last_action,last_action_time

    now=time.time()

    if (

        action != last_action

        or now-last_action_time > 2

    ):

        last_action = action

        last_action_time = now

        return True


    return False



def can_change_mode():

    global mode_change_time

    now=time.time()

    if now-mode_change_time >= 2:

        mode_change_time = now

        return True

    return False


# ==========================
# Camera
# ==========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("Camera error")

    exit()


# ==========================
# Main Loop
# ==========================
while True:

    ret, frame = cap.read()


    if not ret:

        break


    # 鏡像

    frame = cv2.flip(frame,1)

    h,w,_ = frame.shape

    rgb = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2RGB

    )


    mp_image = mp.Image(

        image_format=mp.ImageFormat.SRGB,

        data=rgb

    )


    result = detector.detect_for_video(

        mp_image,

        int(time.time()*1000)

    )


    status = ""


    if result.hand_landmarks:


        for i,hand in enumerate(result.hand_landmarks):


            # ======================
            # 修正左右手
            # ======================
            raw_label = result.handedness[i][0].category_name

            # MediaPipe 左右手修正

            if raw_label == "Left":

                corrected_label = "Right"

            else:

                corrected_label = "Left"


            # 左右手穩定判斷
            label = get_stable_hand_label(
                 i,
                   corrected_label
                )

            y_text = 100 + i*60


            cv2.putText(

                frame,

                label,

                (30,y_text),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (255,0,0),

                2

            )




            # ==================================================
            # 左手
            # ==================================================
            if label == "Left":

                # --------------------------
                # 左手握拳 = ACTION 開關
                # --------------------------
                if detect_fist(hand):


                    if can_change_mode():


                        action_enabled = not action_enabled


                        # 模式互斥

                        if action_enabled:

                            volume_enabled = False



                    status = (

                        "ACTION ON"

                        if action_enabled

                        else

                        "ACTION LOCK"

                    )


                else:

                    # --------------------------
                    # VOLUME 模式
                    # --------------------------
                    if volume_enabled:

                        pinch_distance = distance(

                            hand[4],

                            hand[8]

                        )

                        # 只有 pinch 才調音量
                        if pinch_distance < 0.25:

                            target = map_volume(

                                pinch_distance

                            )

                            alpha = 0.2


                            filtered_volume = (

                                alpha*target

                                +

                                (1-alpha)*filtered_volume

                            )


                            volume_control.SetMasterVolumeLevelScalar(

                                filtered_volume,

                                None

                            )


                            status = (

                                f"Volume "

                                f"{int(filtered_volume*100)}%"

                            )


                    # --------------------------
                    # ACTION 模式切歌
                    # --------------------------

                    elif action_enabled:

                        swipe = detect_left_swipe(hand)

                        if swipe == "NEXT":


                            keyboard.press(

                                Key.media_next

                            )

                            keyboard.release(

                                Key.media_next

                            )


                            status="NEXT SONG"


                        elif swipe == "PREVIOUS":


                            keyboard.press(

                                Key.media_previous

                            )

                            keyboard.release(

                                Key.media_previous

                            )


                            status="PREVIOUS SONG"



            # ==================================================
            # 右手
            # ==================================================
            elif label == "Right":

                # --------------------------
                # OK = VOLUME 開關
                # --------------------------
                if detect_ok(hand):


                    if can_change_mode():


                        volume_enabled = not volume_enabled


                        # 模式互斥

                        if volume_enabled:

                            action_enabled = False


                    status = (

                        "VOLUME ON"

                        if volume_enabled

                        else

                        "VOLUME LOCK"

                    )


                # --------------------------
                # ACTION 播放控制
                # --------------------------
                elif action_enabled:

                    if detect_open_palm(hand):


                        if trigger("PLAY"):


                            keyboard.press(

                                Key.media_play_pause

                            )


                            keyboard.release(

                                Key.media_play_pause

                            )


                        status="PLAY / PAUSE"

            # ==================================================
            # Draw landmarks
            # ==================================================
            for p in hand:


                cv2.circle(

                    frame,

                    (

                        int(p.x*w),

                        int(p.y*h)

                    ),

                    5,

                    (0,255,0),

                    -1

                )


    # ==========================
    # UI
    # ==========================
    action_text = (

        "ACTION ON"

        if action_enabled

        else

        "ACTION LOCK"

    )

    volume_text = (

        "VOLUME ON"

        if volume_enabled

        else

        "VOLUME LOCK"

    )

    cv2.putText(

        frame,

        action_text,

        (30,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0,255,0) if action_enabled else (0,0,255),

        2

    )


    cv2.putText(

        frame,

        volume_text,

        (30,75),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0,255,0) if volume_enabled else (0,0,255),

        2

    )


    cv2.putText(

        frame,

        status,

        (30,220),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        (0,255,255),

        2

    )


    cv2.imshow(

        "AIR DJ",

        frame

    )


    key = cv2.waitKey(10)&0xff


    if key == ord("q"):

        break


# ==========================
# Close
# ==========================
cap.release()

cv2.destroyAllWindows()

detector.close()

print("Finished")