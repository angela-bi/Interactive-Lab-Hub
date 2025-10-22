#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# used ollama_demo.py as a jumping off point
# also used test_microphone.py
# chat logs: https://chatgpt.com/share/68da08ff-659c-800d-b18a-c2fb90eb6e78

import requests
import json
import subprocess
import sys
import os
import sounddevice as sd
import queue
from vosk import Model, KaldiRecognizer

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'UTF-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    import codecs
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def speak_text(text):
    """Simple text-to-speech using espeak"""
    # Clean text to avoid encoding issues
    clean_text = text.encode('ascii', 'ignore').decode('ascii')
    print(f"Assistant: {clean_text}")
    subprocess.run(['espeak', f'"{clean_text}"'], check=False)

def query_ollama(prompt, model="tinyllama"):
    """Send a text prompt to Ollama and stream response"""
    try:
        with requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=300
        ) as r:
            response_text = ""
            for line in r.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("response", "")
                    response_text += token
                    print(token, end="", flush=True)
            print()
            return response_text
    except Exception as e:
        return f"Error: {e}"


def voice_response_demo():
    """Demo: Text input, voice output"""
    print("\n=== VOICE RESPONSE DEMO ===")
    print("Type your message, Ollama will respond with voice")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYour message: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        print("Thinking...")
        response = query_ollama(user_input)
        speak_text(response)

def check_ollama():
    """Check if Ollama is running and model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"Ollama is running. Available models: {model_names}")
            return True
        else:
            print("Ollama is not responding")
            return False
    except Exception as e:
        print(f"Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running with: ollama serve")
        return False

def main():
    """Main demo menu"""
    print("Angela's Ollama conversation demo")
    print("=" * 30)
    
    # Check Ollama connection
    if not check_ollama():
        return
    
    # chatgpt generated, manually modified a bit due to mic issues
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    # load English Vosk model (change if you want another language)
    model = Model(lang="en-us")

    # pick default microphone device
    device_id = "hw:2,0"   # change this based on python -m sounddevice output
    device_info = sd.query_devices(device_id, "input")
    samplerate = int(device_info["default_samplerate"])

    rec = KaldiRecognizer(model, samplerate)

    print("\nSay something! (say 'quit' to exit)")
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                           device=device_id, dtype="int16",
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                import json
                text = json.loads(result).get("text", "")
                if not text.strip():
                    continue
                print(f"\nYou said: {text}")

                if text.lower() in ["quit", "exit", "goodbye"]:
                    print("Exiting...")
                    break

                print("Thinking...")
                response = query_ollama(text)
                speak_text(response)
                break
                # this was manually edited as well
        

if __name__ == "__main__":
    main()