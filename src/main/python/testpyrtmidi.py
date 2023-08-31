# testpyrtmidi.py

import sys
# from enum import Enum
# from copy import copy
import time

import rtmidi

from midiutils import Note, Chord, Patch, Patches, MidiMessage

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
                Note.C2,
                Note.D2,
                Note.E2,
                Note.F2,
                Note.G2,
                Note.A2,
                Note.B2,

                Note.C3,
                # Note.D3,
                # Note.E3,
                # Note.F3,
                # Note.G3,
                # Note.A3,
                # Note.B3,

                # Note.C4,
                # Note.D4,
                # Note.E4,
                # Note.F4,
                # Note.G4,
                # Note.A4,
                # Note.B4,
                # Note.C5,
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

    # Exit

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
        Chord(Note.C3, Note.E3, Note.G3),
        Chord(Note.F3, Note.A3, Note.C4),
        Chord(Note.G3, Note.B3, Note.D4),
        Chord(Note.F3, Note.A3, Note.C4),
        Chord(Note.C3, Note.E3, Note.G3)
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
        Chord(Note.C3, Note.E3, Note.G3),
        Chord(Note.F3, Note.A3, Note.C4),
        Chord(Note.G3, Note.B3, Note.D4),
        Chord(Note.F3, Note.A3, Note.C4),
        Chord(Note.C3, Note.E3, Note.G3)
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

test_Cmaj_arpeggios(port_name="iPad")


"""

    # MIDI notes
    # NOTE: BS-16 uses an alternative convention where middle C is "C4""

    MIDI_NOTE_C2  = 48
    MIDI_NOTE_C2s = 49
    MIDI_NOTE_D2  = 50
    MIDI_NOTE_D2s = 51
    MIDI_NOTE_E2  = 52
    MIDI_NOTE_F2  = 53
    MIDI_NOTE_F2s = 54
    MIDI_NOTE_G2  = 55
    MIDI_NOTE_G2s = 56
    MIDI_NOTE_A2  = 57
    MIDI_NOTE_A2s = 58
    MIDI_NOTE_B2  = 59

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
    MIDI_NOTE_C4s = 73
    MIDI_NOTE_D4  = 74
    MIDI_NOTE_D4s = 75
    MIDI_NOTE_E4  = 76
    MIDI_NOTE_F4  = 77
    MIDI_NOTE_F4s = 78
    MIDI_NOTE_G4  = 79
    MIDI_NOTE_G4s = 80
    MIDI_NOTE_A4  = 81
    MIDI_NOTE_A4s = 82
    MIDI_NOTE_B4  = 83
    MIDI_NOTE_C5  = 84

    MIDI_NUMBER_MID_C = MIDI_NOTE_C3
    MIDI_NAME_MID_C   = "C3"

    # MIDI instrument program numbers, set by "Program change" message
    # Numbers per "General MIDI" (https://en.wikipedia.org/wiki/General_MIDI)
    # NOTE: encoded values are zero-based, may require subtracting 1 from the program number
    # Based on table at https://soundprogramming.net/file-formats/general-midi-instrument-list/

    # Piano:
    GRAND_PIANO             = 1
    BRIGHT_PIANO            = 2
    ELECTRIC_PIANO          = 3
    HONKYTONK_PIANO         = 4
    ELECTRIC_PIANO_1        = 5
    ELECTRIC_PIANO_2        = 6
    HARPSICHORD             = 7
    CLAVINET                = 8
    # Chromatic Percussion:
    CELESTA                 = 9
    GLOCKENSPIEL            = 10
    MUSIC_BOX               = 11
    VIBRAPHONE              = 12
    MARIMBA                 = 13
    XYLOPHONE               = 14
    TUBULAR_BELLS           = 15
    DULCIMER                = 16
    # Organ:
    DRAWBAR_ORGAN           = 17
    PERCUSSIVE_ORGAN        = 18
    ROCK_ORGAN              = 19
    CHURCH_ORGAN            = 20
    REED_ORGAN              = 21
    ACCORDION               = 22
    HARMONICA               = 23
    TANGO_ACCORDION         = 24
    # Guitar:
    ACOUSTIC_GUITAR_NYLON   = 25
    ACOUSTIC_GUITAR_STEEL   = 26
    ELECTRIC_GUITAR_JAZZ    = 27
    ELECTRIC_GUITAR_CLEAN   = 28
    ELECTRIC_GUITAR_MUTED   = 29
    OVERDRIVEN_GUITAR       = 30
    DISTORTION_GUITAR       = 31
    GUITAR_HARMONICS        = 32
    # Bass:
    ACOUSTIC_BASS           = 33
    ELECTRIC_BASS_FINGER    = 34
    ELECTRIC_BASS_PICK      = 35
    FRETLESS_BASS           = 36
    SLAP_BASS_1             = 37
    SLAP_BASS_2             = 38
    SYNTH_BASS_1            = 39
    SYNTH_BASS_2            = 40
    # Strings:
    VIOLIN                  = 41
    VIOLA                   = 42
    CELLO                   = 43
    CONTRABASS              = 44
    TREMOLO_STRINGS         = 45
    PIZZICATO_STRINGS       = 46
    ORCHESTRAL_HARP         = 47
    TIMPANI                 = 48
    STRING_ENSEMBLE_1       = 49
    STRING_ENSEMBLE_2       = 50
    SYNTH_STRINGS_1         = 51
    SYNTH_STRINGS_2         = 52
    CHOIR_AAHS              = 53
    VOICE_OOHS              = 54
    SYNTH_VOICE             = 55
    ORCHESTRA_HIT           = 56
    # Brass:
    TRUMPET                 = 57
    TROMBONE                = 58
    TUBA                    = 59
    MUTED_TRUMPET           = 60
    FRENCH_HORN             = 61
    BRASS_SECTION           = 62
    SYNTH_BRASS_1           = 63
    SYNTH_BRASS_2           = 64
    # Reed:
    SOPRANO_SAX             = 65
    ALTO_SAX                = 66
    TENOR_SAX               = 67
    BARITONE_SAX            = 68
    OBOE                    = 69
    ENGLISH_HORN            = 70
    BASSOON                 = 71
    CLARINET                = 72
    # Pipe:
    PICCOLO                 = 73
    FLUTE                   = 74
    RECORDER                = 75
    PAN_FLUTE               = 76
    BLOWN_BOTTLE            = 77
    SHAKUHACHI              = 78
    WHISTLE                 = 79
    OCARINA                 = 80
    # Synth Lead:
    LEAD_1_SQUARE           = 81
    LEAD_2_SAWTOOTH         = 82
    LEAD_3_CALLIOPE         = 83
    LEAD_4_CHIFF            = 84
    LEAD_5_CHARANG          = 85
    LEAD_6_VOICE            = 86
    LEAD_7_FIFTHS           = 87
    LEAD_8_BASS_LEAD        = 88
    # Synth Pad:
    PAD_1_NEW_AGE           = 89
    PAD_2_WARM              = 90
    PAD_3_POLYSYNTH         = 91
    PAD_4_CHOIR             = 92
    PAD_5_BOWED             = 93
    PAD_6_METALLIC          = 94
    PAD_7_HALO              = 95
    PAD_8_SWEEP             = 96
    # Synth Effects:
    FX_1_RAIN               = 97
    FX_2_SOUNDTRACK         = 98
    FX_3_CRYSTAL            = 99
    FX_4_ATMOSPHERE         = 100
    FX_5_BRIGHTNESS         = 101
    FX_6_GOBLINS            = 102
    FX_7_ECHOES             = 103
    FX_8_SCIFI              = 104
    # Ethnic:
    SITAR                   = 105
    BANJO                   = 106
    SHAMISEN                = 107
    KOTO                    = 108
    KALIMBA                 = 109
    BAG_PIPE                = 110
    FIDDLE                  = 111
    SHANAI                  = 112
    # Percussive:
    TINKLE_BELL             = 113
    AGOGO                   = 114
    STEEL_DRUMS             = 115
    WOODBLOCK               = 116
    TAIKO_DRUM              = 117
    MELODIC_TOM             = 118
    SYNTH_DRUM              = 119
    # Sound effects:
    REVERSE_CYMBAL          = 120
    GUITAR_FRET_NOISE       = 121
    BREATH_NOISE            = 122
    SEASHORE                = 123
    BIRD_TWEET              = 124
    TELEPHONE_RING          = 125
    HELICOPTER              = 126
    APPLAUSE                = 127
    GUNSHOT                 = 128
"""



