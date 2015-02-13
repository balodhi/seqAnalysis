#! /usr/bin/env python

import sys
import os
import argparse
import pdb
import re
import tables as tb
import tempfile
import shutil
import warnings
import operator
import pysam
import numpy as np
from math import sqrt
from scipy import stats
from string import atoi, atof
from multiprocessing import Pool

ANNO_PATH = '/home/user/lib/annotations_hires'
#ANNO_PATH = '/home/user/lib/annotations'
FEATURE_PATH = '/home/user/lib/features_general'
SAMPLE_PATH = '/media/storage2/data/h5'
ANNO_OUT_PATH = '/media/storage2/analysis/profiles/norm'
FEATURE_OUT_PATH = '/media/storage2/analysis/features/norm'

class tab:
    def __init__(self, anno, sample, sample_type, bam_attr, fun, type, flank,
                 data_type, split_anno, strand, norm):
        self.anno = anno
        self.sample = sample
        self.sample_type = sample_type
        self.bam_attr = bam_attr
        self.fun = fun
        self.data_type = data_type
        self.split_anno = split_anno
        self.strand = strand
        self.norm = norm
        #self.norm_by_mean = norm_by_mean
        #self.norm_by_mean_zero = norm_by_mean_zero
        #pdb.set_trace()
        if self.norm == "chrom_mean":
#        if self.norm_by_mean: 
            self.fun = "_".join([self.fun, "chrom_mean"])
        elif self.norm == "chrom_mean_zero":
#        if self.norm_by_mean_zero:
            self.fun = "_".join([self.fun, "chrom_mean_0"])
        self.window_size = 1
        
        # Check if mean chromosome values have been computed
        # If so, read them into window_correct dictionary
        #pdb.set_trace()
        self.window_correct = {}
        
        self.norm_path = ".".join([sample, "chr_means"])
        if self.norm == "chrom_mean_zero":
        #if self.norm_by_mean_zero:
            self.norm_path = self.norm_path + "_0"
        if os.path.exists(self.norm_path):
            for line in open(self.norm_path, 'r'):
                sline = line.split()
                self.window_correct[sline[0]] = float(sline[1])
                
        self.flank = flank
        self.out_path = ""
        if type == "anno":
            self.out_path = "/".join([ANNO_OUT_PATH, self.data_type, self.fun, os.path.basename(anno)])
        elif type == "feature":
            if not split_anno:
                self.out_path = "/".join([FEATURE_OUT_PATH, self.data_type, self.fun, os.path.basename(anno)])
            else:
                self.out_path = "/".join([FEATURE_OUT_PATH, data_type, "split", os.path.basename(anno)])    
        if not os.path.exists(self.out_path): os.makedirs(self.out_path)
        
    def run_h5(self):
        anno = self.anno
        h5 = tb.openFile(SAMPLE_PATH + "/" + self.sample)
        samples = [s._v_name for s in h5.iterNodes("/")]
    
        for sample in samples:
            if self.flank:
                if os.path.exists(self.out_path + "/" + sample + "_flank" + str(self.flank)):
                    print "File exists. Skipping..."
                    continue
            else:
                if os.path.exists(self.out_path + "/" + sample):
                    
                    continue
                    dec = raw_input("File exists. Overwrite? [y/n]")
                    if dec == "n": continue

            print sample
            anno_chrs = os.listdir(anno)
            sample_chrs = [chr._v_name for chr in h5.getNode("/", sample)._f_iterNodes()]
            chrs_tbp = list(set(anno_chrs) & set(sample_chrs))
            tmp_path = tempfile.mkdtemp(suffix=os.path.basename(anno))
            
            exp = 0
    
            pool = Pool(processes=4)
            for chr_tbp in chrs_tbp:
                #tab_h5(self, anno, sample, chr_tbp, tmp_path, self.fun, exp)
                pool.apply_async(tab_h5, (self, anno, sample, chr_tbp, tmp_path, self.fun, exp))
            pool.close()
            pool.join()

            if self.flank == 0:
                self.file_combine(tmp_path, sample)
            else:
                self.file_combine(tmp_path, sample + "_flank" + str(self.flank))
        
    def run_bam(self):
        
        # Check if output file already exists
        if os.path.exists(self.out_path + "/" + self.sample.split(".bam")[0]):
            dec = raw_input("File exists. Overwrite? [y/n]")
            if dec == "n": return
        
        if not os.path.exists(self.sample + ".bai"):
            print "Indexing BAM..."
            pysam.index(self.sample)
            
        # Determine what chromosomes to process
        anno = self.anno     
        chrs_tbp = os.listdir(anno)
        tmp_path = tempfile.mkdtemp(suffix=os.path.basename(anno))
      
      
        pool = Pool(processes=4)

        result = [pool.apply_async(tab_bam, (self, chr_tbp, tmp_path)) for chr_tbp in chrs_tbp]
        #[tab_bam(self, chr_tbp, tmp_path) for chr_tbp in chrs_tbp]
        pool.close()
        pool.join()
        
        # Write window_correct dictionary if not already present
        if self.norm == "chrom_mean" or self.norm == "chrom_mean_zero":
            if not os.path.exists(self.norm_path):
                file = open(self.norm_path, 'w')
                for item in result:
                    item = item.get()
                    out = "\t".join([item[0], str(item[1])]) + "\n"
                    file.write(out)
                
        # Combine chromosome files into one       
        if self.flank == 0:
            self.file_combine(tmp_path, os.path.basename(self.sample).split(".bam")[0])
        else:
            self.file_combine(tmp_path, os.path.basename(self.sample).split(".bam")[0] + "_flank" + str(self.flank))

    def file_combine(self, tmp_path, sample_name):
        anno = self.anno
        if self.split_anno:
            out = open("/".join([self.out_path, sample_name + "_" + str(self.window_size)]), 'w')
        else:
            out = open("/".join([self.out_path, sample_name]), 'w')
        files_tmp = os.listdir(tmp_path)
        for file_tmp in files_tmp:
            a = open(tmp_path + "/" + file_tmp)
            for line in a:
                out.write(line)
        shutil.rmtree(tmp_path)
        out.close()

        
def tab_h5(self, anno, track, chr_tbp, tmp_path, fun, exp):
    #pdb.set_trace()
    print chr_tbp
    h5 = tb.openFile(SAMPLE_PATH + "/" + self.sample)
    sample = h5.getNode("/", track)
    anno_data = open(anno + "/" + chr_tbp)
    sample_data = sample._f_getChild(chr_tbp)
    anno_out_path = tmp_path + "/" + chr_tbp
    anno_out = open(anno_out_path, 'w')
    self.window_size = int(sample_data.getAttr('Resolution'))
    anno_line = anno_data.readline().strip().split()
    flank = self.flank
    start = 0
    end = 0
    vals = 0
    result = 0  
    strand_line = "+"
    strand_factor = 1
    for line in anno_data:
        line = line.strip()
        sline = line.split()
        
        
        if flank == 0:
            start = (atoi(sline[1]) - 1) / self.window_size
            end = (atoi(sline[2]) - 1) / self.window_size
            vals = sample_data[start:(end+1)]            
        else:
            start = [(int(sline[1]) - 1 - flank) / self.window_size, int(sline[2]) / self.window_size]
            end = [(int(sline[1]) - 2) / self.window_size, (int(sline[2]) + flank - 1) / self.window_size] 
            vals = np.append(sample_data[start[0]:(end[0] + 1)], sample_data[start[1]:(end[1] + 1)])
        
        if self.strand:
#            pdb.set_trace()
            if len(sline) == 6: strand_line = sline[5]
            elif len(sline) == 4: strand_line = sline[3]
        
        vals = vals[~np.isnan(vals)]
        if len(vals) > 0:
            #pdb.set_trace()
            if self.split_anno:
                for val in vals:
                    out = "\t".join([line, str(val)]) + "\n"
                    anno_out.write(out) 
            else:
                if self.data_type == "strand_diff":
                    if strand_line == "-":
                        result = -1 * compute_result(vals, fun)
                    else:
                        result = compute_result(vals, fun)
                elif self.data_type == "strand_fraction":
                    if strand_line == "-":
                        result = 1 - compute_result(vals, fun)
                    else:
                        result = compute_result(vals, fun)
                else:
                    result = compute_result(vals, fun)
                #if result > 4: pdb.set_trace()
                out = "\t".join([line, str(result)]) + "\n"
                anno_out.write(out)
        else:
            out = "\t".join([line, "NA"]) + "\n"
            anno_out.write(out)
            
    anno_data.close()
    anno_out.close()
    #h5.close()
        

def tab_bam(obj, chr_tbp , tmp_path):
   
    print chr_tbp
    
    # Setup input annotation file and BAM file  
    anno_data = open(obj.anno + "/" + chr_tbp)
    bam = pysam.Samfile(obj.sample, 'rb')
    
    
    norm_val = 0
    #pdb.set_trace()
    #if obj.norm_by_mean or obj.norm_by_mean_zero:
    if obj.norm == "chrom_mean" or obj.norm == "chrom_mean_zero":
        # Normalize by chromosomal means
        if chr_tbp in obj.window_correct:
            norm_val = obj.window_correct[chr_tbp]
    elif obj.norm == "rpkm":
        # Normalize by Reads per million and by reads per kilobase
        norm_val = 1e6 * 1e3 / (float(obj.window_size) * float(bam.mapped))
    else:
        norm_val = 1
        
    
    # Setup output path
    anno_out_path = tmp_path + "/" + chr_tbp
    anno_out = open(anno_out_path, 'w')
    
    # Pull out variables from group object
    flank = obj.flank
    window_size = obj.window_size
    
    # Initialize frequently altered variables
    vals = 0
    start = 0
    end = 0 
    read_end = 0
    
    # Loop through annotation records
    for line in anno_data:
        line = line.strip()
        sline = line.split()
        vals = 0
        # Extract start and end values of annotation record
        if obj.flank == 0:
            start = [(atoi(sline[1]) - 1)]
            end = [(atoi(sline[2]) - 1)]
            
        else:
            start = [int(sline[1]) - 1 - flank, int(sline[2])]
            end = [int(sline[1]) - 2, int(sline[2]) + flank - 1]
            
        
        # Loop allows flanking regions
        # Generally, only single iteration
        for i in xrange(len(start)):
            try:
                if obj.bam_attr == "count":                    
                    # If strand option set, only count reads if
                    # if read1 and aligning to same strand as feature.
                    # if read2 and aligning to opposite strand
                    if obj.strand:
                        feature_is_reverse = line[5] == "-"
                        reads = bam.fetch(chr_tbp, start[i], end[i] + 1)
                        for read in reads:
                            if read.is_read1 and read.is_reverse == feature_is_reverse:
                                vals += 1
                            elif read.is_read2 and read.is_reverse != feature_is_reverse:
                                vals += 1
                                
                    # Count the number of reads the overlap annotation record
                    elif obj.norm == "chrom_mean" or obj.norm == "chrom_mean_zero":
                        read_count = 0
                        total = 0
                        #pdb.set_trace()
                        for column in bam.pileup(chr_tbp, start[i], end[i] + 1):
                            if column.pos > start[i] and column.pos < end[i] + 1:
                                read_count += column.n
                                total += 1
                        #pdb.set_trace()
                        vals = read_count
            
                    else:
                        vals = bam.count(chr_tbp, start[i], end[i] + 1)

                    # Normalize by the length of the record
                    if obj.fun == "mean":
                        vals /= (float(end[i] + 1 - start[i]))
                        
                
                # Only count read if end aligns within record
                elif obj.bam_attr == "count_ends":
                    reads = bam.fetch(chr_tbp, start[i], end[i] + 1)
                    
                    for read in reads:
                        if read.is_reverse:
                            read_end = read.aend
                        else:
                            #pdb.set_trace()
                            read_end = read.pos
                        if read_end >= start[i] and read_end <= end[i]:
                            #pdb.set_trace()
                            vals += 1
                    
                    # Sum
                    #vals = np.sum(vals)
                    
                    #Normalize by the length of the record
                    vals /= (float(end[i] + 1 - start[i]))        
                
                # Extract insert sizes of read pairs overlapping record
                elif obj.bam_attr == "isize":

                    it = bam.fetch(chr_tbp, start[i], end[i] + 1)
                    nreads = 0
                    for read in it:
                        if read.is_read1:
                            vals += abs(read.isize)
                            nreads += 1
                    if nreads == 0:
                        vals = 0
                        continue
                    vals /= nreads
            except IndexError:
                pdb.set_trace()
            
        if obj.split_anno:
            for val in vals:
                out = "\t".join([line, str(val / norm_val)]) + "\n"
                anno_out.write(out) 
        else:
            out = ""
            
            if obj.bam_attr == "count" or obj.bam_attr == "count_ends":
                if obj.norm == "chrom_mean" or obj.norm=="chrom_mean_zero":
                    if norm_val == 0:
                        total_n = 0
                        count_n = 0
                        print "Computing average values..."
                        for column in bam.pileup(reference=chr_tbp):
                            total_n += column.n
                            count_n += 1
                    
                        norm_val = 1/ (total_n / float(count_n))
                        print "Average coverage = {0}".format(norm_val)
                #pdb.set_trace()    
                out = "\t".join([line, str(vals * norm_val)]) + "\n"
            else:
                out = "\t".join([line, str(vals)]) + "\n"
            
            anno_out.write(out)
        
    anno_data.close()
    anno_out.close()
    
    if obj.norm_by_mean:    
        return [chr_tbp, norm_val]
    else:
        return 0

def compute_result(vals, fun):
    result = 0
    if fun == "mean":
        result = val_mean(vals)
    elif fun == "mean_skip_zero":
        result = val_mean(vals[vals[:]>0])
    elif fun == "mean_abs":
        result = val_mean(abs(vals))
    elif fun == "median":
        result = np.median(vals)
    elif fun == "mode":
        result = val_mode(vals)
    elif fun == "sum":
        result = sum(vals)
        #print result
    elif fun == "var":
        result = val_var(vals)
    elif fun == "cv":
        result = val_cv(vals)
    elif fun == "kurtosis":
        result = val_kurtosis(vals)
    elif fun =="max":
        result = max(vals)
    elif fun == "randc":
        result = val_compareRandom(vals, exp)
    elif fun == "energy":
        result = val_energy(vals)
    return(result)
    
def computeExpected(sample):
    print 'Computing expected RPM per window...'
    read_sum = 0
    window_num = 0
    for chrom in sample._f_iterNodes():
        read_sum = read_sum + sum(chrom)
        window_num = window_num + len(chrom)
    return(read_sum / window_num)
    
def val_mean(vals):
    result = np.mean(vals)
    if np.isnan(result): result = 0
    return result
    
def val_mean_nz(vals):
    result = np.sum()
    
def val_mode(vals):
    counts = {}
    for val in vals:
        if val in counts:
            counts[val] = counts[val] + 1
        else:
            counts[val] = 1
    return(max(counts.iteritems(), key=operator.itemgetter(1))[0])

def val_var(vals):
    mean = val_mean(vals)
    denom = 1
    if len(vals) > 1: denom = len(vals) - 1
    var = sum(pow(vals - mean, 2)) / denom 
    return(var)
    
def val_cv(vals):
    mean = val_mean(vals)
    if mean == 0: return(0)
    sd = sqrt(val_var(vals))
    return(sd / mean)
    
def val_kurtosis(vals):
    result = stats.kurtosis(vals)
    if np.isnan(result): result = 0
    return result

def val_compareRandom(vals, exp):
    val_sum = np.sum(vals)
    exp_sum = len(vals) * exp
    return(val_sum / exp_sum)

def val_energy(vals):
    m = val_mean(vals)
    result = sum(pow(vals - m, 2))
    return(result)
          
def tab_worker(anno, sample, sample_type, bam_attr, fun, type, flank, data_type,
               split_anno, strand, norm):
    #print anno
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if sample_type == "h5":
            obj = tab(anno, sample, sample_type, bam_attr, fun, type, flank,
                      data_type, split_anno, strand, norm)
            obj.run_h5()
        elif sample_type == "bam":
            for bam in sample:
                obj = tab(anno, bam, sample_type, bam_attr, fun, type, flank,
                          data_type, split_anno, strand, norm)
                obj.run_bam()
    
def main(argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='annotation', required=False, default="", help="Annotation file")
    parser.add_argument('-f', dest='feature', required=False, help="Feature file")
    parser.add_argument('--anno_set', action="store_true", required=False, help="Process all annotations")
    parser.add_argument('--feature_set', action="store_true", required=False, help="Process all features")
    parser.add_argument('-t', dest='h5', required=False, help="HDF5 track file")
    parser.add_argument('-b', dest='bam', required=False, nargs='*', help="BAM file")
    parser.add_argument('--bam_attr', required=False, default="count", help="BAM attribute to group")
    parser.add_argument('--data_type', help="Directory for analysis output")
    parser.add_argument('--function', dest='fun', required=False, default="mean",
                        choices=['mean', 'mean_skip_zero', 'mean_abs', 'median', 'mode','sum',
                                 'max', 'var', 'cv', 'kurtosis', 'energy'],
                        help="Summary function to apply to read counts")
    parser.add_argument('--norm', required=False, default="rpkm",
                        choices=['chrom_mean', 'chrom_mean_zero', 'rpkm', 'none'])
    parser.add_argument('--split', dest="split_anno", action="store_true", default=False)
    parser.add_argument('--flank', type=int, required=False, default=0, help="Size of regions flanking bed to compute values for")
    parser.add_argument('--strand', dest="strand", action="store_true", default=False)
    #parser.add_argument('--norm_by_mean', action="store_true", default=False)
    #parser.add_argument('--norm_by_mean_zero', action="store_true", default=False)
    args = parser.parse_args()
    
    fun = args.fun
    
    sample = 0
    sample_type = ""
    if args.h5:
        #sample = tb.openFile(SAMPLE_PATH + "/"+ args.h5, 'a')
        sample = args.h5
        sample_type = "h5"
    elif args.bam:
        sample = args.bam
        sample_type = "bam"
        
    if args.anno_set:
        annos = [ANNO_PATH + "/"+ f for f in os.listdir(ANNO_PATH) if re.search("chr", f)]
        [tab_worker(anno, sample, sample_type, args.bam_attr, fun, "anno", args.data_type, args.split_anno, args.strand) for anno in annos]
        
    elif args.feature_set:
        features = [FEATURE_PATH + "/" + f for f in os.listdir(FEATURE_PATH) if re.search("chr", f)]
        [tab_worker(feature, sample, sample_type, args.bam_attr, fun, "feature", args.flank, args.data_type, args.split_anno, args.strand) for feature in features]
    
    elif args.annotation:
        tab_worker(ANNO_PATH + "/" + args.annotation, sample, sample_type,
                   args.bam_attr, fun, "anno", args.flank, args.data_type,
                   args.split_anno, args.strand, args.norm)
    
    elif args.feature:
        tab_worker(FEATURE_PATH + "/" + args.feature, sample, sample_type,
                   args.bam_attr, fun, "feature", args.flank, args.data_type,
                   args.split_anno, args.strand, args.norm)
    
    
   
if __name__ == "__main__":
    main(sys.argv)
