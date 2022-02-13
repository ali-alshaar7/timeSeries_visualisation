from pynwb import NWBHDF5IO
import sys
import os
sys.path.insert(1, 'OpenEphys_to_NWB')
from OpenEphys_to_NWB import openephys2nwb, OpenEphys
from OpenEphys import load
from openephys2nwb import convertOpenEphystoNWB

def open_file(dir):
    io = NWBHDF5IO( dir , 'r')
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

    return data

def open_ephys_dir(dir):

    data = {}
    cont = []
    spikes = []
    spike_time = []

    for files in os.listdir(dir):
        if files.endswith('.continuous'):

            r = load(os.path.join(dir, files))
            cont.append( r['data'] )
        elif files.endswith('.spikes'):

            r = load(os.path.join(dir, files))
            spikes.append( r['spikes'] )
            spike_time.append( r['timestamps'] )

    data['continuous'] = cont
    data['spikes'] = spikes
    data['spike_time'] = spike_time

    return data

def convert_ephys_nwb(src, save_path):
    io = NWBHDF5IO( save_path, mode='w')
    io.write(convertOpenEphystoNWB(src))
    io.close()