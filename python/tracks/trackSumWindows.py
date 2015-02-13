#!/usr/bin/env python

import sys
import argparse
import tables as tb
import numpy as np
import re
import pdb
import track_util as tutil

class trackProcess:
    def __init__(self, in_track, out_track):
        self.in_track = in_track
        self.out_track = out_track
        self.norm_factor = 0
        
    # Find minimum nonzero value
    # Use reciprocal to convert float values to integers
    # Return transformed, rounded, and integer type converted array
    def int_normalize(self, input_array):
        if self.norm_factor == 0:
            no_zero_array = input_array[input_array[:] > 0]
            curr_min = np.min(no_zero_array)
            self.norm_factor = 1.0 / curr_min 
        return np.round(np.multiply(input_array[:], self.norm_factor)).astype(np.int16)
    
    def sum_windows(self, input_array, step):
        ind = np.arange(0, len(input_array), step)
        out_array = 
        for i in ind:
            
    def run(self):
        out_track_name = self.in_track._v_name
        print out_track_name
        
        test = tutil.checkIfNodeExists(self.out_track, out_track_name)
        if test: return
        
        for chr in self.in_track._f_iterNodes():
            chr_name = chr._v_name
            print chr_name
            track_chr = self.in_track._f_getChild(chr_name)
            
            out_track_chr = self.int_normalize(track_chr)
            
            self.out_track.createArray("/" + out_track_name, chr_name, out_track_chr)
            for name in track_chr._v_attrs._f_list():
                self.out_track.setNodeAttr("/" + "/".join([out_track_name, chr_name]), name, track_chr._v_attrs[name])
    
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='track', help='input track')
    parser.add_argument('-n', dest='subtrack', help="subtrack name. Input 'all' to process all subtracks")
    parser.add_argument('-o', dest='out_name', help='out track file')    
    args = parser.parse_args()
    
    track_file = tb.openFile(args.track)
    out_file = tb.openFile(args.out_name, 'a')
    subtrack_name = args.subtrack
   
    if subtrack_name == "all":
        for subtrack in track_file.iterNodes("/"):
            processor = trackProcess(subtrack, out_file)
            processor.run()
    else:
        subtrack = track_file.getNode("/" + subtrack_name)
        processor = trackProcess(subtrack, out_file)
        processor.run()

    out_file.flush()    
    out_file.close()
    
if __name__ == '__main__':
    main(sys.argv)
