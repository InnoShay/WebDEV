import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyautogui
from pynput import keyboard as pynput_keyboard
import re
import threading

stop_flag = False
notes = []
current_index = 0

def parse_input(text):
    pattern = re.compile(r'\[.*?\]|[a-zA-Z0-9]|\|| ')
    chunks = pattern.findall(text)
    result = []

    for chunk in chunks:
        if chunk.startswith('[') and chunk.endswith(']'):
            keys = list(chunk[1:-1])
            if len(keys) > 1:
                result.append({'type': 'chord', 'keys': keys})
            else:
                result.append({'type': 'single', 'key': keys[0]})
        elif chunk == '|':
            result.append({'type': 'pause'})
        elif chunk == ' ':
            continue
        else:
            result.append({'type': 'single', 'key': chunk})
    return result

def tap(key):
    pyautogui.keyDown(key)
    pyautogui.keyUp(key)

def play_next():
    global current_index, notes_list, stop_flag

    if stop_flag or current_index >= len(notes_list):
        return

    step = notes_list[current_index]

    if step['type'] == 'chord':
        threads = [threading.Thread(target=tap, args=(k,)) for k in step['keys']]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    elif step['type'] == 'single':
        pyautogui.press(step['key'])

    current_index += 1

def load_notes():
    global notes_list, current_index, stop_flag
    stop_flag = False
    raw = note_text.get("1.0", tk.END).strip()

    if not raw:
        messagebox.showwarning("Empty Input", "Paste some notes first.")
        return

    notes_list = parse_input(raw)
    current_index = 0

def stop_playback():
    global stop_flag
    stop_flag = True

def monitor_dash():
    def on_press(key):
        try:
            if key.char == '-':
                play_next()
        except AttributeError:
            pass

    pynput_keyboard.Listener(on_press=on_press).start()

app = tk.Tk()
app.title("Virtual piano autoplayer")
app.geometry("550x360")
app.config(bg="#1e1e1e")

style = ttk.Style()
style.theme_use('clam')

style.configure("Chad.TButton", font=("Arial", 12, "bold"), foreground="white",
                background="#00c853", padding=10)
style.map("Chad.TButton", background=[("active", "#00e676")])

style.configure("Stop.TButton", font=("Arial", 12, "bold"), foreground="white",
                background="#d50000", padding=10)
style.map("Stop.TButton", background=[("active", "#ff1744")])

tk.Label(app, text="Enter your notes:", font=("Arial", 14), fg="white", bg="#1e1e1e").pack(pady=10)

note_text = tk.Text(app, height=6, font=("Consolas", 14), bg="#2e2e2e", fg="lime")
note_text.pack(padx=20, pady=10, fill="both")

btns = tk.Frame(app, bg="#1e1e1e")
btns.pack(pady=10)

ttk.Button(btns, text="📥 Load", command=load_notes, style="Chad.TButton").grid(row=0, column=0, padx=5)
ttk.Button(btns, text="🛑 Stop", command=stop_playback, style="Stop.TButton").grid(row=0, column=1, padx=5)

tk.Label(app, text="Press '-' to play next note", font=("Arial", 12), fg="cyan", bg="#1e1e1e").pack(pady=5)

monitor_dash()
app.mainloop()