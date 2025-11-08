"""
Touchless Computer Control
--------------------------
Control your computer using hand gestures detected by MediaPipe Hands + PyAutoGUI.
This file is imported as a module by server.py.
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" 
import cv2
import mediapipe as mp
import pyautogui
import time
import os
import numpy as np
from collections import deque

# ---------------- Configuration ----------------
COOLDOWN_SECONDS = 0.8  # seconds between gestures
SCROLL_AMOUNT = 400      # pixels per scroll
APP_PATH = r"C:\Users\Public\Desktop\Google Chrome.lnk"  

# Finger landmark IDs
TIP_IDS = {"thumb": 4, "index": 8, "middle": 12, "ring": 16, "pinky": 20}
PIP_IDS = {"thumb": 3, "index": 6, "middle": 10, "ring": 14, "pinky": 18}

# ---------------- MediaPipe Initialization (Global) ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_drawing = mp.solutions.drawing_utils

# Map internal gesture names to UI names (for HTML UI)
GESTURE_UI_MAP = {
    "palm": "Palm (All Fingers)",
    "fist": "Fist (No Fingers)",
    "thumbs_up": "Thumbs Up",
    "two_fingers": "Two Fingers (Index+Middle)",
    "one_finger": "One Finger (Index)",
    "index_thumb": "Index + Thumb",
    "three_fingers": "Three Fingers (Index+Middle+Ring)"
}

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
    if status["index"] and status["middle"] and status["ring"] and not status["thumb"] and not status["pinky"]:
        return "three_fingers"
    return None


# ---------------- Gesture Smoothing ----------------
class GestureSmoother:
    """Smooth out noisy gesture detection."""
    def __init__(self, window=7):  # ✅ FIXED: Proper double underscores
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

    action_taken = False
    if gesture == "palm":
        pyautogui.hotkey("alt", "tab")
        print("[ACTION] Switch App")
        action_taken = True
    elif gesture == "fist":
        pyautogui.press("space")
        print("[ACTION] Play/Pause")
        action_taken = True
    elif gesture == "thumbs_up":
        pyautogui.hotkey("win", "d")
        print("[ACTION] Show Desktop")
        action_taken = True
    elif gesture == "two_fingers":
        pyautogui.scroll(-SCROLL_AMOUNT)
        print("[ACTION] Scroll Down")
        action_taken = True
    elif gesture == "one_finger":
        pyautogui.scroll(SCROLL_AMOUNT)
        print("[ACTION] Scroll Up")
        action_taken = True
    elif gesture == "index_thumb":
        pyautogui.hscroll(SCROLL_AMOUNT)
        print("[ACTION] Scroll Right")
        action_taken = True
    elif gesture == "three_fingers":
        try:
            os.startfile(APP_PATH)
            print(f"[ACTION] Opened App: {APP_PATH}")
        except Exception as e:
            print("[ERROR] Could not open app:", e)
        action_taken = True

    if action_taken:
        last_action_time = now
    return action_taken


# ---------------- Main Function (Called by server.py) ----------------
def get_gesture(frame):
    """
    Main function called by server.py.
    Takes a single OpenCV frame, processes it, performs an action,
    and returns the detected gesture name for the UI.
    """
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    result = hands.process(rgb)

    gesture_label = None
    ui_gesture_name = None

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        handedness_label = (
            result.multi_handedness[0].classification[0].label
            if result.multi_handedness else "Right"
        )

        status = fingers_status(hand_landmarks, handedness_label)
        gesture_label = smoother.add(gesture_from_status(status))

    if gesture_label:
        perform_action(gesture_label)
        ui_gesture_name = GESTURE_UI_MAP.get(gesture_label)

    return ui_gesture_name
