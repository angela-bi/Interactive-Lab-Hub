#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# used ollama_web_app.py and ollama_convo.py as reference code for chatGPT to adapt to my goals.
# chat logs: https://chatgpt.com/share/68da08ff-659c-800d-b18a-c2fb90eb6e78

import requests
import json
import subprocess
import sys
import sounddevice as sd
import queue
from vosk import Model, KaldiRecognizer
import requests
from bs4 import BeautifulSoup

# Globals
RECIPE_CONTEXT = None   # stored recipe
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "phi3:mini"


def speak_text(text):
    """Text-to-speech using espeak"""
    clean_text = text.encode('ascii', 'ignore').decode('ascii')
    print(f"\nAssistant: {clean_text}")
    subprocess.run(['espeak', f'"{clean_text}"'], check=False)


def query_ollama(prompt, model=DEFAULT_MODEL):
    """Send text prompt to Ollama and stream response"""
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
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


def check_ollama():
    """Check Ollama connection"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            names = [m['name'] for m in models]
            print(f"Ollama running. Models: {names}")
            return True
        else:
            print("Ollama not responding")
            return False
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return False


def listen_and_transcribe():
    """Capture voice and return recognized text"""
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    model = Model(lang="en-us")

    # pick default mic device (change if needed)
    device_id = None   # None = default mic
    device_info = sd.query_devices(device_id, "input")
    samplerate = int(device_info["default_samplerate"])

    rec = KaldiRecognizer(model, samplerate)

    print("\n Speak now (say 'quit' to exit)")
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                           device=device_id, dtype="int16",
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = json.loads(result).get("text", "")
                if text.strip():
                    return text

def get_recipe_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # --- INGREDIENTS ---
    ingredients = []
    for li in soup.find_all("li", class_="wprm-recipe-ingredient"):
        amount = li.find("span", class_="wprm-recipe-ingredient-amount")
        unit = li.find("span", class_="wprm-recipe-ingredient-unit")
        name = li.find("span", class_="wprm-recipe-ingredient-name")

        ingredient_text = " ".join(
            filter(None, [
                amount.get_text(strip=True) if amount else None,
                unit.get_text(strip=True) if unit else None,
                name.get_text(strip=True) if name else None
            ])
        )
        if ingredient_text:
            ingredients.append(ingredient_text)

    # --- INSTRUCTIONS ---
    instructions = []
    for idx, li in enumerate(soup.find_all("li", class_="wprm-recipe-instruction"), start=1):
        step = li.find("div", class_="wprm-recipe-instruction-text")
        if step:
            step_text = step.get_text(" ", strip=True)  # preserve spaces in <span>/<div>
            instructions.append(f"Step {idx}: {step_text}")

    return {
        "ingredients": ingredients,
        "instructions": instructions
    }


def main():
    print("=== Baking Assistant (Voice Mode) ===")
    if not check_ollama():
        return

    recipe_input = input("\n Paste recipe text or URL:\n")

    global RECIPE_CONTEXT

    if recipe_input.startswith("http") or recipe_input.startswith("https"):
        print('Fetching recipe from url....')
        RECIPE_CONTEXT = get_recipe_from_url(recipe_input)
        print('recipe context: ', RECIPE_CONTEXT)
    else:
        RECIPE_CONTEXT = recipe_input

    while True:
        text = listen_and_transcribe()
        print(f"\nYou said: {text}")

        if text.lower() in ["quit", "exit", "goodbye"]:
            print("Exiting...")
            break

        # Add recipe as context
        full_prompt = f"Here is the recipe:\n{RECIPE_CONTEXT}\n\nUser question: {text}\nAnswer as a helpful baking assistant. Don't use emojis in your responses."
        
        print("Thinking...")
        response = query_ollama(full_prompt)
        speak_text(response)


if __name__ == "__main__":
    main()
