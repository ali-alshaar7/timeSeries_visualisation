
import numpy as np #new
from PIL import Image, ImageTk
import os

proj_root_dir = os.path.dirname(os.path.abspath(__file__))

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

        self.settings = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "settings.png") ).resize((20,20), resample = Image.BILINEAR) ) 
        self.event = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "event.png") ).resize((20,20), resample = Image.BILINEAR) ) 

        self.save = ImageTk.PhotoImage(Image.open( os.path.join(self.root, "save.png") ).resize((20,20), resample = Image.BILINEAR) ) 