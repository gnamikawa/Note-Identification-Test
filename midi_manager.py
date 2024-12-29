
import rtmidi

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
