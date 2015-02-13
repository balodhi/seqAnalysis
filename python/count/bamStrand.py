#!/usr/bin/env python

import sys
import os
import argparse
import pysam
import pdb
import BAMtoWIG as b2w
from subprocess import Popen

def splitByStrand(bamfile, pe):
    
    bam_prefix = bamfile.split(".bam")[0]
    #pdb.set_trace()
    if pe:
        flags = [('-f 0x42', '-F 0x10', 'plus'), ('-f 0x42', '-F 0x20', 'minus')]
        cmd_args = [['samtools', 'view',
                 '-b', flag[0], flag[1], bamfile,
                 bam_prefix + "_" + flag[2] + ".bam"]for flag in flags]
    else:
        flags = [('-F 0x10', 'plus'), ('-f 0x10', 'minus')]
        cmd_args = [['samtools', 'view',
                 '-b', flag[0], bamfile,
                 bam_prefix + "_" + flag[1] + ".bam"]for flag in flags]
    
    
    
    for cmd_arg in cmd_args:
       # pdb.set_trace()
        print cmd_arg
        if os.path.exists(cmd_arg[len(cmd_arg)-1]): 
            continue
        outfile = open(cmd_arg[len(cmd_arg)-1], 'w')
        p = Popen(cmd_arg[:(len(cmd_arg)-1)], stdout=outfile)
        p.wait()
        pysam.index(cmd_arg[len(cmd_arg)-1])
    
    # Return split BAM names
    return([cmd_arg[len(cmd_arg)-1] for cmd_arg in cmd_args])

def loadTrack(split_bam, outfile):
    
    for bam in split_bam:
        bam_prefix = bam.split(".bam")[0]
        cmd_args = ['ReadStartPileup', '-b', bam,
                    '-o', outfile,
                    '-t', bam_prefix,
                    '-p', '1']
        p = Popen(cmd_args)
        p.wait()

def wig2Track(wig, track, window):
    cmd_args = ['LoadData', '-i', wig,
                '-o', track,
                '-t', wig.split(".wig")[0],
                '-n', window,
                '-g', '/media/storage2/genomedata/chromosomes.trk']
    p = Popen(cmd_args)
    p.wait()
    
    
def main(argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="bamfile")
    parser.add_argument('-o', dest='outfile')
    parser.add_argument('-w', dest='window')
    parser.add_argument('-e', dest="extend", default=0)
    parser.add_argument('--paired-end', dest="pe", action="store_true")
    args = parser.parse_args()
    
    # Split BAM by strand 
    split_bam = splitByStrand(args.bamfile, args.pe)
    
    # Split BAM to Wig
    for bam in split_bam:
        print "BAM to WIG..."
        print bam
        w = b2w.windower(bam, bam.split(".bam")[0] + ".wig", args.window, args.extend, args.pe, "", "", "", "")
        w.window()
        
    #Wig to Track
    for bam in split_bam:
        print "WIG to Track..."
        print bam
        wig2Track(bam.split(".bam")[0] + ".wig", args.outfile, args.window)
        
if __name__ == '__main__':
    main(sys.argv)
