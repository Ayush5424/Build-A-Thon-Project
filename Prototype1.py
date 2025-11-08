"""
Touchless Computer Control
--------------------------
Control your computer using hand gestures detected by MediaPipe Hands + PyAutoGUI.

Gestures:
✋ Palm (all fingers extended)      -> Next App (Alt + Tab)
✊ Fist (no fingers extended)       -> Play/Pause (Space)
👍 Thumb Up                        -> Show Desktop (Win + D)
✌ Two Fingers (Index + Middle)     -> Scroll Down
☝ One Finger (Index only)          -> Scroll Up
👉 Index + Thumb                   -> Scroll Right
👈 Index + Thumb (Left variant)    -> Scroll Left
🤟 Three Fingers (Index + Middle + Ring) -> Open Custom App

Press 'q' to quit.
"""

import cv2
import mediapipe as mp
import pyautogui
import time
import os
from collections import deque

# ---------------- Configuration ----------------
CAM_ID = 0
FRAME_WIDTH, FRAME_HEIGHT = 1280, 720
COOLDOWN_SECONDS = 0.8  # seconds between gestures
SCROLL_AMOUNT = 400      # pixels per scroll
SHOW_OVERLAY = True
APP_PATH = r"C:\Windows\System32\napp.exe"  # change this to your desired app path

# Finger landmark IDs
TIP_IDS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
PIP_IDS = {"thumb": 3, "index": 6, "middle": 10, "ring": 14, "pinky": 18}

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# ---------------- Helper Functions ----------------
def fingers_status(hand_landmarks, handedness_label):
    """Return dict of which fingers are extended."""
    status = {}
    tips = {n: hand_landmarks.landmark[i] for n, i in TIP_IDS.items()}
    pips = {n: hand_landmarks.landmark[i] for n, i in PIP_IDS.items()}

    # For fingers except thumb
    for f in ("index", "middle", "ring", "pinky"):
        status[f] = tips[f].y < pips[f].y - 0.02

    # For thumb
    thumb_tip = tips["thumb"]
    thumb_ip = hand_landmarks.landmark[3]
    if handedness_label == "Right":
        status["thumb"] = thumb_tip.x > thumb_ip.x + 0.02
    else:
        status["thumb"] = thumb_tip.x < thumb_ip.x - 0.02
    return status


def gesture_from_status(status):
    """Return gesture label string based on finger states."""
    if all(status.values()):
        return "palm"
    if not any(status.values()):
        return "fist"
    if status["thumb"] and not any(status[f] for f in ("index", "middle", "ring", "pinky")):
        return "thumbs_up"
    if status["index"] and status["middle"] and not status["ring"] and not status["pinky"]:
        return "two_fingers"
    if status["index"] and not any(status[f] for f in ("middle", "ring", "pinky")):
        return "one_finger"
    if status["index"] and status["thumb"] and not any(status[f] for f in ("middle", "ring", "pinky")):
        return "index_thumb"
    # New: three fingers (index + middle + ring)
    if status["index"] and status["middle"] and status["ring"] and not status["thumb"] and not status["pinky"]:
        return "three_fingers"
    return None


class GestureSmoother:
    """Smooth out noisy gesture detection."""
    def __init__(self, window=7):
        self.deque = deque(maxlen=window)

    def add(self, g):
        self.deque.append(g)
        freq = {}
        for x in self.deque:
            if x:
                freq[x] = freq.get(x, 0) + 1
        if not freq:
            return None
        return max(freq.items(), key=lambda kv: kv[1])[0]


# ---------------- Action Mapping ----------------
last_action_time = 0
smoother = GestureSmoother(window=7)

def perform_action(gesture):
    """Perform real system action for given gesture."""
    global last_action_time
    now = time.time()
    if not gesture or now - last_action_time < COOLDOWN_SECONDS:
        return False

    # Gesture mapping
    if gesture == "palm":
        pyautogui.hotkey("alt", "tab")       # Switch app
        print("[ACTION] Switch App")
    elif gesture == "fist":
        pyautogui.press("space")             # Play/pause
        print("[ACTION] Play/Pause")
    elif gesture == "thumbs_up":
        pyautogui.hotkey("win", "d")         # Show desktop
        print("[ACTION] Show Desktop")
    elif gesture == "two_fingers":
        pyautogui.scroll(-SCROLL_AMOUNT)     # Scroll down
        print("[ACTION] Scroll Down")
    elif gesture == "one_finger":
        pyautogui.scroll(SCROLL_AMOUNT)      # Scroll up
        print("[ACTION] Scroll Up")
    elif gesture == "index_thumb":
        pyautogui.hscroll(SCROLL_AMOUNT)     # Scroll right
        print("[ACTION] Scroll Right")
    elif gesture == "three_fingers":
        try:
            os.startfile(APP_PATH)           # Open chosen app
            print(f"[ACTION] Opened App: {APP_PATH}")
        except Exception as e:
            print("[ERROR] Could not open app:", e)

    last_action_time = now
    return True


# ---------------- Main Loop ----------------
def main():
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    hands = mp_hands.Hands(max_num_hands=1,
                           min_detection_confidence=0.6,
                           min_tracking_confidence=0.6)

    print("🚀 Touchless Control Active! Press 'q' to quit.")
    print("Ensure the window you want to control is active.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            gesture_label = None

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                handedness_label = (
                    result.multi_handedness[0].classification[0].label
                    if result.multi_handedness else "Right"
                )

                status = fingers_status(hand_landmarks, handedness_label)
                gesture_label = smoother.add(gesture_from_status(status))

                if SHOW_OVERLAY:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    y0 = 30
                    for i, (k, v) in enumerate(status.items()):
                        color = (0, 255, 0) if v else (0, 0, 255)
                        cv2.putText(frame, f"{k}:{int(v)}", (10, y0 + i * 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Perform action
            if gesture_label:
                perform_action(gesture_label)

            # Overlay gesture
            if SHOW_OVERLAY:
                text = f"Gesture: {gesture_label or '-'}"
                cv2.putText(frame, text, (10, FRAME_HEIGHT - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            cv2.imshow("Touchless Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()


if __name__ == "__main__":
    main()
