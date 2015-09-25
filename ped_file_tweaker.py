#!/usr/bin/env python

# Script to tweak your ped file
# Ignores comments
# Leaves columns 1-6 unchanged
# For columns 7... alternates " " and "\t" as delimiter
# Then turns alleles into '1' or '2'
# TODO check validity of alleles based on parent genotypes

import sys

class PedRow:
    """Stores one row of ped file data"""
    def __init__(self, fields):
        self.info = fields[:6]
        self.genotypes = fields[6:]

    def to_tsv(self):
        return "\t".join(self.info + self.genotypes)

# Read ped file
with open(sys.argv[1], 'r') as pedfile:
    for line in pedfile:
        if line.startswith("#"):
            sys.stdout.write(line)
            continue
        fields = line.strip().split()
        num_cols = len(fields)
        new_cols = fields[:6] # keep first 6 columns
        # Make new columns with two entries each,
        # separated by a space
        next_entry = ""
        for n in range(6, num_cols):
            if n % 2 == 0:
                next_entry = fields[n]
            else:
                next_entry += " " + fields[n]
                new_cols.append(next_entry)
                next_entry = ""
        ped_row = PedRow(new_cols)
        print(ped_row.to_tsv())
