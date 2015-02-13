#!/usr/bin/env python

import re, os, shutil, time, sys
from string import *
from optparse import OptionParser
import operator





def main(argv):

	parser = OptionParser()

	parser.add_option("-i", "--input", action="store", type="string", dest="input", metavar="<str>")
	parser.add_option("-o", "--ouput", action="store", type="string", dest="output", metavar="<str>")
	parser.add_option("-p", "--pattern", action="store", type="string", dest="pattern", metavar="<str>")


	(opt, args) = parser.parse_args(argv)

	infile = open(opt.input, 'r');
	outfile = open(opt.output, 'w');
	pattern = re.compile(opt.pattern,re.I);

	
	
	# Read in fasta, split, take sequence (element 1)
	# iterate across sequence combining index, index+1
	# check if combination == "CG", +1 to count if true
	# output 

	for line in infile:
		count = 0;
		line = line.strip();
		sline = line.split();
		m = pattern.findall(sline[4])
		count = len(m)
		
		"""
		for index in xrange(len(sline[4])-2):
			test = sline[4][index:index+2]
			if re.match(pattern,test):
				count += 1;
		"""
		out = sline[0] + "\t" + sline[1] + "\t" + sline[2] + "\t" + sline[3] + "\t" + sline[5] + "\t" + str(count) + "\n";
		outfile.write(out);
		
	
if __name__ == "__main__":
	main(sys.argv) 	
