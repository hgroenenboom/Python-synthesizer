import numpy as np
import array
from math import ceil
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
    WNOISE = 8
    AM = 9
    "Types: Sine, Monosine, 1SinePerChannel, Monopulse, Monoadditivesaw, Sineramp, FM, White Noise, AM"

    monoPulseAmp = 0 #
    monoAddSawAmpA = [0] * 6  # de amplitudes van de boventonen van de additieve saw
    monoAddSawPhasA = [0] * 6  # de fases van de boventonen van de additieve saw
    phaseModulator = 0
    filterToggle = 1
    filterHighpass = 1
    filterLowpass = 1
    ringMod = 0
    output = 0

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

        #self.outputFrame = array.array('h', [0]) * self.chan
        self.outputFrame = np.zeros(self.chan, dtype='int16')

    def Run(self, ampMod=1):
        """De Run zal voor een audio frame synthetizeren"""
        if self.type == self.SINE:          #simple sinewave on all channels
            for c in range(self.chan):  #fill buffer with the same sin on every channel
                self.outputFrame[c] = int(32767 * self.amp * np.sin(self.phas) * ampMod)
            self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.MONOSINE:     #simple sinewave for mono use
            for c in range(self.chan):
                self.outputFrame[c] = int(32767 * self.amp * np.sin(self.phas) * ampMod)  #original sinewave
            self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.CSPLITSINE:   #different sines on different channels. is kaput, TODO Fix deze shit
            for c in range(self.chan):       #different sines on different channels
                self.outputFrame[c] = int(32767 * self.amp * np.sin(self.phas) * ampMod)
            self.phas += 2 * np.pi * self.freq / self.rate
        elif self.type == self.MONOPULSE:
            if self.phas > self.plswdth:     #square wave oscillator with pulse width
                self.monoPulseAmp = -1
            else:
                self.monoPulseAmp = 1
            for c in range(self.chan):
                self.outputFrame[c] = int(32767 * self.amp * self.monoPulseAmp * ampMod)
            self.phas += self.freq / self.rate
            self.phas = self.phas % 1.0
        elif self.type == self.MONOADDSAW:      #een additieve saw
            for b in range(self.monoAddSawAmpA.__len__()):       #saw wave using additive synthesis
                self.monoAddSawPhasA[b] += 2 * np.pi * self.freq * (b + 1) / self.rate
                self.monoAddSawAmpA[b] = int(32767 * self.amp * (1 / (b + 1)) * np.sin(self.monoAddSawPhasA[b]))
            for c in range(self.chan):
                self.outputFrame[c] = sum(self.monoAddSawAmpA)
        elif self.type == self.SINERAMP: #ramp van 200-1500 in 10s
            for c in range(self.chan):
                self.outputFrame[c] = int(32767 * self.amp * np.sin(self.phas) * ampMod)
            self.phas += 2 * np.pi * self.freq / self.rate
            if self.freq < 1500:
                self.freq = self.freq + (1500.0 - 200.0) / 44100.0 / 10.0
        elif self.type == self.FM:  #mono FM Synthesis
            for c in range(self.chan):
                self.outputFrame[c] = int(32767 * self.amp * np.sin(self.phas) * ampMod)
            self.phas += 2 * np.pi * (self.freq / self.rate + np.sin(self.phaseModulator) * self.modDepth)
            self.phaseModulator += 2 * np.pi * (self.ratio * self.freq) / self.rate
        elif self.type == self.WNOISE:
            for c in range(self.chan):
                self.outputFrame[c] = int(random.uniform(-32767, 32767) * ampMod)     #Noise
        elif self.type == self.AM:  #mono AM
            if self.ringMod == 0:
                for c in range(self.chan):
                    self.outputFrame[c] = int(32767 * self.amp * (np.sin(self.phas) * np.sin(self.phaseModulator)) * ampMod )  #original sinewave
                self.phas += 2 * np.pi * self.freq / self.rate
                self.phaseModulator += 2 * np.pi * self.freq * self.ratio / self.rate
            else:
                for c in range(self.chan):
                    self.outputFrame[c] = int(32767 * self.amp * (np.sin(self.phas) * (np.sin(self.phaseModulator) * 0.5 + 1)) * ampMod )  # original sinewave
                self.phas += 2 * np.pi * self.freq / self.rate
                self.phaseModulator += 2 * np.pi * self.freq * self.ratio / self.rate
        return (self.outputFrame)

    def getOutput(self):
        return self.outputFrame




class ADSR:

    adsrCounter = 0
    adsrAmp = 0
    adsrStart = 0
    adsrAttStage = 0
    adsrDecStage = 0
    adsrSusStage = 0
    adsrRelStage = 0
    adsrDamp = 2.0
    adsrAmpScaled = 0
    arpTime = 1

    def __init__(self, att=0.01, dec=0.3, sus=0, rel=0.04, audiorate=44100):
        self.att = att
        self.dec = dec
        self.sus = sus
        self.rel = rel
        self.rate = audiorate

    def Run(self):
        if self.adsrCounter > self.arpTime * self.rate or self.adsrCounter == 0:     #initialize ADSR
            self.adsrStart = 0
            self.adsrAmp = 0
            #self.freq *= 3/4 fun

        if self.adsrStart == 0:
            self.adsrCounter = 0
            self.adsrStart = 1
            self.adsrAttStage = 1

        self.adsrCounter += 1
        if self.adsrAttStage == 1:
            if self.att <= 0:
                self.att = 0.001
            self.adsrAmp += 1 / int(ceil(self.att * self.rate))
            if self.adsrAmp > 0.99:
                self.adsrAttStage = 0
                self.adsrDecStage = 1
        if self.adsrDecStage == 1:
            if self.dec <= 0:
                self.dec = 0.001
            self.adsrAmp += -1 / int(ceil(self.dec * self.rate))
            if self.adsrAmp < 0.01:
                self.adsrDecStage = 0
                # if self.adsrAmp < sus:
                #     self.adsrSusStage = 1
                #     self.adsrAmp = sus
                #if self.adsrSusStage == 1:
                #nothing yet
        self.adsrAmpScaled = self.adsrAmp ** self.adsrDamp
        return(self.adsrAmpScaled)

class VCA:
    def __init__(self, audiorate=44100, channels=1, framesperbuffer=256):
        self.chan = channels
        self.rate = audiorate

        self.vca = np.zeros(self.chan, dtype='int16')

    def multiply(self, input1, modulator=1, input2=0, input3=0):
        self.vca = (input1 + input2 + input3) * modulator

    def get(self):
        return self.vca

class Buffer:
    def __init__(self, audiorate=44100, channels=1, framesperbuffer=256):
        self.chan = channels
        self.rate = audiorate
        self.framesPerBuffer = framesperbuffer
        #self.outbuf = array.array('h', [0]) * self.chan * self.framesPerBuffer  # * FRAMESPERBUFFER * CHANNELS  # array of signed ints
        self.outbuf = np.zeros(self.chan * self.framesPerBuffer, dtype='int16')

    def bufferize(self, input, index, channels):
        self.outbuf[index * channels: index * channels + channels:1] = input
        return self.outbuf

    def getOutput(self):
        return self.outbuf

class AverageFilter:  # TODO - filter laten controleren, stereo maken met de channels input
    filterOutput = 0

    def __init__(self, lowpassamount=1, highpassamount=0, channels=1):
        self.lowpassAmount = lowpassamount
        self.highpassAmount = highpassamount
        self.chan = channels

    def Run(self, inputbuffer, index):
        if self.lowpassAmount > 0:      #0 = bypass. Met de waarde filterLowpass kan de filter intensiteit bepaald worden
            filterOutput = 0    #initializeer output met 0
            for p in range(self.lowpassAmount):     #loop "lowpassAmount" keer de lowPass af
                filterOutput += inputbuffer[index - p]  #de specifieke inputbuffer waardes worden bij filteroutput opgeteld
                filterOutput /= self.lowpassAmount      #de filteroutput wordt gedeeld door "lowpassAmount" (de hoeveelheid samples uit de buffer
            inputbuffer[index - self.lowpassAmount] = int(filterOutput)    #hier wordt van de !oudste! bufferwaarde de waarde aangepast zodat de nieuwere waardes nog voor de volgende filterwaardes gebruikt kunnen worden
        if self.highpassAmount > 0:
            filterOutput = 0
            for p in range(self.highpassAmount):
                filterOutput += inputbuffer[index - p]
                filterOutput /= self.highpassAmount
            inputbuffer[index - self.highpassAmount] = int(filterOutput)
        return inputbuffer
