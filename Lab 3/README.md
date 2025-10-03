# Chatterboxes
**NAMES OF COLLABORATORS HERE**
Nophar Shalom (ns2242)

<details>
<summary>Toggle original details</summary>
[![Watch the video](https://user-images.githubusercontent.com/1128669/135009222-111fe522-e6ba-46ad-b6dc-d1633d21129c.png)](https://www.youtube.com/embed/Q8FWzLMobx0?start=19)

In this lab, we want you to design interaction with a speech-enabled device--something that listens and talks to you. This device can do anything *but* control lights (since we already did that in Lab 1).  First, we want you first to storyboard what you imagine the conversational interaction to be like. Then, you will use wizarding techniques to elicit examples of what people might say, ask, or respond.  We then want you to use the examples collected from at least two other people to inform the redesign of the device.

We will focus on **audio** as the main modality for interaction to start; these general techniques can be extended to **video**, **haptics** or other interactive mechanisms in the second part of the Lab.
</details>

## Prep for Part 1: Get the Latest Content and Pick up Additional Parts 

<details>
<summary>Toggle original details</summary>

Please check instructions in [prep.md](prep.md) and complete the setup before class on Wednesday, Sept 23rd.

### Pick up Web Camera If You Don't Have One

Students who have not already received a web camera will receive their [Logitech C270 Webcam](https://www.amazon.com/Logitech-Desktop-Widescreen-Calling-Recording/dp/B004FHO5Y6/ref=sr_1_3?crid=W5QN79TK8JM7&dib=eyJ2IjoiMSJ9.FB-davgIQ_ciWNvY6RK4yckjgOCrvOWOGAG4IFaH0fczv-OIDHpR7rVTU8xj1iIbn_Aiowl9xMdeQxceQ6AT0Z8Rr5ZP1RocU6X8QSbkeJ4Zs5TYqa4a3C_cnfhZ7_ViooQU20IWibZqkBroF2Hja2xZXoTqZFI8e5YnF_2C0Bn7vtBGpapOYIGCeQoXqnV81r2HypQNUzFQbGPh7VqjqDbzmUoloFA2-QPLa5lOctA.L5ztl0wO7LqzxrIqDku9f96L9QrzYCMftU_YeTEJpGA&dib_tag=se&keywords=webcam%2Bc270&qid=1758416854&sprefix=webcam%2Bc270%2Caps%2C125&sr=8-3&th=1) and bluetooth speaker on Wednesday at the beginning of lab. If you cannot make it to class this week, please contact the TAs to ensure you get these. 

### Get the Latest Content

As always, pull updates from the class Interactive-Lab-Hub to both your Pi and your own GitHub repo. There are 2 ways you can do so:

**\[recommended\]**Option 1: On the Pi, `cd` to your `Interactive-Lab-Hub`, pull the updates from upstream (class lab-hub) and push the updates back to your own GitHub repo. You will need the *personal access token* for this.

```
pi@ixe00:~$ cd Interactive-Lab-Hub
pi@ixe00:~/Interactive-Lab-Hub $ git pull upstream Fall2025
pi@ixe00:~/Interactive-Lab-Hub $ git add .
pi@ixe00:~/Interactive-Lab-Hub $ git commit -m "get lab3 updates"
pi@ixe00:~/Interactive-Lab-Hub $ git push
```

Option 2: On your your own GitHub repo, [create pull request](https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2022Fall/readings/Submitting%20Labs.md) to get updates from the class Interactive-Lab-Hub. After you have latest updates online, go on your Pi, `cd` to your `Interactive-Lab-Hub` and use `git pull` to get updates from your own GitHub repo.
</details>

## Part 1.
### Setup 
<details>
<summary>Toggle original details</summary>

Activate your virtual environment

```
pi@ixe00:~$ cd Interactive-Lab-Hub
pi@ixe00:~/Interactive-Lab-Hub $ cd Lab\ 3
pi@ixe00:~/Interactive-Lab-Hub/Lab 3 $ python3 -m venv .venv
pi@ixe00:~/Interactive-Lab-Hub $ source .venv/bin/activate
(.venv)pi@ixe00:~/Interactive-Lab-Hub $ 
```

Run the setup script
```(.venv)pi@ixe00:~/Interactive-Lab-Hub $ pip install -r requirements.txt  ```

Next, run the setup script to install additional text-to-speech dependencies:
```
(.venv)pi@ixe00:~/Interactive-Lab-Hub/Lab 3 $ ./setup.sh
```
</details>

### Text to Speech 
<details>
<summary>Toggle original details</summary>

In this part of lab, we are going to start peeking into the world of audio on your Pi! 

We will be using the microphone and speaker on your webcamera. In the directory is a folder called `speech-scripts` containing several shell scripts. `cd` to the folder and list out all the files by `ls`:

```
pi@ixe00:~/speech-scripts $ ls
Download        festival_demo.sh  GoogleTTS_demo.sh  pico2text_demo.sh
espeak_demo.sh  flite_demo.sh     lookdave.wav
```

You can run these shell files `.sh` by typing `./filename`, for example, typing `./espeak_demo.sh` and see what happens. Take some time to look at each script and see how it works. You can see a script by typing `cat filename`. For instance:

```
pi@ixe00:~/speech-scripts $ cat festival_demo.sh 
#from: https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)#Festival_Text_to_Speech
```
You can test the commands by running
```
echo "Just what do you think you're doing, Dave?" | festival --tts
```

Now, you might wonder what exactly is a `.sh` file? 
Typically, a `.sh` file is a shell script which you can execute in a terminal. The example files we offer here are for you to figure out the ways to play with audio on your Pi!

You can also play audio files directly with `aplay filename`. Try typing `aplay lookdave.wav`.

</details>

\*\***Write your own shell file to use your favorite of these TTS engines to have your Pi greet you by name.**\*\*

My shell file is located in `speech-scripts` under the file name `greet_angela.sh`.

<details>
<summary>Toggle original details</summary>
---
Bonus:
[Piper](https://github.com/rhasspy/piper) is another fast neural based text to speech package for raspberry pi which can be installed easily through python with:
```
pip install piper-tts
```
and used from the command line. Running the command below the first time will download the model, concurrent runs will be faster. 
```
echo 'Welcome to the world of speech synthesis!' | piper \
  --model en_US-lessac-medium \
  --output_file welcome.wav
```
Check the file that was created by running `aplay welcome.wav`. Many more languages are supported and audio can be streamed dirctly to an audio output, rather than into an file by:

```
echo 'This sentence is spoken first. This sentence is synthesized while the first sentence is spoken.' | \
  piper --model en_US-lessac-medium --output-raw | \
  aplay -r 22050 -f S16_LE -t raw -
```
</details>
  
### Speech to Text

<details>
<summary>Toggle original details</summary>

Next setup speech to text. We are using a speech recognition engine, [Vosk](https://alphacephei.com/vosk/), which is made by researchers at Carnegie Mellon University. Vosk is amazing because it is an offline speech recognition engine; that is, all the processing for the speech recognition is happening onboard the Raspberry Pi. 

Make sure you're running in your virtual environment with the dependencies already installed:
```
source .venv/bin/activate
```

Test if vosk works by transcribing text:

```
vosk-transcriber -i recorded_mono.wav -o test.txt
```

You can use vosk with the microphone by running 
```
python test_microphone.py -m en
```

---
Bonus:
[Whisper](https://openai.com/index/whisper/) is a neural network–based speech-to-text (STT) model developed and open-sourced by OpenAI. Compared to Vosk, Whisper generally achieves higher accuracy, particularly on noisy audio and diverse accents. It is available in multiple model sizes; for edge devices such as the Raspberry Pi 5 used in this class, the tiny.en model runs with reasonable latency even without a GPU.

By contrast, Vosk is more lightweight and optimized for running efficiently on low-power devices like the Raspberry Pi. The choice between Whisper and Vosk depends on your scenario: if you need higher accuracy and can afford slightly more compute, Whisper is preferable; if your priority is minimal resource usage, Vosk may be a better fit.

In this class, we provide two Whisper options: A quantized 8-bit faster-whisper model for speed, and the standard Whisper model. Try them out and compare the trade-offs.

Make sure you're in the Lab 3 directory with your virtual environment activated:
```
cd ~/Interactive-Lab-Hub/Lab\ 3/speech-scripts
source ../.venv/bin/activate
```

Then test the Whisper models:
```
python whisper_try.py
```
and

```
python faster_whisper_try.py
```
</details>

\*\***Write your own shell file that verbally asks for a numerical based input (such as a phone number, zipcode, number of pets, etc) and records the answer the respondent provides.**\*\*

The shell file is under `screen_scripts` with the file name `angela_numerical_input.sh`.

### 🤖 NEW: AI-Powered Conversations with Ollama

<details>
<summary>Toggle original details</summary>

Want to add intelligent conversation capabilities to your voice projects? **Ollama** lets you run AI models locally on your Raspberry Pi for sophisticated dialogue without requiring internet connectivity!

#### Quick Start with Ollama

**Installation** (takes ~5 minutes):
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download recommended model for Pi 5
ollama pull phi3:mini

# Install system dependencies for audio (required for pyaudio)
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-dev

# Create separate virtual environment for Ollama (due to pyaudio conflicts)
cd ollama/
python3 -m venv ollama_venv
source ollama_venv/bin/activate

# Install Python dependencies in separate environment
pip install -r ollama_requirements.txt
```
#### Ready-to-Use Scripts

We've created three Ollama integration scripts for different use cases:

**1. Basic Demo** - Learn how Ollama works:
```bash
python3 ollama_demo.py
```

**2. Voice Assistant** - Full speech-to-text + AI + text-to-speech:
```bash
python3 ollama_voice_assistant.py
```

**3. Web Interface** - Beautiful web-based chat with voice options:
```bash
python3 ollama_web_app.py
# Then open: http://localhost:5000
```

#### Integration in Your Projects

Simple example to add AI to any project:
```python
import requests

def ask_ai(question):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi3:mini", "prompt": question, "stream": False}
    )
    return response.json().get('response', 'No response')

# Use it anywhere!
answer = ask_ai("How should I greet users?")
```

**📖 Complete Setup Guide**: See `OLLAMA_SETUP.md` for detailed instructions, troubleshooting, and advanced usage!

</details>

\*\***Try creating a simple voice interaction that combines speech recognition, Ollama processing, and text-to-speech output. Document what you built and how users responded to it.**\*\*

The file is under the `ollama` folder with the file name `ollama_convo.py`. I used `ollama_demo.py` and `test_microphone.py` as references, and used ChatGPT to generate code that: 
1. Records the user's voice
2. Transcribes it using Vosk
3. Uses Ollama to generate a response
4. Uses espeak to play the response out loud.

When testing the script, the speaker was quite loud, so when users heard the response they were a bit startled. The conversation felt a bit unnatural because generating a response and playing it out loud took a bit of time, which felt a bit awkward.

### Serving Pages

<details>
<summary>Toggle original details</summary>

In Lab 1, we served a webpage with flask. In this lab, you may find it useful to serve a webpage for the controller on a remote device. Here is a simple example of a webserver.

```
pi@ixe00:~/Interactive-Lab-Hub/Lab 3 $ python server.py
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 162-573-883
```
From a remote browser on the same network, check to make sure your webserver is working by going to `http://<YourPiIPAddress>:5000`. You should be able to see "Hello World" on the webpage.

</details>

### Storyboard

Storyboard and/or use a Verplank diagram to design a speech-enabled device. (Stuck? Make a device that talks for dogs. If that is too stupid, find an application that is better than that.) 

\*\***Post your storyboard and diagram here.**\*\*

__Storyboard__
![IMG_2F648F698F74-1](https://github.com/user-attachments/assets/016e015a-88f2-45e9-bb52-77642340b2b4)

Write out what you imagine the dialogue to be. Use cards, post-its, or whatever method helps you develop alternatives or group responses. 


__Dialogue__

[Recipe](https://www.chopstickchronicles.com/matcha-cookies-checkerboard/) used in fake situation

Quantity of ingredient
- Person: I just added 95g of plain flour, how much matcha powder did I need again?
- Device: 5 grams. 

Converting quantity
- Person: What is 5 grams of matcha in teaspoons?
- Device: According to Naoki Matcha, 2.5 teaspoons is equivalent to 5 grams of matcha.

Ingredient in context of recipe
- Person: Do I need a high-quality matcha for this recipe?
- Device: According to the recipe, you only need culinary grade matcha.

Questions about satisfactory intermediate result
- Person: I’m mixing my butter and sugar, but I’m not sure when it’s considered done.
- Device: What does it look like?
- Person: It looks a bit lighter than the butter I started with.
- Device: If you’ve been mixing for more than 1 minute at high speed, you should be done.

Questions about next step
- Person: I just finished mixing butter and sugar. What’s the next step?
- Device: According to the recipe, your next step is to divide the mixture into half. Let me know when you’ve done that, and I can provide you with what to do afterwards.

Other tasks
- Person: Can you set a timer for 6 minutes?
- Device: Yes. How would you like me to remind you?
- Person: Remind me when there’s 3 minutes, and count down the last minute.
- Device: Got it.

\*\***Please describe and document your process.**\*\*

During my brainstorming/storyboarding process:
- I wanted to come up with ideas that would benefit from being verbal. One angle I thought of was that speech-centric devices could be good for accessibility; most of the other ideas I had stemmed from the thought that natural language is uniquely good for capturing tasks such as cooking that cannot be cleaning formalized.
- I picked my current idea because of this, and because I thought about how when I bake cookies I usually get my phone dirty or have to cover it with plastic wrap.
- When coming up with the dialogue, I pulled up a recipe I've used before that is pretty intricate (has a lot of steps). I thought of different types of questions a person using the device might ask, such as what the next step is, converting measurements, and asking questions about if a step is finished.

### Acting out the dialogue

Find a partner, and *without sharing the script with your partner* try out the dialogue you've designed, where you (as the device designer) act as the device you are designing.  Please record this interaction (for example, using Zoom's record feature).

\*\***Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**\*\*

[Recording](https://drive.google.com/file/d/1obz2X0c6ejpMoM-W7xDDIVfYY_ohwvuB/view?usp=sharing)

Since most of my dialogues were prompted by the human, all of the situations I covered didn't occur; however, for the situations that did happen, the exchanges between the human and device were much longer. One thing I noticed was that the human dialogue didn't just include the question for the device, but usually also included some sort of framing dialogue. For the "converting quantity" situation, the dialogue from the human I imagined was, "What is 5 grams of matcha in teaspoons?" What Nophar said was, "I don't know what 5 grams of matcha is. What is that in teaspoons?" In the "Questions about satisfactory intermediate result" situation, I expected the human to describe their mixture in terms of what the recipe said (a "creamish color"), but Nophar said "It's clumping together."


### Wizarding with the Pi (optional)
<details>
<summary>Toggle original details</summary>
In the [demo directory](./demo), you will find an example Wizard of Oz project. In that project, you can see how audio and sensor data is streamed from the Pi to a wizard controller that runs in the browser.  You may use this demo code as a template. By running the `app.py` script, you can see how audio and sensor data (Adafruit MPU-6050 6-DoF Accel and Gyro Sensor) is streamed from the Pi to a wizard controller that runs in the browser `http://<YouPiIPAddress>:5000`. You can control what the system says from the controller as well!

\*\***Describe if the dialogue seemed different than what you imagined, or when acted out, when it was wizarded, and how.**\*\*
</details>

# Lab 3 Part 2

**For Part 2, you will redesign the interaction with the speech-enabled device using the data collected, as well as feedback from part 1.**

## Prep for Part 2

**1. What are concrete things that could use improvement in the design of your device? For example: wording, timing, anticipation of misunderstandings...**

I could design conversation progression to prepare for longer chains of conversation and better anticipation of misunderstandings.

**2. What are other modes of interaction _beyond speech_ that you might also use to clarify how to interact?**

I completely forgot that there needs to be something to initiate the conversation, so one way to start the conversation would be prompting the user to upload their recipe on an interface, then having the baking assistant introduce themselves. Other ways beyond speech I could clarify to the user how to interact could include a visual display for possible questions to ask, such as "Ask me to convert measurements" or "Ask me what grade matcha is best to use."

**3. Make a new storyboard, diagram and/or script based on these reflections.**

Script
- Device: Please input your recipe below.
- User adds recipe into input
- Device: Thanks! I'm a chatbot designed to help you with your recipe, Matcha Shortbread Cookies. If you have any questions about this recipe, feel free to ask!
- User: I just added 95g of plain flour, how much matcha powder did I need again?
- Device: 5 grams.
- User: What is 5 grams of matcha in teaspoons?
- Device: According to Naoki Matcha, 2.5 teaspoons is equivalent to 5 grams of matcha.
- User: Do I need a high-quality matcha for this recipe?
- Device: According to the recipe, you only need culinary grade matcha.
- User: I just finished sifting the matcha and flour. What do I do next?
- Device: After sifting the matcha and flour, mix together your butter and sugar.

## Prototype your system

**Document how the system works**

My system is a voice-based baking assistant made of a web-based interface, a Raspberry Pi, a microphone, and a speaker. Its goal is to assist the user in answering questions about a recipe that the user is baking with.

The web interface was made by using `ollama_web_app.py` as a starting point. The original web app is a text-based chatroom style interaction with an ollama model, and I wanted to use the existing UI components and scripts for my own purposes. I wanted the user flow to be as follows:

1. When the user loads the page, there is a message and input box asking them to copy and paste their recipe.
2. After the user submits the recipe, the assistant would send a message offering to answer any questions the user has.
3. The user would be able to click a "Record" button, where they could ask verbal questions about the recipe and get a spoken response back.

<img width="775" height="319" alt="Screenshot 2025-10-03 at 6 09 34 PM" src="https://github.com/user-attachments/assets/a89afd19-026e-46c0-a1f4-bdc89adcecab" />

I started by copying and pasting `ollama_web_app.py`'s python and html files to my own folder `baking_assistant` and toggled some of the UI components such as the font, buttons and scripts. For step 1, I used the existing input box code, and modified the javascript and python scripts. When the user submits their recipe, a function scrapes the recipe link for its ingredients and instructions, and uses that as the context for the recie along with additional prompting "You are a helpful baking assistant offering to help with the recipe. Don't use emojis, only use plain text without astericks, and keep responses brief."

For step 2, I made the first prompt "Hi, who are you?" so that the assistant would introduce itself.

For step 3, I modified one of the original buttons and corresponding scripts in `ollama_web_app.py` to record the user's questions for five seconds and process it using `KaldiRecognizer`. The resulting text would be used to query ollama with the original context, and the answer would be played through the speaker using `espeak`. 

<img width="814" height="741" alt="Screenshot 2025-10-03 at 1 22 51 AM" src="https://github.com/user-attachments/assets/8b0a8241-706b-4384-ba03-0d22f9fc03ba" />


**Include videos or screencaptures of both the system and the controller.**

[Link to Demo](https://drive.google.com/file/d/1Y26ckpSJJhdKyP64QI8ItOYiQOxGTHme/view?usp=drive_link)

## Test the system
Try to get at least two people to interact with your system. (Ideally, you would inform them that there is a wizard _after_ the interaction, but we recognize that can be hard.)

Answer the following:

### What worked well about the system and what didn't?
\*\**your answer here*\*\*

### What worked well about the controller and what didn't?

\*\**your answer here*\*\*

### What lessons can you take away from the WoZ interactions for designing a more autonomous version of the system?

\*\**your answer here*\*\*


### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?

\*\**your answer here*\*\*








