# 🎵 Air DJ

**Air DJ** is a computer-vision-based, contactless music control system that allows users to control music playback and system volume using hand gestures in front of a webcam.

The project combines **OpenCV**, **Google MediaPipe Hand Landmarker**, and Python-based system controls to transform real-time hand movements into music control commands without requiring a physical mouse, keyboard, or controller.

## ✨ Features

- 🖐️ Real-time hand detection through a webcam
- 🤚 Two-hand tracking and left/right hand recognition
- ✊ Left-hand fist — toggle **ACTION mode**
- 👌 Right-hand OK gesture — toggle **VOLUME mode**
- ✋ Right-hand open palm — Play / Pause
- 👉 Left-hand swipe right — Next Track
- 👈 Left-hand swipe left — Previous Track
- 🤏 Left-hand pinch — Volume control
- 🔒 **ACTION and VOLUME modes are mutually exclusive**
- ⏱️ Mode switching includes a cooldown to reduce accidental activation
- 🎚️ Volume control uses smoothing to reduce fluctuations caused by hand movement

## 🧠 How It Works

The system uses a webcam to capture real-time video frames.

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Landmarker
   ↓
21 Hand Landmarks
   ↓
Hand / Gesture Recognition
   ↓
Control Logic
   ↓
Music / Volume Control
```

MediaPipe provides the coordinates of **21 landmarks for each detected hand**. Instead of training a hand-gesture classification model from scratch, this project uses these landmarks as input and implements gesture recognition using geometric relationships between key points.

For example, the distance between the thumb and index finger is used to control volume:

```text
Thumb ●──────● Index Finger
       distance
          ↓
      Volume Level
```

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **OpenCV** | Webcam capture and real-time visualization |
| **MediaPipe** | Hand detection and tracking |
| **Hand Landmarker** | Detection of 21 hand landmarks and handedness |
| **PyCaw** | Windows system volume control |
| **Pynput** | Simulating media keyboard commands |

## 🤖 AI Model

This project uses the **MediaPipe Hand Landmarker** pre-trained model.

The model provides:

- Hand detection
- Left / right hand classification
- 21 hand landmarks
- Real-time hand tracking

No custom neural network training is required.

The main focus of this project is therefore not training a new AI model, but **integrating an existing computer-vision model with custom gesture recognition and human-computer interaction logic**.

## 🎮 Gesture Mapping

### ACTION Mode

| Gesture | Action |
|---|---|
| ✊ Left Fist | Enable / Disable ACTION mode |
| ✋ Right Open Palm | Play / Pause |
| 👉 Left Swipe Right | Next Track |
| 👈 Left Swipe Left | Previous Track |

### VOLUME Mode

| Gesture | Action |
|---|---|
| 👌 Right OK | Enable / Disable VOLUME mode |
| 🤏 Left Pinch | Adjust System Volume |

Only one mode can be active at a time:

```text
ACTION ON
    ↓
VOLUME OFF
```

or

```text
VOLUME ON
    ↓
ACTION OFF
```

This design prevents volume adjustment gestures from accidentally triggering music playback or track switching.

## 📦 Installation

Install the required Python packages:

```bash
pip install opencv-python mediapipe pycaw pynput
```

Download the MediaPipe Hand Landmarker model and place it in the project directory.

Example:

```text
MUSIC_G/
├── hand_test.py
└── hand_landmarker.task
```

Update the model path in the Python program if necessary.

## 🚀 Run

Run the program with:

```bash
python hand_test.py
```

Press:

```text
Q
```

to exit the program.

## 🔬 Project Concept

Air DJ explores the use of **computer vision for natural human-computer interaction (HCI)**.

Instead of interacting with a traditional interface such as:

```text
Mouse → Keyboard → Screen
```

the user interacts directly through physical gestures:

```text
Hand Movement
      ↓
Computer Vision
      ↓
Gesture Recognition
      ↓
Music Control
```

The project demonstrates how an existing AI perception model can be combined with traditional programming logic to create a practical real-time interaction system.

## 📌 Current Development

The current version focuses on the core interaction system and gesture-to-command mapping.

Future improvements may include:

- More robust hand and gesture stabilization
- Multi-frame gesture confirmation
- Improved swipe detection
- Visual music-player interface
- Display of current song information
- Additional gestures and customizable controls
- Support for other operating systems or media applications

---

### Author

Developed as a computer vision / human-computer interaction project.

**Air DJ — Control music with your hands. 🎵🖐️**
