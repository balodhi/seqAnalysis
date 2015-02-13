#! /usr/bin/env python

import os, sys
import pysam
import bam2bed
import sam
import argparse
import BAMtoWIG
import pdb
from subprocess import Popen

fastq_dir = "/media/storage3/data/fastq"
#bam_dir = "/media/storage2/data/rna/tophat"
bam_dir = "/home/user/data/rna/tophat"
wig_dir = "/media/storage2/data/wig"

class tophat_class:
    def __init__(self, date, sample, single_end, index, mean, sd, gtf, library_type, species):
        self.date = date
        #self.sample = sample.split("_")[1]
        self.sample = sample
        self.single_end = single_end
        self.index = index
        self.input_prefix = index[1]
        self.input1 = ""
        self.input2 = ""
        if single_end:
            self.input1 = "/".join([fastq_dir, date, sample, index[0],
                                    "_".join([self.sample, '1.fastq'])])
        else:
            #print self.sample
            self.input1 = "/".join([fastq_dir, date, sample, index[0], 
                                    "_".join([self.sample, '1.fastq'])])
            self.input2 = "/".join([fastq_dir, date, sample, index[0], 
                                    "_".join([self.sample, '3.fastq'])])
        self.mean = mean
        self.sd = sd
        self.gtf = gtf
        self.library_type = library_type
        self.species = species
        self.to_map = True
        #self.samfile = "/".join([sam_dir, self.date, "".join([self.input_prefix, ".sam"])])
        #pdb.set_trace()
        self.output = "/".join([bam_dir, self.date, self.input_prefix])
        if os.path.exists(self.output):
            dec = raw_input("Output file exists. Bypass mapping [y/n]? ")
            if dec == 'y': self.to_map = False
        else: os.makedirs(self.output)
        self.errorlog = "/".join([self.output, "error_log"])
        #self.unmapped = "/".join([bam_dir, self.date, "".join([self.input_prefix, "_unaligned"])])
        #self.bamfile = "/".join([bam_dir, self.date, "".join([self.input_prefix, ".bam"])])
        #sam_dir_date = "/".join([sam_dir, self.date])
        #if not os.path.exists(sam_dir_date): os.mkdir(sam_dir_date)
        #bam_dir_date = "/".join([bam_dir, self.date])
        #if not os.path.exists(bam_dir_date): os.mkdir(bam_dir_date)

    def map(self):        
        if self.to_map:
            if self.single_end:
                if self.gtf != 'blank': 
                    cmd_args = ['tophat', '-p', '6', '-o', self.output, 
                        '-r', self.mean, '--mate-std-dev', self.sd, 
                        '-G', self.gtf, '--library-type', self.library_type, 
                        self.species, self.input1]
                else:
                    cmd_args = ['tophat', '-p', '6', '-o', self.output, 
                        '-r', self.mean, '--mate-std-dev', self.sd,
                        '--library-type', self.library_type,
                        self.species, self.input1]
            else:
                if self.gtf != 'blank': 
                    cmd_args = ['tophat', '-p', '10', '-o', self.output, 
                        '-r', self.mean, '--mate-std-dev', self.sd, 
                        '-G', self.gtf, '--library-type', self.library_type, 
                        self.species, self.input1, self.input2]
                else:
                    cmd_args = ['tophat', '-p', '10', '-o', self.output, 
                        '-r', self.mean, '--mate-std-dev', self.sd,
                        '--library-type', self.library_type,
                        self.species, self.input1, self.input2]
            #print self.errorlog
            print "Mapping with tophat: " + " ".join(cmd_args[1:])
            errorlog = open(self.errorlog, 'a')
            try:
                tophat = Popen(cmd_args, stderr=errorlog)
                tophat.wait()
            except:
                return
            errorlog.close()
            #bam.proc([self.output + "/accepted_hits.bam", "False"])
            
    def wig(self):
        window_size = str(200)
        bamname = "/".join([self.output, "accepted_hits_sort.bam"])
        wigdir = "/".join([wig_dir, self.input_prefix])
        if not os.path.exists(wigdir): os.makedirs(wigdir)
        wigfile = "/".join([wigdir, "_".join([self.input_prefix, window_size]) + ".wig"])
        extend = self.mean
        pe = not self.single_end
        wi = BAMtoWIG.windower(bamname, wigfile, window_size, extend, pe)
        print "Writing WIG..."
        wi.window()
        wi.wigfile.close()
        wi.tdf()
        
def tophat(date, sample, single_end, index, mean, sd, gtf, library_type, species):
    #print "here"
    print sample
    tophat_obj = tophat_class(date, sample, single_end, index, mean, sd, gtf, library_type, species)
    tophat_obj.map()
    #tophat_obj.wig()
    #tophat_obj.sam2bam()
    
def main(argv):
     
    parser = argparse.ArgumentParser(description="Run tophat on given fastq files.\nOutputs to " + bam_dir)
    parser.add_argument('-d', dest='date')
    parser.add_argument('-i', '--input_fastq', nargs='+', metavar='fastq', required=True, 
                        dest='fastq_files', help='read1 and read3 of library')
    
    parser.add_argument('-n', '--index', dest='index', required=False, help='index number of library')
    parser.add_argument('-r', '--mate-inner-dist', metavar='mean', required=True, 
                        dest='mean', help='mean size of library (minus adaptors)')
    parser.add_argument('-s', '--mate-std-dev', metavar='sd', required=True, dest='sd', help='standard deviation of library')
    parser.add_argument('-g', '--GTF', metavar='gtf', dest='gtf', required=False, default='blank',
                        help='reference gtf file to map reads to')
    parser.add_argument('--species', action="store", dest='species', default="mm9", required=False)
    parser.add_argument('--single-end', action='store_true', dest='single_end', default=False)
    parser.add_argument('--stranded', action='store_true', required=False, dest='strand', default=False, help="indicate if library contains strand information")
    parser.add_argument('--rmdup', action='store_true', required=False, dest='rmdup', default=False, help="remove duplicates")
    args = parser.parse_args()
    
    index = str(0)
    if args.index: index = args.index
    index_split = index.split("-")
    #input_prefix = args.fastq_files[0].split('_')[0] + "_" + index[1]
    #input_prefix = index_split[1]
    #output_path =  bam_dir + input_prefix 
    library_type = 'fr-unstranded'
    if args.strand: library_type = 'fr-secondstrand'
    
    tophat(args.date, args.fastq_files[0], args.single_end, index_split, \
           args.mean, args.sd, args.gtf, library_type, args.species)
    
    #bamfile = bam_dir + "/accepted_hits.bam"
    #bamfile = bam_dir + input_prefix + "/accepted_hits.bam"
    #sam.sam2bam(samfile, bamfile) 
    #sam.proc(bamfile, args.rmdup)
    
    #bam = output_path + input_prefix + "a.bam"
    #bed = bed_dir + input_prefix + ".bed"
    #sam.bam2bed(bam, bed)

    
if __name__ == "__main__":
    main(sys.argv)
