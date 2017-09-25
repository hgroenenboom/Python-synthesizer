import numpy as np
import array
import random

class Oscillator():
    """De Oscillator class bevat meerdere soorten oscillators die met een callback aangeroepen kunnen worden."""
    SINE = 1
    MONOSINE = 2
    CSPLITSINE = 3
    MONOPULSE = 4
    MONOADDSAW = 5
    SINERAMP = 6
    FM = 7
    NOISEAVRGFILTER = 8
    AM = 9

    monoPulseAmp = 0 #
    monoAddSawAmpA = [0] * 6  # de amplitudes van de boventonen van de additieve saw
    monoAddSawPhasA = [0] * 6  # de fases van de boventonen van de additieve saw
    phaseModulator = 0
    filterToggle = 1
    filterHighpass = 1
    filterLowpass = 1
    ringMod = 0

    def __init__(self, frequency=100, phase=0, type=SINE, channels=2, rate=44100, amp=0.5, pulsewidth=0.5, ratio=1.25, modDepth = 1):
        """De initializer van Oscillator"""
        self.freq = frequency
        self.phas = phase
        self.type = type
        self.chan = channels
        self.rate = rate
        self.plswdth = pulsewidth
        self.amp = amp
        self.ratio = ratio
        self.modDepth = modDepth

        self.outbuf = array.array('h', [0]) * self.chan * 256 #* FRAMESPERBUFFER * CHANNELS  # array of signed ints

    def Run(self, frame_count):
        """De Run(frame_count) functie zal op basis van de frame_count een byte array aanmaken van de output buffer"""
        if self.type == self.SINE:          #simple sinewave on all channels
            for n in range(frame_count):
                for c in range(self.chan):  #fill buffer with the same sin on every channel
                    self.outbuf[n*self.chan+c] = int(32767 * self.amp * np.sin(self.phas))
                self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.MONOSINE:     #simple sinewave for mono use
            for n in range(frame_count):
                self.outbuf[n] = int(32767 * self.amp * np.sin(self.phas))  #original sinewave
                self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.CSPLITSINE:   #different sines on different channels. is kaput, TODO Fix deze shit
            for n in range(frame_count):
                for c in range(self.chan):       #different sines on different channels
                    self.outbuf[c*self.chan+c] = int(32767 * self.amp * np.sin(self.phas))
                self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.MONOPULSE:    #simple square wave for mono use
            for n in range(frame_count):
                if self.phas > self.plswdth:     #square wave oscillator with pulse width
                    self.monoPulseAmp = -1
                else:
                    self.monoPulseAmp = 1
                self.outbuf[n] = int(32767 * self.amp * self.monoPulseAmp)
                self.phas += self.freq / self.rate
                self.phas = self.phas % 1.0
        elif self.type == self.MONOADDSAW:      #een additieve saw
            for n in range(frame_count):
                for b in range(self.monoAddSawAmpA.__len__()):       #saw wave using additive synthesis
                     self.monoAddSawPhasA[b] += 2 * np.pi * self.freq * (b + 1) / self.rate
                     self.monoAddSawAmpA[b] = int(32767 * self.amp * (1 / (b + 1)) * np.sin(self.monoAddSawPhasA[b]))
                self.outbuf[n] = sum(self.monoAddSawAmpA)
        elif self.type == self.SINERAMP: #ramp van 200-1500 in 10s
            for n in range(frame_count):
                self.outbuf[n*self.chan + 0] = int(32767 * self.amp * np.sin(self.phas))
                self.phas += 2 * np.pi * self.freq / self.rate
                if self.freq < 1500:
                    self.freq = self.freq + (1500.0 - 200.0) / 44100.0 / 10.0
        elif self.type == self.FM:  #mono FM Synthesis
            for n in range(frame_count):
                self.outbuf[n] = int(32767 * self.amp * np.sin(self.phas))
                self.phas += 2 * np.pi * (self.freq / self.rate + np.sin(self.phaseModulator) * self.modDepth)
                self.phaseModulator += 2 * np.pi * (self.ratio * self.freq) / self.rate
        elif self.type == self.NOISEAVRGFILTER:
            for n in range(frame_count):
                self.outbuf[n] = int(random.uniform(-32767, 32767))     #Noise
                self.outbuf[n] = int(random.uniform(-32767, 32767))     #Noise
            if self.filterToggle == 1:  #als de filter toggle niet 1 is worden de filters niet gebruikt
                if self.filterLowpass > 0:      #met de waarde filterLowpass kan de filter intensiteit bepaald worden
                    for n in range(frame_count):
                        x = 0
                        for p in range(self.filterLowpass):     #hier wordt afgelezen hoeveel bufferwaardes er uitgemiddeld moeten worden.
                            x += self.outbuf[n-p]
                            x /= self.filterLowpass
                        self.outbuf[n - self.filterLowpass] = int(x)    #hier wordt van de !oudste! bufferwaarde de waarde aangepast zodat de nieuwere waardes nog voor de volgende filterwaardes gebruikt kunnen worden
                if self.filterHighpass > 0:
                        for n in range(frame_count):
                            x = 0
                            for p in range(self.filterHighpass):
                                x += self.outbuf[n - p]
                                x /= self.filterHighpass
                            self.outbuf[n - self.filterHighpass] = int(x)
        elif self.type == self.AM:  #mono AM
            if self.ringMod == 0:
                for n in range(frame_count):
                    self.outbuf[n] = int(32767 * self.amp * (np.sin(self.phas) * np.sin(self.phaseModulator)) )  #original sinewave
                    self.phas += 2 * np.pi * self.freq / self.rate
                    self.phaseModulator += 2 * np.pi * self.freq * self.ratio / self.rate
            else:
                for n in range(frame_count):
                    self.outbuf[n] = int(32767 * self.amp * (np.sin(self.phas) * (np.sin(self.phaseModulator) * 0.5 + 1)))  # original sinewave
                    self.phas += 2 * np.pi * self.freq / self.rate
                    self.phaseModulator += 2 * np.pi * self.freq * self.ratio / self.rate
        return (self.outbuf)
        #return (self.outbuf.tobytes())

    def output(self):
        return self.outbuf

class ADSR:

    adsrCounter = 0
    adsrAmp = 0
    adsrStart = 0
    adsrAttStage = 0
    adsrDecStage = 0
    adsrSusStage = 0
    adsrRelStage = 0
    adsrExp = 4

    def __init__(self, att=0.01, dec=0.3, sus=0, rel=0.04):
        self.att = att
        self.dec = dec
        self.sus = sus
        self.rel = rel
        self.adsrBuf = array.array('f', [0]) * self.chan * 256  # * FRAMESPERBUFFER * CHANNELS  # array of signed ints

    def Run(self, frame_count):
        if self.adsrCounter > 100000 or self.adsrCounter == 0:     #initialize ADSR
            self.adsrStart = 0
            self.adsrAmp = 0
            #self.freq *= 3/4 fun

        if self.adsrStart == 0:
            self.adsrCounter = 0
            self.adsrStart = 1
            self.adsrAttStage = 1

        for n in range(frame_count):
            self.adsrCounter += 1
            if self.adsrAttStage == 1:
                self.adsrAmp += 1 / int(self.att * self.rate)
                if self.adsrAmp > 0.99:
                    self.adsrAttStage = 0
                    self.adsrDecStage = 1
            if self.adsrDecStage == 1:
                self.adsrAmp += -1 / int(self.dec * self.rate)
                if self.adsrAmp < 0.01:
                    self.adsrDecStage = 0
                    # if self.adsrAmp < sus:
                    #     self.adsrSusStage = 1
                    #     self.adsrAmp = sus
                    #if self.adsrSusStage == 1:
                    #nothing yet
            self.adsrBuf[n] = self.adsrAmp**self.adsrExp
        return(self.adsrBuf)

class VCA:
    def __init__(self, audiorate=44100, channels=1, framesperbuffer=256):
        self.chan = channels
        self.rate = audiorate

    def multiply(self, input1, input2):
        return input1 * input2

class Buffer:
    def __init__(self, audiorate=44100, channels=1, framesperbuffer=256):
        self.chan = channels
        self.rate = audiorate
        self.framesPerBuffer = framesperbuffer
        self.outbuf = array.array('h', [0]) * self.chan * self.framesPerBuffer  # * FRAMESPERBUFFER * CHANNELS  # array of signed ints

    def bufferize(self, frame_count, input, index):
        self.outbuf[index] = input
        return self.outbuf


def callback(in_data,frame_count,time_info,status): #callback zoals pyAudio deze verwacht, TODO - document incoming prameters
    global countDown, output, multipleOscillators

    countDown += 1
    #if countDown > 1: stream.stop_stream()   #de countdown: de audio wordt gestopt als de threshold bereikt wordt wanneer deze regel aanstaat

    if multipleOscillators == 1:
        output = oscA[0].Run(frame_count)
        for i in range(1, len(oscA)):
            output = np.add(output, oscA[i].Run(frame_count))
    else:
        output = osc.Run(frame_count)
        # osc.ADSR(frame_count, att=0.001, dec=2)
        #print("adsr is called")

    return(output.tobytes(), pyaudio.paContinue)