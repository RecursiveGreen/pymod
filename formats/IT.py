import struct
from pymod.constants import *
from pymod.module import *
from pymod.util import *

class ITEnvelope(Envelope):
    """The definition of an envelope for an IT instrument. There are a total
       of three envelopes: Volume (130h), Panning (182h), and Pitch (1D4h)."""
    def __init__(self, file=None, type=0):
        super(ITEnvelope, self).__init__(type)
        self.flags = 0
                
        if file:
            # Load the IT envelope data
            itenvflags = struct.unpack("<B", file.read(1))[0]
            itnodenum = struct.unpack("<B", file.read(1))[0]
            itloopbegin = struct.unpack("<B", file.read(1))[0]
            itloopend = struct.unpack("<B", file.read(1))[0]
            itsustloopbegin = struct.unpack("<B", file.read(1))[0]
            itsustloopend = struct.unpack("<B", file.read(1))[0]
            itnodepoints =[]
        
            if type ==0:
                for i in range(25):
                    itnodepoints.append(list(struct.unpack("<BH", file.read(3))))
            else:
                for i in range(25):
                    itnodepoints.append(list(struct.unpack("<bH", file.read(3))))

            itRESERVED = file.read(1)
            
            # Parse it into the generic Envelope
            self.nodes = CLAMP(itnodenum, 2, 25)
            self.loopbegin = MIN(itloopend, self.nodes)
            self.loopend = CLAMP(itloopend, self.loopbegin, self.nodes)
            self.sustloopbegin = MIN(itsustloopbegin, self.nodes)
            self.sustloopend = CLAMP(itsustloopend, self.sustloopbegin, self.nodes)
            
            self.values = []
            self.ticks = []
            for i in range(self.nodes):
                if type == 0:
                    self.values.append(CLAMP(itnodepoints[i][0], 0, 64))
                else:
                    self.values.append(CLAMP(itnodepoints[i][0] + 32, 0, 64))
                self.ticks.append(itnodepoints[i][1])
            
            self.ticks[0] = 0    # sanity check (do I stiil need this?)

            for i in range(4):
                if itenvflags & (1 << i):
                    self.flags = self.flags | ENV_FLAGS[type][i]
            
            if type == 2 and itenvflags & 0x80:
                self.flags = self.flags | ENV_FILTER


class ITInstrumentOld(Instrument):
    """Definition of an Impulse Tracker instrument before version 2.00"""
    def __init__(self, file=None, offset=0):
        super(ITInstrumentOld, self).__init__()
        self.itinstoldtrackerver = 0
        self.itinstoldnumsamples = 0
        
        if file:
            # Load the old IT instrument data
            file.seek(offset)
            
            itinstoldid = struct.unpack("<4s", file.read(4))[0]
            itinstoldfilename = struct.unpack("<12s", file.read(12))[0].strip()
            itinstoldZERO = struct.unpack("<B", file.read(1))[0]
            itinstoldflags = struct.unpack("<B", file.read(1))[0]
            itinstoldvolloopbegin = struct.unpack("<B", file.read(1))[0]
            itinstoldvolloopend = struct.unpack("<B", file.read(1))[0]
            itinstoldsustloopbegin = struct.unpack("<B", file.read(1))[0]
            itinstoldsustloopend = struct.unpack("<B", file.read(1))[0]
            itinstoldRESERVED1 = struct.unpack("<H", file.read(2))[0]
            itinstoldfadeout = struct.unpack("<H", file.read(2))[0]
            itinstoldnna = struct.unpack("<B", file.read(1))[0]
            itinstolddnc = struct.unpack("<B", file.read(1))[0]
            self.itinstoldtrackerver = struct.unpack("<H", file.read(2))[0]
            self.itinstoldnumsamples = struct.unpack("<B", file.read(1))[0]
            itinstoldRESERVED2 = struct.unpack("<B", file.read(1))[0]
            itinstoldname = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            itinstoldRESERVED3 = list(struct.unpack("<HHH", file.read(6)))
            
            itinstoldnotekeytable = []
            for i in range(120):
                itinstoldnotekeytable.append(list(struct.unpack("<BB", file.read(2))))
            
            itinstoldvolumeenv = list(struct.unpack("<200B", file.read(200)))
            
            itinstoldnodes = []
            for i in range(25):
                itinstoldnodes.append(list(struct.unpack("<BB", file.read(2))))
            
            # Parse it into the generic Instrument
            self.name = itinstoldname
            self.filename = itinstoldfilename

            self.newnoteact = itinstoldnna
            if itinstolddnc:
                self.dupchktype = DCT_NOTE
                self.dupchkaction = DCA_NOTECUT

            self.fadeout = itinstoldfadeout << 6
            self.pitchpansep = 0
            self.pitchpancenter = NOTE_MIDC
            self.globalvol = 128
            self.panning = 128

            for i in range(120):
                if itinstoldnotekeytable[i][0] > NOTE_NONE and itinstoldnotekeytable[i][0] <= NOTE_LAST:
                    self.notemap[i] = itinstoldnotekeytable[i][0] + NOTE_FIRST
                else:
                    self.notemap[i] = i + NOTE_FIRST
                self.samplemap[i] = itinstoldnotekeytable[i][1]

            if itinstoldflags & 1:
                self.flags = self.flags | ENV_VOLUME
            if itinstoldflags & 2:
                self.flags = self.flags | ENV_VOLLOOP
            if itinstoldflags & 4:
                self.flags = self.flags | ENV_VOLSUSTAIN

            self.volumeenv.loopbegin = itinstoldvolloopbegin
            self.volumeenv.loopend = itinstoldvolloopend
            self.volumeenv.sustloopbegin = itinstoldsustloopbegin
            self.volumeenv.sustloopend = itinstoldsustloopend
            self.volumeenv.nodes = 25
        
            for i in range(25):
                if itinstoldnodes[i][0] == 0xff:
                    self.volumeenv.nodes = i
                    break
                self.volumeenv.ticks[i] = itinstoldnodes[i][0]
                self.volumeenv.values[i] = itinstoldnodes[i][1]


class ITInstrument(Instrument):
    """Definition of an Impulse Tracker instrument"""
    def __init__(self, file=None, offset=0):
        super(ITInstrument, self).__init__()
        self.itinsttrackerver = 0
        self.itinstnumsamples = 0
        
        if file:
            # Load the IT instrument data
            file.seek(offset)
            
            itinstid = struct.unpack("<4s", file.read(4))[0]
            itinstfilename = struct.unpack("<12s", file.read(12))[0]
            itinstZERO = struct.unpack("<B", file.read(1))[0]
            itinstnna = struct.unpack("<B", file.read(1))[0]
            itinstdupchktype = struct.unpack("<B", file.read(1))[0]
            itinstdupchkaction = struct.unpack("<B", file.read(1))[0]
            itinstfadeout = struct.unpack("<H", file.read(2))[0]
            itinstpitchpansep = struct.unpack("<b", file.read(1))[0]
            itinstpitchpancenter = struct.unpack("<B", file.read(1))[0]
            itinstglobalvol = struct.unpack("<B", file.read(1))[0]
            itinstdefaultpan = struct.unpack("<B", file.read(1))[0]
            itinstrandvol = struct.unpack("<B", file.read(1))[0]
            itinstrandpan = struct.unpack("<B", file.read(1))[0]
            self.itinsttrackerver = struct.unpack("<H", file.read(2))[0]
            self.itinstnumsamples = struct.unpack("<B", file.read(1))[0]
            itinstRESERVED1 = struct.unpack("<B", file.read(1))[0]
            itinstname = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            itinstinitfiltercut = struct.unpack("<B", file.read(1))[0]
            itinstinitfilterres = struct.unpack("<B", file.read(1))[0]
            itinstmidichannel = struct.unpack("<B", file.read(1))[0]
            itinstmidiprogram = struct.unpack("<B", file.read(1))[0]
            itinstmidibank = struct.unpack("<H", file.read(2))[0]
            
            itinstnotekeytable = []
            for i in range(120):
                itinstnotekeytable.append(list(struct.unpack("<BB", file.read(2))))
            
            self.volumeenv = ITEnvelope(file, 0)
            self.panningenv = ITEnvelope(file, 1)
            self.pitchenv = ITEnvelope(file, 2)
            
            # Parse it into the generic Instrument
            self.name = itinstname
            self.filename = itinstfilename

            self.newnoteact = itinstnna
            self.dupchktype = itinstdupchktype
            self.dupchkaction = itinstdupchkaction
            self.fadeout = itinstfadeout << 5
            self.pitchpansep = CLAMP(itinstpitchpansep, -32, 32)
            self.pitchpancenter = MIN(itinstpitchpancenter, 119)
            self.globalvol = MIN(itinstglobalvol, 128)
            
            self.panning = MIN((itinstdefaultpan & 127), 64) * 4
            if not itinstdefaultpan & 128: self.flags = self.flags | ENV_SETPANNING
        
            self.volswing = MIN(itinstrandvol, 100)
            self.panswing = MIN(itinstrandpan, 64)
            self.initfiltercut = itinstinitfiltercut
            self.initfilterres = itinstinitfilterres

            # straight from Schism Tracker, and still confusing. . .
            # self.midichannelmask = ((0, 1 << (itinstmidichannel - 1))[itinstmidichannel > 0], 0x10000 + itinstmidichannel)[itinstmidichannel > 16]
            
            # TODO: not correct, but the above doesn't work. . .
            self.midichannelmask = itinstmidichannel
            self.midiprogram = itinstmidiprogram
            self.midibank = itinstmidibank

            for i in range(120):
                if itinstnotekeytable[i][0] > NOTE_NONE and itinstnotekeytable[i][0] <= NOTE_LAST:
                    self.notemap[i] = itinstnotekeytable[i][0] + NOTE_FIRST
                else:
                    self.notemap[i] = i + NOTE_FIRST
                self.samplemap[i] = itinstnotekeytable[i][1]

            self.flags = self.flags | self.volumeenv.flags
            self.flags = self.flags | self.panningenv.flags
            self.flags = self.flags | self.pitchenv.flags


class ITSample(Sample):
    """Definition of an Impulse Tracker sample"""
    def __init__(self, file=None, offset=0):
        if not file:
            self.id = 'IMPS'
            self.filename = ''
            self.ZERO = 0
            self.globalvol = 0
            self.flags = 0
            self.volume = 0
            self.name = ''
            self.convertflags = 0
            self.defaultpan = 0
            self.length = 0
            self.loopbegin = 0
            self.loopend = 0
            self.c5speed = 0
            self.susloopbegin = 0
            self.susloopend = 0
            self.offset = 0
            self.vibspeed = 0
            self.vibdepth = 0
            self.vibrate = 0
            self.vibtype = 0
            
            self.data = []            #TODO!
        else:
            file.seek(offset)
            
            self.id = struct.unpack("<4s", file.read(4))[0]
            self.filename = struct.unpack("<12s", file.read(12))[0]
            self.ZERO = struct.unpack("<B", file.read(1))[0]
            self.globalvol = struct.unpack("<B", file.read(1))[0]
            self.flags = struct.unpack("<B", file.read(1))[0]
            self.volume = struct.unpack("<B", file.read(1))[0]
            self.name = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            self.convertflags = struct.unpack("<B", file.read(1))[0]
            self.defaultpan = struct.unpack("<B", file.read(1))[0]
            self.length = struct.unpack("<L", file.read(4))[0]
            self.loopbegin = struct.unpack("<L", file.read(4))[0]
            self.loopend = struct.unpack("<L", file.read(4))[0]
            self.c5speed = struct.unpack("<L", file.read(4))[0]
            self.susloopbegin = struct.unpack("<L", file.read(4))[0]
            self.susloopend = struct.unpack("<L", file.read(4))[0]
            self.offset = struct.unpack("<L", file.read(4))[0]
            self.vibspeed = struct.unpack("<B", file.read(1))[0]
            self.vibdepth = struct.unpack("<B", file.read(1))[0]
            self.vibrate = struct.unpack("<B", file.read(1))[0]
            self.vibtype = struct.unpack("<B", file.read(1))[0]
            
            self.data = []            #TODO!


class IT(Module):
    """A class that holds an IT module file"""
    
    def __init__(self, filename=None):
        if not filename:
            self.id = 'IMPM'
            self.songname = ''
            self.RESERVED1 = 0
            self.ordernum = 0
            self.instrumentnum = 0
            self.samplenum = 0
            self.patternnum = 0
            self.cwtv = 0x0214
            self.cmwt = 0x0214
            self.flags = []
            self.special = []
            self.globalovl = 0
            self.mixvol = 0
            self.speed = 0
            self.tempo = 0
            self.panningsep = 0
            self.midipwd = 0
            self.messagelen = 0
            self.messageoffset = 0
            self.RESERVED2 = 0
            self.message = ''
            self.channelpan = []
            self.channelvol = []
            self.orders = []
            self.instrumentoffset = []
            self.sampleoffset = []
            self.patternoffset = []
        else:
            f = open(filename, 'rb')

            self.id = struct.unpack("<4s", f.read(4))[0]                       # 'IMPM'
            self.songname = struct.unpack("<26s", f.read(26))[0].replace('\x00', ' ').strip()      # Song title (padded with NULL)
            self.RESERVED1 = struct.unpack("<H", f.read(2))[0]                # RESERVED (??)
            self.ordernum = struct.unpack("<H", f.read(2))[0]                # Number of orders in song
            self.instrumentnum = struct.unpack("<H", f.read(2))[0]             # Number of instruments in song
            self.samplenum = struct.unpack("<H", f.read(2))[0]               # Number of samples in song
            self.patternnum = struct.unpack("<H", f.read(2))[0]               # Number of patterns in song
    
            self.cwtv = []
            self.cwtv.insert(0, int(hex(ord(f.read(1)))[2:]))
            self.cwtv.insert(0, int(hex(ord(f.read(1)))[2:]))                      # Created with tracker version (IT y.xx = 0yxxh)
        
            self.cmwt = []                                                  # Compatible with tracker that's version greater than value
            self.cmwt.insert(0, int(hex(ord(f.read(1)))[2:]))
            self.cmwt.insert(0, int(hex(ord(f.read(1)))[2:]))               
    
            self.flags = struct.unpack("<H", f.read(2))[0]
            self.special = struct.unpack("<H", f.read(2))[0]
            self.globalvol = struct.unpack("<B", f.read(1))[0]
            self.mixvol = struct.unpack("<B", f.read(1))[0]
            self.speed = struct.unpack("<B", f.read(1))[0]
            self.tempo = struct.unpack("<B", f.read(1))[0]
            self.panningsep = struct.unpack("<B", f.read(1))[0]
            self.midipwd = struct.unpack("<B", f.read(1))[0]
            self.messagelen = struct.unpack("<H", f.read(2))[0]
            self.messageoffset = struct.unpack("<I", f.read(4))[0]
            self.RESERVED2 = struct.unpack("<I", f.read(4))[0]
    
            self.channelpan = list(struct.unpack("<64B", f.read(64)))
            self.channelvol = list(struct.unpack("<64B", f.read(64)))
    
            self.orders = list(struct.unpack("<%iB" % (self.ordernum), f.read(self.ordernum)))

            self.instrumentoffset = []
            if self.instrumentnum > 0:
                self.instrumentoffset = list(struct.unpack("<%iL" % (self.instrumentnum), f.read(self.instrumentnum * 4)))

            self.sampleoffset = []
            if self.samplenum > 0:
                self.sampleoffset = list(struct.unpack("<%iL" % (self.samplenum), f.read(self.samplenum * 4)))

            self.patternoffset = []
            if self.patternnum > 0:
                self.patternoffset = list(struct.unpack("<%iL" % (self.patternnum), f.read(self.patternnum * 4)))
        
            self.message = ''
            if self.messagelen > 0 and self.messageoffset > 0:
                f.seek(self.messageoffset)
                self.message = struct.unpack("<%is" % (self.messagelen), f.read(self.messagelen))[0].replace('\r', '\n').replace('\x00', ' ').rstrip()
            
            self.instruments = []
            if self.instrumentoffset:
                for offset in self.instrumentoffset:
                    if self.cmwt[0] < 2:
                        self.instruments.append(ITInstrumentOld(f, offset))
                    else:
                        self.instruments.append(ITInstrument(f, offset))
            
            self.samples = []
            if self.sampleoffset:
                for offset in self.sampleoffset:
                    self.samples.append(ITSample(f, offset))
            
            self.patterns = []
            if self.patternoffset:
                for offset in self.patternoffset:
                    if offset == 0:
                        self.patterns.append(Pattern())
                    else:
                        self.patterns.append(Pattern(f, offset))
                    
            f.close()

