import tkinter as tk
import random
import time
import csv
import os
from functools import lru_cache
import rtmidi
from PIL import ImageTk
import musictheory as mt
from music21 import stream, note, converter
from PIL import Image, ImageTk
from functools import lru_cache
import io
from music21 import *


class Config:
    NOTE_TO_MIDI = {
        "C0": 12,
        "C#0": 13,
        "D0": 14,
        "D#0": 15,
        "E0": 16,
        "F0": 17,
        "F#0": 18,
        "G0": 19,
        "G#0": 20,
        "A0": 21,
        "A#0": 22,
        "B0": 23,
        "C1": 24,
        "C#1": 25,
        "D1": 26,
        "D#1": 27,
        "E1": 28,
        "F1": 29,
        "F#1": 30,
        "G1": 31,
        "G#1": 32,
        "A1": 33,
        "A#1": 34,
        "B1": 35,
        "C2": 36,
        "C#2": 37,
        "D2": 38,
        "D#2": 39,
        "E2": 40,
        "F2": 41,
        "F#2": 42,
        "G2": 43,
        "G#2": 44,
        "A2": 45,
        "A#2": 46,
        "B2": 47,
        "C3": 48,
        "C#3": 49,
        "D3": 50,
        "D#3": 51,
        "E3": 52,
        "F3": 53,
        "F#3": 54,
        "G3": 55,
        "G#3": 56,
        "A3": 57,
        "A#3": 58,
        "B3": 59,
        "C4": 60,
        "C#4": 61,
        "D4": 62,
        "D#4": 63,
        "E4": 64,
        "F4": 65,
        "F#4": 66,
        "G4": 67,
        "G#4": 68,
        "A4": 69,
        "A#4": 70,
        "B4": 71,
        "C5": 72,
        "C#5": 73,
        "D5": 74,
        "D#5": 75,
        "E5": 76,
        "F5": 77,
        "F#5": 78,
        "G5": 79,
        "G#5": 80,
        "A5": 81,
        "A#5": 82,
        "B5": 83,
        "C6": 84,
        "C#6": 85,
        "D6": 86,
        "D#6": 87,
        "E6": 88,
        "F6": 89,
        "F#6": 90,
        "G6": 91,
        "G#6": 92,
        "A6": 93,
        "A#6": 94,
        "B6": 95,
        "C7": 96,
        "C#7": 97,
        "D7": 98,
        "D#7": 99,
        "E7": 100,
        "F7": 101,
        "F#7": 102,
        "G7": 103,
        "G#7": 104,
        "A7": 105,
        "A#7": 106,
        "B7": 107,
        "C8": 108,
    }
    OUTPUT_CSV = "results.csv"


class MidiPortManager:
    def __init__(self):
        self.rtmidi_in = rtmidi.MidiIn()
        self.current_ports = self.get_ports()

    def get_ports(self):
        return self.rtmidi_in.get_ports()

    def open_port(self, port_index, callback):
        if self.rtmidi_in.is_port_open():
            self.rtmidi_in.close_port()
        self.rtmidi_in.open_port(port_index)
        self.rtmidi_in.set_callback(callback)

    def is_port_open(self):
        return self.rtmidi_in.is_port_open()

    def has_ports_changed(self):
        new_ports = self.get_ports()
        if new_ports != self.current_ports:
            self.current_ports = new_ports
            return True
        return False


class NoteImageManager:
    @staticmethod
    @lru_cache(maxsize=32)
    def render_note_image(note_name):
        try:
            # Create a music21 stream
            s = stream.Stream()
            n = note.Note(note_name)
            s.append(n)
            png_path = s.write(fmt="musicxml.png")

            # Convert PNG binary data to a PIL image
            image = Image.open(png_path)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            raise ValueError(f"The note '{note_name}' could not be rendered: {e}")


class CSVLogger:
    def __init__(self, output_file):
        self.output_file = output_file
        self.setup_csv()

    def setup_csv(self):
        if not os.path.isfile(self.output_file):
            with open(self.output_file, mode="w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["was_correct", "tested_note", "time_taken"])

    def log_result(self, was_correct, note, time_taken):
        with open(self.output_file, mode="a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([str(was_correct), note, f"{time_taken:.3f}"])


class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        return 0 if self.start_time is None else time.time() - self.start_time


class NoteTrainer:
    def __init__(self, master):
        self.master = master
        self.master.title("Note Reading Trainer (rtmidi)")
        self.midi_manager = MidiPortManager()
        self.logger = CSVLogger(Config.OUTPUT_CSV)
        self.timer = Timer()
        self.available_ports = self.midi_manager.get_ports()
        self.status_label = None
        self.last_connection_state = None
        self.create_widgets()
        self.select_initial_device()
        self.show_random_note()

    def create_widgets(self):
        tk.Label(self.master, text="Select MIDI Input Port:").pack()
        self.port_var = tk.StringVar(self.master)
        self.port_var.set(
            self.available_ports[0] if self.available_ports else "No Ports Available"
        )
        self.port_menu = tk.OptionMenu(
            self.master,
            self.port_var,
            *self.available_ports if self.available_ports else ["No Ports Available"],
            command=self.on_select_midi_port,
        )
        self.port_menu.pack(pady=5)
        self.status_label = tk.Label(self.master, text="Status: Disconnected", fg="red")
        self.status_label.pack(pady=5)
        self.note_label = tk.Label(self.master)
        self.note_label.pack(pady=20)
        tk.Button(self.master, text="Next Note", command=self.show_random_note).pack(
            pady=10
        )
        self.monitor_connection()

    def select_initial_device(self):
        if self.available_ports:
            self.on_select_midi_port(self.available_ports[0])

    def on_select_midi_port(self, port):
        try:
            idx = self.available_ports.index(port)
            self.midi_manager.open_port(idx, self.midi_callback)
        except ValueError:
            messagebox.showerror("Error", "Selected port not found in list.")

    def midi_callback(self, event, data=None):
        message, _ = event
        if (message[0] & 0xF0) == 0x90 and message[2] > 0:
            print(f"Note On: {message[1]}")

    def monitor_connection(self):
        current_ports = self.midi_manager.get_ports()
        current_state = bool(current_ports and self.midi_manager.is_port_open())
        if current_state != self.last_connection_state:
            self.status_label.config(
                text="Status: Connected" if current_state else "Status: Disconnected",
                fg="green" if current_state else "red",
            )
            self.last_connection_state = current_state
        if self.midi_manager.has_ports_changed():
            self.available_ports = current_ports
            self.port_var.set(
                self.available_ports[0]
                if self.available_ports
                else "No Ports Available"
            )
            self.update_port_menu()
        self.master.after(500, self.monitor_connection)

    def update_port_menu(self):
        menu = self.port_menu.children["menu"]
        menu.delete(0, "end")
        for port in self.available_ports:
            menu.add_command(
                label=port, command=lambda value=port: self.port_var.set(value)
            )

    def show_random_note(self):
        self.current_note = random.choice(list(Config.NOTE_TO_MIDI.keys()))
        image = NoteImageManager.render_note_image(self.current_note)
        self.note_label.config(
            image=image, text="" if image else f"No image for {self.current_note}"
        )
        self.note_label.image = image
        self.timer.start()


if __name__ == "__main__":
    us = environment.UserSettings()
    us["musescoreDirectPNGPath"] = r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe"

    root = tk.Tk()
    app = NoteTrainer(root)
    root.mainloop()
