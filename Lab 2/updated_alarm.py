# chatgpt log: https://chatgpt.com/share/68f2fbc9-c338-800d-a6f6-6eccc3eea4e1

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alarm Clock with Loudest Video Playback on Raspberry Pi 5 + Mini PiTFT (ST7789)
Features:
- Shows current time and alarm time on display
- Button A (GPIO23): increment hour
- Button B (GPIO24): increment minute
- Both buttons pressed together: snooze (stop video, +5 min)
"""

import subprocess
import cv2
import os, glob, re, time, datetime
import digitalio, board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# ---------------------------
# SPI + Display setup
# ---------------------------
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
    rotation=90
)

# ---------------------------
# Backlight + Buttons
# ---------------------------
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output(value=True)

buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

# ---------------------------
# Video Scan (instant start)
# ---------------------------
VIDEO_DIR = "./videos"
VIDEO_EXTENSIONS = ("*.mp4", "*.mov", "*.MOV", "*.avi", "*.mkv")

video_files = []
for ext in VIDEO_EXTENSIONS:
    video_files.extend(glob.glob(os.path.join(VIDEO_DIR, ext)))

if not video_files:
    print("No videos found in", VIDEO_DIR)
    exit(1)

# Instant-start: just sort alphabetically
ranked_videos = sorted(video_files)

print("Videos found:")
for i, v in enumerate(ranked_videos):
    print(f"{i+1}. {v}")


# ---------------------------
# Helper functions
# ---------------------------
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
width = disp.width
height = disp.height

def show_clock(current_time, alarm_time, message=""):
    """Draw current and alarm times."""
    image = Image.new("RGB", (height, width))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

    draw.text((10, 60), f"TIME: {current_time}", fill=(255, 255, 255), font=font)
    draw.text((10, 90), f"ALARM: {alarm_time}", fill=(255, 255, 0), font=font)
    if message:
        draw.text((10, 130), message, fill=(100, 200, 255), font=font)

    disp.image(image)

def play_video(video_path):
    """Play video (with ffplay for audio + OpenCV for frames)."""
    print(f"Playing: {video_path}")
    audio_proc = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", video_path]
    )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file")
        return

    # Get display dimensions (respect rotation)
    screen_w = disp.width
    screen_h = disp.height
    if disp.rotation % 180 == 90:
        # Swap if in landscape mode
        screen_w, screen_h = screen_h, screen_w

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)

        # --- Resize and center crop to fit screen safely ---
        image_ratio = image.width / image.height
        screen_ratio = screen_w / screen_h

        if screen_ratio < image_ratio:
            # Image is wider → scale by height
            scaled_width = int(image.width * screen_h / image.height)
            scaled_height = int(screen_h)
        else:
            # Image is taller → scale by width
            scaled_width = int(screen_w)
            scaled_height = int(image.height * screen_w / image.width)

        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Center-crop safely within bounds
        x = max(0, (scaled_width - screen_w) // 2)
        y = max(0, (scaled_height - screen_h) // 2)
        image = image.crop((x, y, x + screen_w, y + screen_h))

        # Extra guard: ensure final size is never too big
        if image.width > screen_w or image.height > screen_h:
            image = image.resize((screen_w, screen_h))

        # Show on display
        disp.image(image)

    cap.release()
    audio_proc.wait()


# ---------------------------
# Main Logic
# ---------------------------
alarm_hour = 7
alarm_minute = 0
started = False
video_index = 0

print("Alarm clock ready. Use buttons to set alarm time.")

while True:
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    alarm_time = f"{alarm_hour:02d}:{alarm_minute:02d}"

    show_clock(current_time, alarm_time)

    # Trigger alarm
    if not started and now.hour == alarm_hour and now.minute == alarm_minute:
        started = True
        print("Alarm triggered! Playing loudest video.")
        result = play_video(ranked_videos[video_index])
        if result == "snooze":
            started = False
            snooze_time = now + datetime.timedelta(minutes=5)
            alarm_hour, alarm_minute = snooze_time.hour, snooze_time.minute
            print(f"Alarm snoozed until {alarm_hour:02d}:{alarm_minute:02d}")
        else:
            print("Video finished. Alarm cleared.")
            started = False

    # Button A → increment hour
    if not buttonA.value and buttonB.value:
        alarm_hour = (alarm_hour + 1) % 24
        print(f"Alarm hour set to {alarm_hour:02d}")
        time.sleep(0.3)

    # Button B → increment minute
    if not buttonB.value and buttonA.value:
        alarm_minute = (alarm_minute + 1) % 60
        print(f"Alarm minute set to {alarm_minute:02d}")
        time.sleep(0.3)

    time.sleep(0.2)
