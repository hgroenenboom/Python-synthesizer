from tkinter import *

SLIDER1VAL = 0


def print_value(val):
    print("scale1 = ", val)


class callGUI(Frame):  # GUI is een extension van Frame. Frame is een systeem class die het mogelijk maakt om windows te maken.
    """ A GUI app """
    """ A GUI app """
    global SLIDER1VAL

    def __init__(self, master):
        """ Constructor: init the frame """
        Frame.__init__(self, master)
        # self.grid()
        self.button_clicks = 0
        self.create_widgets()
        self.initialize()

    def create_widgets(self):
        self.button1 = Button(self, text="Button 1")
        # self.button1.grid()

        self.button2 = Button(self, text="Button 2")
        # self.button2.grid()

        self.button3 = Button(self, text="Button 3")
        # self.button3.grid()

        self.sliderFreq = self.makeSlider("Main Frequency", 20, 1000, 200)
        self.sliderFreq.pack()
        self.sliderAmp = self.makeSlider("Oscillator Amplitude", 0, 1, 0.5, 0.001)
        self.sliderAmp.pack()
        self.sliderRatio = self.makeSlider("Modulator Ratio", 0.001, 10.00, 1.02, 0.001)
        self.sliderRatio.pack()
        self.sliderModDepth = self.makeSlider("ModDepth", 0, 0.4, 0.13, 0.001)
        self.sliderModDepth.pack()
        self.sliderType = self.makeSlider("Synthesis Type: Sine, Monosine, 1SinePerChannel, Monopulse, Monoadditivesaw, Sineramp, FM, White Noise, AM", 1, 9, 7, 1)
        self.sliderType.pack()
        self.sliderAtt = self.makeSlider("Attack of the ADSR", 0, 1, 0.01, 0.0001)
        self.sliderAtt.pack()
        self.sliderDec = self.makeSlider("Decay of the ADSR", 0, 1, 0.4, 0.0001)
        self.sliderDec.pack()
        self.sliderArpTime = (self.makeSlider("Rate of the Arpeggio", 0, 2, 0.5, 0.001))
        self.sliderArpTime.pack()

    def initialize(self):
        self.grid()

    def makeSlider(self, name="slider", frm=0.0, to=1.0, set=0.0, resolution=0.1, len=400, wdth=10, sliderlen=30):
        x = Scale(self)
        x.config(orient=HORIZONTAL, length=len, width=wdth, sliderlength=sliderlen, from_=frm, to_=to, tickinterval=200, resolution=resolution)
        x.set(set)
        x.config(label=name)
        return x

    def callMainLoop(self):
        print("yolo")
        self.root.mainloop()

# print(app.slider1.get())
