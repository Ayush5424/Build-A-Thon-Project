# 🖐️ Touchless Computer Control 

Control your computer without touching the mouse or keyboard!  
This project uses MediaPipe Hands + OpenCV + WebSockets + PyAutoGUI  
to recognize hand gestures in real time and perform system actions like scrolling, switching apps, or showing the desktop.

# Overview

Touchless Computer Control allows users — especially doctors, factory workers, or lab technicians —  
to interact with their computers in sterile or hands-free environments using simple hand gestures.

It works through a browser + Python WebSocket server that communicates video frames,  
detects gestures, and triggers system actions automatically.


#✋ Supported Gestures & Actions

| Gesture  | Description                      | Action |                                           |
|----------|----------------------------------|--------|------------------------------------------ |
| 🖐️ Palm (All Fingers)        | All fingers extended              | Switch App (Alt + Tab)        | 
| ✊ Fist (No Fingers)         | All fingers closed                | Play / Pause (Space)          |
| 👍 Thumbs Up                 | Only thumb raised                 | Show Desktop (Win + D)        |
| ✌️ Two Fingers               | Index + Middle raised             | Scroll Down                   |
| ☝️ One Finger                | Index finger raised               | Scroll Up                     |
| 🤟 Index + Thumb             | Index and thumb extended          | Scroll Right                  |
| 🤘 Three Fingers             | Index + Middle + Ring extended    | Open App (file path)          |


# Tech Stack

- Python 3.10+
- MediaPipe – Hand tracking & landmarks detection  
- OpenCV – Frame handling  
- WebSockets – Real-time browser ↔ Python communication  
- PyAutoGUI – System control (scrolling, app switching, etc.)  
- TailwindCSS + JavaScript – Clean UI in browser

  Live Site : https://ayush5424.github.io/Build-A-Thon-Project/
