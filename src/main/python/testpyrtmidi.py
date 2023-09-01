# testpyrtmidi.py

import sys
# from enum import Enum
# from copy import copy
import time
import itertools
import rtmidi

from midiutils import Note, Chord, KeySignature, Patch, Patches, MidiMessage

# @@TODO:
#
# Move MidiOut to separate module.
#
# NOTE:
#
# To connect to iPad BS-16 synthesizer using MIDI:
#   1. in BS-16, enable "Bluetooth > Local Midi service" 
#      (from "Midi utility" button shown as 5-pin DIN connector)
#   2. in Audio Midi setup on Mac, "Bluetooth configuration", connect "IPad"
#      (or whatever name was used)



# ---- MIDI output class ----

class MidiOut:

    def midi_open(self):
       if not self.midiout:
            self.midiout         = rtmidi.MidiOut()
            self.available_ports = self.midiout.get_ports()

    def midi_close(self):
        if self.midiout:
            # self.midiout.close()
            del self.midiout
            self.midiout = None
        return

    def get_port_name(self, port_num):
        if self.available_ports:
            self.available_ports[port_num]
        else:
            print(f"MidiOut.get_port_name: cannot find available Midi ports")
        return None

    def get_port_num(self, port_name):
        if self.available_ports:
            for i in range(len(self.available_ports)):
                if port_name in self.available_ports[i]:
                    return i
            print(f"MidiOut.get_port_num: MIDI port '{port_name}' not found")
        else:
            print(f"MidiOut.get_port_num: cannot find available MIDI ports")
        return None

    def print_port_info(self):
        for i in range(len(self.available_ports)):
            print(f"Port {i:02d}: {self.available_ports[i]:s}")
        return

    def __init__(self, port_number=None, port_name=None):
        # Open a Midi port.
        #
        # port_number   if provided is the (system dependent) number of a Midi port 
        #               to which Midi data will be sent
        # port_name     if provided is the (system dependent) name of a Midi port 
        #               to which Midi data will be sent.  If no such port already 
        #               exists, creates a new virtual MIDI port.
        #
        # Only one of these port values may be provided.
        self.midiout        = None
        self.midi_port_num  = None
        self.midi_port_name = None
        self.midi_open()
        self.print_port_info()
        if port_number is not None:
            self.midi_port_num  = port_number
            self.midi_port_name = self.get_port_name(port_number)
        elif port_name is not None:
            midi_port = self.get_port_num(port_name)
            if midi_port:
                self.midi_port_num  = midi_port
                self.midi_port_name = port_name
        if self.midi_port_num is not None:
            print(f"MidiOut: Using MIDI port {self.midi_port_num:02d} ({self.midi_port_name:s})")
            self.midiout.open_port(self.midi_port_num, self.midi_port_name)
        elif self.midi_port_name is not None:
            print(f"MidiOut: Creating virtual MIDI port {self.midi_port_name:s}")
            self.midiout.open_virtual_port(self.midi_port_name)
        else:
            print(f"MidiOut: No available MIDI port specified")
        return

    def send(self, message):
        """
        Send Midi message to port.

        NOTE: it not clear that rtmidi supports "running status"
        (https://cmtext.indiana.edu/MIDI/chapter3_channel_voice_messages.php).
        But the rtmidi2 Python library appears to have methods that could utilize this.
        """
        #print(f"send: {message}")
        if isinstance(message[0],list):
            for m in message:
                self.send(m)
        else:
            self.midiout.send_message(message)
        return

# ---- Test helper ----

def assertEq(s1, s2):
    if s1 != s2:
        print(f"AssertEq: {s1} != {s2}")
        raise AssertionError(("Eq", s1, s2))

# ---- Test output ----

def test_scales(port_number=None, port_name=None):
    # Channel number to use, in range 1-16, appears in the initial message byte
    channel = 1
    # Generate some notes
    midiout = MidiOut(port_number=port_number, port_name=port_name)
    try:
        for p in Patches():
            scale_notes = (
                Note.C3,
                Note.D3,
                Note.E3,
                Note.F3,
                Note.G3,
                Note.A3,
                Note.B3,

                Note.C4,
                Note.D4,
                Note.E4,
                Note.F4,
                Note.G4,
                Note.A4,
                Note.B4,

                Note.C5,
                )
            print(f"program_change: {p}")
            midiout.send(MidiMessage.program_change(channel, p))
            for note in (scale_notes):
                print(f"Play note {note}")
                midiout.send(MidiMessage.note_on(channel, note))
                time.sleep(0.25)
                midiout.send(MidiMessage.note_off(channel, note))
                time.sleep(0.05)
    finally:
        # midiout.close()
        del midiout
    return


# test_scales(port_name="iPad")

def test_Cmaj_chords(port_number=None, port_name=None):
    # Channel number to use, in range 1-16, appears in the initial message byte
    channel = 1
    # Instrument (program number) to use, in range 1-128
    patch = Patch.GRAND_PIANO
    # patch = Patch.CHURCH_ORGAN
    # Generate some notes
    midiout = MidiOut(port_number=port_number, port_name=port_name)
    midiout.send(MidiMessage.program_change(channel, patch))
    Cmaj_chords = (
        Chord(Note.C4, Note.E4, Note.G4),
        Chord(Note.F4, Note.A4, Note.C5),
        Chord(Note.G4, Note.B4, Note.D5),
        Chord(Note.F4, Note.A4, Note.C5),
        Chord(Note.C4, Note.E4, Note.G4)
        )
    try:
        for _ in range(4):
            for c in Cmaj_chords:
                print(f"Play chord {c}")
                midiout.send(MidiMessage.chord_on(channel, c))
                time.sleep(0.5)
                midiout.send(MidiMessage.chord_off(channel, c))
                time.sleep(0.05)
    finally:
        # midiout.close()
        del midiout
    return


# test_Cmaj_chords(port_name="iPad")

def test_Cmaj_arpeggios(port_number=None, port_name=None):
    # Channel number to use, in range 1-16, appears in the initial message byte
    channel1 = 1
    channel2 = 2
    # Instrument (program number) to use, in range 1-128
    # patch = Patch.GRAND_PIANO
    patch1 = Patch.REED_ORGAN
    patch2 = Patch.ORCHESTRAL_HARP
    # Generate some notes
    midiout = MidiOut(port_number=port_number, port_name=port_name)
    midiout.send(MidiMessage.program_change(channel1, patch1))
    midiout.send(MidiMessage.program_change(channel2, patch2))
    Cmaj_chords = (
        Chord(Note.C4, Note.E4, Note.G4),
        Chord(Note.F4, Note.A4, Note.C5),
        Chord(Note.G4, Note.B4, Note.D5),
        Chord(Note.F4, Note.A4, Note.C5),
        Chord(Note.C4, Note.E4, Note.G4)
        )
    try:
        for _ in range(2):
            for c in Cmaj_chords:
                print(f"Play arpeggio {c}")
                midiout.send(MidiMessage.chord_on(channel2, c))
                for n in c:
                    midiout.send(MidiMessage.note_on(channel1, n))
                    time.sleep(0.35)
                    midiout.send(MidiMessage.note_off(channel1, n))
                for n in list(reversed(c))[1:]:
                    midiout.send(MidiMessage.note_on(channel1, n))
                    time.sleep(0.35)
                    midiout.send(MidiMessage.note_off(channel1, n))
                midiout.send(MidiMessage.chord_off(channel2, c))
                time.sleep(0.35)
    finally:
        # midiout.close()
        del midiout
    return

# test_Cmaj_arpeggios(port_name="iPad")

def test_keysig_scales(port_number=None, port_name=None):
    # Channel number to use, in range 1-16, appears in the initial message byte
    channel = 1
    # Instrument (program number) to use, in range 1-128
    patch = Patch.GRAND_PIANO
    # patch = Patch.CHURCH_ORGAN
    # Generate some notes
    midiout = MidiOut(port_number=port_number, port_name=port_name)
    midiout.send(MidiMessage.program_change(channel, patch))
    keysigs = []
    for s in ('Cmaj', 'Amin'):
        keysigs.append(KeySignature.get_key(s))
    try:
        for keysig in keysigs:
            print(f"Play {keysig} scale")
            notes = itertools.chain(keysig.iter_octave(4), [keysig.get_note(5,1)])
            #notes = keysig.iter_octave(4)
            for note in notes:
                print(f"Play note {note}")
                midiout.send(MidiMessage.note_on(channel, note))
                time.sleep(0.25)
                midiout.send(MidiMessage.note_off(channel, note))
                time.sleep(0.25)
    finally:
        # midiout.close()
        del midiout
    return

test_keysig_scales(port_name="iPad")


# End.

