import struct
from pymod.constants import *

class Sample(object):
    """A simple sample object"""
    def __init__(self):
        self.length = 0
        self.loopbegin = 0
        self.loopend = 0
        self.sustloopbegin = 0
        self.sustloopend = 0
        self.c5speed = 8363
        self.panning = 0
        self.volume = 256
        self.globalvol = 64
        self.flags = 0
        self.vibtype = 0
        self.vibrate = 0
        self.vibdepth = 0
        self.vibspeed = 0
        self.name = ''
        self.filename = ''
        
        self.played = 0
        self.globalvolsaved = 0
        self.adlibbytes = []

        self.data = []
    
    def load(self, file, offset, loadflags):
        if self.flags & CHN_ADLIB or self.length < 1 or not file:
            self.data = []
            return
        
        # Here we go. . .
        file.seek(offset)
        
        # 1: 8-bit unsigned PCM data
        if loadflags == SF(SF_PCMU, SF_8, SF_M, SF_LE):
            for i in range(self.length):
                self.data.append(struct.unpack("<b", file.read(1))[0] - 0x80)
            self.adjustloops()
            return
    
        # 2: 8-bit ADPCM data with linear table
        if loadflags == SF(SF_PCMD, SF_8, SF_M, SF_LE):
            delta = 0
            for i in range(self.length):
                delta = delta + struct.unpack("<b", file.read(1))[0]
                self.data.append(delta)
            self.adjustloops()
            return
        
        # 4: 16-bit ADPCM data with linear table
        if loadflags == SF(SF_PCMD, SF_16, SF_M, SF_LE):
            ustmp = 0
            delta16 = 0
            for i in range(self.length):
                ustmp = struct.unpack("<H", file.read(2))[0]
                delta16 = delta16 + ustmp
                self.data.append(struct.unpack("<h", struct.pack("<H", delta16))[0]) # ugly. . .
            self.adjustloops()
            return
        
        # 5: 16-bit signed PCM data
        if loadflags == SF(SF_PCMS, SF_16, SF_M, SF_LE):
            for i in range(self.length):
                self.data.append(struct.unpack("<h", file.read(2))[0])
            self.adjustloops()
            return
        
        # 16-bit signed mono PCM motorola byte order
        if loadflags == SF(SF_PCMS, SF_16, SF_M, SF_BE):
            for i in range(self.length):
                self.data.append(struct.unpack(">H", file.read(2))[0])
            self.adjustloops()
            return
        
        # 6: 16-bit unsigned PCM data
        if loadflags == SF(SF_PCMU, SF_16, SF_M, SF_LE):
            for i in range(self.length):
                self.data.append(struct.unpack("<h", file.read(1))[0] - 0x8000)
            self.adjustloops()
            return
    
    def adjustloops(self):
        pass


class Envelope(object):
    """A simple envelope object"""
    def __init__(self, type=0):
        self.ticks = [0, 100]
        if type == 0:
            self.values = [64, 64]
        else:
            self.values = [32, 32]
        self.nodes = 2
        self.loopbegin = 0
        self.loopend = 0
        self.sustloopbegin = 0
        self.sustloopend = 0


class Instrument(object):
    """A simple instrument object"""
    def __init__(self, sample=0):
        self.fadeout = 0
        self.flags = 0
        self.globalvol = 128
        self.panning = 128
        self.samplemap = []
        self.notemap = []
        for i in range(128):      #not sure why this is 128, instead of 120. . .
            self.samplemap.append(sample)
            self.notemap.append(i + 1)
        self.volumeenv = Envelope(type=0)
        self.panningenv = Envelope(type=1)
        self.pitchenv = Envelope(type=2)
        self.newnoteact = 0
        self.dupchktype = 0
        self.dupchkaction = 0
        self.panswing = 0
        self.volswing = 0
        self.initfiltercut = 0
        self.initfilterres = 0
        self.midibank = -1
        self.midiprogram = -1
        self.midichannelmask = 0
        self.pitchpansep = 0
        self.pitchpancenter = 60
        self.name = ''
        self.filename = ''
        self.played = 0


class Channel(object):
    """A simple channel object"""
    def __init__(self, panning=0, volume=0, flags=0):
        self.panning = panning
        self.volume = volume
        self.flags = flags


class Note(object):
    """A simple note object"""
    def __init__(self, note=0, instrument=0, voleffect=0, volparam=0, effect=0, param=0):
        self.note = note
        self.instrument = instrument
        self.voleffect = voleffect
        self.volparam = volparam
        self.effect = effect
        self.param = param


class Pattern(object):
    """A pattern object"""
    def __init__(self, rows=64, channels=64):
        self.rows = rows
        self.channels = channels
        self.data = []


class Module(object):
    pass

