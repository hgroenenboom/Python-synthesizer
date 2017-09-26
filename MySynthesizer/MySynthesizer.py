#
# Basic pyaudio program playing a real time mono sine wave
#
# (ME) 2015 Marc Groenewegen
#

import pyaudio
import time
import array
import numpy as np
import GUI              #Bevat de gui Class
import modsynth         #Bevat alle synthese classes
from tkinter import *    #GUI

#de full caps dingetjes zijn constanten. Je maakt iets dus full caps als je aan wilt geven dat dit nooit runtime verandert.
WIDTH = 2 # sample size in bytes
CHANNELS = 1 # number of samples in a frame
RATE = 44100
FRAMESPERBUFFER = 256

countDown = 0
outputDevice=3
disableCloseInput = 0
multipleOscillators = 0
updateSpeed = 5000

#
# Function showDevices() lists available input- and output devices
#
class paAuWrapper():
    def __init__(self):
        print("Een audio wrapper van PyAudio")

    def showDevices(self, p):
        """print alle beschikbare in en output devices"""
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range (0,numdevices):
            if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))
            if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
                print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))

    def setOutputDevice(self, p):
        global outputDevice
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range (0,numdevices):
            print("maxOutputChannels at index ", i , ": ", p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels'))
            if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
                print(p.get_device_info_by_host_api_device_index(0,i).get('name').find("Built-in"))
            if p.get_device_info_by_host_api_device_index(0,i).get('name').find("Built-in") >= 0:
                outputDevice=i
            print("Selected device number: ", str(outputDevice))

# def freqRamp(freqStart=200, freqEnd=400, TIME=2):   #not in use, TODO: maak de functie zo dat hij de stijgende stappen uit een lijst leest die hij heeft gegenereerd ipv ze terplekke genereerd
#     """deze functie is nu outdated"""
#     TIME_STEP = 100
#     freqInc = (freqEnd - freqStart) / (TIME * TIME_STEP)
#     freq = freqStart
#     for n in range(TIME * TIME_STEP):
#         freq += freqInc
#         time.sleep(.01)
#         sineFrequency[0] = freq
#     return freq


#
# Create array of signed ints to hold one sample buffer
# Make it global so it doesn't get re-allocated for every frame
#
outbuf = array.array('h', [0]) * FRAMESPERBUFFER * CHANNELS # array of signed ints
outbuftest = np.zeros(FRAMESPERBUFFER * CHANNELS, np.dtype('int16'))
output = outbuf

if multipleOscillators == 1:
    oscA = [modsynth.Oscillator((i + 1) * 400, 0, modsynth.Oscillator.WNOISE, CHANNELS, RATE, 0.5 / (i + 1), i * 0.1 + 0.2) for i in range(10)]
else:
    osc1 = modsynth.Oscillator(frequency=300, phase=0, type=modsynth.Oscillator.FM, channels=CHANNELS, rate=RATE, amp=0.5, pulsewidth=0.5, ratio=1.005, modDepth=0.015)
    osc1.filterHighpass = 2  #dubbele lowpass filter
    osc1.filterLowpass = 2  #dubbele highpass filter
    # osc2 = modsynth.Oscillator(600, 0, type=modsynth.Oscillator.FM, channels=CHANNELS, rate=RATE, modDepth= 0.013, amp=0, ratio=1.001)
    #lp1 = modsynth.AverageFilter(0, 0, CHANNELS)
    ampEnv1 = modsynth.ADSR(att=0.01, dec=1, sus=0, rel=0, audiorate=RATE)
    vca1 = modsynth.VCA()
    buffer = modsynth.Buffer(audiorate=RATE, channels=CHANNELS, framesperbuffer=FRAMESPERBUFFER)
print("audio objecten zijn geinitializeerd")

#
# Create the callback function which is called by pyaudio
#   whenever it needs output-data or has input-data
#
# As we are working with 16-bit integers, the range is from -32768 to 32767
#

def callback(in_data,frame_count,time_info,status): #callback zoals pyAudio deze verwacht, TODO - document incoming prameters
    global countDown, output, multipleOscillators

    countDown += 1
    #if countDown > 2: stream.stop_stream()   #de countdown: de audio wordt gestopt als de threshold bereikt wordt wanneer deze regel aanstaat

    if multipleOscillators == 1:
        output = oscA[0].Run(frame_count)
        for i in range(1, len(oscA)):
            output = np.add(output, oscA[i].Run(frame_count))
    else:
        for n in range(frame_count):
            vca1.multiply(osc1.Run(), ampEnv1.Run()) # , osc2.Run()
            buffer.bufferize(vca1.get(), n, CHANNELS)
            #lp1.Run(buffer.getOutput(), n) #TODO - filter laten controleren

    return(buffer.getOutput().tobytes(), pyaudio.paContinue)


    #########################
    # Start of main program #
    #########################


#
# get a handle to the pyaudio interface
#
paHandle = pyaudio.PyAudio()
pW = paAuWrapper()
print("\nAvailable devices: ")
pW.showDevices(paHandle)
print("\n")
# select a device
pW.setOutputDevice(paHandle)
devinfo = paHandle.get_device_info_by_index(outputDevice)
print("Selected device name: ",devinfo.get('name'))

#
# open a stream with some given properties
#
stream = paHandle.open(format=paHandle.get_format_from_width(WIDTH),
                       channels=CHANNELS,
                       rate=RATE,
                       frames_per_buffer=FRAMESPERBUFFER,
                       input=False, # no input
                       output=True, # only output
                       output_device_index=outputDevice, # choose output device
                       stream_callback=callback)

stream.start_stream()

# create a window
root = Tk()

# set window props
root.title("ME Gui")
# root.geometry("500x500")

app = GUI.callGUI(master=root)

# Make sure that the main program doesn't finish until all
#  audio processing is done

# while stream.is_active():
#     #app.update()
#     app.mainloop()
#     if disableCloseInput == 0:
#         closeInput = input("\nPress q to exit, 'ramp' to start freqRamp, 'env' to trigger the ADSR and 'test' to disable the close input\n").split(" ")
#         if (closeInput[0] == 'q'):
#             print("Closing...")
#             stream.stop_stream()
#         elif (closeInput[0] == "ramp"):
#             print("Ramping")
#             #freqRamp(int(closeInput[1])s, int(closeInput[2]), int(closeInput[3]))
#         elif (closeInput[0] == "test"):
#             disableCloseInput = 1
#         elif (closeInput[0] == "env"):
#             osc1.adsrStart = 0
#     time.sleep(0.01)

while 1:
    app.update()
    updateSpeed += 1
    if updateSpeed >= 99:
        if osc1.freq != app.sliderFreq.get():
            osc1.freq = app.sliderFreq.get()
        if osc1.ratio != app.sliderRatio.get():
            osc1.ratio = app.sliderRatio.get()
        if osc1.type != app.sliderType.get():
            osc1.type = app.sliderType.get()
        if osc1.modDepth != app.sliderModDepth.get()**2.0:
            osc1.modDepth = app.sliderModDepth.get()** 2.0
        if osc1.amp != app.sliderAmp.get()**2.0:
            osc1.amp = app.sliderAmp.get()**2.0
        if ampEnv1.att != app.sliderAtt.get():
            ampEnv1.att = app.sliderAtt.get()
        if ampEnv1.dec != app.sliderDec.get():
            ampEnv1.dec = app.sliderDec.get()
        if ampEnv1.arpTime != app.sliderArpTime.get():
            ampEnv1.arpTime = app.sliderArpTime.get()
        updateSpeed = 0
