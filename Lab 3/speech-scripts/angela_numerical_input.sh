#!/usr/bin/env bash

# chat log: https://chatgpt.com/share/68da03e5-7c1c-800d-840d-00d8170e2013
# used chatgpt for initial code, tweaked question and did some debugging to get microphone input to work

# CONFIG
PROMPT="Please say your favorite number"
OUTPUT_FILE="response.wav"
MODEL_SIZE="tiny"   # whisper model size

# 1. Speak the prompt
sleep 2
echo "$PROMPT" | festival --tts
sleep 2

# 2. Record user response (5 seconds, mono, 16kHz)
echo "Recording... (speak now)"
arecord -d 5 -f S16_LE -r 16000 -c 1 -D hw:2,0 "$OUTPUT_FILE"
echo "Recording finished."

# 3. Transcribe using faster-whisper Python
python3 << 'EOF'
from faster_whisper import WhisperModel
import sys

model = WhisperModel("tiny", device="cpu", compute_type="int8")
segments, info = model.transcribe("response.wav", beam_size=5)

result_text = ""
for segment in segments:
    result_text += segment.text.strip() + " "

print("\nTranscription result:", result_text.strip())
with open("response.txt", "w") as f:
    f.write(result_text.strip())
EOF

# 4. Confirm back to user
echo "You said: $(cat response.txt)" | festival --tts
