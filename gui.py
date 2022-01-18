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
        self.window.geometry("500x500")
        self.canvas = None
        self.data = open_file(dir)
        self.x1 = 0
        self.x2 = 100
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
        base = "dummy text" #new
        a = fig.add_subplot(111)
        a.set_facecolor('xkcd:black')
        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.spines['left'].set_visible(False)
        a.plot(self.data['continuous'][0][ self.x1 : self.x2 ])
        
        
        
        self.canvas.draw()

    def zoom_o(self):
        self.x2 += 100
        self.clear_space()
        self.plot()

    def zoom_i(self):
        self.x2 -= 100
        if self.x2 < 100:
            self.x2 = 100
        self.clear_space()
        self.plot()

root = Tk() #new
dir = r'C:\Users\alish\Desktop\current_year\xcelleration\ephys2nwb\OPEN_EPHYS\nwbnew.nwb'
my_mclass = mclass(root, dir) #new
root.mainloop() #new