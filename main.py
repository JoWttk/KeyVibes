from pynput import keyboard
import pygame
import threading
import tkinter as tk
from tkinter import ttk
import os
import json

SOUND_FOLDER = "sounds"
CONFIG_PATH = "config.json"

pygame.mixer.init()
SOUNDS = {
    "space": pygame.mixer.Sound(os.path.join(SOUND_FOLDER, "espaco.wav")),
    "enter": pygame.mixer.Sound(os.path.join(SOUND_FOLDER, "enter-apagar.wav")),
    "key": pygame.mixer.Sound(os.path.join(SOUND_FOLDER, "key.wav"))
}

DEFAULT_VOLUMES = {
    "space": 0.5,
    "enter": 0.5,
    "key": 0.5
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                return {k: float(data.get(k, DEFAULT_VOLUMES[k])) for k in DEFAULT_VOLUMES}
        except:
            return DEFAULT_VOLUMES.copy()
    return DEFAULT_VOLUMES.copy()

def save_config(volumes):
    with open(CONFIG_PATH, "w") as f:
        json.dump(volumes, f)

VOLUMES = load_config()

for key, sound in SOUNDS.items():
    sound.set_volume(VOLUMES[key])

key_state = {}

def play(sound_key):
    def _play():
        SOUNDS[sound_key].set_volume(VOLUMES[sound_key])
        SOUNDS[sound_key].play()
    threading.Thread(target=_play, daemon=True).start()

def on_press(key):
    try:
        if hasattr(key, 'char'): 
            if key.char not in key_state or not key_state[key.char]:
                key_state[key.char] = True
                play("key")
        elif key == keyboard.Key.space:
            if not key_state.get('space', False):
                key_state['space'] = True
                play("space")
        elif key == keyboard.Key.enter:
            if not key_state.get('enter', False):
                key_state['enter'] = True
                play("enter")
    except Exception as e:
        print("Erro:", e)

def on_release(key):
    try:
        if hasattr(key, 'char'): 
            if key.char in key_state:
                key_state[key.char] = False
        elif key == keyboard.Key.space:
            key_state['space'] = False
        elif key == keyboard.Key.enter:
            key_state['enter'] = False
    except Exception as e:
        print("Erro:", e)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def start_gui():
    def update_volume(sound_key, value):
        VOLUMES[sound_key] = float(value)

    def on_close():
        save_config(VOLUMES)
        listener.stop()
        root.destroy()

    root = tk.Tk()
    root.title("Key Vibes")
    root.geometry("320x220")
    root.resizable(False, False)

    title = ttk.Label(root, text="Volume Controller", font=("Segoe UI", 12, "bold"))
    title.pack(pady=(10, 5))

    for key, label in [("space", "Space"), ("enter", "Enter"), ("key", "Keys")]:
        ttk.Label(root, text=label, font=("Segoe UI", 10)).pack(pady=(5, 0))
        slider = ttk.Scale(root, from_=0.0, to=1.0, value=VOLUMES[key], command=lambda val, k=key: update_volume(k, val))
        slider.pack(padx=20, fill="x")

    ttk.Button(root, text="Close", command=on_close).pack(pady=15)

    root.mainloop()

start_gui()
