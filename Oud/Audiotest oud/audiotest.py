#
# Basic pyaudio program playing a real time mono sine wave
#
# (ME) 2015 Marc Groenewegen
#

import pyaudio
import time
import array
import numpy as np
#import GUI
import oscillator

#de full caps dingetjes zijn constanten. Je maakt iets dus full caps als je aan wilt geven dat dit nooit runtime verandert.
WIDTH = 2 # sample size in bytes
CHANNELS = 1 # number of samples in a frame
RATE = 44100
FRAMESPERBUFFER = 256

countDown = 0
outputDevice=3
disableCloseInput = 0
multipleOscillators = 0

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
#       TIME_STEP = 100
#       freqInc = (freqEnd - freqStart) / (TIME * TIME_STEP)
#       freq = freqStart
#       for n in range(TIME * TIME_STEP):
#           freq += freqInc
#           time.sleep(.01)
#           sineFrequency[0] = freq
#       return freq


#
# Create array of signed ints to hold one sample buffer
# Make it global so it doesn't get re-allocated for every frame
#
outbuf = array.array('h', [0]) * FRAMESPERBUFFER * CHANNELS # array of signed ints
output = outbuf

if multipleOscillators == 1:
    oscA = [oscillator.Oscillator((i + 1) * 400, 0, oscillator.Oscillator.MONOSINE, CHANNELS, RATE, 0.5 / (i + 1),  i * 0.1 + 0.2) for i in range(10)]
else:
    osc = oscillator.Oscillator(frequency=300, phase=0, type=oscillator.Oscillator.FM, channels=CHANNELS, rate=RATE, amp=0.5, pulsewidth=0.1, ratio=1.005, modDepth=0.015)
    osc.filterHighpass = 2  #dubbele lowpass filter
    osc.filterLowpass = 2  #dubbele highpass filter
    adsr = oscillator.ADSR(att=0.01,dec=1,sus=0,rel=0)
    buffer = oscillator.Buffer(audiorate=RATE,channels=CHANNELS,framesperbuffer=FRAMESPERBUFFER)
print("oscillator gemaakt + buffer gemaakt")

#
# Create the callback function which is called by pyaudio
#   whenever it needs output-data or has input-data
#
# As we are working with 16-bit integers, the range is from -32768 to 32767
#

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

# Make sure that the main program doesn't finish until all
#  audio processing is done
while stream.is_active():
    if disableCloseInput == 0:
        closeInput = input("\nPress q to exit, 'ramp' to start freqRamp, 'env' to trigger the ADSR and 'test' to disable the close input").split(" ")
        if (closeInput[0] == 'q'):
              print("Closing...")
              stream.stop_stream()
        elif (closeInput[0] == "ramp"):
              print("Ramping")
              freqRamp(int(closeInput[1]), int(closeInput[2]), int(closeInput[3]))
        elif (closeInput[0] == "test"):
            disableCloseInput = 1
        elif (closeInput[0] == "env"):
            osc.adsrStart = 0
        time.sleep(1)

closeInput = input