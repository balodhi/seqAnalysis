#!/usr/bin/env python

import os
import shutil
import sys
from string import *
from math import *
from optparse import OptionParser
import operator

"""
Three sets of intervals of length opt.window:
        opt.flank times upstream and downstream
        gene body divided into opt.number equally spaced windows of length opt.window        
"""

def main(argv):

	parser = OptionParser()

	parser.add_option("-i", "--input", action="store", type="string", dest="input", metavar="<str>")
	parser.add_option("-o", "--ouput", action="store", type="string", dest="output", metavar="<str>")
	parser.add_option("-f", action="store", type="int", dest="flank", metavar="<int>")
	parser.add_option("-w", action="store", type="int", dest="window", metavar="<int>")
	parser.add_option("-n", action="store", type="int", dest="number", metavar="<int>")

	(opt, args) = parser.parse_args(argv)
	
	infile = open(opt.input, 'r');
	outfile = open(opt.output, 'w');
	window = opt.window
#	round_factor = int(-log10(window))
	number = opt.number
	flank = opt.flank
	genome_sizes = open('/users/bradcolquitt/BEDTools/genomes/mouse.mm9.genome.txt','r');

	d = {}
	for line in genome_sizes:
		line = line.strip();
		sline = line.split();
		if len(sline) > 0:
			d[sline[0]]=sline[1];
			
	line_number = 0
	strand = "+"
	name = ""
	
	for line in infile:
		++line_number
		line = line.strip();
		sline = line.split();
		
#                initial_start = int(round(atoi(sline[1]),round_factor)) + 1;
#		initial_end = int(round(atoi(sline[2]),round_factor));
		
		initial_start = atoi(sline[1])
		intial_end = atoi(sline[2])
 
		if len(sline) == 6: strand = sline[5]
		else: strand = "+"
		
		if len(sline) >= 4: name = sline[3]
		else: name = line_number
		
		span = initial_end - initial_start + 1
                remain = span - number*window
		rwindow = remain/(number)
	
                if remain < 0 or rwindow % window != 0 :
                        continue;
			
                for x in xrange(3):
                        if x == 0:
                                start = initial_start - flank * window
                                end = initial_end + flank * window
				step_amount = 0
				section_range = xrange(flank)
                                for index in section_range:	
                                        out = "";
                                        if strand == "+":
                                                end = start + window - 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(index+1) + "\t" + strand + "\n"
                                                start = end + 1
                                        else:
						start = end - window + 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(index+1) + "\t" + strand + "\n"
                                                end = start - 1;  
					if (start and end >=0) and (start and end <= atoi(d[sline[0]])): 
                                        	outfile.write(out);
                        elif x == 1:
				start = initial_start
                                end = initial_end
				step_amount = rwindow
				section_range = xrange(number)
				
                                for index in section_range:
                                        out = "";
                                        if strand == "+":
                                                end = start + window - 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(flank+index+1) + "\t" + strand + "\n"
                                                start = end + rwindow + 1
                                        else:
                                                start = end - window + 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(flank+index+1) + "\t" + strand + "\n"
                                                new_end = start - rwindow - 1
                                        if (start and end >=0) and (start and end <= atoi(d[sline[0]])): 
                                        	outfile.write(out);                                             
			elif x == 2:
				start = initial_end + 1
                                end = initial_start - 1 
				step_amount = 0
				section_range = xrange(flank)
				
                                for index in section_range:
                                        out = "";
                                        if strand == "+":
                                                end = start + window - 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(flank+number+index+1)  + "\t" + strand + "\n"
                                                start = end+1
                                        else:
                                                start = end - window + 1
                                                out = sline[0] + "\t" + str(start) + "\t" + str(end) + "\t" + name + "\t" + str(flank+number+index+1)  + "\t" + strand + "\n"
                                                end = start-1;   
                                        if (start and end >=0) and (start and end <= atoi(d[sline[0]])): 
                                        	outfile.write(out);
	outfile.close();
		
if __name__ == "__main__":
	main(sys.argv) 	
