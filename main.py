import rtmidi
from pythonosc import udp_client, osc_server
from pythonosc.dispatcher import Dispatcher

DEFAULT_COLOR = 3
DEFAULT_CHANNEL = 0x90
ON_CHANNEL = 0x9B
OFF_CHANNEL = 0x96


class OSC2MIDI:
    def __init__(self) -> None:
        self.midiin = rtmidi.MidiIn()
        self.midiout = rtmidi.MidiOut()

        input_ports = self.midiin.get_ports()
        for i in range(len(input_ports)):
            print(f"Input port {i}: {input_ports[i]}")

        input_port_id = int(input("Enter input port id: "))
        self.midiin.open_port(input_port_id)

        output_ports = self.midiout.get_ports()
        for i in range(len(output_ports)):
            print(f"Output port {i}: {output_ports[i]}")

        output_port_id = int(input("Enter output port id: "))
        self.midiout.open_port(output_port_id)

    def midi_out_callback(self, node, value):
        if "/node/" in node:
            original_value = int(value * 255)
            is_active = original_value >> 7
            note = int(node.split("/")[-1])
            midi_value = original_value & 0x7F
            if 0x64 <= note <= 0x77:
                channel = 0x90
                if original_value == 0:
                    midi_value = 0  # Off
                elif original_value == 255:
                    midi_value = 0x03  # On
                else:
                    midi_value = 0x02  # Blink
            else:
                channel = ON_CHANNEL if is_active else OFF_CHANNEL
            node_out = [channel, note, midi_value]
            self.midiout.send_message(node_out)

    def on_midi_in(self, x, _):
        note, __ = x
        midi_cmd = note[0] & 0xF0
        note_number = note[1]
        if midi_cmd == 0x90:
            # node on
            self.client.send_message(f"/node/{note_number}", 1)
        elif midi_cmd == 0x80:
            # node off
            self.client.send_message(f"/node/{note_number}", 0)
        else:
            value = int((note[2] * 255) / 127)
            self.client.send_message(f"/slider/{note_number}", value)

    def init_surface(self):
        for pad in range(0x40):
            node_out = [DEFAULT_CHANNEL, pad, DEFAULT_COLOR]
            self.midiout.send_message(node_out)

    def start(self):
        self.init_surface()
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 7700)
        dispatcher = Dispatcher()
        dispatcher.map("*", self.midi_out_callback)
        server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9000), dispatcher)
        self.midiin.set_callback(self.on_midi_in)

        print("OSC Server started")
        server.serve_forever()


if __name__ == "__main__":
    a = OSC2MIDI()
    a.start()
