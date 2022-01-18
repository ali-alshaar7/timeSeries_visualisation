from pynwb import NWBHDF5IO

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
            spikes.append(ephys_ts[f].data)

    data['continuous'] = cont
    data['spikes'] = spikes
    return data
