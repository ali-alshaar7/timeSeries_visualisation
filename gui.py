import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from nwb_loader import open_file

from matplotlib.figure import Figure
from tkinter import *
import os


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np #new


class mclass:
    def __init__(self, window):
        self.window = window

        self.window.bind("<MouseWheel>", self.mouse_wheel)
        self.window.bind('<B1-Motion>', self.pan)  
        self.window.bind('<1>', self.initialise_pan)   

        self.window.geometry("1000x500")
        self.canvas = None
        self.data = []
        self.channel = []
        self.truncate = tk.Frame(root)

        self.x1 = 0
        self.zoom = 100
        self.initial_B1_x = 0
        self.initial_B1_y = 0
        self.start_x = tk.StringVar()
        self.end_x = tk.StringVar()
        self.channel_option = tk.StringVar()
        self.channel_option.set("0")
        self.channel_options = []
        self.is_there_plot = False

        self.plot_button = Button(window, text="Plot", command=self.plot)
        self.zoom_button = Button(window, text="zoom out", command=self.zoom_o)
        self.zoom_in_button = Button(window, text="zoom in", command=self.zoom_i)
        self.clear_button = Button(window, text="Clear Space", command=self.clear_space)
        self.file_select = Button(window, text="Select NWB File", command=self.select_file)
        self.set_plot_window = Button(window, text="set plot window", command=self.trunc_set)

        self.start_x_entry = Entry(self.truncate, textvariable=self.start_x)
        self.end_x_entry = Entry(self.truncate, textvariable=self.end_x)

        self.truncate.pack(side="top")

        self.file_select.pack(side="top")

    def clear_space(self): #new
        self.canvas._tkcanvas.destroy()
        self.is_there_plot = False

    def plot(self):

        if self.data == []:
            print("Please select a file")
            return

        if self.is_there_plot == True:
            self.clear_space()
        
        self.is_there_plot = True
        self.channel = self.data['continuous'][int(float(self.channel_option.get()))]

        self.zoom_button.pack(side="top")
        self.zoom_in_button.pack(side="top")
        self.clear_button.pack(side="top")

        self.start_x_entry.pack(side="top")
        self.end_x_entry.pack(side="top")
        self.set_plot_window.pack(side="top")

        fig = Figure(figsize=(15, 12))
        self.canvas = FigureCanvasTkAgg(fig, master=self.window)
        self.canvas.get_tk_widget().pack()
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)

        a = fig.add_subplot(111)
        a.set_facecolor('xkcd:black')
        a.grid(color = 'brown')

        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.spines['left'].set_visible(False)

        dat = self.channel

        a.plot( np.linspace(self.x1, self.zoom + self.x1, self.zoom ),
                dat[ self.x1 : self.zoom + self.x1 ] )
        
        
        
        self.canvas.draw()

    def zoom_o(self):

        if self.data == []:
            print("Please select a file")
            return

        self.zoom += 100
        self.plot()

    def zoom_i(self):

        if self.data == []:
            print("Please select a file")
            return

        self.zoom -= 100
        if self.zoom < 100:
            self.zoom = 100

        self.plot()

    def mouse_wheel(self, event):

        if self.data == []:
            print("Please select a file")
            return

        if event.num == 5 or event.delta == -120:
            self.zoom_o()
        if event.num == 4 or event.delta == 120:
            self.zoom_i()

    def pan(self, event):

        if self.data == []:
            print("Please select a file")
            return

        self.x1 += ( event.x -  self.initial_B1_x)

        if self.x1 < 0:
            self.x1 = 0
        elif self.x1 >= self.channel.size - 1 - self.zoom:
            self.x1 = self.channel.size - 1 - self.zoom

        self.plot()

    def initialise_pan(self, event):

        if self.data == []:
            print("Please select a file")
            return

        self.initial_B1_x = event.x
        self.initial_B1_y = event.y

    def select_file(self):
        filetypes = (
            ('nwb files', '*.nwb'),
            ('All files', '*.*')
        )

        filename = tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        self.data = open_file(filename)
        self.channel_options = np.linspace(0, len(self.data['continuous']) - 1 ,  
                               len(self.data['continuous']) ).tolist()

        self.chan_select_menu = OptionMenu(self.window ,self.channel_option, *self.channel_options )
        
        self.plot_button.pack(side="top")
        self.chan_select_menu.pack(side="top")

    def trunc_set(self):

        self.x1 = int(self.start_x.get())
        self.zoom = int(self.end_x.get()) - int(self.x1)

        if self.x1 < 0:
            self.x1 = 0
        elif self.x1 >= self.channel.size - 1 - self.zoom:
            self.x1 = self.channel.size - 1 - self.zoom

        self.plot()

    def select_ophys(self):

        filename = tk.filedialog.askdirectory(parent=root,initialdir="/",
                    title='Please select a directory')



root = Tk() #new
root.title("xCELLeration time series viewer")
my_mclass = mclass(root) #new
root.mainloop() #new