import struct
from pymod.constants import *
from pymod.module import *
from pymod.tables import *
from pymod.util import *

class MODNote(Note):
    """The definition of a generic MOD note and it's effects"""
    def __init__(self, pattdata=[]):
        if pattdata:
            note = self.mod_period_to_note(((pattdata[0] & 0xf) << 8) + pattdata[1])
            instrument = (pattdata[0] & 0xf0) + (pattdata[2] >> 4)
            voleffect = VOLFX_NONE
            volparam = 0
            effect = pattdata[2] & 0xf
            param = pattdata[3]
            super(MODNote, self).__init__(note, instrument, voleffect, volparam, effect, param)
        else:
            super(MODNote, self).__init__(0, 0, 0, 0, 0, 0)
        
    def mod_period_to_note(self, period):
        if period:
            for num in range(NOTE_LAST + 1):
                if period >= (32 * period_table[num % 12] >> (num / 12 + 2)):
                    return num + 1
        return NOTE_NONE
    
    def __unicode__(self):
        keys = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
        commands = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if self.note == 0: ret1 = '...'
        elif self.note > 0 and self.note <=120:
            split = divmod(self.note-1, 12)
            ret1 = '%s%s' % (keys[split[1]], str(split[0]))
        elif self.note == 254: ret1 = '^^^'
        elif self.note == 255: ret1 = '==='

        if self.instrument: ret2 = str(self.instrument).zfill(2)
        else: ret2 = '..'

        # No volume columns for MOD files
        ret3 = '..'

        if self.effect: letter = commands[self.effect-1]
        else: letter = '.'
        ret4 = '%s%s' % (letter, hex(self.param)[2:].zfill(2).upper())
        
        return '%s %s %s %s' % (ret1, ret2, ret3, ret4)

    def __repr__(self):
        return self.__unicode__()


class MODPattern(Pattern):
    """The definition of the MOD pattern"""
    def __init__(self, file=None, rows=64, channels=4):
        super(MODPattern, self).__init__(rows, channels)
        
        if file:
            self.load(file)
        else:
            self.data = self.empty(self.rows, self.channels)
        
    def empty(self, rows, channels):
        pattern = []
        for row in range(rows):
            pattern.append([])
            for channel in range(channels):
                pattern[row].append(MODNote())
        return pattern
        
    def load(self, file):
        self.data = self.empty(self.rows, self.channels)

        for row in range(self.rows):
            for channel in range(self.channels):
                self.data[row][channel] = MODNote(list(struct.unpack(">4B", file.read(4))))


class MODSample(Sample):
    """Definition of an MOD sample"""
    def __init__(self, file=None):
        super(MODSample, self).__init__()
        self.modsamploadflags = SF_8 | SF_LE | SF_M | SF_PCMS
        
        if file: self.load(file, 0)
        
    def load(self, file, loadtype=0):
        
        if loadtype == 0:
            # Loads the MOD sample headers
            modsampname = struct.unpack(">22s", file.read(22))[0]
            modsamplength = struct.unpack(">H", file.read(2))[0]
            modsampfinetune = struct.unpack(">b", file.read(1))[0]
            modsampvolume = struct.unpack(">B", file.read(1))[0]
            modsamploopbegin = struct.unpack(">H", file.read(2))[0]
            modsamplooplength = struct.unpack(">H", file.read(2))[0]

            # Parse it into generic Sample
            self.name = modsampname
            self.filename = modsampname
            self.volume = MIN(modsampvolume, 64) * 4
            self.length = modsamplength * 2
            self.c5speed = MOD_FINETUNE(modsampfinetune)
            self.loopbegin = modsamploopbegin
            if modsamplooplength > 2: self.flags = self.flags | CHN_LOOP
            self.loopend = self.loopbegin + modsamplooplength

        elif loadtype == 1:
            # . . .otherwise, load sample data
            super(MODSample, self).load(file, file.tell(), self.modsamploadflags)


class MOD(Module):
    """A class that holds a generic MOD file"""
    MOD_TYPES = (
        ('M.K.', 'Amiga-NewTracker', 4),
        ('M!K!', 'Amiga-ProTracker', 4),
        ('M&K!', 'Amiga-NoiseTracker', 4),
        ('N.T.', 'Amiga-NoiseTracker?', 4),    # ???, mentioned in libModplug
        ('CD81', '8 Channel Falcon', 8),
        ('OCTA', 'Amiga Oktalyzer', 8),        # SchismTracker/libModplug have
        ('OKTA', 'Amiga Oktalyzer', 8),        # 'C' or 'K', but not both
        ('FLT4', '4 Channel Startrekker', 4),
        ('FLT8', '8 Channel Startrekker', 8),
        ('2CHN', '2 Channel MOD', 2),
        ('3CHN', '3 Channel MOD', 3),          # Does this show up ever?
        ('4CHN', '4 Channel MOD', 4),
        ('5CHN', '5 Channel TakeTracker', 5),
        ('6CHN', '6 Channel MOD', 6),
        ('7CHN', '7 Channel TakeTracker', 7),
        ('8CHN', '8 Channel MOD', 8),
        ('9CHN', '9 Channel TakeTracker', 9),
        ('10CH', '10 Channel MOD', 10),
        ('11CH', '11 Channel TakeTracker', 11),
        ('12CH', '12 Channel MOD', 12),
        ('13CH', '13 Channel TakeTracker', 13),
        ('14CH', '14 Channel MOD', 14),
        ('15CH', '15 Channel TakeTracker', 15),
        ('16CH', '16 Channel MOD', 16),
        ('18CH', '18 Channel MOD', 18),
        ('20CH', '20 Channel MOD', 20),
        ('22CH', '22 Channel MOD', 22),
        ('24CH', '24 Channel MOD', 24),
        ('26CH', '26 Channel MOD', 26),
        ('28CH', '28 Channel MOD', 28),
        ('30CH', '30 Channel MOD', 30),
        ('32CH', '32 Channel MOD', 32),
        ('16CN', '16 Channel MOD', 16),        # Not certain where these two
        ('32CN', '32 Channel MOD', 32),        # come from. (libModplug)
        ('TDZ1', '1 Channel TakeTracker', 1),
        ('TDZ2', '2 Channel TakeTracker', 2),
        ('TDZ3', '3 Channel TakeTracker', 3),
        ('TDZ4', '4 Channel MOD', 4),
        ('TDZ5', '5 Channel MOD', 5),
        ('TDZ6', '6 Channel MOD', 6),
        ('TDZ7', '7 Channel MOD', 7),
        ('TDZ8', '8 Channel MOD', 8),
        ('TDZ9', '9 Channel MOD', 9)
    )
        
    def __init__(self, filename=None):
        super(MOD, self).__init__()
        if not filename:
            self.id = '4CHN'                # /b/, for teh lulz. . .(bad joke)
            self.tracker = '4 Channel MOD'
            self.restartpos = 0
            self.channelnum = 4
            self.samplenum = 31
        else:
            f = open(filename, 'rb')        # NOTE: MOD files should be big-endian!
            
            f.seek(1080)                    # Magic number is in middle of file.
            magic = struct.unpack(">4s", f.read(4))[0]
            
            self.id = ''
            for TYPE in self.MOD_TYPES:
                if magic == TYPE[0]:
                    self.id = magic
                    self.tracker = TYPE[1]
                    self.channelnum = TYPE[2]
                    self.samplenum = 31
                    break
            if self.id == '':
                self.id = '????'
                self.tracker = '*OLD* 4 Channel MOD'
                self.channelnum = 4
                self.samplenum = 15
            
            f.seek(0)
            
            self.name = struct.unpack(">20s", f.read(20))[0]   # Song title (padded with NULL)
            
            self.samples = []
            for num in range(self.samplenum):
                self.samples.append(MODSample(f))    # Loading sample headers
            
            self.ordernum = struct.unpack(">B", f.read(1))[0]           # Number of orders in song
            self.restartpos = struct.unpack(">B", f.read(1))[0]         # Restart position
            self.orders = list(struct.unpack(">128B", f.read(128)))
            
            # Fixes for buggy Startrekker MOD's. . .
            fixed = 0 
            if self.id == 'FLT8':
                for order in self.orders:
                    if order & 1:
                        fixed = 1
                        self.id = 'FLT4'
                        self.tracker = '4 Channel Startrekker (buggy)'
                        self.channelnum = 4
                if not fixed:
                    for num in range(128):
                        self.orders[num] = self.orders[num] >> 1
            
            self.patternnum = max(self.orders) + 1
            self.tempo = 125
            self.speed = 6
            
            curpos = f.tell()
            
            # Testing for WOW files. . .
            if self.id == 'M.K.':
                f.seek(0, 2)
                sampsize = 0
                for num in range(self.samplenum):
                    sampsize = sampsize + self.samples[num].length
                if f.tell() == 2048 * self.patternnum + sampsize + 3132:
                    self.channelnum = 8
                    self.tracker = 'Mods Grave WOW'
            
            f.seek(curpos)
            if self.id != '????':
                f.seek(4, 1)                         # Skip the magic id. . .
            
            self.patterns = []
            if self.patternnum:
                for num in range(self.patternnum):
                    self.patterns.append(MODPattern(f, channels=self.channelnum))

            for num in range(self.samplenum):
                self.samples[num].load(f, 1)         # Loading sample data

            f.close()

