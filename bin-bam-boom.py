#!/usr/bin/env python
#
# python bin-bam-boom.py pooled-reads.bam contig-to-bin-map.tsv outprefix

import pysam
import sys

inbam = sys.argv[1]
mapfile = sys.argv[2]
prefix = sys.argv[3]

# Load contig-->bin map into a dictionary
# Create an output file for each bin
outfiles = dict()
contig_bin_map = dict()
for line in open(mapfile, 'r'):
    contigid, binid = line.strip().split()
    contigid = contigid.split(' ')[0]
    contig_bin_map[contigid] = binid
    if binid not in outfiles:
        outfilename = prefix + '.' + binid + '.fastq'
        outfiles[binid] = open(outfilename, 'w')

# Iterate over all alignments
bam = pysam.AlignmentFile(inbam, 'rb')
for alignment in bam:
    if alignment.is_secondary or alignment.is_supplementary:
        continue # Ignore these ones

    contigid = bam.get_reference_name(alignment.tid)
    if contigid not in contig_bin_map:
        message = 'contig ID "{:s}" not found'.format(contigid)
        raise ValueError(message)
    binid = contig_bin_map[contigid]
    outfile = outfiles[binid]

    # Formulate a proper read name
    readname = alignment.qname
    if alignment.flag & 1:
        # Logical XOR: if the read is paired, it should be first in pair
        # or second in pair, not both.
        assert (alignment.flag & 64) != (alignment.flag & 128)
        suffix = '/1' if record.flag & 64 else '/2'
        if not readname.endswith(suffix):
            readname += suffix

    # Print read to appropriate output file
    print('@', readname, '\n', alignment.seq, '\n+\n', alignment.qual, sep='',
          file=outfile)
