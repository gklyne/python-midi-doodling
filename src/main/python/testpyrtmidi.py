# testqt6shapes.py

import sys
# from enum import Enum
# from copy import copy
import time

import rtmidi

# @@TODO:
#
#


# ---- Test helper ----

def assertEq(s1, s2):
    if s1 != s2:
        print(f"AssertEq: {s1} != {s2}")
        raise AssertionError(("Eq", s1, s2))

# ---- Test simple sound output - scale of notes C-C


def _print_device_info(available_ports):
    for i in range(len(available_ports)):
        print(f"Port {i:02d}: {available_ports[i]:s}")

def test_piano_scale(device_id=None):

    GRAND_PIANO = 0
    CHURCH_ORGAN = 19

    MIDI_NUMBER_MID_C = 60
    MIDI_NAME_MID_C   = "C3"


    MIDI_NOTE_C3  = 60
    MIDI_NOTE_C3s = 61
    MIDI_NOTE_D3  = 62
    MIDI_NOTE_D3s = 63
    MIDI_NOTE_E3  = 64
    MIDI_NOTE_F3  = 65
    MIDI_NOTE_F3s = 66
    MIDI_NOTE_G3  = 67
    MIDI_NOTE_G3s = 68
    MIDI_NOTE_A3  = 69
    MIDI_NOTE_A3s = 70
    MIDI_NOTE_B3  = 71
    MIDI_NOTE_C4  = 72

    instrument = GRAND_PIANO
    #instrument = CHURCH_ORGAN

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    
    if available_ports:
        _print_device_info(available_ports)
        midiout.open_port(2)
    else:
        midiout.open_virtual_port("My virtual output")

    try:
        for i in range(2):
            scale_notes = (
                MIDI_NOTE_C3,
                MIDI_NOTE_D3,
                MIDI_NOTE_E3,
                MIDI_NOTE_F3,
                MIDI_NOTE_G3,
                MIDI_NOTE_A3,
                MIDI_NOTE_B3,
                MIDI_NOTE_C4,
                )


            for note in (scale_notes):
                print(f"Play note {note}")
                note_on  = [0x90, note, 112]
                note_off = [0x80, note, 0]
                midiout.send_message(note_on)
                time.sleep(0.5)
                midiout.send_message(note_off)
                time.sleep(0.1)

    finally:
        # midiout.close()
        del midiout

    # Exit


test_piano_scale(6)
