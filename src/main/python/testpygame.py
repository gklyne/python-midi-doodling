# testpygame.py

import sys
# from enum import Enum
# from copy import copy
import time

import pygame
import pygame.midi


# @@TODO:
#
#


# ---- Test helper ----

def assertEq(s1, s2):
    if s1 != s2:
        print(f"AssertEq: {s1} != {s2}")
        raise AssertionError(("Eq", s1, s2))

# ---- Test simple sound output - scale of notes C-C


def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(
            "%2i: interface :%s:, name :%s:, opened :%s:  %s"
            % (i, interf, name, opened, in_out)
        )


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

    pygame.init()
    pygame.midi.init()
    _print_device_info()

    if device_id is None:
        port = pygame.midi.get_default_output_id()
    else:
        port = device_id
    print(f"using output_id :{port}:")

    midi_out = pygame.midi.Output(port, latency=0)
    midi_out.set_instrument(instrument, channel=0)
    try:
        for i in range(1):
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
                midi_out.note_on(note, 64, channel=0)
                time.sleep(0.5)
                midi_out.note_off(note, 64, channel=0)
                time.sleep(0.1)

    finally:
        midi_out.close()
        del midi_out

    pygame.midi.quit()
    # Exit


test_piano_scale(8)
