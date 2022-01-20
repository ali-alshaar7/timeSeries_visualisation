import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from nwb_loader import open_file

from matplotlib.figure import Figure
from tkinter import *
import os

import xlrd
from xlrd import open_workbook
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import ALL

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np #new


class mclass:
    def __init__(self, window, dir):
        self.window = window
        self.window.bind("<MouseWheel>", self.mouse_wheel)
        self.window.bind('<B1-Motion>', self.pan)  
        self.window.bind('<1>', self.initialise_pan)        
        self.window.geometry("1000x500")
        self.canvas = None
        self.data = open_file(dir)
        self.x1 = 0
        self.zoom = 100
        self.initial_B1_x = 0
        self.initial_B1_y = 0
        self.button = Button(window, text="Plot", command=self.plot)
        self.zoom_button = Button(window, text="zoom out", command=self.zoom_o)
        self.zoom_in_button = Button(window, text="zoom in", command=self.zoom_i)
        self.clear_button = Button(window, text="Clear Space", command=self.clear_space)
        self.button.pack(side="top")
        self.zoom_button.pack(side="top")
        self.zoom_in_button.pack(side="top")
        self.clear_button.pack(side="top")

    def clear_space(self): #new
        self.canvas._tkcanvas.destroy()

    def plot(self):
        fig = Figure(figsize=(15, 12))
        self.canvas = FigureCanvasTkAgg(fig, master=self.window)
        self.canvas.get_tk_widget().pack()
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)

        a = fig.add_subplot(111)
        a.set_facecolor('xkcd:black')

        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.spines['left'].set_visible(False)

        dat = self.data['continuous'][0]

        a.plot( np.linspace(self.x1, self.zoom + self.x1, self.zoom ),
                dat[ self.x1 : self.zoom + self.x1 ] )
        
        
        
        self.canvas.draw()

    def zoom_o(self):
        self.zoom += 100
        self.clear_space()
        self.plot()

    def zoom_i(self):
        self.zoom -= 100
        if self.zoom < 100:
            self.zoom = 100
        self.clear_space()
        self.plot()

    def mouse_wheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.zoom_o()
        if event.num == 4 or event.delta == 120:
            self.zoom_i()

    def pan(self, event):
        self.x1 += ( event.x -  self.initial_B1_x)

        if self.x1 < 0:
            self.x1 = 0
        elif self.x1 >= self.data['continuous'][0].size - 1 - self.zoom:
            self.x1 = self.data['continuous'][0].size - 1 - self.zoom

        self.clear_space()
        self.plot()

    def initialise_pan(self, event):
        self.initial_B1_x = event.x
        self.initial_B1_y = event.y



root = Tk() #new
dir = r'C:\Users\alish\Desktop\current_year\xcelleration\OPEN_EPHYS\nwbnew.nwb'
my_mclass = mclass(root, dir) #new
root.mainloop() #new