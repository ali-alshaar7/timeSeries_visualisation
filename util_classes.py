import tkinter as tk
from pynwb import NWBFile, TimeSeries, NWBHDF5IO, ecephys
from pynwb.file import Subject

from OpenEphys_to_NWB import openephys2nwb, OpenEphys , defaults
from OpenEphys import load
from defaults import default_metadata
from openephys2nwb import readMetaData

from tkinter import *
import numpy as np 

from dateutil import parser
import json
from datetime import datetime
import itertools
import os


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

class event_storage:
    def __init__( self, parent ):
        self.event_flag = [ False, False ]
        self.borders = [125, 900, 50]
        self.event_markers = [ 0, 0  ]
        self.cur_data = []
        self.event_name = tk.StringVar()
        self.event_desc = tk.StringVar()
        self.parent = parent

    def save(self):
        norm = self.parent.zoom/(self.borders[1] - self.borders[0])
        x1 = int(self.event_markers[0] * norm)
        x2 = int(self.event_markers[1] * norm)

        it_series = TimeSeries(name = self.event_name.get(), data =  self.cur_data
                                                ,timestamps = np.linspace(x1 +self.parent.x1, 
                                                x2 + self.parent.x1 , x2-x1 ), unit = 'v', 
                                                description = self.event_desc.get() )

        self.parent.nwb_obj.add_acquisition(it_series )