# Final Project  

Collaborators: Kyle Li (kl2296), Nophar Shalom (ns2242)

Requirements:
1. Project plan: Big idea, timeline, parts needed, fall-back plan. (Can be same as previous turn-in, but updated if you changed your plan)
2. Functioning project: The finished project should be a device, system, interface, etc. that people can interact with.
3. Documentation of design process
4. Archive of all code, design patterns, etc. used in the final design. (As with labs, the standard should be that the documentation would allow you to recreate your project if you woke up with amnesia.)
5. Video of someone using your project

## Project plan  
<img width="1007" height="564" alt="Screenshot 2025-12-11 at 1 07 05 PM" src="https://github.com/user-attachments/assets/5fc27aab-237c-43e0-9be7-f6c8cebca19f" />  
<img width="1000" height="560" alt="Screenshot 2025-12-11 at 1 07 19 PM" src="https://github.com/user-attachments/assets/d84d8b19-5ef3-48bd-82b9-8c68a4b9802f" />

Big idea: Our big idea was to make an interactive installation resembling the New York City skyline. Given a QR code of a song, the system would play the song over its speakers, project the album cover onto a building, and sample its dominant colors to create synchronized LED light pulses that illuminate the building interiors.

Timeline: Our initial plan was highlighted in the screenshot. However, as we were planning out the components needed, our plan changed a bit. Here was our revised breakdown:

![IMG_923AACFAA2C0-1](https://github.com/user-attachments/assets/37fa3141-f17e-4506-949a-5f0e54afe011)

For each component, we came up with a breakdown of what we needed to do:
- Buildings
  - Design buildings
  - Cut buildings
- Base
  - Design base
  - Cut base
- QR scanner
  - Write code for webcam -> recognizing song
- Song-related code
  - Write code that gets album from song
  - Write code to detect colors in album
- Lights 
  - Installation of lights
  - Write code to change colors of the lights
- Display and speaker
  - Screen that shows song, write code that displays song on screen
  - Write code that plays song

This is how we broke it down into a timeline:
| DATE   | TO DO                                                                                                                                                                                                                                                                          |
|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Nov 17 | By Nov 17: Implement webcam input to detect song QR code. From the spotify link, use spotify API to get metadata like album cover. Design building cut patterns. <br> During Nov 17: Given the song, play the corresponding track. Start cutting buildings |
| Nov 19 | By Nov 19: Display song on screen. Connect lights with Pi. Extract dominant colors from album art. Get lights to work <br> During Nov 19: Finish designing and printing buildings and base. |
| Nov 24 | By Nov 24: Play song on speakers, get lights to work                                                                                                                                                                                                                                        |
| Dec 1  | Protype showcase deadline; get prototype be functional (e.g. scan song -> plays songs and gets album cover)                                                                                                                                                                                                            |
| Dec 5  | Finalize prototype. Conduct tests with users to ensure the experience is intuitive, engaging, and safe.                                                                                                                                                                                                   |
| Dec 14 | Compile design process, source code, reflections, project documentation, demo video, and group work questionnaire.                                                                                                                                                                     |

## Documentation of design process

### Buildings and Base

We used makeabox.io to create the designs for the base and buildings, which we exported to Illustrator and used Trotec to cut out acrylic and wood. This took a lot of trial and error---sometimes, makeabox.io made a box that didn't fit together, and sometimes we added the wrong material/thickness so it didn't completely cut out the designs. [Video of laser cutting](https://drive.google.com/file/d/1b2aTOYd5n_8dTt5-nXg4UEktvBCX7vKe/view?usp=sharing)

In addition to being able to assemble individual buildings and the base, the design also had to involve fitting the acrylic buildings onto the wooden base. This also took some trial and error, because we had to modify the width of the holes cut in the base so that we were able to fit the acrylic buildings on top of the base. [Video of earlier prototype](https://drive.google.com/file/d/1vNrLCEC3M1uJeTkorbxCvN4FkjzVsQPe/view?usp=drive_link)

### Overview: Input (QR code) -> song information -> outputs (pi display, speakers, LED lights)

This is how we broke down the process of input (QR code) to outputs (pi screen, speaker, lights):

![IMG_96BF61FF06B5-1](https://github.com/user-attachments/assets/90b052b8-19c9-41c8-974e-5ecf68c43348)

### QR code -> song link, album cover

We used `CV2` to get song information from a user scanning a song's QR code with the webcam. We initially thought that we could use spotify because they have a developer API so we could get its metadata like the album, etc.

```
def find_spotify_qr():
   """
   Opens webcam, scans for QR codes, and returns the FIRST valid Spotify track URL found.
   """
   print("Scanning for Spotify QR codes... (press 'q' to quit)")


   cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
   if not cap.isOpened():
       print("Failed to open")
   else:
       print("Opened!")


   try:
       while True:
           ret, frame = cap.read()
           if not ret:
               continue


           qr_codes = decode(frame)
           for code in qr_codes:
               link = code.data.decode('utf-8')


               # Only accept Spotify track links
               if "open.spotify.com/track/" in link:
                   print(f"Found Spotify Track: {link}")
                   cap.release()
                   cv2.destroyAllWindows()
                   return link


           cv2.imshow('QR Scanner', frame)
           if cv2.waitKey(1) & 0xFF == ord('q'):
               break


   finally:
       cap.release()
       cv2.destroyAllWindows()


   return None
```

After getting the song, we realized that in order to play the song, the process to do so through spotify would involve many steps (involving signing into the spotify developer account after the link is opened). We changed our code to take in a QR code for a youtube link, which would both allow us to get a png of the album cover for the pi and LEDs, and play the song over the speaker without additional hurdles. 

Below is the relevant snippet in our `___main___` function"
```
print("Starting Webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Webcam not found.")
        return

    print("Scanner Running. Waiting for QR codes...")
    
    # Flash blue to show it's ready
    show_status_color(0, 0, 255)
    time.sleep(0.5)
    show_status_color(0, 0, 0) # Clear to black

    last_played_link = None
    last_seen_time = 0

    try:
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                break

            qr_codes = decode(frame)

            # Reset logic: If no code seen for RESET_TIME, allow rescanning
            if not qr_codes:
                if last_played_link is not None and (time.time() - last_seen_time > RESET_TIME):
                    print("Resetting... Ready for new code.")
                    last_played_link = None
                    show_status_color(0, 0, 0) # Clear screen to black when reset

            for code in qr_codes:
                link = code.data.decode('utf-8')
                last_seen_time = time.time()

                if link != last_played_link:
                    print("-" * 30)
                    print(f"Found: {link}")
```

### Song -> play song on speaker

After getting the song url, we sent a request to a laptop connected to the same server, and to play the song, we connected our speaker to laptop over bluetooth. 

Below is the relevant snippet in our `___main___` function:
```
# 2. Send to Laptop
    try:
        requests.get(f"http://{LAPTOP_IP}:{LAPTOP_PORT}/play", params={'url': link}, timeout=1)
        print("Sent to laptop.")
    except:
        print("Could not connect to laptop.")
```
This code makes it so that once a song is found, the youtube link opens in the laptop.

### Song -> pi screen 

After getting the song url, we were also able to convert the Youtube thumbnail into a PIL Image, which we displayed in the pi screen.

Below is the relevant snippet in the helper function `get_youtube_thumbnail`:
```
def get_youtube_thumbnail(url):
    """
    Downloads YouTube thumbnail and converts it to a PIL Image 
    that fits the ST7789 screen.
    """
    video_id = ""
    if "v=" in url:
        try:
            video_id = url.split("v=")[1].split("&")[0]
        except: pass
    elif "youtu.be/" in url:
        try:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        except: pass

    if not video_id:
        return None

    # Download High Quality Thumb
    thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    print(f"Downloading art: {thumb_url}")
    
    try:
        resp = requests.get(thumb_url, timeout=2)
        if resp.status_code == 200:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(resp.content))
            
            # Resize and Crop to fit the screen dimensions
            image = ImageOps.fit(image, (display.width, display.height), method=Image.LANCZOS)
            return image
    except Exception as e:
        print(f"Image download failed: {e}")
    
    return None
```

Below is the relevant snippet in our `___main___` function, where we called `get_youtube_thumbnail` to get the PIL image and displayed it on the pi screen:
```
# 3. Get Album Art
art_image = get_youtube_thumbnail(link)

# 4. Display Art
if art_image:
    display.image(art_image)
```

By the showcase deadline of December 1, we had everything working except the LED lights. [Here is a video we recorded of it working.](https://drive.google.com/file/d/1paV4NpYWIWsTyBRG5n4qti43AxIXps6V/view?usp=drive_link)

### Song album cover -> LED lights 

The hardest part of the whole process was getting the LED lights to display the dominant colors of the album. This involved writing code to extract the dominant colors from the album art:

```
def extract_primary_colors(image, num_colors=3):
    """
    Given a PIL Image, returns `num_colors` dominant colors as RGB tuples.
    Uses k-means clustering on all pixels.
    """
    # Convert image to numpy array
    img = image.convert("RGB")
    img_np = np.array(img)

    # Flatten pixel array into (num_pixels, 3)
    pixels = img_np.reshape(-1, 3)

    # KMeans clustering
    kmeans = KMeans(n_clusters=num_colors, n_init="auto")
    kmeans.fit(pixels)

    # Cluster centers are the dominant colors
    colors = kmeans.cluster_centers_.astype(int)

    # Convert to list of (R, G, B)
    return [tuple(color) for color in colors]
```

When we tried to get the LED lights to work, our combined lack of electrical engineering experience resulted in all of our Raspberry Pis being nonfunctional or partially broken. Nophar managed to get a Raspberry Pi 4, which she reprogrammed to make it work and connect successfully with the LED lights. Video of LED lights working for the first time

--- 

## Final Functioning project  



### Video of someone using our project


### Archive of all code, design patterns, etc. used in the final design. (As with labs, the standard should be that the documentation would allow you to recreate your project if you woke up with amnesia.)

Code for raspberry pi

Code for computer

Laser cut designs

---

## Feedback and future directions
