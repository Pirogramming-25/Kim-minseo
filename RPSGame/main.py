import math
import time

import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python import vision

from visualization import draw_manual, print_RSP_result


MODEL_PATH = "hand_landmarker.task"


def calculate_distance(point1, point2):
    return math.sqrt(
        (point1.x - point2.x) ** 2
        + (point1.y - point2.y) ** 2
        + (point1.z - point2.z) ** 2
    )


def is_finger_open(hand_landmarks, tip_idx, pip_idx):

    wrist = hand_landmarks[0]
    tip = hand_landmarks[tip_idx]
    pip = hand_landmarks[pip_idx]

    tip_distance = calculate_distance(wrist, tip)
    pip_distance = calculate_distance(wrist, pip)

    return tip_distance > pip_distance


def recognize_rps(hand_landmarks):
    index_open = is_finger_open(hand_landmarks, 8, 6)
    middle_open = is_finger_open(hand_landmarks, 12, 10)
    ring_open = is_finger_open(hand_landmarks, 16, 14)
    pinky_open = is_finger_open(hand_landmarks, 20, 18)

    finger_states = [
        index_open,
        middle_open,
        ring_open,
        pinky_open,
    ]

    open_count = sum(finger_states)

    if open_count == 0:
        return 0

    if open_count == 4:
        return 1

    if (
        index_open
        and middle_open
        and not ring_open
        and not pinky_open
    ):
        return 2

    return None


def main():
    base_options = mp.tasks.BaseOptions(
        model_asset_path=MODEL_PATH
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        start_time = time.time()

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Can't receive frame. Exiting...")
                break

            # 거울처럼 보이도록 좌우 반전
            frame = cv.flip(frame, 1)

            # OpenCV의 BGR 이미지를 RGB로 변환
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame,
            )

            timestamp_ms = int((time.time() - start_time) * 1000)

            detection_result = landmarker.detect_for_video(
                mp_image,
                timestamp_ms,
            )

            rps_result = None

            if detection_result.hand_landmarks:
                hand_landmarks = detection_result.hand_landmarks[0]
                rps_result = recognize_rps(hand_landmarks)

            frame = draw_manual(frame, detection_result)
            frame = print_RSP_result(frame, rps_result)

            cv.imshow("Rock Paper Scissors", frame)

            if cv.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()