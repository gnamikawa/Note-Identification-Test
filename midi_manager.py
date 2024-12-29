import rtmidi


class MidiPortManager:
    def __init__(self):
        """Initialize the MIDI port manager."""
        self.rtmidi_in: rtmidi.MidiIn = rtmidi.MidiIn()
        self.current_ports: list[str] = self.get_ports()

    def get_ports(self) -> list[str]:
        """Get the list of available MIDI ports.

        Returns:
            list[str]: The list of available MIDI ports.
        """
        return self.rtmidi_in.get_ports()

    def open_port(self, port_index: int, callback: callable) -> None:
        """Open the specified MIDI port and set the callback for incoming messages.

        Args:
            port_index (int): The index of the MIDI port to open.
            callback (callable): The callback function for incoming MIDI messages.
        """
        if self.rtmidi_in.is_port_open():
            self.rtmidi_in.close_port()
        self.rtmidi_in.open_port(port_index)
        self.rtmidi_in.set_callback(callback)

    def is_port_open(self) -> bool:
        """Check if a MIDI port is currently open.

        Returns:
            bool: True if a MIDI port is open, False otherwise.
        """
        return self.rtmidi_in.is_port_open()

    def has_ports_changed(self) -> bool:
        """Check if the list of available MIDI ports has changed.

        Returns:
            bool: True if the list of available MIDI ports has changed, False otherwise.
        """
        new_ports = self.get_ports()
        if new_ports != self.current_ports:
            self.current_ports = new_ports
            return True
        return False
