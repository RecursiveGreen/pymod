import struct

class Note(object):
    """A simple note object"""
    def __init__(self, note=0, instrument=0, voleffect=0, volparam=0, effect=0, param=0):
        self.note = note
        self.instrument = instrument
        self.voleffect = voleffect
        self.volparam = volparam
        self.effect = effect
        self.param = param

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

        if self.voleffect == 0: ret3 = '..'
        elif self.voleffect == 1: ret3 = str(self.volparam).zfill(2).upper()
        elif self.voleffect == 2: ret3 = str(self.volparam + 128).zfill(2).upper()
        elif self.voleffect == 3: ret3 = str(self.volparam + 85).zfill(2).upper()
        elif self.voleffect == 4: ret3 = str(self.volparam + 95).zfill(2).upper()
        elif self.voleffect == 5: ret3 = str(self.volparam + 65).zfill(2).upper()
        elif self.voleffect == 6: ret3 = str(self.volparam + 75).zfill(2).upper()
        elif self.voleffect == 8: ret3 = str(self.volparam + 203).zfill(2).upper()
        elif self.voleffect == 11: ret3 = str(self.volparam + 193).zfill(2).upper()
        elif self.voleffect == 12: ret3 = str(self.volparam + 115).zfill(2).upper()
        elif self.voleffect == 13: ret3 = str(self.volparam + 105).zfill(2).upper()
        
        if self.effect: letter = commands[self.effect-1]
        else: letter = '.'
        ret4 = '%s%s' % (letter, hex(self.param)[2:].zfill(2).upper())
        
        return '%s %s %s %s' % (ret1, ret2, ret3, ret4)

    def __repr__(self):
        return self.__unicode__()


class Pattern(object):
    """A pattern object"""
    def __init__(self, file=None, offset=0, length=0, rows=64, channels=64):
        self.length = length
        self.rows = rows
                
        self.data = self.empty(self.rows, channels)
        
        if file:
            file.seek(offset)
            
            self.length = struct.unpack("<H", file.read(2))[0]
            self.rows = struct.unpack("<H", file.read(2))[0]
            RESERVED = struct.unpack("<BBBB", file.read(4))
            
            lastnote = []
            for i in range(channels):
                lastnote.append(Note())
                
            lastmask = []
            for i in range(channels):
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
                        self.data[currow][curchannel].voleffect = 1
                        self.data[currow][curchannel].volparam = temp
                    elif temp >= 65 and temp <= 74:
                        self.data[currow][curchannel].voleffect = 5
                        self.data[currow][curchannel].volparam = temp - 65
                    elif temp >= 75 and temp <= 84:
                        self.data[currow][curchannel].voleffect = 6
                        self.data[currow][curchannel].volparam = temp - 75
                    elif temp >= 85 and temp <= 94:
                        self.data[currow][curchannel].voleffect = 3
                        self.data[currow][curchannel].volparam = temp - 85
                    elif temp >= 95 and temp <= 104:
                        self.data[currow][curchannel].voleffect = 4
                        self.data[currow][curchannel].volparam = temp - 95
                    elif temp >= 105 and temp <= 114:
                        self.data[currow][curchannel].voleffect = 13
                        self.data[currow][curchannel].volparam = temp - 105
                    elif temp >= 115 and temp <= 124:
                        self.data[currow][curchannel].voleffect = 12
                        self.data[currow][curchannel].volparam = temp - 115
                    elif temp >= 128 and temp <= 192:
                        self.data[currow][curchannel].voleffect = 2
                        self.data[currow][curchannel].volparam = temp - 128
                    elif temp >= 193 and temp <= 202:
                        self.data[currow][curchannel].voleffect = 11
                        self.data[currow][curchannel].volparam = temp - 193
                    elif temp >= 203 and temp <= 212:
                        self.data[currow][curchannel].voleffect = 8
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
                    
    def empty(self, rows, channels):
        pattern = []
        for row in range(rows):
            pattern.append([])
            for channel in range(channels):
                pattern[row].append(Note())
        return pattern


class ITEnvelope(object):
    """The definition of an envelope for an IT instrument. There are a total
       of three envelopes: Volume (130h), Panning (182h), and Pitch (1D4h)."""
    def __init__(self, file=None, volume=False):
        if not file:
            self.flags = 0
            self.nodenum = 0
            self.loopbegin = 0
            self.loopend = 0
            self.sustloopbegin = 0
            self.sustloopend = 0
            self.nodepoints = []
            self.RESERVED = 0
        else:
            self.flags = struct.unpack("<B", file.read(1))[0]
            self.nodenum = struct.unpack("<B", file.read(1))[0]
            self.loopbegin = struct.unpack("<B", file.read(1))[0]
            self.loopend = struct.unpack("<B", file.read(1))[0]
            self.sustloopbegin = struct.unpack("<B", file.read(1))[0]
            self.sustloopend = struct.unpack("<B", file.read(1))[0]
            self.nodepoints =[]
        
            if volume:
                for i in range(25):
                    self.nodepoints.append(list(struct.unpack("<BH", file.read(3))))
            else:
                for i in range(25):
                    self.nodepoints.append(list(struct.unpack("<bH", file.read(3))))

            self.RESERVED = file.read(1)


class ITInstrumentOld(object):
    """Definition of an Impulse Tracker instrument before version 2.00"""
    def __init__(self, file=None, offset=0):
        if not file:
            self.id = 'IMPI'
            self.filename = ''
            self.ZERO = 0          #redundant much?
            self.flags = 0
            self.volloopbegin = 0
            self.volloopend = 0
            self.susloopbegin = 0
            self.susloopend = 0
            self.RESERVED1 = 0
            self.fadeout = 0
            self.nna = 0
            self.dnc = 0
            self.trackerver = []    #something below 2.00??
            self.numsamples = 0
            self.RESERVED2 = 0
            self.name = ''
            self.RESERVED3 = [0, 0, 0]
            self.notekeytable = []
            self.volumeenv = []
            self.nodes = []
        else:
            file.seek(offset)
            
            self.id = struct.unpack("<4s", file.read(4))[0]
            self.filename = struct.unpack("<12s", file.read(12))[0].strip()
            self.ZERO = struct.unpack("<B", file.read(1))[0]
            self.flags = struct.unpack("<B", file.read(1))[0]
            self.volloopbegin = struct.unpack("<B", file.read(1))[0]
            self.volloopend = struct.unpack("<B", file.read(1))[0]
            self.susloopbegin = struct.unpack("<B", file.read(1))[0]
            self.susloopend = struct.unpack("<B", file.read(1))[0]
            self.RESERVED1 = struct.unpack("<H", file.read(2))[0]
            self.fadeout = struct.unpack("<H", file.read(2))[0]
            self.nna = struct.unpack("<B", file.read(1))[0]
            self.dnc = struct.unpack("<B", file.read(1))[0]
            
            self.trackerver = []
            self.trackerver.insert(0, int(hex(ord(file.read(1)))[2:]))
            self.trackerver.insert(0, int(hex(ord(file.read(1)))[2:]))
            
            self.numsamples = struct.unpack("<B", file.read(1))[0]
            self.RESERVED2 = struct.unpack("<B", file.read(1))[0]
            self.name = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            self.RESERVED3 = list(struct.unpack("<HHH", file.read(6)))
            
            self.notekeytable = []
            for i in range(120):
                self.notekeytable.append(list(struct.unpack("<BB", file.read(2))))
            
            self.volumeenv = list(struct.unpack("<200B", file.read(200)))
            
            self.nodes = []
            for i in range(25):
                self.nodes.append(list(struct.unpack("<BB", file.read(2))))
                
class ITInstrument(object):
    """Definition of an Impulse Tracker instrument"""
    def __init__(self, file=None, offset=0):
        if not file:
            self.id = 'IMPI'
            self.filename = ''
            self.ZERO = 0
            self.nna = 0
            self.dupchktype = 0
            self.dupchkaction = 0
            self.fadeout = 0
            self.pitchpansep = 0
            self.pitchpancenter = 0
            self.globalvol = 0
            self.defaultpan = 0
            self.randvol = 0
            self.randpan = 0
            self.trackerver = []    #something below 2.00??
            self.numsamples = 0
            self.RESERVED1 = 0
            self.name = ''
            self.initfiltercut = 0
            self.initfilterres = 0
            self.midichannel = 0
            self.midiprogram = 0
            self.midibank = 0
            self.notekeytable = []
            self.volumeenv = ITEnvelope()
            self.panningenv = ITEnvelope()
            self.pitchenv = ITEnvelope()
        else:
            file.seek(offset)
            
            self.id = struct.unpack("<4s", file.read(4))[0]
            self.filename = struct.unpack("<12s", file.read(12))[0]
            self.ZERO = struct.unpack("<B", file.read(1))[0]
            self.nna = struct.unpack("<B", file.read(1))[0]
            self.dupchktype = struct.unpack("<B", file.read(1))[0]
            self.dupchkaction = struct.unpack("<B", file.read(1))[0]
            self.fadeout = struct.unpack("<H", file.read(2))[0]
            self.pitchpansep = struct.unpack("<b", file.read(1))[0]
            self.pitchpancenter = struct.unpack("<B", file.read(1))[0]
            self.globalvol = struct.unpack("<B", file.read(1))[0]
            self.defaultpan = struct.unpack("<B", file.read(1))[0]
            self.randvol = struct.unpack("<B", file.read(1))[0]
            self.randpan = struct.unpack("<B", file.read(1))[0]
            
            self.trackerver = []
            self.trackerver.insert(0, int(hex(ord(file.read(1)))[2:]))
            self.trackerver.insert(0, int(hex(ord(file.read(1)))[2:]))
            
            self.numsamples = struct.unpack("<B", file.read(1))[0]
            self.RESERVED1 = struct.unpack("<B", file.read(1))[0]
            self.name = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            self.initfiltercut = struct.unpack("<B", file.read(1))[0]
            self.initfilterres = struct.unpack("<B", file.read(1))[0]
            self.midichannel = struct.unpack("<B", file.read(1))[0]
            self.midiprogram = struct.unpack("<B", file.read(1))[0]
            self.midibank = struct.unpack("<H", file.read(2))[0]
            
            self.notekeytable = []
            for i in range(120):
                self.notekeytable.append(list(struct.unpack("<BB", file.read(2))))
            
            self.volumeenv = ITEnvelope(file, volume=True)
            self.panningenv = ITEnvelope(file)
            self.pitchenv = ITEnvelope(file)


class ITSample(object):
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


class IT(object):
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
            self.cwtv = [2, 14]
            self.cmwt = [2, 14]
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

