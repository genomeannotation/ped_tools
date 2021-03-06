#!/usr/bin/env python

# Script to tweak your ped file
# Ignores comments
# Leaves columns 1-6 unchanged
# For columns 7... alternates " " and "\t" as delimiter
# Then turns alleles into '1' or '2'
# Checks validity of alleles based on parent genotypes
# if parents are 0 0, don't change children
# if one allele is illegal, entire genotype must be 0 0

import sys
from src.ped_classes import PedRow, Family

def read_ped(filename):
    """Read ped file, return list of Family objects and count of genotypes columns"""
    # Read ped file
    families = []
    current_family = None
    current_family_id = None
    number_of_genotypes = 0
    sys.stderr.write("Reading %s...\n" % sys.argv[1])
    with open(filename, 'r') as pedfile:
        for line in pedfile:
            if line.startswith("#"):
                sys.stdout.write(line)
                continue
            fields = line.strip().split()
            num_cols = len(fields)
            new_cols = fields[:6] # keep first 6 columns
            # Make new columns with two entries each,
            # separated by a space
            first_allele = ""
            second_allele = ""
            for n in range(6, num_cols):
                if n % 2 == 0:
                    first_allele = fields[n]
                else:
                    second_allele = fields[n]
                    genotype = first_allele + " " + second_allele
                    new_cols.append(genotype)
                    first_allele = ""
                    second_allele = ""
            ped_row = PedRow(new_cols)
            row_family_id = ped_row.family_id()
            if row_family_id != current_family_id:
                # Save current family if we have one
                if current_family:
                    families.append(current_family)
                # Create new family
                current_family = Family()
                current_family_id = row_family_id
            # Add this row to current family
            if ped_row.row_type() == "mom":
                current_family.mom = ped_row
            elif ped_row.row_type() == "dad":
                current_family.dad = ped_row
            else:
                current_family.children.append(ped_row)
            # Find out how many genotype columns we have
            # (Only executes once)
            if number_of_genotypes == 0:
                number_of_genotypes = len(new_cols[6:])
        # Add last family!
        families.append(current_family)
    return families, number_of_genotypes

def main():
    # Inspect each column and validate genotypes
    # Then modify genotypes to "1 1" style entries
    families, number_of_genotypes = read_ped(sys.argv[1])
    sys.stderr.write("Converting genotypes...\n")
    genotypes_corrected = 0
    for i in range(number_of_genotypes):
        for family in families:
            # Validate genotypes
            sys.stderr.write("Validating genotypes for family %s, column %d\n" % 
                    (family.mom.family_id(), i))
            genotypes_corrected += family.validate_genotypes(i)
            sys.stderr.write("...corrected %d genotypes.\n" % genotypes_corrected)
            # Convert letters to numbers
            family.letter_to_numbers(i)

    sys.stderr.write("%d invalid genotypes were corrected in total.\n" % genotypes_corrected)

    # Print stuff
    sys.stderr.write("Writing results...\n")
    for family in families:
        print(family.mom.to_tsv())
        print(family.dad.to_tsv())
        for child in family.children:
            print(child.to_tsv())

##########################

if __name__ == "__main__":
    main()
