from unittest.mock import patch, MagicMock
from config import Config
from note_image import NoteImageManager
from trainer import NoteTrainer
from tkinter import Tk, PhotoImage, OptionMenu
import os
import random
import time


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Update_Midi_Port_Dropdown(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value
    mock_midi_manager.get_ports.return_value = ["MIDI Device 1", "MIDI Device 2"]

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager
    app.available_ports = mock_midi_manager.get_ports()

    # Simulate UI update
    app.port_var.set("MIDI Device 1")
    app.port_menu = OptionMenu(app.master, app.port_var, *app.available_ports)
    app.port_menu.pack()

    # Check if the OptionMenu contains the correct values
    menu = app.port_menu["menu"]
    menu_items = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1)]
    assert menu_items == ["MIDI Device 1", "MIDI Device 2"]

    # Check if the selected value is correct
    assert app.port_var.get() == "MIDI Device 1"

    root.destroy()


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_React_To_Midi_Connection(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value
    mock_midi_manager.get_ports.side_effect = [
        [],
        ["MIDI Device 1"],
        [],
        ["MIDI Device 1"],
        [],
    ]
    mock_midi_manager.is_port_open.side_effect = [False, True, False]
    mock_midi_manager.has_ports_changed.return_value = True

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager

    # Test each state
    app._monitor_connection()
    assert "Disconnected" in app.status_label.cget("text")

    app._monitor_connection()
    assert "Connected" in app.status_label.cget("text")

    app._monitor_connection()
    assert "Disconnected" in app.status_label.cget("text")
    root.destroy()


@patch("tkinter.OptionMenu", new=MagicMock())
@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Configure_Window(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    """Test window configuration settings"""
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager

    assert not app.master.resizable()[0]  # width not resizable
    assert not app.master.resizable()[1]  # height not resizable
    root.destroy()


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Initialize_Midi_Manager(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    """Test MIDI manager initialization and port setup"""
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value
    mock_midi_manager.get_ports.return_value = ["MIDI Device 1", "MIDI Device 2"]

    app = NoteTrainer(root)

    # Check if the OptionMenu contains the correct values
    menu = app.port_menu["menu"]
    menu_items = [menu.entrycget(i, "label") for i in range(menu.index("end") + 1)]
    assert menu_items == ["MIDI Device 1", "MIDI Device 2"]

    # Check if the selected value is correct
    assert app.port_var.get() == "MIDI Device 1"  # Should default to first port
    assert app.port_menu.cget("text") == "MIDI Device 1"  # Should be set in UI

    root.destroy()


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Handle_Midi_Callback_Correct_Note(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager
    app.current_note = random.choice(list(Config.TESTED_NOTES.keys()))
    midi_note = Config.TESTED_NOTES[app.current_note]

    app._midi_callback([0x90, midi_note, 127])

    assert "Correct" in app.correct_note_label.cget("text")
    assert app.total_time == 0.0
    assert app.attempts == 0

    root.destroy()


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Handle_Midi_Callback_Incorrect_Note(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager
    app.current_note = random.choice(list(Config.TESTED_NOTES.keys()))
    incorrect_midi_note = (Config.TESTED_NOTES[app.current_note] + 1) % 128

    app._midi_callback([0x90, incorrect_midi_note, 127])

    assert "Correct" not in app.correct_note_label.cget("text")
    assert app.total_time > 0.0
    assert app.attempts == 1

    root.destroy()


@patch("trainer.MidiPortManager")
@patch("trainer.NoteImageManager.render_note_image")
def test_Can_Update_Time_Label(
    mock_render_note_image: MagicMock, MockMidiPortManager: MagicMock
) -> None:
    root: Tk = Tk()
    mock_render_note_image.return_value = PhotoImage()
    mock_midi_manager = MockMidiPortManager.return_value

    app = NoteTrainer(root)
    app.midi_manager = mock_midi_manager
    app.timer.start()

    time.sleep(0.1)
    app._update_time_label()

    elapsed_time = float(app.time_label.cget("text").split(": ")[1][:-1])
    assert elapsed_time >= 0.1

    root.destroy()
