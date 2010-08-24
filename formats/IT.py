import struct
from pymod.constants import *
from pymod.module import *
from pymod.util import *

class ITNote(Note):
    """The definition of an note and it's effects in IT"""
    def __init__(self, note=0, instrument=0, voleffect=0, volparam=0, effect=0, param=0):
        super(ITNote, self).__init__(note, instrument, voleffect, volparam, effect, param)

    def __unicode__(self):
        keys = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
        commands = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if self.note == 0: ret1 = '...'
        elif self.note > 0 and self.note <=120:
            split = divmod(self.note-1, 12)
            ret1 = '%s%s' % (keys[split[1]], str(split[0]))
        elif self.note == 254: ret1 = '^^^'
        elif self.note == 255: ret1 = '==='
        else: ret1 = '~~~'

        if self.instrument: ret2 = str(self.instrument).zfill(2)
        else: ret2 = '..'

        if self.voleffect == VOLFX_NONE: ret3 = '..'
        elif self.voleffect == VOLFX_VOLUME: ret3 = str(self.volparam).zfill(2).upper()
        elif self.voleffect == VOLFX_PANNING: ret3 = str(self.volparam + 128).zfill(2).upper()
        elif self.voleffect == VOLFX_VOLSLIDEUP: ret3 = str(self.volparam + 85).zfill(2).upper()
        elif self.voleffect == VOLFX_VOLSLIDEDOWN: ret3 = str(self.volparam + 95).zfill(2).upper()
        elif self.voleffect == VOLFX_FINEVOLUP: ret3 = str(self.volparam + 65).zfill(2).upper()
        elif self.voleffect == VOLFX_FINEVOLDOWN: ret3 = str(self.volparam + 75).zfill(2).upper()
        elif self.voleffect == VOLFX_VIBRATODEPTH: ret3 = str(self.volparam + 203).zfill(2).upper()
        elif self.voleffect == VOLFX_TONEPORTAMENTO: ret3 = str(self.volparam + 193).zfill(2).upper()
        elif self.voleffect == VOLFX_PORTAUP: ret3 = str(self.volparam + 115).zfill(2).upper()
        elif self.voleffect == VOLFX_PORTADOWN: ret3 = str(self.volparam + 105).zfill(2).upper()
        
        if self.effect: letter = commands[self.effect-1]
        else: letter = '.'
        ret4 = '%s%s' % (letter, hex(self.param)[2:].zfill(2).upper())
        
        return '%s %s %s %s' % (ret1, ret2, ret3, ret4)

    def __repr__(self):
        return self.__unicode__()


class ITPattern(Pattern):
    """The definition of the IT pattern"""
    def __init__(self, file=None, offset=0, rows=64, channels=64):
        super(ITPattern, self).__init__(rows, channels)
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
                pattern[row].append(ITNote())
        return pattern
        
    def load(self, file, offset):
        file.seek(offset)
            
        self.length = struct.unpack("<H", file.read(2))[0]
        self.rows = struct.unpack("<H", file.read(2))[0]
        RESERVED = struct.unpack("<BBBB", file.read(4))
        
        self.data = self.empty(self.rows, self.channels)
        
        lastnote = []
        for i in range(self.channels):
            lastnote.append(ITNote())
                
        lastmask = []
        for i in range(self.channels):
            lastmask.append(0)    
                
        curchannel = 0
        currow = 0
        channelvar = 0
        maskvar = 0
        temp = 0
            
        while currow < self.rows:
            channelvar = struct.unpack("<B", file.read(1))[0]
            if channelvar == 0: currow = currow + 1
                
            curchannel = (channelvar - 1) & 63
            
            if channelvar & 128:
                maskvar = struct.unpack("<B", file.read(1))[0]
                lastmask[curchannel] = maskvar
            else:
                maskvar = lastmask[curchannel]
            
            if maskvar & 1:
                temp = struct.unpack("<B", file.read(1))[0]
                if temp >= 0 and temp < 121:
                    self.data[currow][curchannel].note = temp + 1
                else:
                    self.data[currow][curchannel].note = temp
                lastnote[curchannel].note = temp
                
            if maskvar & 2:
                self.data[currow][curchannel].instrument = struct.unpack("<B", file.read(1))[0]
                lastnote[curchannel].instrument = self.data[currow][curchannel].instrument
                
            if maskvar & 4:
                temp = struct.unpack("<B", file.read(1))[0]
                if temp >= 0 and temp <= 64:
                    self.data[currow][curchannel].voleffect = VOLFX_VOLUME
                    self.data[currow][curchannel].volparam = temp
                elif temp >= 65 and temp <= 74:
                    self.data[currow][curchannel].voleffect = VOLFX_FINEVOLUP
                    self.data[currow][curchannel].volparam = temp - 65
                elif temp >= 75 and temp <= 84:
                    self.data[currow][curchannel].voleffect = VOLFX_FINEVOLDOWN
                    self.data[currow][curchannel].volparam = temp - 75
                elif temp >= 85 and temp <= 94:
                    self.data[currow][curchannel].voleffect = VOLFX_VOLSLIDEUP
                    self.data[currow][curchannel].volparam = temp - 85
                elif temp >= 95 and temp <= 104:
                    self.data[currow][curchannel].voleffect = VOLFX_VOLSLIDEDOWN
                    self.data[currow][curchannel].volparam = temp - 95
                elif temp >= 105 and temp <= 114:
                    self.data[currow][curchannel].voleffect = VOLFX_PORTADOWN
                    self.data[currow][curchannel].volparam = temp - 105
                elif temp >= 115 and temp <= 124:
                    self.data[currow][curchannel].voleffect = VOLFX_PORTAUP
                    self.data[currow][curchannel].volparam = temp - 115
                elif temp >= 128 and temp <= 192:
                    self.data[currow][curchannel].voleffect = VOLFX_PANNING
                    self.data[currow][curchannel].volparam = temp - 128
                elif temp >= 193 and temp <= 202:
                    self.data[currow][curchannel].voleffect = VOLFX_TONEPORTAMENTO
                    self.data[currow][curchannel].volparam = temp - 193
                elif temp >= 203 and temp <= 212:
                    self.data[currow][curchannel].voleffect = VOLFX_VIBRATODEPTH
                    self.data[currow][curchannel].volparam = temp - 203                                
                
                lastnote[curchannel].voleffect = self.data[currow][curchannel].voleffect
                lastnote[curchannel].volparam = self.data[currow][curchannel].volparam
        
            if maskvar & 8:
                self.data[currow][curchannel].effect = struct.unpack("<B", file.read(1))[0]
                self.data[currow][curchannel].param = struct.unpack("<B", file.read(1))[0]
                lastnote[curchannel].effect = self.data[currow][curchannel].effect
                lastnote[curchannel].param = self.data[currow][curchannel].param
                    
            if maskvar & 16:
                self.data[currow][curchannel].note = lastnote[curchannel].note
                
            if maskvar & 32:
                self.data[currow][curchannel].instrument = lastnote[curchannel].instrument
                    
            if maskvar & 64:
                self.data[currow][curchannel].voleffect = lastnote[curchannel].voleffect
                self.data[currow][curchannel].volparam = lastnote[curchannel].volparam
                    
            if maskvar & 128:
                self.data[currow][curchannel].effect = lastnote[curchannel].effect
                self.data[currow][curchannel].param = lastnote[curchannel].param


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
        
            if type == 0:
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
        
        if file: self.load(file, offset)
        
    def load(self, file, offset):
        # Load the old IT instrument data
        file.seek(offset)
            
        itinstoldid = struct.unpack("<4s", file.read(4))[0]
        itinstoldfilename = struct.unpack("<12s", file.read(12))[0]
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
        itinstoldname = struct.unpack("<26s", file.read(26))[0]
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
        
        if file: self.load(file, offset)
        
    def load(self, file, offset):    
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
        itinstname = struct.unpack("<26s", file.read(26))[0]
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
    def __init__(self, file=None, offset=0, cwtv=0x0214):
        super(ITSample, self).__init__()
        self.itsamploadflags = SF_LE
        self.itsampoffset = 0
        
        if file: self.load(file, offset, cwtv)
        
    def load(self, file, offset, cwtv):
        # Load the IT sample headers
        file.seek(offset)
            
        itsampid = struct.unpack("<4s", file.read(4))[0]
        itsampfilename = struct.unpack("<12s", file.read(12))[0]
        itsampZERO = struct.unpack("<B", file.read(1))[0]
        itsampglobalvol = struct.unpack("<B", file.read(1))[0]
        itsampflags = struct.unpack("<B", file.read(1))[0]
        itsampvolume = struct.unpack("<B", file.read(1))[0]
        itsampname = struct.unpack("<26s", file.read(26))[0]
        itsampconvertflags = struct.unpack("<B", file.read(1))[0]
        itsampdefaultpan = struct.unpack("<B", file.read(1))[0]
        itsamplength = struct.unpack("<L", file.read(4))[0]
        itsamploopbegin = struct.unpack("<L", file.read(4))[0]
        itsamploopend = struct.unpack("<L", file.read(4))[0]
        itsampc5speed = struct.unpack("<L", file.read(4))[0]
        itsampsustloopbegin = struct.unpack("<L", file.read(4))[0]
        itsampsustloopend = struct.unpack("<L", file.read(4))[0]
        self.itsampoffset = struct.unpack("<L", file.read(4))[0]
        itsampvibspeed = struct.unpack("<B", file.read(1))[0]
        itsampvibdepth = struct.unpack("<B", file.read(1))[0]
        itsampvibrate = struct.unpack("<B", file.read(1))[0]
        itsampvibtype = struct.unpack("<B", file.read(1))[0]

        # Parse it into generic Sample
        self.name = itsampname
        self.filename = itsampfilename

        if itsampdefaultpan & 128:
            self.flags = self.flags | CHN_PANNING
            itsampdefaultpan = itsampdefaultpan & 127

        self.globalvol = MIN(itsampglobalvol, 64)
        self.volume = MIN(itsampvolume, 64) * 4
        self.panning = MIN(itsampdefaultpan, 64) * 4
        self.length = itsamplength
        self.loopbegin = itsamploopbegin
        self.loopend = itsamploopend
        self.c5speed = itsampc5speed
        self.sustloopbegin = itsampsustloopbegin
        self.sustloopend = itsampsustloopend

        self.vibspeed = MIN(itsampvibspeed, 64)
        self.vibdepth = MIN(itsampvibdepth, 32)
        self.vibrate = itsampvibrate
        self.vibtype = itsampvibtype

        if itsampflags & 16: self.flags = self.flags | CHN_LOOP
        if itsampflags & 32: self.flags = self.flags | CHN_SUSTAINLOOP
        if itsampflags & 64: self.flags = self.flags | CHN_PINGPONGLOOP
        if itsampflags & 128: self.flags = self.flags | CHN_PINGPONGSUSTAIN

        # Fixing old IT bug of setting this flag incorrectly.
        if cwtv < 0x0214: itsampflags = itsampflags & ~4

        if itsampflags & 1:
            if itsampflags & 8:
                self.itsamploadflags = self.itsamploadflags | SF_M
                self.itsamploadflags = self.itsamploadflags | (SF_IT214, SF_IT215)[bool(itsampconvertflags & 4)]
            else:
                self.itsamploadflags = self.itsamploadflags | (SF_M, SF_SS)[bool(itsampflags & 4)]
                self.itsamploadflags = self.itsamploadflags | ((SF_PCMU, SF_PCMS)[bool(itsampconvertflags & 1)], SF_PCMD)[bool(itsampconvertflags & 4)]
            
            self.itsamploadflags = self.itsamploadflags | (SF_8, SF_16)[bool(itsampflags & 2)]
            
            super(ITSample, self).load(file, self.itsampoffset, self.itsamploadflags)
        else:
            self.length = 0


class IT(Module):
    """A class that holds an IT module file"""
    def __init__(self, filename=None):
        super(IT, self).__init__()
        if not filename:
            self.id = 'IMPM'
            self.RESERVED1 = 0
            self.cwtv = 0x0214
            self.cmwt = 0x0214
            self.special = 0
            self.globalvol = 0
            self.mixvol = 0
            self.panningsep = 0
            self.midipwd = 0
            self.messagelen = 0
            self.messageoffset = 0
            self.RESERVED2 = 0
            self.message = ''
            self.channelpan = []
            self.channelvol = []
            self.instrumentoffset = []
            self.sampleoffset = []
            self.patternoffset = []
        else:
            f = open(filename, 'rb')

            self.filename = filename
            self.id = struct.unpack("<4s", f.read(4))[0]            # 'IMPM'
            self.name = struct.unpack("<26s", f.read(26))[0]        # Song title (padded with NULL)
            self.RESERVED1 = struct.unpack("<H", f.read(2))[0]      # RESERVED (??)
            self.ordernum = struct.unpack("<H", f.read(2))[0]       # Number of orders in song
            self.instrumentnum = struct.unpack("<H", f.read(2))[0]  # Number of instruments in song
            self.samplenum = struct.unpack("<H", f.read(2))[0]      # Number of samples in song
            self.patternnum = struct.unpack("<H", f.read(2))[0]     # Number of patterns in song
            self.cwtv = struct.unpack("<H", f.read(2))[0]           # Created with tracker version (IT y.xx = 0yxxh)
            self.cmwt = struct.unpack("<H", f.read(2))[0]           # Compatible with tracker that's version greater than value
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
                self.message = struct.unpack("<%is" % (self.messagelen), f.read(self.messagelen))[0]
            
            self.instruments = []
            if self.instrumentoffset:
                for offset in self.instrumentoffset:
                    if self.cmwt < 0x0200:
                        self.instruments.append(ITInstrumentOld(f, offset))
                    else:
                        self.instruments.append(ITInstrument(f, offset))
            
            self.samples = []
            if self.sampleoffset:
                for offset in self.sampleoffset:
                    self.samples.append(ITSample(f, offset, self.cwtv))
            
            self.patterns = []
            if self.patternoffset:
                for offset in self.patternoffset:
                    if offset == 0:
                        self.patterns.append(ITPattern())
                    else:
                        self.patterns.append(ITPattern(f, offset))
                    
            f.close()
            
    def detect(filename):
        f = open(filename, 'rb')
        id = struct.unpack("<4s", f.read(4))[0]
        f.close()
        if id == 'IMPM':
            return 2
        else:
            return 0
    detect = staticmethod(detect)
    
    def getmessage(self):
        return self.message.replace('\r', '\n').replace('\x00', ' ').rstrip()

