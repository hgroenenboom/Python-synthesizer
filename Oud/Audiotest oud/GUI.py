from tkinter import *

SLIDER1VAL = 0

def print_value(val):
    print("scale1 = ", val)

class GUI(Frame): #GUI is een extension van Frame. Frame is een systeem class die het mogelijk maakt om windows te maken.
  """ A GUI app """
  """ A GUI app """
  global SLIDER1VAL

  def __init__(self,master):
    """ Constructor: init the frame """
    Frame.__init__(self,master)
    #self.grid()
    self.button_clicks=0
    self.create_widgets()
    self.initialize()

  def create_widgets(self):
    self.button1 =  Button(self, text="Button 1")
    #self.button1.grid()

    self.button2 =  Button(self, text="Button 2")
    #self.button2.grid()

    self.button3 =  Button(self, text="Button 3")
    #self.button3.grid()

    self.slider1 = Scale(self)
    self.slider1.config(orient=HORIZONTAL)
    self.slider1.config(length=400)
    self.slider1.config(width=10)
    self.slider1.config(sliderlength=20)
    self.slider1.config(from_=0)
    self.slider1.config(to_=1000)
    self.slider1.config(tickinterval=200)
    self.slider1.grid_location(200,300)
    #scale = Tkinter.Scale(orient='horizontal', from_=0, to=128, command=print_value)
    self.slider1.pack()
    SLIDER1VAL = self.slider1.get()

  def initialize(self):
      self.grid()


# # create a window
# root = Tk()
#
# # set window props
# root.title("ME Gui")
# #root.geometry("500x500")
#
# app = GUI(root)
#
# root.mainloop()
#
# print(app.slider1.get())

#print(app.slider1.get())
