# midiutils.py
#
# Utilities for constructing MIDI messages
#
# Defines classes 'Note', 'Chord', 'Scale', 'Patch' and 'MidiMessage' to serve as
# namespaces for constants and functions.
#
# Intended to be independent of any actual Midi library used.  
# Assumes Midi messages are represented as a sequence of byte values (integers).
#

# ---- Test helper ----

def assertEq(s1, s2):
    if s1 != s2:
        print(f"AssertEq: {s1} != {s2}")
        raise AssertionError(("Eq", s1, s2))

# ----------
# Note class
# ----------

class Note:
    """
    Defines a set of constants used (by convention) to represent note pitches in Midi messages

    See: https://computermusicresource.com/midikeys.html

    Later changed to follow Scientific pitch notation (SPN), also known as 
    American standard pitch notation (ASPN) and international pitch notation (IPN),
    per https://en.wikipedia.org/wiki/Scientific_pitch_notation.

    This also conveniently matches the key labels used in my BS-16 synthesizer software.
    """
    notes = [[] for _ in range(128)]
    accidental_flat  = "♭"  # 0x266d, U+266D
    accidental_nat   = "♮"  # 0x266e, U+266E
    accidental_sharp = "♯"  # 0x266f, U+266F

    @classmethod
    def __class__init__(cls):
        Note.def_octave_notes(0, 12)
        Note.def_octave_notes(1, 24)
        Note.def_octave_notes(2, 36)
        Note.def_octave_notes(3, 48)
        Note.def_octave_notes(4, 60)
        Note.def_octave_notes(5, 72)
        Note.def_octave_notes(6, 84)
        Note.def_octave_notes(7, 96)
        Note.def_octave_notes(8, 108)
        Note.def_octave_notes(9, 120)
        setattr(cls, 'MID_C',      Note.C4)
        setattr(cls, 'MID_C_NOTE', Note.notes[Note.C4.midinum][0])
        return cls

    @classmethod 
    def def_octave_notes(cls, octavenum, basenotenum):
        octave_notes = (
              { 'name': "C",  'id': "C",    'offset': 0  }
            , { 'name': "C♮", 'id': "Cnat", 'offset': 0  }
            , { 'name': "C♯", 'id': "Cs",   'offset': 1  }
            , { 'name': "D♭", 'id': "Db",   'offset': 1  }
            , { 'name': "D",  'id': "D",    'offset': 2  }
            , { 'name': "D♮", 'id': "Dnat", 'offset': 2  }
            , { 'name': "D♯", 'id': "Ds",   'offset': 3  }
            , { 'name': "E♭", 'id': "Eb",   'offset': 3  }
            , { 'name': "E",  'id': "E",    'offset': 4  }
            , { 'name': "E♮", 'id': "Enat", 'offset': 4  }
            , { 'name': "F",  'id': "F",    'offset': 5  }
            , { 'name': "F♮", 'id': "Fnat", 'offset': 5  }
            , { 'name': "F♯", 'id': "Fs",   'offset': 6  }
            , { 'name': "G♭", 'id': "Gb",   'offset': 6  }
            , { 'name': "G",  'id': "G",    'offset': 7  }
            , { 'name': "G♮", 'id': "Gnat", 'offset': 7  }
            , { 'name': "G♯", 'id': "Gs",   'offset': 8  }
            , { 'name': "A♭", 'id': "Ab",   'offset': 8  }
            , { 'name': "A",  'id': "A",    'offset': 9  }
            , { 'name': "A♮", 'id': "Anat", 'offset': 9  }
            , { 'name': "A♯", 'id': "As",   'offset': 10 }
            , { 'name': "B♭", 'id': "Bb",   'offset': 10 }
            , { 'name': "B",  'id': "B",    'offset': 11 }
            , { 'name': "B♮", 'id': "Bnat", 'offset': 11 }
            )
        for n in octave_notes:
            midinum  = basenotenum+n['offset']
            if midinum < 128:
                note = Note(n['name'], n['id'], octavenum, n['offset'], midinum)
                setattr(cls, note.ident, note)
                cls.notes[midinum].append(note)
        return

    @classmethod 
    def from_midinum(cls, midinum):
        # Returns list of Note objects corresponding to the supplied MIDI note number,
        # or None if the supplied value is not a valid MIDI note number
        #
        if midinum >= 0 and midinum < 128:
            return cls.notes[midinum]
        return None

    @classmethod 
    def from_octave_offset(cls, octavenum, semioffset):
        # Returns list of Note objects corresponding to the supplied octave and 
        # offset in semitones.
        #
        # octavenum     is the octave number, per scientific pitch notation.
        # semioffset    is the offset in semitones of a note within the octave.
        #
        # NOTE:
        # This implementation depends on the simple relationship between MIDI 
        # note numbers and chromatic (semitone) notes across all the octaves.
        #
        midinum  = octavenum*12+semioffset
        #print(f"from_octave_offset: {octavenum}, {semioffset} -> {midinum}")
        return cls.from_midinum(midinum)

    def __init__(self, name, id, octavenum, octaveoff, midinum):
        """
        Create a Note object.

        name        is a display name of a note within an octave (C, C♯, etc.)
        id          is an code identifier for a note within an octave (C, Cs, etc.)
        octavenum   is the note's octave number, per scientific pitch notation
        octaveoff   is the note's chromatic scale offset within the octave (C is 0)
        midinum     is the note's MIDI note number
        """
        noteid   = id[0] + str(octavenum) + id[1:]
        midiname = name  + str(octavenum)
        self.ident     = noteid
        self.notename  = name
        self.midiname  = midiname
        self.midinum   = midinum
        self.octavenum = octavenum
        self.octaveoff = octaveoff
        return

    def __str__(self):
        return self.midiname

    def __longstr__(self):
        return f"Note({self.ident:5s} ({self.midinum}): {self.notename},{self.octavenum},{self.octaveoff}, {self.midiname})"

    def __repr__(self):
        return f"Note.{self.ident}"

Note.__class__init__()

# ---- Test ----
if __name__ == "__main__":
    print(f"Mid_C number {Note.MID_C.midinum}, note {Note.MID_C_NOTE}")
    for i in range(Note.C4.midinum, Note.G5.midinum+1):
        print(f"Note number {i} ({Note.notes[i][0]!r}), "
              f"names {[n.midiname for n in Note.notes[i]]}, "
              f"ids {[n.ident for n in Note.notes[i]]}")
    for i in range(Note.C4.midinum, Note.G5.midinum):
        print(i, ": ", Note.notes[i][0].__longstr__())
        print(i, ": ", Note.notes[i][1].__longstr__())
    for i in range(Note.C4.midinum, Note.G5.midinum):
        print(i, ": ", repr(Note.notes[i][0]))
        print(i, ": ", repr(Note.notes[i][1]))
# ----


# -----------------
# Chord class
# -----------------

class Chord:
    """
    Represents an arbitrary selection of notes to be played together
    """

    def __init__(self, *notes):
        self.notes = notes
        return

    def __str__(self):
        return "+".join(map(str, self.notes))

    def __iter__(self):
        for n in self.notes:
            yield n
        return

    def __reversed__(self):
        return Chord(*reversed(self.notes))

# ---- Test ----
if __name__ == "__main__":
    Cchord = Chord(Note.C4, Note.E4, Note.G4)
    print(f"C chord {Cchord}")
    for n in Cchord:
        print(f"C chord note {n}")
# ----

# ------------------
# KeySignature class
# ------------------

class KeySignature:
    """
    Represents a key signature class, and provides methods to access notes and chords
    using notes from its scale.

    See:
        https://en.wikipedia.org/wiki/Scale_(music) 
        https://en.wikipedia.org/wiki/Scientific_pitch_notation
    """

    # Major scales here are grouped together with their relative minors
    keysig_params = {
        'C_maj':    { 'name': "C major",  'base': Note.C4,  'type': "major"  },
        'A_min':    { 'name': "A minor",  'base': Note.A4,  'type': "minor"  },

        'G_maj':    { 'name': "G major",  'base': Note.G4,  'type': "major"  },
        'D_min':    { 'name': "D minor",  'base': Note.D4,  'type': "minor"  },

        'D_maj':    { 'name': "D major",  'base': Note.D4,  'type': "major"  },
        'G_min':    { 'name': "G minor",  'base': Note.G4,  'type': "minor"  },

        'A_maj':    { 'name': "A major",  'base': Note.A4,  'type': "major"  },
        'C_min':    { 'name': "C minor",  'base': Note.C4,  'type': "minor"  },

        'E_maj':    { 'name': "E major",  'base': Note.E4,  'type': "major"  },
        'F_min':    { 'name': "F minor",  'base': Note.F4,  'type': "minor"  },

        'B_maj':    { 'name': "B major",  'base': Note.B4,  'type': "major"  },
        'Bb_min':   { 'name': "B♭ minor", 'base': Note.B4b, 'type': "minor"  },

        'Fs_maj':   { 'name': "F♯ major", 'base': Note.F4s, 'type': "major"  },
        'Eb_min':   { 'name': "E♭ minor", 'base': Note.E4b, 'type': "minor"  },
    }

    scale_intervals = {
        'major': [0, 2, 4, 5, 7, 9, 11],    # 2,2,1,2,2,2,1
        'minor': [0, 2, 3, 5, 7, 8, 10],    # 2,1,2,2,1,2,2
    }

    @classmethod
    def __class_init__(cls):
        return

    @classmethod
    def iter_keys(cls):
        return cls.keysig_params.keys()

    @classmethod
    def get_key(cls, id):
        params = cls.keysig_params[id]
        return KeySignature(id, params['name'], params['base'], params['type'])

    def __init__(self, sigid, signame, sigbase, sigtype):
        """
        Creates a key signature object.

        sigid       is the identifier (used for names in code)
        signame     is the display name
        sigbase     is the base (root of 1st chord) in octave 4 per Scientific 
                    Pitch Notation (i.e. the octave containing middle-C),
                    supplied as a Note value
        sigtype     is the type of scale, which in turn defines a set of intervals
                    within an octave that correspond to the scale notes
        """
        self.sigid     = sigid
        self.signame   = signame
        self.sigbase   = sigbase
        self.sigtype   = sigtype
        self.intervals = self.scale_intervals[sigtype]
        return

    def __str__(self):
        return self.signame

    def get_note(self, octavenum, degree):
        """
        Returns a Note object corresponding to the indicated octave and degree.

        octavenum   is the octave number, per scientific pitch notation, in which
                    the dominant note of the scale occurs.
        degree      is the number 1-7 of the scale note within the octave, where
                    the dominant note is number 1.
        """
        rootoctave = self.sigbase.octavenum
        rootoffset = self.sigbase.octaveoff
        noteoctave = rootoctave-4 + octavenum        
        noteoffset = rootoffset   + self.intervals[degree-1]
        if noteoffset >= 12:
            noteoctave += 1
            noteoffset -= 12
        rootnotes = Note.from_octave_offset(noteoctave, noteoffset)
        #print(f"get_note {octavenum}, {degree} -> {rootnotes}")
        return rootnotes[0]

    def iter_octave(self, octavenum):
        # Iterator over notes in scale for given octave
        for i in range(1, len(self.intervals)+1):
            yield self.get_note(octavenum, i)
        return

# -----------------
# Patch class
# -----------------

class Patch:
    """
    Identifiers and labels for patches in General Midi
    """
    patch_list = [None for _ in range(129)]

    @classmethod
    def set_patch(cls, patchid, patchnum, patchname):
        patch = Patch(patchid, patchnum, patchname)
        setattr(cls, patchid, patch)
        cls.patch_list[patchnum] = patch
        return

    @classmethod
    def __iter_patches__(cls):
        for i in range(len(cls.patch_list)):
            if cls.patch_list[i]:
                yield cls.patch_list[i]
        return

    @classmethod
    def __class_init__(cls):
        # MIDI instrument program patches, set by "Program change" message
        # Numbers per "General MIDI" (https://en.wikipedia.org/wiki/General_MIDI)
        # NOTE: encoded values are zero-based, may require subtracting 1 from the program number
        # Based on table at https://soundprogramming.net/file-formats/general-midi-instrument-list/
        #
        # Piano:
        cls.set_patch("GRAND_PIANO",             1, "Grand piano")
        cls.set_patch("BRIGHT_PIANO" ,           2, "Bright piano")
        cls.set_patch("ELECTRIC_PIANO",          3, "Electric piano")
        cls.set_patch("HONKYTONK_PIANO",         4, "Honkytonk piano")
        cls.set_patch("ELECTRIC_PIANO_1",        5, "Electric piano 1")
        cls.set_patch("ELECTRIC_PIANO_2",        6, "Electric piano 2")
        cls.set_patch("HARPSICHORD",             7, "Harpsichord")
        cls.set_patch("CLAVINET",                8, "Clavinet")
        # Chromatic Percussion:
        cls.set_patch("CELESTA",                 9, "Celesta")
        cls.set_patch("GLOCKENSPIEL",           10, "Glockenspiel")
        cls.set_patch("MUSIC_BOX",              11, "Music box")
        cls.set_patch("VIBRAPHONE",             12, "Vibraphone")
        cls.set_patch("MARIMBA",                13, "Marimba")
        cls.set_patch("XYLOPHONE",              14, "Xylophone")
        cls.set_patch("TUBULAR_BELLS",          15, "Tubular bells")
        cls.set_patch("DULCIMER",               16, "Dulcimer")
        # Organ:
        cls.set_patch("DRAWBAR_ORGAN",          17, "Drawbar organ")
        cls.set_patch("PERCUSSIVE_ORGAN",       18, "Percussive organ")
        cls.set_patch("ROCK_ORGAN",             19, "Rock organ")
        cls.set_patch("CHURCH_ORGAN",           20, "Church organ")
        cls.set_patch("REED_ORGAN",             21, "Reed organ")
        cls.set_patch("ACCORDION",              22, "Accordion")
        cls.set_patch("HARMONICA",              23, "Harmonica")
        cls.set_patch("TANGO_ACCORDION",        24, "Tango accordion")
        # Guitar:
        cls.set_patch("ACOUSTIC_GUITAR_NYLON",  25, "Acoustic guitar nylon")
        cls.set_patch("ACOUSTIC_GUITAR_STEEL",  26, "Acoustic guitar steel")
        cls.set_patch("ELECTRIC_GUITAR_JAZZ",   27, "Electric guitar jazz")
        cls.set_patch("ELECTRIC_GUITAR_CLEAN",  28, "Electric guitar clean")
        cls.set_patch("ELECTRIC_GUITAR_MUTED",  29, "Electric guitar muted")
        cls.set_patch("OVERDRIVEN_GUITAR",      30, "Overdriven guitar")
        cls.set_patch("DISTORTION_GUITAR",      31, "Distortion guitar")
        cls.set_patch("GUITAR_HARMONICS",       32, "Guitar harmonics")
        # Bass:
        cls.set_patch("ACOUSTIC_BASS",          33, "Acoustic bass")
        cls.set_patch("ELECTRIC_BASS_FINGER",   34, "Electric bass finger")
        cls.set_patch("ELECTRIC_BASS_PICK",     35, "Electric bass pick")
        cls.set_patch("FRETLESS_BASS",          36, "Fretless bass")
        cls.set_patch("SLAP_BASS_1",            37, "Slap bass 1")
        cls.set_patch("SLAP_BASS_2",            38, "Slap bass 2")
        cls.set_patch("SYNTH_BASS_1",           39, "Synth bass 1")
        cls.set_patch("SYNTH_BASS_2",           40, "Synth bass 2")
        # Strings:
        cls.set_patch("VIOLIN",                 41, "Violin")
        cls.set_patch("VIOLA",                  42, "Viola")
        cls.set_patch("CELLO",                  43, "Cello")
        cls.set_patch("CONTRABASS",             44, "Contrabass")
        cls.set_patch("TREMOLO_STRINGS",        45, "Tremolo strings")
        cls.set_patch("PIZZICATO_STRINGS",      46, "Pizzicato strings")
        cls.set_patch("ORCHESTRAL_HARP",        47, "Orchestral harp")
        cls.set_patch("TIMPANI",                48, "Timpani")
        cls.set_patch("STRING_ENSEMBLE_1",      49, "String ensemble 1")
        cls.set_patch("STRING_ENSEMBLE_2",      50, "String ensemble 2")
        cls.set_patch("SYNTH_STRINGS_1",        51, "Synth strings 1")
        cls.set_patch("SYNTH_STRINGS_2",        52, "Synth strings 2")
        cls.set_patch("CHOIR_AAHS",             53, "Choir aahs")
        cls.set_patch("VOICE_OOHS",             54, "Voice oohs")
        cls.set_patch("SYNTH_VOICE",            55, "Synth voice")
        cls.set_patch("ORCHESTRA_HIT",          56, "Orchestra hit")
        # Brass:
        cls.set_patch("TRUMPET",                57, "Trumpet")
        cls.set_patch("TROMBONE",               58, "Trombone")
        cls.set_patch("TUBA",                   59, "Tuba")
        cls.set_patch("MUTED_TRUMPET",          60, "Muted trumpet")
        cls.set_patch("FRENCH_HORN",            61, "French horn")
        cls.set_patch("BRASS_SECTION",          62, "Brass section")
        cls.set_patch("SYNTH_BRASS_1",          63, "Synth brass 1")
        cls.set_patch("SYNTH_BRASS_2",          64, "Synth brass 2")
        # Reed:
        cls.set_patch("SOPRANO_SAX",            65, "Soprano sax")
        cls.set_patch("ALTO_SAX",               66, "Alto sax")
        cls.set_patch("TENOR_SAX",              67, "Tenor sax")
        cls.set_patch("BARITONE_SAX",           68, "Baritone sax")
        cls.set_patch("OBOE",                   69, "Oboe")
        cls.set_patch("ENGLISH_HORN",           70, "English horn")
        cls.set_patch("BASSOON",                71, "Bassoon")
        cls.set_patch("CLARINET",               72, "Clarinet")
        # Pipe:
        cls.set_patch("PICCOLO",                73, "Piccolo")
        cls.set_patch("FLUTE",                  74, "Flute")
        cls.set_patch("RECORDER",               75, "Recorder")
        cls.set_patch("PAN_FLUTE",              76, "Pan flute")
        cls.set_patch("BLOWN_BOTTLE",           77, "Blown bottle")
        cls.set_patch("SHAKUHACHI",             78, "Shakuhachi")
        cls.set_patch("WHISTLE",                79, "Whistle")
        cls.set_patch("OCARINA",                80, "Ocarina")
        # Synth Lead:
        cls.set_patch("LEAD_1_SQUARE",          81, "Lead 1 square")
        cls.set_patch("LEAD_2_SAWTOOTH",        82, "Lead 2 sawtooth")
        cls.set_patch("LEAD_3_CALLIOPE",        83, "Lead 3 calliope")
        cls.set_patch("LEAD_4_CHIFF",           84, "Lead 4 chiff")
        cls.set_patch("LEAD_5_CHARANG",         85, "Lead 5 charang")
        cls.set_patch("LEAD_6_VOICE",           86, "Lead 6 voice")
        cls.set_patch("LEAD_7_FIFTHS",          87, "Lead 7 fifths")
        cls.set_patch("LEAD_8_BASS_LEAD",       88, "Lead 8 bass lead")
        # Synth Pad:
        cls.set_patch("PAD_1_NEW_AGE",          89, "Pad 1 new age")
        cls.set_patch("PAD_2_WARM",             90, "Pad 2 warm")
        cls.set_patch("PAD_3_POLYSYNTH",        91, "Pad 3 polysynth")
        cls.set_patch("PAD_4_CHOIR",            92, "Pad 4 choir")
        cls.set_patch("PAD_5_BOWED",            93, "Pad 5 bowed")
        cls.set_patch("PAD_6_METALLIC",         94, "Pad 6 metallic")
        cls.set_patch("PAD_7_HALO",             95, "Pad 7 halo")
        cls.set_patch("PAD_8_SWEEP",            96, "Pad 8 sweep")
        # Synth Effects:
        cls.set_patch("FX_1_RAIN",              97, "Fx 1 rain")
        cls.set_patch("FX_2_SOUNDTRACK",        98, "Fx 2 soundtrack")
        cls.set_patch("FX_3_CRYSTAL",           99, "Fx 3 crystal")
        cls.set_patch("FX_4_ATMOSPHERE",       100, "Fx 4 atmosphere")
        cls.set_patch("FX_5_BRIGHTNESS",       101, "Fx 5 brightness")
        cls.set_patch("FX_6_GOBLINS",          102, "Fx 6 goblins")
        cls.set_patch("FX_7_ECHOES",           103, "Fx 7 echoes")
        cls.set_patch("FX_8_SCIFI",            104, "Fx 8 scifi")
        # Ethnic:
        cls.set_patch("SITAR",                 105, "Sitar")
        cls.set_patch("BANJO",                 106, "Banjo")
        cls.set_patch("SHAMISEN",              107, "Shamisen")
        cls.set_patch("KOTO",                  108, "Koto")
        cls.set_patch("KALIMBA",               109, "Kalimba")
        cls.set_patch("BAG_PIPE",              110, "Bag_pipe")
        cls.set_patch("FIDDLE",                111, "Fiddle")
        cls.set_patch("SHANAI",                112, "Shanai")
        # Percussive:
        cls.set_patch("TINKLE_BELL",           113, "Tinkle bell")
        cls.set_patch("AGOGO",                 114, "Agogo")
        cls.set_patch("STEEL_DRUMS",           115, "Steel drums")
        cls.set_patch("WOODBLOCK",             116, "Woodblock")
        cls.set_patch("TAIKO_DRUM",            117, "Taiko drum")
        cls.set_patch("MELODIC_TOM",           118, "Melodic tom")
        cls.set_patch("SYNTH_DRUM",            119, "Synth drum")
        # Sound effects:
        cls.set_patch("REVERSE_CYMBAL",        120, "Reverse cymbal")
        cls.set_patch("GUITAR_FRET_NOISE",     121, "Guitar fret noise")
        cls.set_patch("BREATH_NOISE",          122, "Breath noise")
        cls.set_patch("SEASHORE",              123, "Seashore")
        cls.set_patch("BIRD_TWEET",            124, "Bird tweet")
        cls.set_patch("TELEPHONE_RING",        125, "Telephone ring")
        cls.set_patch("HELICOPTER",            126, "Helicopter")
        cls.set_patch("APPLAUSE",              127, "Applause")
        cls.set_patch("GUNSHOT",               128, "Gunshot")
        #
        return

    def __init__(self, patchid, patchnum, patchname):
        self.id       = patchid
        self.patchnum = patchnum
        self.name     = patchname
        return

    def __str__(self):
        return f"Patch({self.patchnum:3d}, {self.name})"

Patch.__class_init__()

Patches = Patch.__iter_patches__

# -----------------
# MidiMessage class
# -----------------

class MidiMessage:
    """
    Provides support functions for generating Midi messages
    """

    # Message construction functions
    # Functions return a sequence of byte values that can be sent on a Midi port

    @staticmethod
    def note_on(channel, note, velocity=64):
        # channel   MIDI channel number 1-16
        # note      Note value, instance of Note class (above)
        # velocity  Key press velocity (1-127, defaults to 64).  0 may turn note off.
        #
        # See: https://cmtext.indiana.edu/MIDI/chapter3_channel_voice_messages.php
        return [0x90+channel-1, note.midinum, velocity]

    @staticmethod
    def note_off(channel, note, velocity=64):
        # channel   MIDI channel number 1-16
        # note      Note value, instance of Note class (above)
        # velocity  Key release velocity (1-127, defaults to 64).
        #
        # See: https://cmtext.indiana.edu/MIDI/chapter3_channel_voice_messages.php
        return [0x80+channel-1, note.midinum, velocity]

    @staticmethod
    def chord_on(channel, chord, velocity=64):
        # channel   MIDI channel number 1-16
        # chord     Chord value, instance of Chord class (above)
        # velocity  Key press velocity (1-127, defaults to 64).  0 may turn chord off.
        #
        # Returns list of messages to start playing chord
        return [ MidiMessage.note_on(channel, n, velocity) for n in chord]

    @staticmethod
    def chord_off(channel, chord, velocity=64):
        # channel   MIDI channel number 1-16
        # chord     Chord value, instance of Chord class (above)
        # velocity  Key press velocity (1-127, defaults to 64).  0 may turn chord off.
        #
        # Returns list of messages to stop playing chord
        return [ MidiMessage.note_off(channel, n, velocity) for n in chord]

    @staticmethod
    def program_change(channel, patch):
        # Selects patch ("voice") used on designated channel.
        #
        # channel   MIDI channel number 1-16
        # patch     Patch object (see above) to be used with designated channel
        #
        # See: https://cmtext.indiana.edu/MIDI/chapter3_channel_voice_messages.php
        return[0xC0+channel-1, patch.patchnum-1]

    @staticmethod
    def bank_switch(channel, banknum):
        # May be used to extend range of patches available to use
        #
        # channel   MIDI channel number 1-16
        # banknum   Bank number (1-128) @@@is this correct??@@@
        #
        # TODO (if needed): split out bank number into MSB and LSB and assemble two controller messages
        #
        # See: https://cmtext.indiana.edu/MIDI/chapter3_controller_change2.php
        return[0xB0+channel-1, 32, banknum-1]





