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
        self.reltone = 0
        self.finetune = 0
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
    
    def getname(self):
        return self.name.replace('\x00', ' ').rstrip()
    
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
        
        # 2: 8-bit signed PCM data
        if loadflags == SF(SF_PCMS, SF_8, SF_M, SF_LE):
            for i in range(self.length):
                self.data.append(struct.unpack("<b", file.read(1))[0])
            self.adjustloops()
            return
    
        # 3: 8-bit ADPCM data with linear table
        if loadflags == SF(SF_PCMD, SF_8, SF_M, SF_LE):
            delta = 0
            for i in range(self.length):
                delta = delta + struct.unpack("<b", file.read(1))[0]
                self.data.append(delta)
            self.adjustloops()
            return
        
        # 4: 16-bit ADPCM data with linear table
        if loadflags == SF(SF_PCMD, SF_16, SF_M, SF_LE):
            delta16 = 0
            for i in range(self.length):
                delta16 = delta16 + struct.unpack("<h", file.read(2))[0]
                self.data.append(delta16)
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
        self.mididrumkey = 0
        self.pitchpansep = 0
        self.pitchpancenter = 60
        self.name = ''
        self.filename = ''
        self.played = 0
        
    def getname(self):
        return self.name.replace('\x00', ' ').rstrip()


class Channel(object):
    """A simple channel object"""
    def __init__(self):
        # Most used mixing info
        self.cursampledata = []
        self.pos = 0
        self.poslo = 0
        self.inc = 0
        self.rightvol = 0
        self.leftvol = 0
        self.rightramp = 0
        self.leftramp = 0
        
        # Other info. . .
        self.length = 0
        self.flags = flags
        self.loopbegin = 0
        self.loopend = 0
        self.ramprightvol = 0
        self.rampleftvol = 0
        self.filterY1 = 0
        self.filterY2 = 0
        self.filterY3 = 0
        self.filterY4 = 0
        self.filterA0 = 0
        self.filterB0 = 0
        self.filterB1 = 0
        self.rofs = 0
        self.lofs = 0
        self.ramplength = 0
        self.sampledata = []
        self.newrightvol = 0
        self.newleftvol = 0
        self.realvolume = 0
        self.realpanning = 0
        self.volume = volume
        self.panning = panning
        self.fadeoutvol = 0
        self.period = 0
        self.c4speed = 0
        self.portamentodest = 0
        self.instrument = Instrument()
        self.sample = Sample()
        self.volenvpos = 0
        self.panenvpos = 0
        self.pitchenvpos = 0
        self.masterchn = 0
        self.vumeter = 0
        self.globalvol = 0
        self.instvol = 0
        self.finetune = 0
        self.transpose = 0
        self.portamentoslide = 0
        self.autovibdepth = 0
        self.autovibpos = 0
        self.vibratopos = 0
        self.tremolopos = 0
        self.panbrellopos = 0
        
        self.volswing = 0
        self.panswing = 0
        
        self.note = 0
        self.nna = 0
        self.newnote = 0
        self.newinst = 0
        self.command = 0
        self.arpeggio = 0
        self.oldvolumeslide = 0
        self.oldfinevolupdown = 0
        self.oldportaupdown = 0
        self.oldfineportaupdown = 0
        self.oldpanslide = 0
        self.oldchnvolslide = 0
        self.vibratotype = 0
        self.vibratospeed = 0
        self.vibratodepth = 0
        self.tremolotype = 0
        self.tremolospeed = 0
        self.tremolodepth = 0
        self.panbrellotype = 0
        self.panbrellospeed = 0
        self.panbrellodepth = 0
        self.oldcmdex = 0
        self.oldvolparam = 0
        self.oldtempo = 0
        self.oldoffset = 0
        self.oldhioffset = 0
        self.cutoff = 0
        self.resonance = 0
        self.retrigcount = 0
        self.retrigparam = 0
        self.tremorcount = 0
        self.tremorparam = 0
        self.patternloop = 0
        self.patternloopcount = 0
        self.rownote = 0
        self.rowinst = 0
        self.rowvolcmd = 0
        self.rowvol = 0
        self.rowcmd = 0
        self.rowparam = 0
        self.leftvu = 0
        self.rightvu = 0
        self.activemacro = 0
        self.padding = 0


class ChannelSettings(object):
    """An object for storing channel settings"""
    def __init__(self):
        self.panning = 0
        self.volume = 0
        self.flags = 0
        self.mixplugin = 0
        self.name = ''


class MixPlugin(object):
    """An object for storing plugin data (VSTi)"""
    def __init__(self):
        self.flags = 0
        self.voldecayleft = 0
        self.voldecayright = 0
        self.mixbuffer = 0
        self.outbufferleft = 0.0
        self.outbufferright = 0.0
        self.plugindatasize = 0
        self.plugindata = []
        self.pluginid1 = 0
        self.pluginid2 = 0
        self.inputrouting = 0
        self.outputrouting = 0
        self.RESERVED = 0
        self.name = ''
        self.libraryname = ''


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
    """A plain module object"""
    def __init__(self):
        self.filename = ''
        self.moduletype = ''
        self.id = ''
        self.name = ''
        self.tracker = ''
        self.cwtv = 0
        self.cmwt = 0
        self.tempo = 0
        self.speed = 0
        self.flags = 0
        self.channelnum = 0
        self.ordernum = 0
        self.patternnum = 0
        self.instrumentnum = 0
        self.samplenum = 0
        self.orders = []
        self.patterns = []
        self.instruments = []
        self.samples = []
    
    def getname(self):
        return self.name.replace('\x00', ' ').strip()

    def __unicode__(self):
        return '%s Module (%s)' % (self.__class__.__name__, (self.getname(), self.filename)[bool(self.getname() == '')])
    
    def __repr__(self):
        return self.__unicode__()

