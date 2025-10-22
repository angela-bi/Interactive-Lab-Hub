#!/usr/bin/env python3
# SparkFun VCNL4040 Proximity Sensor + VLC + Qwiic GPIO Disco (continuous while playing)

import qwiic_proximity
import time
import sys
import statistics
import vlc
import yt_dlp
import os
import smbus2
import random
import threading

# -----------------------------
# CONFIG
# -----------------------------
YOUTUBE_URL = "https://youtu.be/EPo5wWmKEaI?si=P4iQHYS6ml0Li500"
TEMP_FILE = "/tmp/video.mp4"
SAMPLE_WINDOW = 10
MOVEMENT_THRESHOLD = 5
CHECK_INTERVAL = 0.4

# I2C setup for TCA9534 GPIO expander
I2C_ADDR = 0x27
bus = smbus2.SMBus(1)
OUTPUT_REG = 0x01
CONFIG_REG = 0x03

# Configure all pins as outputs
bus.write_byte_data(I2C_ADDR, CONFIG_REG, 0x00)

# Flag to control disco thread
disco_running = False

# -----------------------------
# FUNCTIONS
# -----------------------------
def download_video(url):
    """Download YouTube video to a local MP4 file using yt_dlp."""
    print("Downloading video to /tmp/video.mp4 ... (this may take ~30s)")
    ydl_opts = {
        'quiet': False,
        'format': 'best[ext=mp4]/best',
        'outtmpl': TEMP_FILE,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return TEMP_FILE


def disco_thread():
    """Flash LEDs randomly while disco_running is True."""
    global disco_running
    while disco_running:
        pattern = random.randint(0, 255)
        bus.write_byte_data(I2C_ADDR, OUTPUT_REG, pattern)
        time.sleep(random.uniform(0.05, 0.25))
    # Turn off LEDs when stopping
    bus.write_byte_data(I2C_ADDR, OUTPUT_REG, 0x00)


def runExample():
    global disco_running
    print("\nSparkFun VCNL4040 Proximity + VLC + Disco Lights\n")
    oProx = qwiic_proximity.QwiicProximity()

    if not oProx.connected:
        print("The Qwiic Proximity device isn't connected. Please check your connection.", file=sys.stderr)
        return

    oProx.begin()

    # Ensure video is available
    if not os.path.exists(TEMP_FILE):
        video_path = download_video(YOUTUBE_URL)
    else:
        video_path = TEMP_FILE
        print("Using cached video:", video_path)

    # Start VLC
    print("Starting VLC player...")
    player = vlc.MediaPlayer(video_path)
    player.play()
    time.sleep(5)

    readings = []
    is_playing = True
    disco_thread_obj = None

    while True:
        proxValue = oProx.get_proximity()
        print(f"Proximity Value: {proxValue}")

        readings.append(proxValue)
        if len(readings) > SAMPLE_WINDOW:
            readings.pop(0)

        if len(readings) >= SAMPLE_WINDOW:
            variation = statistics.stdev(readings)
            print(f"Variation: {variation:.2f}")

            if variation > MOVEMENT_THRESHOLD:
                if not is_playing:
                    print("Movement detected: PLAY + Disco!")
                    player.play()
                    is_playing = True

                    # Start disco thread
                    if not disco_running:
                        disco_running = True
                        disco_thread_obj = threading.Thread(target=disco_thread)
                        disco_thread_obj.start()

            else:
                if is_playing:
                    print("Stable distance: PAUSE + lights off")
                    player.pause()
                    is_playing = False

                    # Stop disco thread
                    if disco_running:
                        disco_running = False
                        if disco_thread_obj:
                            disco_thread_obj.join()
                            disco_thread_obj = None

        time.sleep(CHECK_INTERVAL)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit):
        print("\nExiting program. Cleaning up temporary file.")
        try:
            # Stop disco thread and turn off LEDs
            disco_running = False
            bus.write_byte_data(I2C_ADDR, OUTPUT_REG, 0x00)

            if os.path.exists(TEMP_FILE):
                os.remove(TEMP_FILE)
                print("Deleted:", TEMP_FILE)
        except Exception as e:
            print("Could not clean up properly:", e)
        sys.exit(0)