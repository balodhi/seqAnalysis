#! /bin/bash

echo $1
echo "${1}.metrics"

java -jar /seq/picard_current/CollectRnaSeqMetrics.jar REF_FLAT=/home/brad/lib/gtf/taeGut1_ens.rf RIBOSOMAL_INTERVALS=/home/brad/lib/ucsc/taeGut1_rrna.interval STRAND_SPECIFICITY="FIRST_READ_TRANSCRIPTION_STRAND" INPUT=$1 OUTPUT="${1}.metrics" REFERENCE_SEQUENCE=/home/brad/lib/genomes/taeGut1.fa CHART="${1}_coverage.pdf"
