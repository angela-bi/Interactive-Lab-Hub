import subprocess
import cv2
from PIL import Image
import digitalio, board
import adafruit_rgb_display.st7789 as st7789
import os, glob, re, time, datetime

# ---------------------------
# Setup Display
# ---------------------------
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000
spi = board.SPI()
disp = st7789.ST7789(
    spi, cs=cs_pin, dc=dc_pin, rst=reset_pin,
    baudrate=BAUDRATE, width=135, height=240,
    x_offset=53, y_offset=40,
)

# Backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output(value=True)

# ---------------------------
# Buttons
# ---------------------------
buttonA = digitalio.DigitalInOut(board.D23)  # next video
buttonA.switch_to_input(pull=digitalio.Pull.UP)

# ---------------------------
# Video Scan + Loudness Ranking
# ---------------------------
VIDEO_DIR = "./videos"
VIDEO_EXTENSIONS = ("*.mp4", "*.mov", "*.MOV", "*.avi", "*.mkv")

video_files = []
for ext in VIDEO_EXTENSIONS:
    video_files.extend(glob.glob(os.path.join(VIDEO_DIR, ext)))

if not video_files:
    print("No videos found in", VIDEO_DIR)
    exit(1)

def get_max_volume(video_path):
    """Return max_volume in dB (closer to 0 = louder)."""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-af", "volumedetect", "-f", "null", "-"
        ]
        result = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        matches = re.findall(r"max_volume: (-?\d+(\.\d+)?) dB", result.stderr)
        if matches:
            return float(matches[-1][0])
    except Exception as e:
        print(f"Error analyzing {video_path}: {e}")
    return -9999.0

# Rank videos loudest → quietest
ranked_videos = sorted(video_files, key=get_max_volume, reverse=True)
print("Videos ranked by loudness:")
for i, v in enumerate(ranked_videos):
    print(f"{i+1}. {v}")

# ---------------------------
# Video Playback Function
# ---------------------------
def play_video(video_path):
    print(f"Playing: {video_path}")
    # Start audio in background
    audio_proc = subprocess.Popen([
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", video_path
    ])

    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert and display
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)

        # Resize/crop for screen
        if disp.rotation % 180 == 90:
            height, width = disp.width, disp.height
        else:
            width, height = disp.width, disp.height

        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))

        disp.image(image)

        # Button check (break early to switch video)
        if buttonA.value == False:  # button pressed (active-low)
            print("Button pressed -> switching video")
            cap.release()
            audio_proc.terminate()
            return "next"

    cap.release()
    audio_proc.wait()
    return "done"

# ---------------------------
# Main Loop
# ---------------------------
TARGET_TIME = "16:00"  # <-- set target time (HH:MM 24hr)

started = False
video_index = 0

print(f"Waiting until {TARGET_TIME} to play loudest video...")

while True:
    now = datetime.datetime.now().strftime("%H:%M")

    if not started and now == TARGET_TIME:
        started = True
        video_index = 0
        play_video(ranked_videos[video_index])

    if started:
        # If button is pressed, cycle through next loudest
        if buttonA.value == False:  # active-low
            video_index = (video_index + 1) % len(ranked_videos)
            time.sleep(0.3)  # debounce
            play_video(ranked_videos[video_index])

    time.sleep(0.2)
