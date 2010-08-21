import struct
from pymod.constants import *
from pymod.module import *
from pymod.util import *

class S3MNote(Note):
    """The definition of an note and it's effects in Scream Tracker 3"""
    def __init__(self, note=0, instrument=0, voleffect=0, volparam=0, effect=0, param=0):
        super(S3MNote, self).__init__(note, instrument, voleffect, volparam, effect, param)

    def __unicode__(self):
        keys = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
        commands = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if self.note == 0: ret1 = '...'
        elif self.note > 0 and self.note <=120:
            split = divmod(self.note-1, 12)
            ret1 = '%s%s' % (keys[split[1]], str(split[0]))
        elif self.note == 254: ret1 = '^^^'
        elif self.note == 255: ret1 = '==='

        if self.instrument: ret2 = str(self.instrument).zfill(2)
        else: ret2 = '..'

        if self.voleffect == VOLFX_NONE: ret3 = '..'
        else: ret3 = str(self.volparam).zfill(2).upper()

        if self.effect: letter = commands[self.effect-1]
        else: letter = '.'
        ret4 = '%s%s' % (letter, hex(self.param)[2:].zfill(2).upper())
        
        return '%s %s %s %s' % (ret1, ret2, ret3, ret4)

    def __repr__(self):
        return self.__unicode__()


class S3MPattern(Pattern):
    """The definition of the S3M pattern"""
    def __init__(self, file=None, offset=0, rows=64, channels=32):
        super(S3MPattern, self).__init__(rows, channels)
        self.length = 0
        
        if file:
            self.load(file, offset)
        else:
            self.data = self.empty(self.rows, self.channels)
        
    def empty(self, rows, channels):
        pattern = []
        for row in range(rows):
            pattern.append([])
            for channel in range(channels):
                pattern[row].append(S3MNote())
        return pattern
        
    def load(self, file, offset):
        file.seek(offset)
            
        self.length = struct.unpack("<H", file.read(2))[0]
        self.rows = 64                  # always 64 rows with S3M
        
        self.data = self.empty(self.rows, self.channels)

        curchannel = 0
        currow = 0
        maskvar = 0
        channelvar = 0
        temp = 0
        end = offset + self.length + 2
            
        while currow < self.rows and file.tell() < end:
            maskvar = struct.unpack("<B", file.read(1))[0]
            curchannel = (maskvar & 31)
            
            if maskvar == 0: currow = currow + 1
            
            if maskvar & 32:
                temp = struct.unpack("<B", file.read(1))[0]
                if temp == 255:
                    self.data[currow][curchannel].note = NOTE_NONE
                elif temp == 254:
                    self.data[currow][curchannel].note = (NOTE_CUT, NOTE_OFF)[curchannel > 16 and curchannel < 26]
                else:
                    self.data[currow][curchannel].note = (temp >> 4) * 12 + (temp & 0x0F) + 13
                self.data[currow][curchannel].instrument = struct.unpack("<B", file.read(1))[0]
                
            if maskvar & 64:
                self.data[currow][curchannel].voleffect = VOLFX_VOLUME
                temp = struct.unpack("<B", file.read(1))[0]
                if self.data[currow][curchannel].volparam == 255:
                    self.data[currow][curchannel].voleffect = VOLFX_NONE
                    self.data[currow][curchannel].volparam = 0
                elif self.data[currow][curchannel].volparam > 64:
                    self.data[currow][curchannel].volparam = 64
                else:
                    self.data[currow][curchannel].volparam = temp
                    
            if maskvar & 128:
                temp = struct.unpack("<B", file.read(1))[0]
                self.data[currow][curchannel].param = struct.unpack("<B", file.read(1))[0]
                if temp == 255:
                    self.data[currow][curchannel].effect = 0
                    self.data[currow][curchannel].param = 0
                else:
                    self.data[currow][curchannel].effect = temp


class S3MSample(Sample):
    """Definition of an Scream Tracker 3 sample"""
    def __init__(self, file=None, offset=0, ffi=2):
        super(S3MSample, self).__init__()
        self.s3msamploadflags = SF_LE
        self.s3msampoffset = 0
        
        if file: self.load(file, offset, ffi)
        
    def load(self, file, offset, ffi):
        # Load the S3M sample headers
        file.seek(offset)
        
        s3msamptype = struct.unpack("<B", file.read(1))[0]
        s3msampfilename = struct.unpack("<12s", file.read(12))[0]
        s3msampmemseg = list(struct.unpack("<3B", file.read(3)))
        
        if s3msamptype == 0:                # No sample
            file.seek(12, 1)            # skip loop info
            s3msampvolume = struct.unpack("<B", file.read(1))[0]
            file.seek(3, 1)             # unused byte
            s3msamplength = 0
            s3msamploopbegin = 0
            s3msamploopend = 0
        elif s3msamptype == 1:              # regular sample
            self.s3msampoffset = (s3msampmemseg[1] | (s3msampmemseg[2] << 8) | (s3msampmemseg[0] << 16)) * 16
            s3msamplength = struct.unpack("<L", file.read(4))[0]
            s3msamploopbegin = struct.unpack("<L", file.read(4))[0]
            s3msamploopend = struct.unpack("<L", file.read(4))[0]
            s3msampvolume = struct.unpack("<B", file.read(1))[0]
            file.seek(1, 1)             # unused byte
            s3msamppack = struct.unpack("<B", file.read(1))[0]
            s3msampflags = struct.unpack("<B", file.read(1))[0]
            
            if s3msampflags & 1: self.flags = self.flags | CHN_LOOP
            
            self.s3msamploadflags = SF_LE | (SF_PCMS, SF_PCMU)[ffi == 2] | (SF_8, SF_16)[bool(s3msampflags & 4)] | (SF_M, SF_SS)[bool(s3msampflags & 2)]
        elif s3msamptype > 1:
            self.adlibbytes = list(struct.unpack("<12B", file.read(12)))
            s3msampvolume = struct.unpack("<B", file.read(1))[0]
            file.seek(3, 1)             # skipping Dsk (?) and two unused bytes
            s3msamplength = 0
            s3msamploopbegin = 0
            s3msamploopend = 0
            self.flags = self.flags | CHN_ADLIB

        s3msampc5speed = struct.unpack("<L", file.read(4))[0]
        file.seek(12, 1)             # skip unused bytes & int. memory variables
        s3msampname = struct.unpack("<28s", file.read(28))[0].replace('\x00', ' ').rstrip()
        
        if s3msamptype == 0:            # none if unused, otherwise SCRS or SCRI
            s3msampid = ''
        else:
            s3msampid = struct.unpack("<4s", file.read(4))[0]

        # Parse it into generic Sample
        self.name = s3msampname
        self.filename = s3msampfilename
        self.volume = MIN(s3msampvolume, 64) * 4
        self.length = s3msamplength
        self.loopbegin = s3msamploopbegin
        self.loopend = s3msamploopend
        self.c5speed = s3msampc5speed

        if s3msamptype > 0:
            super(S3MSample, self).load(file, self.s3msampoffset, self.s3msamploadflags)


class S3M(Module):
    """A class that holds an S3M module file"""
    def __init__(self, filename=None):
        if not filename:
            self.songname = ''
            self.b1Atch = 0x1A              # byte 1A temp char. . . ;)
            self.type = 16
            self.RESERVED1 = 0
            self.ordernum = 0
            self.samplenum = 0
            self.patternnum = 0
            self.flags = 0
            self.cwtv = 0x1320
            self.fileformat = 2
            self.id = 'SCRM'
            self.globalvol = 0
            self.speed = 0
            self.tempo = 0
            self.mastervol = 0
            self.ultraclick = 0
            self.defaultpan = 0
            self.RESERVED2 = []
            self.special = 0
            self.channelset = []
            self.orders = []
            self.sampleoffset = []
            self.patternoffset = []
            self.channelpan = []            
        else:
            f = open(filename, 'rb')
            
            self.songname = struct.unpack("<28s", f.read(28))[0].replace('\x00', ' ').strip()    # Song title (padded with NULL)
            self.b1Atch = struct.unpack("<B", f.read(1))[0]             # 0x1A
            self.type = struct.unpack("<B", f.read(1))[0]               # File Type (16 = ST3)
            self.RESERVED1 = struct.unpack("<H", f.read(2))[0]          # RESERVED (??)
            self.ordernum = struct.unpack("<H", f.read(2))[0]           # Number of orders in song
            self.samplenum = struct.unpack("<H", f.read(2))[0]          # Number of samples in song
            self.patternnum = struct.unpack("<H", f.read(2))[0]         # Number of patterns in song
            self.flags = struct.unpack("<H", f.read(2))[0]
            self.cwtv = struct.unpack("<H", f.read(2))[0]               # Created with tracker version (S3M y.xx = 1yxxh)
            self.fileformat = struct.unpack("<H", f.read(2))[0]
            self.id = struct.unpack("<4s", f.read(4))[0]                # 'SCRM'
            self.globalvol = struct.unpack("<B", f.read(1))[0]
            self.speed = struct.unpack("<B", f.read(1))[0]
            self.tempo = struct.unpack("<B", f.read(1))[0]
            self.mastervol = struct.unpack("<B", f.read(1))[0]
            self.ultraclick = struct.unpack("<B", f.read(1))[0]
            self.defaultpan = struct.unpack("<B", f.read(1))[0]
            self.RESERVED2 = list(struct.unpack("<8B", f.read(8)))
            self.special = struct.unpack("<H", f.read(2))[0]
            
            self.channelset = list(struct.unpack("<32B", f.read(32)))
            self.orders = list(struct.unpack("<%iB" % (self.ordernum), f.read(self.ordernum)))
            
            self.sampleoffset = []
            if self.samplenum > 0:
                self.sampleoffset = map(lambda x: x * 16, list(struct.unpack("<%iH" % (self.samplenum), f.read(self.samplenum * 2))))
            
            self.patternoffset = []
            if self.patternnum > 0:
                self.patternoffset = map(lambda x: x * 16, list(struct.unpack("<%iH" % (self.patternnum), f.read(self.patternnum * 2))))
            
            self.channelpan = list(struct.unpack("<32B", f.read(32)))
            
            self.samples = []
            if self.sampleoffset:
                for offset in self.sampleoffset:
                    self.samples.append(S3MSample(f, offset, self.fileformat))
            
            self.patterns = []
            if self.patternoffset:
                for offset in self.patternoffset:
                    if offset == 0:
                        self.patterns.append(S3MPattern())
                    else:
                        self.patterns.append(S3MPattern(f, offset))
                    
            f.close()
