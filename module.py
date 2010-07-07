import struct

class Sample(object):
    """A simple sample object"""
    def __init__(self):
        self.length = 0
        self.loopbegin = 0
        self.loopend = 0
        self.susloopbegin = 0
        self.susloopend = 0
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


class Module(object):
    pass

