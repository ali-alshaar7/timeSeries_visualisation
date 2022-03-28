import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from nwb_loader import open_file, open_ephys_dir, convert_ephys_nwb

from matplotlib.figure import Figure
from tkinter import *
import os
import itertools
from dateutil import parser
import json
from datetime import datetime

from pynwb import NWBFile, TimeSeries, NWBHDF5IO, ecephys
from pynwb.file import Subject

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np 
from PIL import Image, ImageTk

from OpenEphys_to_NWB import openephys2nwb, OpenEphys , defaults
from OpenEphys import load
from defaults import default_metadata
from openephys2nwb import readMetaData

import time

from images import Button_icons, proj_root_dir
from util_classes import conc_files, event_storage
        

class Channel_window:
    def __init__(self, root, dat, X1, Zoom, from_ephys, dir , spike, file_obj, io):

        self.from_ephys = from_ephys
        self.root = root
        self.nwb_obj = file_obj
        self.io = io
        self.root_path = dir

        self.big_data = dat
        self.big_spike = spike

        self.data = self.big_data
        if self.big_spike is not None:
            self.spike = self.big_spike[0].data
            self.spike_time = self.big_spike[0].timestamps
        else:
            self.spike = None
            self.spike_time = None

        self.conc_files = conc_files()
        self.icons = Button_icons()
        self.event_adder = event_storage(self)

        self.start_x = tk.StringVar()
        self.end_x = tk.StringVar()


        self.x1 = X1
        self.zoom = Zoom
        self.cur_spike = None

        self.chan_frame = tk.Frame(root)
        self.plot_frame = tk.Frame(root)

        self.figure = None
        self.canvas = None
        

        self.grid_on = BooleanVar()
        self.plot_color = StringVar()
        self.plot_line_color = []

        for i in range(0,len(self.data) ):
            s= StringVar()
            s.set('white')
            self.plot_line_color.append(s)

        self.check_grid = None
        self.plot_color_select = None
        self.plot_line_color_select = [None] * len(self.data)

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

        self.next_spike_button = Button(self.chan_frame, text="next spike", command=self.next_spike,
                                image = self.icons.next_spike)
        self.last_spike_button = Button(self.chan_frame , text="last spike", command=self.last_spike,
                                image = self.icons.last_spike )

        self.concatanate_button  = Button(self.chan_frame, text = "concatanate", image = self.icons.concatanate ,
                                    command = self.concatanate_data )

        self.export = Button(self.chan_frame, text="export to NWB", command=self.export_nwb,
                                image = self.icons.export)
        self.save_button = Button(self.chan_frame, text="save file", command=self.save_nwb,
                                image = self.icons.save)

        self.settings_button = Button(self.chan_frame, text="settings", command=self.settings,
                                image = self.icons.settings)

        self.event_button = Button(self.chan_frame, text="add event", command=self.add_event,
                                image = self.icons.event)

        self.start_x_entry = Entry(self.chan_frame, textvariable=self.start_x)
        self.end_x_entry = Entry(self.chan_frame, textvariable=self.end_x)


        self.grid_on.set(True)

        self.chan_frame.pack(side=TOP )
        self.plot_frame.pack(side=TOP )

        self.root.bind( '<Button-1>', self.initial_pos )
        self.root.bind( '<B1-Motion>', self.final_pos )

    def add_event(self):

        if( self.event_adder.event_flag[0] ):
            self.event_adder.event_flag[0] = False
            cur_data = []
            norm = self.zoom/(self.event_adder.borders[1] - self.event_adder.borders[0])
            x1 = int(self.event_adder.event_markers[0] * norm) +self.x1
            x2 = int(self.event_adder.event_markers[1] * norm) +self.x1

            for dat in self.data:

                cur_data.append( dat[x1 : x2 ] )

            self.event_adder.cur_data = cur_data

            event_win = Toplevel(self.root)
            event_win.title("Concatenate")
            event_win.geometry("250x100")

            save_button = Button( event_win , text="save concatanted file", 
                                    command=self.event_adder.save,
                                    image = self.icons.save)
            name = Entry( event_win , textvariable=self.event_adder.event_name)
            description = Entry( event_win , textvariable=self.event_adder.event_desc)
            name_label = Label(event_win, text="event name")
            description_label = Label(event_win, text="event description")

            name.grid(row=0, column=1)
            description.grid(row=1, column=1)
            name_label.grid(row=0, column=0)
            description_label.grid(row=1, column=0)

            save_button.grid(row=2, column=1)
        
        
        self.event_adder.event_flag[0] = ~self.event_adder.event_flag[0]

    def clear_space(self): #new
        self.canvas._tkcanvas.destroy()

    def set_color(self):
        self.plot(True, None)
    
    def zoom_o(self):

        self.zoom *= 2
        if self.x1 + self.zoom >= self.data[0].size - 1:
            self.zoom = self.data[0].size  - self.x1 - 1
        self.plot(True, None  )

    def zoom_i(self):

        self.zoom = int(self.zoom/2)
        if self.zoom < 10:
            self.zoom = 10

        self.plot(True, None  )
    
    def pan_right(self):
        
        self.x1 += int(self.zoom/2)
        if self.x1 >= self.data[0].size - 1 - self.zoom:
            self.x1 = self.data[0].size  - 1 - self.zoom
        self.plot(True, None  )
    
    def next_spike(self):
        if self.spike is not None:
            for spike, time_stamp in zip(  np.array(self.spike) , np.array(self.spike_time)  ):
                if time_stamp >= self.x1 and self.cur_spike != time_stamp:
                    self.cur_spike = time_stamp
                    self.x1 = int(time_stamp)
                    if self.zoom < 100:
                        self.zoom = 100
                    self.plot(True, spike )
                    return 

        print("no spikes this way")    

    def last_spike(self):
        if self.spike is not None:
            for spike, time_stamp in zip( reversed(np.array(self.spike)) 
                                        , reversed(np.array(self.spike_time)) ):
                if time_stamp < self.x1 and self.cur_spike != time_stamp:

                    self.cur_spike = time_stamp
                    self.x1 = int( time_stamp )

                    if self.zoom < 100:
                        self.zoom = 100

                    self.plot(True, spike  )
                    return 

        print("no spikes this way")   


    def pan_left(self):

        self.x1 -= int(self.zoom/2)
        if self.x1 < 0:
            self.x1 = 0
        self.plot(True, None  )
    
    def trunc_set(self):

        self.x1 = int(self.start_x.get())
        self.zoom = int(self.end_x.get()) - int(self.x1)

        if self.x1 < 0:
            self.x1 = 0
        elif self.x1 >= self.data[0].size  - 1 - self.zoom:
            self.x1 = self.data[0].size  - 1 - self.zoom

        self.plot(True, None  )

    def export_nwb(self):
        files = [('NWB Files', '*.nwb'), ('All Files', '*.*')]
        file = tk.filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        convert_ephys_nwb(self.nwb_obj, str(file.name) )

    def save_nwb(self):

        self.io.write( self.nwb_obj )
        self.io.close()
        self.io = NWBHDF5IO( self.root_path , 'a')
        self.nwb_obj = self.io.read()

    def initial_pos(self, event):

        if self.event_adder.event_flag[0] and event.y > self.event_adder.borders[2]:
            self.event_adder.event_markers[0] = max(event.x - self.event_adder.borders[0], 0)

    def final_pos(self, event):
        if self.event_adder.event_flag[0]:
            self.event_adder.event_markers[1] = min(event.x - self.event_adder.borders[0], 
                                    self.event_adder.borders[1] - self.event_adder.borders[0] )
            if self.event_adder.event_markers[1] < self.event_adder.event_markers[0]:
                self.event_adder.event_markers[1] = self.event_adder.event_markers[0]+1

            self.event_adder.event_flag[1]  = True
            self.plot(True, None)


    def concatanate_data(self):

        conc_win = Toplevel(self.root)
        conc_win.title("Concatenate")
        conc_win.geometry("400x100")

        file1_button = Button( conc_win , text="selct file 1", command=self.select_file1,
                                image = self.icons.file1)
        file2_button = Button( conc_win , text="select file 2", command=self.select_file2,
                                image = self.icons.file2)
        metadata_button = Button( conc_win , text="select metadat file", command=self.select_metadata,
                                image = self.icons.metadata)
        save_button = Button( conc_win , text="save concatanted file", 
                                command=self.conc_files.concatanate,
                                image = self.icons.export)

        x11_entry = Entry( conc_win , textvariable=self.conc_files.x11)
        x12_entry = Entry( conc_win , textvariable=self.conc_files.x12)

        x21_entry = Entry( conc_win , textvariable=self.conc_files.x21)
        x22_entry = Entry( conc_win , textvariable=self.conc_files.x22)

        file_start = Label(conc_win, text="file start")
        file_end = Label(conc_win, text="file end")

        file1_button.grid(row=0, column=2)
        file2_button.grid(row=0, column=3)

        file_start.grid(row=1, column=0)
        file_end.grid(row=2, column=0)

        metadata_button.grid(row=1, column=4)
        save_button.grid(row=2, column=4)

        x11_entry.grid(row=1, column=2)
        x12_entry.grid(row=2, column=2)
        x21_entry.grid(row=1, column=3)
        x22_entry.grid(row=2, column=3)

    def settings(self): 

        conc_win = Toplevel(self.root)
        conc_win.title("Settings")
        conc_win.geometry("1000x400")

        channel_color_label = [None] * len(self.data)

        color_options = ["black", "blue", "white", "green", "red"] 
        self.check_grid = Checkbutton( conc_win, text="grid", variable=self.grid_on)
        self.plot_color_select = OptionMenu( conc_win , self.plot_color,
                                    *color_options )
        plot_color_label = Label( conc_win, text="plot background color" )
        save_button = Button( conc_win , text="save", command=self.set_color )

        self.check_grid.grid(row=0, column=1)
        plot_color_label.grid(row=1, column=0)
        self.plot_color_select.grid(row=1, column=1)

        for i in range(0, len(self.data)):
            self.plot_line_color_select[i] = OptionMenu( conc_win , self.plot_line_color[i],
                                    *color_options )
            channel_color_label[i] = Label( conc_win, text=f"channel {i} plot color" )

            self.plot_line_color_select[i].grid(row= 2+i, column=1 )
            channel_color_label[i].grid(row=2+i, column=0)

        self.check_grid.grid_on = self.grid_on
        save_button.grid(row= 2+len(self.data) , column=1)

    def select_file1(self):
        filetypes = (
            ('nwb files', '*.continuous'),
            ('All files', '*.*')
        )

        filename = tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        self.conc_files.file1 = filename

    def select_file2(self):
        filetypes = (
            ('nwb files', '*.continuous'),
            ('All files', '*.*')
        )

        filename = tk.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)

        self.conc_files.file2 = filename

    def select_metadata(self):
        filetypes = (
            ('nwb files', '*.txt'),
            ('All files', '*.*')
        )

        filename = tk.filedialog.askopenfilename(
            title='select metadata file',
            initialdir='/',
            filetypes=filetypes)

        self.conc_files.metadata = filename

    def plot(self, erase_bool, spike):
        start = time.time()

        if erase_bool == True:
            self.clear_space()
        else:

            start_label = Label(self.chan_frame, text="data start")
            end_label = Label(self.chan_frame, text="data end")

            start_label.grid(row=0, column=0)
            end_label.grid(row=1, column=0)
            self.set_plot_window.grid(row=0, column=2)
            self.zoom_button.grid(row=0, column=3)
            self.zoom_in_button.grid(row=0, column=4)
            self.pan_left_button.grid(row=0, column=5)
            self.pan_right_button.grid(row=0, column=6)
            self.clear_button.grid(row=0, column=7)
            self.last_spike_button.grid( row=0, column=8 )
            self.next_spike_button.grid( row=0, column=9 )
            self.concatanate_button.grid( row=0, column=10 )
            self.settings_button.grid( row=0, column=11 )
            self.event_button.grid( row=0, column=12 )
            if self.from_ephys:
                self.export.grid(row=1, column=2)
            else:
                self.save_button.grid(row=1, column=2)


            self.start_x_entry.grid(row=0, column=1)
            self.end_x_entry.grid(row=1, column=1)

        s2 = time.time()

        self.figure = Figure(figsize=(15, 12)) 
        self.canvas = FigureCanvasTkAgg( self.figure , master=self.plot_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)
        a = self.figure.add_subplot(111)
        a.set_facecolor( 'xkcd:' + self.plot_color.get() )

        if bool(self.grid_on.get()):
            a.grid(color = 'brown')

        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        a.spines['bottom'].set_visible(False)
        a.spines['left'].set_visible(False)


        for i, dat in enumerate(self.data):
            a.plot( np.linspace(self.x1, self.zoom + self.x1, self.zoom ),
                dat[ self.x1 : self.zoom + self.x1 ] , color = str(self.plot_line_color[i].get()) )
            
            if self.event_adder.event_flag[1] :
                norm = self.zoom/(self.event_adder.borders[1] - self.event_adder.borders[0])
                x1 = int(self.event_adder.event_markers[0] * norm) +self.x1
                x2 = int(self.event_adder.event_markers[1] * norm) +self.x1
                
                a.axvline( x1 , linewidth=3.0 )
                a.axvline( x2 , linewidth=3.0 )

            if spike is not None:
                sam_len = spike.shape[0]
                a.plot( np.linspace(self.x1, sam_len + self.x1, sam_len ),
                dat[ self.x1 : sam_len + self.x1 ],  linewidth=5.0 , color = str(self.plot_line_color[i].get())  )

        s3 = time.time()
        
        self.canvas.draw()

        s4 = time.time()

        

        

class GUI:
    def __init__(self, window):
        self.window = window

        self.window.geometry("1000x500")
        self.icons = Button_icons()
        self.channels = None

        self.is_there_plot = False

        self.plot_button = Button( window , text="Plot", image = self.icons.plot, command=self.plot)
        self.file_select = Button( window, text="Select NWB File",image = self.icons.nwb, command=self.select_file)
        self.folder_select = Button( window, text="Select OPhys directory File",image = self.icons.ephys, command=self.select_ophys)

        self.file_select.pack(side=LEFT, anchor=NW)
        self.folder_select.pack(side=LEFT, anchor=NW)

    def plot(self):

        cur_plot = self.channels

        self.file_select.destroy()
        self.folder_select.destroy()
        self.plot_button.destroy()
        
        cur_plot.plot(self.is_there_plot, None)
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

        dat, nwbfile, io = open_file(filename)

        s = np.array(dat['spikes']) 
        if len(s) == 0:
            s = None
        self.channels = Channel_window( self.window, dat['continuous'], 0, 100, False, filename,
                                        s, nwbfile, io)
        
        
        self.plot_button.pack(side=LEFT, anchor=NW)


    def select_ophys(self):

        filename = tk.filedialog.askdirectory(parent=root,initialdir="/",
                    title='Please select a directory')

        dat, nwbfile = open_ephys_dir(filename)

        s = np.array(dat['spikes']) 
        if len(s) == 0:
            s = None

        self.channels = Channel_window( self.window, dat['continuous'], 0, 100, True, filename,
                                        s, nwbfile, None)

        self.plot_button.pack(side=LEFT, anchor=NW)



root = Tk() #new
root.title("xCELLeration time series viewer")
my_mclass = GUI(root) #new
root.mainloop() #new