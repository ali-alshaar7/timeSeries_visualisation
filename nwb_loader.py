from pynwb import NWBHDF5IO
import sys
import os
sys.path.insert(1, 'OpenEphys_to_NWB')
from OpenEphys_to_NWB import openephys2nwb, OpenEphys
from OpenEphys import load
from openephys2nwb import convertOpenEphystoNWB

def open_file(dir):
    io = NWBHDF5IO( dir , 'a')
    nwbfile = io.read()

    ephys_ts = nwbfile.acquisition

    data = {}
    cont = []
    spikes = []

    for f in ephys_ts:
        if f.split('_')[0] == 'continuous':
            cont.append(ephys_ts[f].data)
        else:
            spikes.append(ephys_ts[f])

    data['continuous'] = cont
    data['spikes'] = spikes

    return data, nwbfile, io

def open_ephys_dir(dir):

    nwbfile = convertOpenEphystoNWB(dir)

    ephys_ts = nwbfile.acquisition

    data = {}
    cont = []
    spikes = []

    for f in ephys_ts:
        if f.split('_')[0] == 'continuous':
            cont.append(ephys_ts[f].data)
        else:
            spikes.append(ephys_ts[f])

    data['continuous'] = cont
    data['spikes'] = spikes

    return data, nwbfile

def convert_ephys_nwb( nwbfile , save_path):
    io = NWBHDF5IO( save_path, mode='w')
    io.write( nwbfile )
    io.close()