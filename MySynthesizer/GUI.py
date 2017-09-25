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

        self.slider1 = Scale(self)
        self.slider1.config(orient=HORIZONTAL)
        self.slider1.config(length=400)
        self.slider1.config(width=10)
        self.slider1.config(sliderlength=20)
        self.slider1.config(from_=20)
        self.slider1.config(to_=1000)
        self.slider1.config(tickinterval=200)
        self.slider1.set(200)
        # self.slider1.grid(row = 0)
        self.s = self.slider1
        self.s.pack()
        self.slider1.config(label="swag")
        # SLIDER1VAL = self.slider1.get()

        self.slider2 = Scale(self)
        self.slider2.config(orient=HORIZONTAL, length=400, width=10, sliderlength=20, from_=0.001, to_=10.00, tickinterval=200)
        self.slider2.set(2)
        # self.slider2.grid(row = 1)
        self.slider2.config(label="swag2")
        self.s = self.slider2
        self.s.pack()

        self.slider3 = Scale(self)
        self.slider3.config(orient=HORIZONTAL, length=400, width=10, sliderlength=20, from_=1, to_=9, tickinterval=200)
        self.slider3.set(2)
        # self.slider2.grid(row = 1)
        self.slider3.config(label="swag3")
        self.s = self.slider3
        self.s.pack()

    def initialize(self):
        self.grid()

    def callMainLoop(self):
        print("yolo")
        self.root.mainloop()

# print(app.slider1.get())
