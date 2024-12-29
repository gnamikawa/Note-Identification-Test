# MIDI Note Reading Trainer

A Python application to help musicians practice note reading using a MIDI keyboard.

Best combined with a statistics visualization tool. Recommended for use with Grafana. Anything that supports CSV should be compatible.

## Features

- Real-time MIDI input detection
- Visual note display using musical notation
- Success rate tracking and logging
- Automatic MIDI device detection and connection

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

## Testing

Run the test suite using pytest:

```sh
pytest test_trainer.py
```

## License

MIT
