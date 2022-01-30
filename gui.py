import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from nwb_loader import open_file, open_ephys_dir, convert_ephys_nwb

from matplotlib.figure import Figure
from tkinter import *
import os


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np #new
from PIL import Image, ImageTk

import time

class Button_icons:
    def __init__( self ):
        self.root = r"C:\Users\alish\Desktop\current_year\xcelleration\ts_visualisation\images\icons"
        self.zoom_in = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "zoom_in.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.zoom_out = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "zoom_out.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        
        self.pan_right =ImageTk.PhotoImage(Image.open( os.path.join(self.root, "pan_right.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.pan_left = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "pan_left.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.truncate = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "truncate.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.plot = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "plot.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.select_nwb = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "select_nwb.jpg") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.clear = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "clear.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.export = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "export.png") ).resize((20,20), resample = Image.BILINEAR) ) 

class Channel_window:
    def __init__(self,root, dat, X1, Zoom, from_ephys, dir ):

        self.from_ephys = from_ephys
        self.root_path = dir

        self.data = dat

        self.start_x = tk.StringVar()
        self.end_x = tk.StringVar()

        self.x1 = X1
        self.zoom = Zoom
        self.canvas = None

        self.icons = Button_icons()

        self.chan_frame = tk.Frame(root)
        self.plot_frame = tk.Frame(root)

        self.grid_on = BooleanVar()
        self.plot_color = StringVar()
        self.plot_color.set('black')

        self.zoom_button = Button(self.chan_frame, text="zoom out", command=self.zoom_o, 
                                image = self.icons.zoom_out)
        self.zoom_in_button = Button(self.chan_frame, text="zoom in", command=self.zoom_i,
                                image = self.icons.zoom_in)

        self.pan_right_button = Button(self.chan_frame, text="pan right", command=self.pan_right,
                                image = self.icons.pan_right)
        self.pan_left_button = Button(self.chan_frame, text="pan left", command=self.pan_left,
                                image = self.icons.pan_left)

        self.clear_button = Button(self.chan_frame, text="Clear Space", command=self.clear_space,
                                image = self.icons.clear)
        self.set_plot_window = Button(self.chan_frame, text="set plot window", command=self.trunc_set,
                                image = self.icons.truncate)

        self.export = Button(self.chan_frame, text="export to NWB", command=self.export_nwb,
                                image = self.icons.export)

        self.start_x_entry = Entry(self.chan_frame, textvariable=self.start_x)
        self.end_x_entry = Entry(self.chan_frame, textvariable=self.end_x)

        color_options = ["black", "blue", "white", "green"] 
        self.check_grid = Checkbutton(self.chan_frame, text="grid", variable=self.grid_on, command=self.set_grid)
        self.plot_color_select = OptionMenu( self.chan_frame , self.plot_color,
                                    *color_options , command = self.set_color)
        
        self.grid_on.set(True)
        self.check_grid.grid_on = self.grid_on

        self.chan_frame.pack(side="top")
        self.plot_frame.pack(side="top")

    def clear_space(self): #new
        self.canvas._tkcanvas.destroy()

    def set_color(self, event):
        self.plot(True)
    def set_grid(self):
        self.plot(True)
    
    def zoom_o(self):

        self.zoom *= 2
        self.plot(True)

    def zoom_i(self):

        self.zoom = int(self.zoom/2)
        if self.zoom < 100:
            self.zoom = 100

        self.plot(True)
    
    def pan_right(self):
        
        self.x1 += int(self.zoom/2)
        if self.x1 >= self.data.size - 1 - self.zoom:
            self.x1 = self.data.size - 1 - self.zoom
        self.plot(True)
    
    def pan_left(self):

        self.x1 -= int(self.zoom/2)
        if self.x1 < 0:
            self.x1 = 0
        self.plot(True)
    
    def trunc_set(self):

        self.x1 = int(self.start_x.get())
        self.zoom = int(self.end_x.get()) - int(self.x1)

        if self.x1 < 0:
            self.x1 = 0
        elif self.x1 >= self.data.size - 1 - self.zoom:
            self.x1 = self.data.size - 1 - self.zoom

        self.plot(True)

    def export_nwb(self):
        files = [('NWB Files', '*.nwb'), ('All Files', '*.*')]
        file = tk.filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        convert_ephys_nwb(self.root_path, str(file.name) )

    def plot(self, erase_bool):
        start = time.time()

        if erase_bool == True:
            self.clear_space()
        else:
            self.set_plot_window.grid(row=0, column=1)
            self.zoom_button.grid(row=0, column=2)
            self.zoom_in_button.grid(row=0, column=3)
            self.pan_left_button.grid(row=0, column=4)
            self.pan_right_button.grid(row=0, column=5)
            self.clear_button.grid(row=0, column=6)
            self.plot_color_select .grid( row=0, column=7 )
            self.check_grid.grid(row=0, column=8)
            if self.from_ephys:
                self.export.grid(row=1, column=1)


            self.start_x_entry.grid(row=0, column=0)
            self.end_x_entry.grid(row=1, column=0)

        
        s1 = time.time()

        

        fig = Figure(figsize=(15, 12))
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)

        s2 = time.time()

        a = fig.add_subplot(111)
        a.set_facecolor( 'xkcd:' + self.plot_color.get() )

        if bool(self.grid_on.get()):
            a.grid(color = 'brown')

        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.spines['left'].set_visible(False)

        a.plot( np.linspace(self.x1, self.zoom + self.x1, self.zoom ),
                self.data[ self.x1 : self.zoom + self.x1 ] )
        
        s3 = time.time()
        
        self.canvas.draw()

        s4 = time.time()

        #print(s1 - start, s2 - s1, s3-s2, s4-s3)
        

        

class GUI:
    def __init__(self, window):
        self.window = window

        self.window.geometry("1000x500")
        self.channels = []

        self.channel_option = tk.IntVar()
        self.channel_option.set("0")
        self.channel_options = [0]
        self.is_there_plot = False

        self.plot_button = Button( window , text="Plot", command=self.plot)
        self.file_select = Button( window, text="Select NWB File", command=self.select_file)
        self.folder_select = Button( window, text="Select OPhys directory File", command=self.select_ophys)

        self.file_select.pack(side="top")
        self.folder_select.pack(side="top")

    def plot(self):

        cur_plot = self.channels[ self.channel_option.get() ]

        cur_plot.plot(self.is_there_plot)
        self.is_there_plot = True


    def select_file(self):
        filetypes = (
            ('nwb files', '*.nwb'),
            ('All files', '*.*')
        )

        filename = tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        dat = open_file(filename)
        self.channel_options = np.linspace(0, len( dat['continuous']) - 1 ,  
                               len( dat['continuous']) ).tolist()

        for conts in dat['continuous']:
            self.channels.append( Channel_window( self.window, conts, 0, 100, False, filename  ) )
        
        self.chan_select_menu = OptionMenu( self.window ,self.channel_option,*self.channel_options )
        
        self.plot_button.pack(side="top")
        self.chan_select_menu.pack(side="top")


    def select_ophys(self):

        filename = tk.filedialog.askdirectory(parent=root,initialdir="/",
                    title='Please select a directory')
        
        dat = open_ephys_dir(filename)
        self.channel_options = np.linspace(0, len( dat['continuous']) - 1 ,  
                               len( dat['continuous']) ).tolist()

        for conts in dat['continuous']:
            self.channels.append( Channel_window( self.window, conts, 0, 100, True, filename ) )
        
        self.chan_select_menu = OptionMenu( self.window ,self.channel_option,*self.channel_options )
        
        self.plot_button.pack(side="top")
        self.chan_select_menu.pack(side="top")



root = Tk() #new
root.title("xCELLeration time series viewer")
my_mclass = GUI(root) #new
root.mainloop() #new