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
import numpy as np #new
from PIL import Image, ImageTk

from OpenEphys_to_NWB import openephys2nwb, OpenEphys, defaults
from OpenEphys import load
from defaults import default_metadata
from openephys2nwb import readMetaData

import time

proj_root_dir = r"C:\Users\alish\Desktop\current_year\xcelleration\ts_visualisation"

class Button_icons:
    def __init__( self ):
        self.root = os.path.join(proj_root_dir, "images\icons")
        self.zoom_in = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "zoom_in.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.zoom_out = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "zoom_out.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        
        self.pan_right =ImageTk.PhotoImage(Image.open( os.path.join(self.root, "pan_right.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.pan_left = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "pan_left.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.truncate = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "truncate.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.plot = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "plot.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        
        self.clear = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "clear.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.export = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "export.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.ephys = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "ephys.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.nwb = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "nwb.jpg") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.last_spike =ImageTk.PhotoImage(Image.open( os.path.join(self.root, "last_spike.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.next_spike = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "next_spike.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.concatanate = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "concatanate.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.file1 = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "file1.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.file2 = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "file2.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.metadata = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "metadata.png") ).resize((20,20), resample = Image.BILINEAR) ) 

class conc_files:
    def __init__( self ):
        self.file1 = None
        self.file2 = None
        self.metadata = None
        self.x11 = tk.StringVar()
        self.x12 = tk.StringVar()
        self.x21 = tk.StringVar()
        self.x22 = tk.StringVar()

    def concatanate(self):
        r = load(self.file1)
        r2 = load(self.file2)['data']
        
        r_x11 = int(float(str(self.x11.get())))
        r_x12 = len(r['data']) - 1
        r_x21 = int(float(str(self.x21.get())))
        r_x22 = len(r2) - 1

        if str(self.x12.get()).lower() != "max":
            r_x12 = int(float(str(self.x12.get())))
        if str(self.x22.get()).lower() != "max":
            r_x22 = int(float(str(self.x22.get())))

        dat = TimeSeries(name = ( os.path.basename(self.file1) ).split('.')[0],  
                        data = np.concatenate((r['data'][r_x11:r_x12] ,
                        r2[ r_x21:r_x22]), axis=0),   unit = 'V',
                        starting_time=0.0, rate=float(r['header']['sampleRate']),
                        conversion=r['header']['bitVolts'])


        metadata = {}
        if self.metadata is not  None:
            metadata = readMetaData( self.metadata )
        else:
            metadata = default_metadata
            metadata['file_electrodes'][str(os.path.basename(self.file1)) ] = [0]

        create_date = datetime.now()

        nwbfile = NWBFile( str(metadata['session']['description']) , 'NWB_out', 
                      parser.parse(metadata['session']['start_time']),
                      file_create_date = create_date )

        device = nwbfile.create_device(name = str(metadata['session']['device_name']) )

        electrode_name = str(metadata['electrode_group']['name'])
        description = str(metadata['electrode_group']['description'])
        location = str(metadata['electrode_group']['location'])

        electrode_group = nwbfile.create_electrode_group(electrode_name,
                                                        description=description,
                                                        location=location,
                                                        device=device)

        for electrode_metadata in metadata['electrode_metadata']:
            nwbfile.add_electrode(id= int(electrode_metadata['id']),
                                x= float(electrode_metadata['x']), 
                                y= float(electrode_metadata['y']), 
                                z= float(electrode_metadata['z']),
                                imp= float(electrode_metadata['impedance']),
                                location= str(electrode_metadata['location']), 
                                filtering=  str(electrode_metadata['filtering']),
                                group=electrode_group)

        electrode_table_region = nwbfile.create_electrode_table_region( 
                                      json.loads(metadata['file_electrodes'][str(os.path.basename(self.file1) )]) 
                                      , str(os.path.basename(self.file1))+' electrodes' )

        cont_dat = ecephys.ElectricalSeries(name = "continuous_"+r['header']['channel'],
                                                data = dat,
                                                electrodes = electrode_table_region,
                                                rate=float(r['header']['sampleRate'] )  )

        nwbfile.add_acquisition(cont_dat )

        files = [('NWB Files', '*.nwb'), ('All Files', '*.*')]
        file = tk.filedialog.asksaveasfile(filetypes = files, defaultextension = files)

        io = NWBHDF5IO( str(file.name), mode='w')
        io.write(nwbfile)
        io.close()



class Channel_window:
    def __init__(self,root, dat, X1, Zoom, from_ephys, dir , spike, spike_time):

        self.from_ephys = from_ephys
        self.root = root
        self.root_path = dir

        self.big_data = dat
        self.big_spike = spike
        self.big_spike_time = spike_time

        if from_ephys == False:
            self.data = self.big_data
            if self.big_spike is not None:
                self.spike = self.big_spike[0].data
                self.spike_time = self.big_spike_time[0].timestamps
            else:
                self.spike = None
                self.spike_time = None
        else:
            self.data = self.big_data
            if self.big_spike is not None:
                self.spike = self.big_spike[0]
                self.spike_time = self.big_spike_time[0]
            else:
                self.spike = None
                self.spike_time = None

        self.conc_files = conc_files()

        self.start_x = tk.StringVar()
        self.end_x = tk.StringVar()

        self.x1 = X1
        self.zoom = Zoom
        self.cur_spike = None

        self.icons = Button_icons()

        self.chan_frame = tk.Frame(root)
        self.plot_frame = tk.Frame(root)
        self.figure = None
        self.canvas = None
        

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

        self.next_spike_button = Button(self.chan_frame, text="next spike", command=self.next_spike,
                                image = self.icons.next_spike)
        self.last_spike_button = Button(self.chan_frame , text="last spike", command=self.last_spike,
                                image = self.icons.last_spike )

        self.concatanate_button  = Button(self.chan_frame, text = "concatanate", image = self.icons.concatanate ,
                                    command = self.concatanate_data )

        self.export = Button(self.chan_frame, text="export to NWB", command=self.export_nwb,
                                image = self.icons.export)

        self.start_x_entry = Entry(self.chan_frame, textvariable=self.start_x)
        self.end_x_entry = Entry(self.chan_frame, textvariable=self.end_x)

        color_options = ["black", "blue", "white", "green"] 
        self.check_grid = Checkbutton(self.chan_frame, text="grid", variable=self.grid_on, command=self.set_grid)
        self.plot_color_select = OptionMenu( self.chan_frame , self.plot_color,
                                    *color_options , command = self.set_color)

        self.plot_frame.bind('<B1-Motion>', self.position )

        self.grid_on.set(True)
        self.check_grid.grid_on = self.grid_on

        self.chan_frame.pack(side=TOP )
        self.plot_frame.pack(side=TOP )

    def clear_space(self): #new
        self.canvas._tkcanvas.destroy()

    def set_color(self, event):
        self.plot(True, None)

    def set_grid(self):
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
                print(spike.shape, time_stamp)
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

        convert_ephys_nwb(self.root_path, str(file.name) )

    def position(self, event):
        print(event.x)

    def concatanate_data(self):

        conc_win = Toplevel(self.root)
        conc_win.title("New Window")
        conc_win.geometry("300x300")

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

        file1_button.grid(row=0, column=1)
        file2_button.grid(row=0, column=2)
        metadata_button.grid(row=0, column=3)
        save_button.grid(row=0, column=4)
        x11_entry.grid(row=1, column=1)
        x12_entry.grid(row=2, column=1)
        x21_entry.grid(row=1, column=2)
        x22_entry.grid(row=2, column=2)

    
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
            self.set_plot_window.grid(row=0, column=1)
            self.zoom_button.grid(row=0, column=2)
            self.zoom_in_button.grid(row=0, column=3)
            self.pan_left_button.grid(row=0, column=4)
            self.pan_right_button.grid(row=0, column=5)
            self.clear_button.grid(row=0, column=6)
            self.plot_color_select .grid( row=0, column=7 )
            self.check_grid.grid(row=0, column=8)
            self.last_spike_button.grid( row=0, column=9 )
            self.next_spike_button.grid( row=0, column=10 )
            self.concatanate_button.grid( row=0, column=11 )
            if self.from_ephys:
                self.export.grid(row=1, column=1)


            self.start_x_entry.grid(row=0, column=0)
            self.end_x_entry.grid(row=1, column=0)

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


        for dat in self.data:
            a.plot( np.linspace(self.x1, self.zoom + self.x1, self.zoom ),
                dat[ self.x1 : self.zoom + self.x1 ] )

            if spike is not None:
                sam_len = spike.shape[0]
                a.plot( np.linspace(self.x1, sam_len + self.x1, sam_len ),
                dat[ self.x1 : sam_len + self.x1 ],  linewidth=5.0 )
        '''
        if spike is not None:
            sam_len = spike.shape[0]
            print(sam_len)
            for dat in np.swapaxes(spike, 0,1):
                print(dat)
                a.plot( np.linspace(self.x1, sam_len + self.x1, sam_len ),
                    dat , linewidth=5.0 )
        '''
        s3 = time.time()
        
        self.canvas.draw()

        s4 = time.time()

        #print(s1 - start, s2 - s1, s3-s2, s4-s3)
        

        

class GUI:
    def __init__(self, window):
        self.window = window

        self.window.geometry("1000x500")
        self.icons = Button_icons()
        self.channels = None

        self.channel_option = tk.IntVar()
        self.channel_option.set("0")
        self.channel_options = [0]
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

        dat = open_file(filename)
        self.channel_options = np.linspace(0, len( dat['continuous']) - 1 ,  
                               len( dat['continuous']) ).tolist()

        s = np.array(dat['spikes']) 
        if len(s) == 0:
            s = None
        self.channels = Channel_window( self.window, dat['continuous'], 0, 100, False, filename,
                                        s, s )
        
        
        self.plot_button.pack(side=LEFT, anchor=NW)


    def select_ophys(self):

        filename = tk.filedialog.askdirectory(parent=root,initialdir="/",
                    title='Please select a directory')
        
        dat = open_ephys_dir(filename)
        self.channel_options = np.linspace(0, len( dat['continuous']) - 1 ,  
                               len( dat['continuous']) ).tolist()

        s = np.array(dat['spikes']) 
        t = np.array(dat['spike_time'])
        if len(s) == 0:
            s = None
        if len(t) == 0:
            t = None
        self.channels = Channel_window( self.window, dat['continuous'] , 0, 100, True, filename,
                                        s, t )
        self.plot_button.pack(side=LEFT, anchor=NW)



root = Tk() #new
root.title("xCELLeration time series viewer")
my_mclass = GUI(root) #new
root.mainloop() #new