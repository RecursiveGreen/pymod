import struct
from pymod.constants import *
from pymod.module import *
from pymod.util import *

class XMNote(Note):
    """The definition of an note and it's effects in Fast Tracker II"""
    def __init__(self, note=0, instrument=0, voleffect=0, volparam=0, effect=0, param=0):
        super(XMNote, self).__init__(note, instrument, voleffect, volparam, effect, param)

    def __unicode__(self):
        keys = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
        commands = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if self.note == 0: ret1 = '...'
        elif self.note > 0 and self.note <=120:
            split = divmod(self.note-13, 12)
            ret1 = '%s%s' % (keys[split[1]], str(split[0]))
        elif self.note == 254: ret1 = '^^^'
        elif self.note == 255: ret1 = '==='

        if self.instrument: ret2 = hex(self.instrument)[2:].zfill(2).upper()
        else: ret2 = '..'

        if self.voleffect == VOLFX_NONE: ret3 = '..'
        elif self.voleffect == VOLFX_VOLUME: ret3 = hex(self.volparam)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_VOLSLIDEDOWN: ret3 = hex(self.volparam + 0x60)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_VOLSLIDEUP: ret3 = hex(self.volparam + 0x70)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_FINEVOLDOWN: ret3 = hex(self.volparam + 0x80)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_FINEVOLUP: ret3 = hex(self.volparam + 0x90)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_VIBRATOSPEED: ret3 = hex(self.volparam + 0xA0)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_VIBRATODEPTH: ret3 = hex(self.volparam + 0xB0)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_PANNING: ret3 = hex(((self.volparam - 2) >> 2) + 0xC0)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_PANSLIDELEFT: ret3 = hex(self.volparam + 0xD0)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_PANSLIDERIGHT: ret3 = hex(self.volparam + 0xE0)[2:].zfill(2).upper()
        elif self.voleffect == VOLFX_TONEPORTAMENTO: ret3 = hex(self.volparam + 0xF0)[2:].zfill(2).upper()

        if self.effect: letter = commands[self.effect-1]
        else: letter = '.'
        ret4 = '%s%s' % (letter, hex(self.param)[2:].zfill(2).upper())
        
        return '%s %s %s %s' % (ret1, ret2, ret3, ret4)

    def __repr__(self):
        return self.__unicode__()


class XMPattern(Pattern):
    """The definition of the XM pattern"""
    def __init__(self, file=None, rows=64, channels=32):
        super(XMPattern, self).__init__(rows, channels)
        self.headerlen = 9
        self.packtype = 0
        self.packsize = rows * channels
        
        if file:
            self.load(file)
        else:
            self.data = self.empty(self.rows, self.channels)
        
    def empty(self, rows, channels):
        pattern = []
        for row in range(rows):
            pattern.append([])
            for channel in range(channels):
                pattern[row].append(XMNote())
        return pattern
        
    def load(self, file):
        self.headerlen = struct.unpack("<L", file.read(4))[0]
        self.packtype = struct.unpack("<B", file.read(1))[0]
        self.rows = struct.unpack("<H", file.read(2))[0]
        self.packsize = struct.unpack("<H", file.read(2))[0]
        
        self.data = self.empty(self.rows, self.channels)

        maskvar = 0
        end = file.tell() + self.packsize
        
        for row in range(self.rows):
            for channel in range(self.channels):
                if file.tell() < end:
                    maskvar = struct.unpack("<B", file.read(1))[0]
                    note = 0
                    inst = 0
                    voldata = 0
                    command = 0
                    param = 0
                    
                    if maskvar & 128:
                        if maskvar & 1: note = struct.unpack("<B", file.read(1))[0]
                        if maskvar & 2: inst = struct.unpack("<B", file.read(1))[0]
                        if maskvar & 4: voldata = struct.unpack("<B", file.read(1))[0]
                        if maskvar & 8: command = struct.unpack("<B", file.read(1))[0]
                        if maskvar & 16: param = struct.unpack("<B", file.read(1))[0]
                    else:
                        note = maskvar
                        inst = struct.unpack("<B", file.read(1))[0]
                        voldata = struct.unpack("<B", file.read(1))[0]
                        command = struct.unpack("<B", file.read(1))[0]
                        param = struct.unpack("<B", file.read(1))[0]
                        
                    # Cleanup. . .
                    if note > NOTE_NONE and note < 97:
                        self.data[row][channel].note = note + 12
                    elif note == 97:
                        self.data[row][channel].note = NOTE_OFF
                    else:
                        self.data[row][channel].note = NOTE_NONE
                        
                    if inst == 255:
                        self.data[row][channel].instrument = 0
                    else:
                        self.data[row][channel].instrument = inst
                        
                    if voldata >= 16 and voldata <= 80:
                        self.data[row][channel].voleffect = VOLFX_VOLUME
                        self.data[row][channel].volparam = voldata - 16
                    elif voldata >= 96:
                        volcmd = voldata & 0xF0
                        voldata = voldata & 0x0F
                        self.data[row][channel].volparam = voldata
                        
                        if volcmd == 0x60: self.data[row][channel].voleffect = VOLFX_VOLSLIDEDOWN
                        if volcmd == 0x70: self.data[row][channel].voleffect = VOLFX_VOLSLIDEUP
                        if volcmd == 0x80: self.data[row][channel].voleffect = VOLFX_FINEVOLDOWN
                        if volcmd == 0x90: self.data[row][channel].voleffect = VOLFX_FINEVOLUP
                        if volcmd == 0xA0: self.data[row][channel].voleffect = VOLFX_VIBRATOSPEED
                        if volcmd == 0xB0: self.data[row][channel].voleffect = VOLFX_VIBRATODEPTH
                        if volcmd == 0xC0:
                            self.data[row][channel].voleffect = VOLFX_PANNING
                            self.data[row][channel].volparam = (voldata << 2) + 2
                        if volcmd == 0xD0: self.data[row][channel].voleffect = VOLFX_PANSLIDELEFT
                        if volcmd == 0xE0: self.data[row][channel].voleffect = VOLFX_PANSLIDERIGHT
                        if volcmd == 0xF0: self.data[row][channel].voleffect = VOLFX_TONEPORTAMENTO
                        
                    self.data[row][channel].effect = command
                    self.data[row][channel].param = param


class XMEnvelope(Envelope):
    """The definition of an envelope for an XM instrument. There are a total
       of two envelopes: Volume and Panning."""
    def __init__(self, type=0):
        super(XMEnvelope, self).__init__(type)


class XMSample(Sample):
    """Definition of an Fast Tracker II sample"""
    def __init__(self, file=None):
        super(XMSample, self).__init__()
        self.xmsamploadflags = SF_LE | SF_M | SF_PCMD
        
        if file: self.load(file, 0)
        
    def load(self, file, loadtype=0):
        
        if loadtype == 0:
            # Loads the XM sample headers
            xmsamplength = struct.unpack("<L", file.read(4))[0]
            xmsamploopbegin = struct.unpack("<L", file.read(4))[0]
            xmsamploopend = struct.unpack("<L", file.read(4))[0] + xmsamploopbegin
            xmsampvolume = struct.unpack("<B", file.read(1))[0]
            xmsampfinetune = struct.unpack("<b", file.read(1))[0]
            xmsampflags = struct.unpack("<B", file.read(1))[0]
            xmsamppanning = struct.unpack("<B", file.read(1))[0]
            xmsamprelnote = struct.unpack("<b", file.read(1))[0]
            xmsampRESERVED = struct.unpack("<B", file.read(1))[0]
            xmsampname = struct.unpack("<22s", file.read(22))[0]

            # Parse it into generic Sample
            self.name = xmsampname
            self.filename = xmsampname
            self.volume = MIN(xmsampvolume, 64) * 4
            self.length = xmsamplength
            self.loopbegin = xmsamploopbegin
            self.loopend = xmsamploopend
            self.flags = CHN_PANNING
            
            if self.loopbegin >= self.loopend:
                xmsampflags = xmsampflags & ~3
            if xmsampflags & 3:
                if xmsampflags & 3 == 2: self.flags = self.flags | CHN_PINGPONGLOOP
                if xmsampflags & 3 == 1: self.flags = self.flags | CHN_LOOP
            if xmsampflags & 0x10:
                self.flags = self.flags | CHN_16BIT
                self.length = self.length >> 1
                self.loopbegin = self.loopbegin >> 1
                self.loopend = self.loopend >> 1
            
            self.panning = xmsamppanning
            self.c5speed = transpose_to_frequency(xmsamprelnote, xmsampfinetune)

        elif loadtype == 1:
            # . . .otherwise, load sample data
            self.xmsamploadflags = self.xmsamploadflags | (SF_8, SF_16)[bool(self.flags & CHN_16BIT)]
            super(XMSample, self).load(file, file.tell(), self.xmsamploadflags)


class XMInstrument(Instrument):
    """Definition of an Fast Tracker II instrument"""
    def __init__(self, file=None):
        super(XMInstrument, self).__init__()
        self.xminstnumsamples = 0
        self.samples = []
        
        if file: self.load(file)
        
    def load(self, file):    
        # Load the XM instrument data
        xminstheadsize = struct.unpack("<L", file.read(4))[0]
        xminstname = struct.unpack("<22s", file.read(22))[0]
        xminsttype = struct.unpack("<B", file.read(1))[0]    # random junk, supposedly. . .
        self.xminstnumsamples = struct.unpack("<H", file.read(2))[0]
        self.name = xminstname
        
        xminstsmpheadsize = struct.unpack("<L", file.read(4))[0]
        
        if self.xminstnumsamples > 0:
            xminstnotekeytable = []
            for i in range(96):
                xminstnotekeytable.append(struct.unpack("<B", file.read(1))[0])
            
            xminstvolenv= []
            for i in range(12):
                xminstvolenv.append(list(struct.unpack("<HH", file.read(4))))
            
            xminstpanenv= []
            for i in range(12):
                xminstpanenv.append(list(struct.unpack("<HH", file.read(4))))
                
            xminstvolpoints = struct.unpack("<B", file.read(1))[0]
            xminstpanpoints = struct.unpack("<B", file.read(1))[0]
            xminstvolsustpnt = struct.unpack("<B", file.read(1))[0]
            xminstvollpstpnt = struct.unpack("<B", file.read(1))[0]
            xminstvollpedpnt = struct.unpack("<B", file.read(1))[0]
            xminstpansustpnt = struct.unpack("<B", file.read(1))[0]
            xminstpanlpstpnt = struct.unpack("<B", file.read(1))[0]
            xminstpanlpedpnt = struct.unpack("<B", file.read(1))[0]
            xminstvolenvtype = struct.unpack("<B", file.read(1))[0]
            xminstpanenvtype = struct.unpack("<B", file.read(1))[0]
            xminstvibtype = struct.unpack("<B", file.read(1))[0]
            xminstvibsweep = struct.unpack("<B", file.read(1))[0]
            xminstvibdepth = struct.unpack("<B", file.read(1))[0]
            xminstvibrate = struct.unpack("<B", file.read(1))[0]
            xminstvolfadeout = struct.unpack("<H", file.read(2))[0]
            xminstRESERVED1 = list(struct.unpack("<11H", file.read(22)))
            
            # Parse it into the generic Instrument
            for i in range(96):
                self.notemap[i] = i
                self.samplemap[i] = xminstnotekeytable[i]
                
            self.volumeenv = XMEnvelope()
            self.volumeenv.ticks = []
            self.volumeenv.values = []
            self.panningenv = XMEnvelope()
            self.panningenv.ticks = []
            self.panningenv.values = []
            for i in range(12):
                self.volumeenv.ticks.append(xminstvolenv[i][0])
                self.volumeenv.values.append(xminstvolenv[i][1])
                self.panningenv.ticks.append(xminstpanenv[i][0])
                self.panningenv.values.append(xminstpanenv[i][1])
                
            self.volumeenv.nodes = xminstvolpoints
            self.panningenv.nodes = xminstpanpoints
                
            self.volumeenv.sustloopbegin = xminstvolsustpnt
            self.volumeenv.sustloopend = xminstvolsustpnt
            self.volumeenv.loopbegin = xminstvollpstpnt
            self.volumeenv.loopend = xminstvollpedpnt
            self.panningenv.sustloopbegin = xminstpansustpnt
            self.panningenv.sustloopend = xminstpansustpnt
            self.panningenv.loopbegin = xminstpanlpstpnt
            self.panningenv.loopend = xminstpanlpedpnt

            if xminstvolenvtype & 1: self.flags | ENV_VOLUME
            if xminstvolenvtype & 2: self.flags | ENV_VOLSUSTAIN
            if xminstvolenvtype & 4: self.flags | ENV_VOLLOOP
            if xminstpanenvtype & 1: self.flags | ENV_PANNING
            if xminstpanenvtype & 2: self.flags | ENV_PANSUSTAIN
            if xminstpanenvtype & 4: self.flags | ENV_PANLOOP
            
            self.fadeout = xminstvolfadeout
            
            if self.xminstnumsamples:
                # Load headers. . .
                for num in range(self.xminstnumsamples):
                    self.samples.append(XMSample(file))
                    self.samples[num].vibtype = xminstvibtype
                    self.samples[num].vibrate = xminstvibsweep
                    self.samples[num].vibdepth = xminstvibdepth
                    self.samples[num].vibspeed = xminstvibrate
                # . . .followed by sample data
                for num in range(self.xminstnumsamples):
                    self.samples[num].load(file, 1)


class XM(Module):
    """A class that holds an XM module file"""
    def __init__(self, filename=None):
        super(XM, self).__init__()
        if not filename:
            self.id = 'Extended Module: '        # 17 char length (stupid space)
            self.b1Atch = 0x1A                   # byte 1A temp char. . . ;)
            self.tracker = 'FastTracker v2.00'
            self.cwtv = 0x0104
            self.headerlength = 0
            self.restartpos = 0
            self.channelnum = 32
        else:
            f = open(filename, 'rb')
            
            self.filename = filename
            self.id = struct.unpack("<17s", f.read(17))[0]          # 'Extended module: '
            self.name = struct.unpack("<20s", f.read(20))[0]        # Song title (padded with NULL)
            self.b1Atch = struct.unpack("<B", f.read(1))[0]         # 0x1A
            self.tracker = struct.unpack("<20s", f.read(20))[0]
            self.cwtv = struct.unpack("<H", f.read(2))[0]           # Created with tracker version (XM y.xx = 0yxxh)
            self.headerlength = struct.unpack("<L", f.read(4))[0]
            self.ordernum = struct.unpack("<H", f.read(2))[0]       # Number of orders in song
            self.restartpos = struct.unpack("<H", f.read(2))[0]     # Restart position
            self.channelnum = struct.unpack("<H", f.read(2))[0]     # Number of channels in song
            self.patternnum = struct.unpack("<H", f.read(2))[0]     # Number of patterns in song
            self.instrumentnum = struct.unpack("<H", f.read(2))[0]  # Number of instruments in song
            self.flags = struct.unpack("<H", f.read(2))[0]
            self.tempo = struct.unpack("<H", f.read(2))[0]
            self.speed = struct.unpack("<H", f.read(2))[0]
            
            self.orders = list(struct.unpack("<256B", f.read(256)))
            
            self.patterns = []
            if self.patternnum:
                for num in range(self.patternnum):
                    self.patterns.append(XMPattern(f, channels=self.channelnum))

            self.instruments = []
            if self.instrumentnum:
                for num in range(self.instrumentnum):
                    self.instruments.append(XMInstrument(f))

            f.close()
            
    def detect(filename):
        f = open(filename, 'rb')
        id = struct.unpack("<17s", f.read(17))[0]
        f.close()
        if id == 'Extended Module: ':
            return 2
        else:
            return 0
    detect = staticmethod(detect)
            
    def gettracker(self):
        return self.tracker.replace('\x00', ' ').strip()
    
    def __unicode__(self):
        return 'XM Module (%s)' % ((self.getname(), self.filename)[bool(self.getname() == '')])
    
    def __repr__(self):
        return self.__unicode__()

