import struct

class ITEnvelope(object):
    """The definition of an envelope for an IT instrument. There are a total
       of three envelopes: Volume (130h), Panning (182h), and Pitch (1D4h)."""

    def __init__(self, file=None, volume=False):
        if not file:
	    self.flags = [0, 0, 0, 0, 0, 0, 0, 0]
	    self.nodenum = 0
	    self.loopbegin = 0
	    self.loopend = 0
	    self.sustloopbegin = 0
	    self.sustloopend = 0
	    self.nodepoints = []
	    self.RESERVED = 0
	else:
	    self.flags = list(bin(struct.unpack("<B", file.read(1))[0])[2:].zfill(8))
	    self.flags.reverse()

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
            self.flags = [0, 0, 0, 0, 0, 0, 0, 0]
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
            
            self.flags = list(bin(struct.unpack("<B", file.read(1))[0])[2:].zfill(8))
	    self.flags.reverse()
            
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
            self.flags = [0, 0, 0, 0, 0, 0, 0, 0]
            self.volume = 0
            self.name = ''
            self.convertflags = [0, 0, 0, 0, 0, 0, 0, 0]
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
            
            self.flags = list(bin(struct.unpack("<B", file.read(1))[0])[2:].zfill(8))
	    self.flags.reverse()
            
            self.volume = struct.unpack("<B", file.read(1))[0]
            self.name = struct.unpack("<26s", file.read(26))[0].replace('\x00', ' ').rstrip()
            
            self.convertflags = list(bin(struct.unpack("<B", file.read(1))[0])[2:].zfill(8))
	    self.convertflags.reverse()
            
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
            self.RESERVED1 = f.read(2)                # RESERVED (??)
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
	
	    self.flags = list(bin(struct.unpack("<H", f.read(2))[0])[2:].zfill(16))
	    self.flags.reverse()
        
	    self.special = list(bin(struct.unpack("<H", f.read(2))[0])[2:].zfill(16))
	    self.special.reverse()
	
	    self.globalvol = struct.unpack("<B", f.read(1))[0]
	    self.mixvol = struct.unpack("<B", f.read(1))[0]
	    self.speed = struct.unpack("<B", f.read(1))[0]
	    self.tempo = struct.unpack("<B", f.read(1))[0]
	    self.panningsep = struct.unpack("<B", f.read(1))[0]
	    self.midipwd = struct.unpack("<B", f.read(1))[0]
	    self.messagelen = struct.unpack("<H", f.read(2))[0]
	    self.messageoffset = struct.unpack("<I", f.read(4))[0]
	    self.RESERVED2 = f.read(4)
	
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
                    
            f.close()


#mod = IT('SILENT.IT')
#print mod.id, mod.songname, '.'