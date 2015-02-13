#! /usr/bin/env python

import sys
import os
import argparse
import re
import shutil
from string import atoi, atof
from multiprocessing import Pool

FEATURE_PATH = '/home/user/lib/annotations/'
SAMPLE_PATH = '/media/storage2/data/medips_split/'
OUT_PATH = '/media/storage2/analysis/features/'
SAMPLES = []
"""
CELLS_SAMPLES = ['omp_hmedip.bed', 'ngn_hmedip.bed', 'icam_hmedip.bed',
                 'omp_medip.bed', 'ngn_medip.bed', 'icam_medip.bed']
"""
CELLS_SAMPLES = ['omp_hmc_rlm', 'ngn_hmc_rlm', 'icam_hmc_rlm',
                 'omp_mc_rlm', 'ngn_mc_rlm', 'icam_mc_rlm']
"""
D3A_SAMPLES = ['moe_wt_mc.bed', 'moe_d3a_mc.bed',
               'moe_wt_hmc.bed', 'moe_d3a_hmc.bed']
"""
D3A_SAMPLES = ['moe_wt_mc_rlm', 'moe_d3a_mc_rlm',
               'moe_wt_hmc_rlm', 'moe_d3a_hmc_rlm']


class tab:
    def __init__(self, feature_path, feature, samples, window):
        self.feature_path = feature_path
        self.feature_files = [f for f in os.listdir(self.feature_path) if re.search("chr", f)]
        self.feature = feature
        self.sample_path = SAMPLE_PATH + "W" + window + "/"
        self.samples = samples
        print self.feature_files
    def feature_interface(self):
        if self.feature != "":
            self.sample_interface(self.feature, single=True)
        else:
            for feature in self.feature_files:
                self.sample_interface(feature)
    def sample_interface(self, feature, single=False):
        if single:
            tab_interface([self.feature_path + feature, self.sample_path + self.samples[0]])
        else:
            pool = Pool(processes=len(self.samples))
        #print feature
            tasks = [([self.feature_path + feature, self.sample_path + sample],) for sample in self.samples]
            [pool.apply_async(tab_interface, t) for t in tasks] 
#        
        
        pool.close()
        pool.join()

def file_combine(feature, sample):
    out_prefix = OUT_PATH + os.path.basename(sample)
    if not os.path.exists(out_prefix): os.mkdir(out_prefix)
    out = open(OUT_PATH + os.path.basename(sample) + "/" + os.path.basename(feature), 'wa')
    tmp_path = sample + "/" + os.path.basename(feature) + "_tmp"
    files_tmp = os.listdir(tmp_path)
    for file_tmp in files_tmp:
        a = open(tmp_path + "/" + file_tmp)
        for line in a:
            out.write(line)
    shutil.rmtree(tmp_path)
    out.close()

def tab_core(args):
    feature_data = args[0]
    sample_data = args[1]
    feature_out = args[2]
    norm_factor = args[3]
    feature_line = feature_data.readline().strip().split()
    prev_sample_line = ['0','0','0','0']
    raw = 0
    norm = 0
    count = 0
    #within = False
    for line in feature_data:
        feature_line = line.strip().split()
        if len(feature_line) < 2:
            continue
        for sample_line in sample_data:
            sample_line = sample_line.strip().split()
            if len(sample_line) > 1:
            #print sample_line, feature_line
                if atoi(sample_line[1]) >= atoi(feature_line[1]):
            #    within = True
                    dist_j1 = abs(atoi(prev_sample_line[1]) - atoi(feature_line[1]))
                    dist_j2 = abs(atoi(sample_line[1]) - atoi(feature_line[1]))
                    if dist_j1 < dist_j2:
                       raw = raw + atof(prev_sample_line[2]) / norm_factor
                       norm = norm + atof(prev_sample_line[3])
                    else:
                        raw = raw + atof(sample_line[2]) / norm_factor
                        norm = norm + atof(sample_line[3])
                    count = count + 1
                #if within:
                if atoi(sample_line[1]) >= atoi(feature_line[2]):
                    if count > 0:
                        raw_mean = raw / count
                        norm_mean = norm / count
                        out = "\t".join(feature_line) + "\t" + str(raw_mean) + "\t" + str(norm_mean) + "\n"
                        feature_out.write(out)
                        raw = 0
                        norm = 0
                        count = 0
                        break 
            prev_sample_line = sample_line

def tab_interface(args):
    feature = args[0]
    sample = args[1]
    out_path = "/".join([OUT_PATH, os.path.basename(sample), os.path.basename(feature)])
    if os.path.exists(out_path):
        print "file exists: " + out_path
        return
    norm_factor = atoi(open(sample + "/total_reads").read()) / 1E6
    feature_chrs = os.listdir(feature)
    sample_chrs = os.listdir(sample)
    chrs_tbp = list(set(feature_chrs) & set(sample_chrs))
    tmp_path = sample + "/" + os.path.basename(feature) + "_tmp/"
    if not os.path.exists(tmp_path): os.mkdir(tmp_path)
    for chr_tbp in chrs_tbp:
        feature_data = open(feature + "/" + chr_tbp)
        sample_data = open(sample + "/" + chr_tbp)
        feature_out_path = tmp_path + chr_tbp
        if os.path.exists(feature_out_path): 
            print "continue"
            continue
        feature_out = open(feature_out_path, 'w')
        args = [feature_data, sample_data, feature_out, norm_factor]
        tab_core(args)
        feature_data.close()
        sample_data.close()
        feature_out.close()    
    file_combine(feature, sample)
    
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='feature_set')
    parser.add_argument('-f', dest='feature', required=False, default="")
    parser.add_argument('-s', dest='sample_set')
    parser.add_argument('-w', dest='window')
    args = parser.parse_args()
    feature_path = '/home/user/lib/features_general/'
    feature = args.feature
    #if args.feature_set == "hires":
    #    feature_path = '/home/user/lib/featuretations_hires/'
    #elif args.feature_set == "std":
    #    feature_path = '/home/user/lib/features/'
    samples = []
    if args.sample_set == "cells":
        samples = CELLS_SAMPLES
    elif args.sample_set == "d3a":
        samples = D3A_SAMPLES
 
    obj = tab(feature_path, feature, samples, args.window) 
    obj.feature_interface()

   
if __name__ == "__main__":
    main(sys.argv)
