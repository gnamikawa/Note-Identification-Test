# MIDI Note Reading Trainer

A Python application to help musicians practice note reading using a MIDI keyboard.

## Features

- Real-time MIDI input detection
- Visual note display using musical notation
- Performance tracking and logging
- Multiple octave range support (A0-C8)
- Automatic MIDI device detection and connection
- Session-based practice tracking

## Requirements

- Python 3.x
- MIDI keyboard/device
- Required Python packages:
  ```
  python-rtmidi
  Pillow
  ```

## Installation

1. Clone this repository
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Connect your MIDI keyboard to your computer
2. Run the application:
   ```sh
   python main.py
   ```
3. Select your MIDI input device from the dropdown menu
4. Practice by playing the displayed notes on your MIDI keyboard
5. Results are logged to a CSV file for tracking progress

## Project Structure

- [`main.py`](main.py) - Application entry point
- [`trainer.py`](trainer.py) - Main application logic and UI
- [`midi_manager.py`](midi_manager.py) - MIDI device handling
- [`note_image.py`](note_image.py) - Musical notation rendering
- [`config.py`](config.py) - Application configuration and note mappings
- [`logger.py`](logger.py) - Performance logging to CSV
- [`timer.py`](timer.py) - Time tracking utilities
- [`test_trainer.py`](test_trainer.py) - Unit tests

## Testing

Run the test suite using pytest:

```sh
pytest test_trainer.py
```

## License

MIT
