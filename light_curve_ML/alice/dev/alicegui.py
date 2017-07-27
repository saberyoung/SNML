import tkinter as tk
'''
import numpy as np
import alice

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
        NavigationToolbar2TkAgg
from matplotlib.figure import Figure

'''
###############################     MAIN WINDOW ##########################
class MainMenu(tk.Frame):

   def __init__(self, master=None):
      super().__init__(master)
      self.pack()
      self.initUI()

   def initUI(self):

      tL = tk.Label(self,text='SN=')
      tL.grid(row=0,column=0,sticky="W")

      self.snname = tk.Entry(self,width=30)
      self.snname.grid(row=0,column=1,sticky='E')
      self.snname.insert(0,'snname')

      tL = tk.Label(self,text='date=')
      tL.grid(row=0,column=2,sticky="W")

      self._date = tk.Entry(self,width=10)
      self._date.grid(row=0,column=3,sticky='E')
      self._date.insert(0,'_date')

      tL = tk.Label(self,text='label=')
      tL.grid(row=0,column=4,sticky="W")

      self.fig = Figure(figsize=(7,5))
      self.ax0 = self.fig.add_axes([0.1,.1,.85,.8])
      self.ax0.plot(np.arange(10),np.arange(10),'-')
      self.ax0.set_title('')   

     self.w_plot = FigureCanvasTkAgg(self.fig, master=self)
     self.w_plot.get_tk_widget().grid(row=1,column=0,columnspan=3)

#      self.w_plot.show()
 
################################   call to main #########################
if __name__ == "__main__":

   root = tk.Tk()
#   root.geometry("+5+5")
#   root.title('Alice GUI        @enrico.cappellaro')   
#   root.option_add( "*font", "fixed 12 bold " ) 
#   root.protocol('WM_DELETE_WINDOW', root.quit)
   app = MainMenu(master=root)
   app.mainloop()

'''
import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
'''
