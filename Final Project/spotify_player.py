import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import vlc
import requests
import sys
import io
from PIL import Image, ImageDraw, ImageFont
import digitalio
import board
import adafruit_rgb_display.st7789 as st7789
import time

# ------------------------------
# CONFIG
# ------------------------------

SPOTIFY_CLIENT_ID = sys.argv[1]
SPOTIFY_CLIENT_SECRET = sys.argv[2]

scroll_x = 0

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# ------------------------------
# SETUP PI TFT DISPLAY
# ------------------------------

cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000
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
)

width = disp.width
height = disp.height

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# ------------------------------
# UTILITIES
# ------------------------------

def get_album_info(track_url):
    track_id = track_url.split("/")[-1].split("?")[0]
    track_info = sp.track(track_id)
    return track_info

def get_itunes_preview(track_name, artist_name):
    url = "https://itunes.apple.com/search"
    params = {"term": f"{artist_name} {track_name}", "limit": 1}
    try:
        resp = requests.get(url, params=params).json()
        if resp.get("resultCount", 0) > 0:
            return resp["results"][0].get("previewUrl")
        return None
    except:
        return None

def download_album_art(url):
    try:
        img_data = requests.get(url).content
        return Image.open(io.BytesIO(img_data))
    except:
        return None

# ------------------------------
# DISPLAY FUNCTION
# ------------------------------

def display_song_on_tft(song_name, artist_name, album_art_url):
    global scroll_x

    # In landscape mode, image buffer must be 240x135
    img_width = 240
    img_height = 135

    # Create the buffer in landscape
    image = Image.new("RGB", (img_width, img_height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    # -----------------------------
    # LOAD & POSITION ALBUM ART
    # -----------------------------
    album_img = download_album_art(album_art_url)

    if album_img:
        # Fit art into the LEFT half (135x135)
        album_img = album_img.resize((135, 135), Image.BICUBIC)
        image.paste(album_img, (0, 0))   # left side

    # -----------------------------
    # SCROLLING TEXT ON RIGHT SIDE
    # -----------------------------
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20
        )
    except:
        font = ImageFont.load_default()

    text = f"{song_name}   -   {artist_name}"

    # how wide the scrolling area is
    scroll_area_x = 140
    scroll_area_y = 10
    scroll_area_width = 90  # right side of screen

    text_width = draw.textlength(text, font=font)

    # draw text twice for seamless loop
    draw.text(
        (scroll_area_x - scroll_x, scroll_area_y),
        text,
        font=font,
        fill=(255, 255, 255),
    )
    draw.text(
        (scroll_area_x - scroll_x + text_width + 40, scroll_area_y),
        text,
        font=font,
        fill=(255, 255, 255),
    )

    # update scroll
    scroll_x = (scroll_x + 2) % (text_width + 40)

    # -----------------------------
    # Rotate final image to portrait
    # -----------------------------
    disp.image(image, rotation=90)

# ------------------------------
# PLAYBACK
# ------------------------------

def play_song(track_url):
    info = get_album_info(track_url)

    song_name = info["name"]
    artist_name = info["artists"][0]["name"]
    album_art_url = info["album"]["images"][0]["url"]
    preview_url = info["preview_url"]

    # ----------------------------------
    # CONTINUOUS UPDATE LOOP FOR SCROLL
    # ----------------------------------
    import threading
    stop_scrolling = False
    
    def updater():
        while not stop_scrolling:
            display_song_on_tft(song_name, artist_name, album_art_url)
            time.sleep(0.05)   # scrolling speed
    
    t = threading.Thread(target=updater)
    t.daemon = True
    t.start()

    # ----------------------------------
    # AUDIO PLAYBACK
    # ----------------------------------
    if preview_url:
        print("Playing Spotify preview...")
        player = vlc.MediaPlayer(preview_url)
        player.play()
        time.sleep(30)  # keep UI alive while playing
        stop_scrolling = True
        return

    itunes_url = get_itunes_preview(song_name, artist_name)

    if itunes_url:
        print("Playing iTunes preview...")
        player = vlc.MediaPlayer(itunes_url)
        player.play()
        time.sleep(30)
        stop_scrolling = True
        return

    print("No preview available anywhere.")
    time.sleep(10)
    stop_scrolling = True


# ------------------------------
# MAIN
# ------------------------------

if __name__ == "__main__":
    track_url = "https://open.spotify.com/track/2D1rYPinUnikGU9xNWylnN"
    play_song(track_url)
