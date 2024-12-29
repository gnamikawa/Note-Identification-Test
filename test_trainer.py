import pytest
from unittest.mock import Mock, patch
from trainer import NoteTrainer
from midi_manager import MidiPortManager
from tkinter import Tk, PhotoImage


@pytest.fixture
def trainer_app(monkeypatch):
    # Mock the MIDI manager to prevent real MIDI initialization
    mock_midi_manager = Mock(spec=MidiPortManager)
    mock_midi_manager.get_ports.return_value = ["MIDI Device 1", "MIDI Device 2"]
    monkeypatch.setattr("trainer.MidiPortManager", lambda: mock_midi_manager)

    # Create the trainer app
    root = Tk()

    # Mock the NoteImageManager to prevent image rendering issues
    with patch(
        "trainer.NoteImageManager.render_note_image",
        return_value=PhotoImage(master=root),
    ):
        app = NoteTrainer(root)
        app.midi_manager = mock_midi_manager  # Override with mock
        yield app
        root.destroy()


def test_midi_port_dropdown(trainer_app):
    # Simulate monitoring connection with mocked ports
    trainer_app.monitor_connection()

    # Assert that the dropdown updated with the mocked ports
    assert trainer_app.port_var.get() == "MIDI Device 1"
    assert trainer_app.available_ports == ["MIDI Device 1", "MIDI Device 2"]


def test_midi_label_reacts_to_connection(trainer_app):
    # Set up initial state with no devices
    trainer_app.midi_manager.get_ports.side_effect = [[], ["MIDI Device 1"], []]

    # Validate is_port_open behavior directly to match app logic
    trainer_app.midi_manager.is_port_open.side_effect = [False, True, False]

    # First call: No devices connected
    trainer_app.monitor_connection()
    assert trainer_app.status_label.cget("text") == "Status: Disconnected"
    assert trainer_app.status_label.cget("fg") == "red"

    # Simulate connected state
    trainer_app.monitor_connection()
    assert trainer_app.status_label.cget("text") == "Status: Connected"
    assert trainer_app.status_label.cget("fg") == "green"

    # Simulate disconnected state
    trainer_app.monitor_connection()
    assert trainer_app.status_label.cget("text") == "Status: Disconnected"
    assert trainer_app.status_label.cget("fg") == "red"
