import tkinter as tk
from tkinter import messagebox
import random
from config import Config
from midi_manager import MidiPortManager
from note_image import NoteImageManager
from logger import CSVLogger
from timer import Timer
from ulid import ulid
from concurrent.futures import ThreadPoolExecutor
import os
from PIL import Image, ImageTk
import time
from typing import Optional


class NoteTrainer:
    def __init__(self, master: tk.Tk):
        self.master: tk.Tk = master
        self.master.title("Note Reading Trainer (rtmidi)")
        self.master.geometry("800x600")
        self.master.resizable(False, False)  # Make the UI unresizable
        self.midi_manager: MidiPortManager = MidiPortManager()
        self.logger: CSVLogger = CSVLogger(Config.OUTPUT_CSV)
        self.timer: Timer = Timer()
        self.total_time: float = 0.0
        self.attempts: int = 0
        self.available_ports: list[str] = []
        self.status_label: Optional[tk.Label] = None
        self.last_connection_state: Optional[bool] = None
        self.selected_port: Optional[str] = None
        self.session_id: Optional[str] = None
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=os.cpu_count()
        )
        self._clean_up_and_regenerate_notes()
        self._initialize_ui()
        self._select_initial_device()
        self._populate_cache()
        self._show_random_note()

    def _clean_up_and_regenerate_notes(self) -> None:
        NoteImageManager.clean_up_musicxml_files()
        NoteImageManager.regenerate_missing_notes()

    def _initialize_ui(self) -> None:
        self.available_ports = self.midi_manager.get_ports()
        tk.Label(self.master, text="Select MIDI Input Port:").pack()
        self.port_var: tk.StringVar = tk.StringVar(self.master)
        self.port_var.set(
            self.available_ports[0] if self.available_ports else "No Ports Available"
        )
        self.port_menu: tk.OptionMenu = tk.OptionMenu(
            self.master,
            self.port_var,
            *self.available_ports if self.available_ports else ["No Ports Available"],
        )
        self.port_menu.pack()  # Ensure the port_menu is packed into the UI
        # Add a frame to contain the note image
        self.note_frame: tk.Frame = tk.Frame(self.master)
        self.note_frame.pack(pady=20, expand=True, fill="both")

        self.note_label: tk.Label = tk.Label(self.note_frame)
        self.note_label.pack(expand=True)

        self.time_label: tk.Label = tk.Label(self.master, text="Time Taken: 0.000s")
        self.time_label.pack(pady=5)
        self.correct_note_label: tk.Label = tk.Label(self.master, text="")
        self.correct_note_label.pack(pady=5)
        self.status_label = tk.Label(self.master, text="Status: Disconnected", fg="red")
        self.status_label.pack(pady=5)
        tk.Button(self.master, text="Next Note", command=self._show_random_note).pack(
            pady=10
        )
        self._monitor_connection()

    def _update_time_label(self) -> None:
        if self.timer.start_time is not None:
            elapsed_time = time.time() - self.timer.start_time
            self.time_label.config(text=f"Time Taken: {elapsed_time:.2f}s")
        self.master.after(10, self._update_time_label)

    def _select_initial_device(self) -> None:
        if self.available_ports:
            self.selected_port = self.available_ports[0]
            self.port_var.set(
                self.selected_port
            )  # Update port_var to the first available port
            self._on_select_midi_port(self.selected_port)
        else:
            self.selected_port = None

    def _on_select_midi_port(self, port: str) -> None:
        try:
            idx = self.available_ports.index(port)
            self.midi_manager.open_port(idx, self._midi_callback)
            self.selected_port = port
        except ValueError:
            messagebox.showerror("Error", "Selected port not found in list.")

    def _midi_callback(self, event: list[int], data: Optional[any] = None) -> None:
        if not event or len(event) < 1:
            return
        message = event
        if (message[0] & 0xF0) == 0x90 and message[2] > 0:  # Note-On event
            midi_note = message[1]
            # Look up in full note range
            guessed_note = next(
                (
                    key
                    for key, value in Config.NOTE_TO_MIDI.items()
                    if value == midi_note
                ),
                f"Note{midi_note}",  # Show actual note number instead of Unknown
            )
            time_taken = self.timer.stop()
            self.total_time += time_taken
            self.attempts += 1
            # Validate against tested range
            is_correct = Config.TESTED_NOTES.get(self.current_note) == midi_note

            if self.session_id is None:
                self.session_id = str(ulid())

            # Log the result, including the guessed note
            self.logger.log_result(
                self.session_id,
                self.current_note,
                guessed_note,
                time_taken,  # Log time_taken in seconds
                self._get_timestamp(),
            )

            if is_correct:
                self.correct_note_label.config(
                    text=f"Correct: {self.current_note} in {time_taken:.3f}s",
                    fg="green",
                )
                print(f"Correct! Played note matches: {self.current_note}")
                self.total_time = 0.0  # Reset total time for the next note
                self.attempts = 0
                self.session_id = None  # Reset session ID for the next note
                self._show_random_note()
            else:
                self.correct_note_label.config(
                    text="",
                )
                self.total_time += time_taken  # Update total time for incorrect note
                print(
                    f"Incorrect. Played {midi_note}, Expected {Config.NOTE_TO_MIDI.get(self.current_note)}"
                )

    def _monitor_connection(self) -> None:
        current_ports = self.midi_manager.get_ports()
        current_state = bool(current_ports and self.midi_manager.is_port_open())

        if self.midi_manager.has_ports_changed():
            self.available_ports = current_ports
            self._update_port_menu()

            # Automatically reconnect if the previously selected port is reconnected
            if self.selected_port in self.available_ports:
                self._on_select_midi_port(self.selected_port)
            elif self.available_ports:  # Select the first available port
                self._select_initial_device()
            else:  # No ports available
                self.status_label.config(text="Status: Disconnected", fg="red")

        if current_state != self.last_connection_state:
            self.status_label.config(
                text="Status: Connected" if current_state else "Status: Disconnected",
                fg="green" if current_state else "red",
            )
            self.last_connection_state = current_state

        self.master.after(500, self._monitor_connection)

    def _update_port_menu(self) -> None:
        menu = self.port_menu.children["menu"]
        menu.delete(0, "end")
        for port in self.available_ports:
            menu.add_command(
                label=port, command=lambda value=port: self.port_var.set(value)
            )
        self.port_var.set(
            self.selected_port
            if self.selected_port in self.available_ports
            else "No Ports Available"
        )

    def _populate_cache(self) -> None:
        for note in Config.NOTE_TO_MIDI.keys():
            image_path = NoteImageManager.get_image_path(note)
            if not os.path.isfile(image_path):
                self.executor.submit(NoteImageManager.render_note_image, note)

    def _show_random_note_thread(self) -> None:
        # Select from tested notes only
        self.current_note = random.choice(list(Config.TESTED_NOTES.keys()))
        try:
            image = NoteImageManager.render_note_image(self.current_note)
            self.original_image = image  # Store original image
            self.note_label.config(
                image=image, text="" if image else f"No image for {self.current_note}"
            )
            self.note_label.image = image
        except Exception as e:
            self.note_label.config(
                text=f"Error displaying note: {self.current_note} because {e}"
            )
        self.timer.start()
        self.time_label.config(text="Time Taken: 0.000s")
        self._update_time_label()

    def _show_random_note(self) -> None:
        self.timer.start()
        self.executor.submit(self._show_random_note_thread)
        self.executor.submit(self._show_random_note_thread)

    def _get_timestamp(self) -> str:
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
