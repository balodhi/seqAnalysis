#! /bin/bash

prefix="${1//.sam}"
bam=${prefix}.bam
sort_bam=${prefix}_sort

samtools view -Sb $1 > ${prefix}.bam 
samtools sort $bam $sort_bam
samtools index ${sort_bam}.bam

