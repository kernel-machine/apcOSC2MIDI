import rtmidi
from pythonosc import udp_client, osc_server
from pythonosc.dispatcher import Dispatcher

midiin = rtmidi.MidiIn()
midiout = rtmidi.MidiOut()

input_ports = midiin.get_ports()
for i in range(len(input_ports)):
    print(f"Input port {i}: {input_ports[i]}")

input_port_id = int(input("Enter input port id: "))
midiin.open_port(input_port_id)

output_ports = midiout.get_ports()
for i in range(len(output_ports)):
    print(f"Output port {i}: {output_ports[i]}")

output_port_id = int(input("Enter output port id: "))
midiout.open_port(output_port_id)

client = udp_client.SimpleUDPClient("127.0.0.1", 7700)
dispatcher = Dispatcher()


def midi_out_callback(node, value):
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
                midi_value = 0x02  # Blink
            else:
                midi_value = 0x03  # On
        else:
            channel = 0x9B if is_active else 0x96
        node_out = [channel, note, midi_value]
        midiout.send_message(node_out)


dispatcher.map("*", midi_out_callback)
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9000), dispatcher)


def on_midi_in(x, _):
    note, __ = x
    midi_cmd = note[0] & 0xF0
    note_number = note[1]
    if midi_cmd == 0x90:
        # node on
        client.send_message(f"/node/{note_number}", 1)
    elif midi_cmd == 0x80:
        # node off
        client.send_message(f"/node/{note_number}", 0)
    else:
        value = int((note[2] * 255) / 127)
        client.send_message(f"/slider/{note_number}", value)


midiin.set_callback(on_midi_in)

print("OSC Server started")
server.serve_forever()
