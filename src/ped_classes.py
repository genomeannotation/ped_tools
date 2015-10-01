class PedRow:
    """Stores one row of ped file data"""
    def __init__(self, fields):
        self.info = fields[:6]
        self.genotypes = fields[6:]

    def to_tsv(self):
        genotypes = [str(g) for g in self.genotypes]
        return "\t".join(self.info + genotypes)

    def row_type(self):
        """Return 'mom', 'dad', or 'child' for a given PedRow"""
        if self.info[2] != "0":
            return "child"
        else:
            if self.info[1][1] == "F":
                return "mom"
            else:
                return "dad"

    def family_id(self):
        """Return family id of PedRow"""
        return self.info[1].split("_")[2]

def get_legal_genotypes(mom, dad):
    legal_genotypes = set()
    legal_genotypes.add("0 0")
    mom1 = mom[0]
    mom2 = mom[2]
    dad1 = dad[0]
    dad2 = dad[2]
    legal_genotypes.add(mom1 + " " + dad1)
    legal_genotypes.add(mom1 + " " + dad2)
    legal_genotypes.add(mom2 + " " + dad1)
    legal_genotypes.add(mom2 + " " + dad2)
    return legal_genotypes

def valid_genotype(mom_genotype, dad_genotype, child_genotype):
    # TODO not sure if this is fully accurate...
    # @ssim says if one parent missing, no correction
    # but if mom is missing and dad is "G G", then "A A" is impossible, no?
    if mom_genotype == "0 0" or dad_genotype == "0 0" or child_genotype == "0 0":
        return True
    legal_genotypes = get_legal_genotypes(mom_genotype, dad_genotype)
    for genotype in legal_genotypes:
        if str(genotype) == str(child_genotype):
            return True
    return False

def get_all_genotypes_with(allele):
    """Return a list of all genotypes containing a given allele"""
    result = []
    for base in "ACGT":
        result.append(allele + " " + base)
    return result

def get_valid_combos(mom, dad):
    """Return set of valid genotypes given mom and dad with known values"""
    result = set()
    for mom_allele in [mom[0], mom[2]]:
        for dad_allele in [dad[0], dad[2]]:
            alleles = sorted( [mom_allele, dad_allele] )
            result.add( alleles[0] + " " + alleles[1] )
    return result

def get_valid_genotypes(mom, dad):
    valid_genotypes = set()
    if mom == "0 0":
        dad1 = dad[0]
        dad2 = dad[2]
        for base in "ACGT":
            valid_genotypes |= set(get_all_genotypes_with(dad1))
            valid_genotypes |= set(get_all_genotypes_with(dad2))
    elif dad == "0 0":
        mom1 = mom[0]
        mom2 = mom[2]
        for base in "ACGT":
            valid_genotypes |= set(get_all_genotypes_with(mom1))
            valid_genotypes |= set(get_all_genotypes_with(mom2))
    else:
        valid_genotypes |= set(get_valid_combos(mom, dad))
    return valid_genotypes




class Family:
    """Stores a mom PedRow, a dad PedRow, and child PedRows"""
    def __init__(self):
        self.mom = None
        self.dad = None
        self.children = []

    def validate_genotypes(self, column):
        """Change invalid child genotypes to '0 0'"""
        genotypes_corrected = 0
        mom_genotype = self.mom.genotypes[column]
        dad_genotype = self.dad.genotypes[column]
        if mom_genotype == "0 0" and dad_genotype == "0 0":
            # If we know nothing about the parents, leave kids alone
            return genotypes_corrected
        else:
            # One or both parents' genotypes are known
            valid_genotypes = get_valid_genotypes(mom_genotype, dad_genotype)
            for child in self.children:
                if child.genotypes[column] not in valid_genotypes:
                    child.genotypes[column] = "0 0"
                    genotypes_corrected += 1
        return genotypes_corrected

    def letter_to_numbers(self, column):
        """Change genotypes like 'A G' to '1 2'"""
        # TODO omg this method needs refactored like bad
        # Figure out what bases are present
        bases_present = set()
        all_genotypes = []
        all_genotypes.append(self.mom.genotypes[column])
        all_genotypes.append(self.dad.genotypes[column])
        for child in self.children:
            all_genotypes.append(child.genotypes[column])
        for genotype in all_genotypes:
            for base in "ACGT":
                if base in genotype:
                    bases_present.add(base)
        if len(bases_present) > 2:
            sys.stderr.write("Error, more than 2 different bases in column %d\n" % i)
            sys.exit()
        # Figure out how to map bases to numbers
        base_to_number = {
                "0": "0",
                }
        if len(bases_present) >= 1:
            base_to_number[sorted(bases_present)[0]] = "1"
        if len(bases_present) == 2:
            base_to_number[sorted(bases_present)[1]] = "2"
        # Convert mom genotype
        if self.mom.genotypes[column][0] in base_to_number:
            new_mom_genotype = base_to_number[self.mom.genotypes[column][0]] + " "
        else:
            new_mom_genotype = "0 "
        if self.mom.genotypes[column][2] in base_to_number:
            new_mom_genotype += base_to_number[self.mom.genotypes[column][2]]
        else:
            new_mom_genotype += "0"
        self.mom.genotypes[column] = new_mom_genotype
        # Convert dad genotype
        if self.dad.genotypes[column][0] in base_to_number:
            new_dad_genotype = base_to_number[self.dad.genotypes[column][0]] + " "
        else:
            new_dad_genotype = "0 "
        if self.dad.genotypes[column][2] in base_to_number:
            new_dad_genotype += base_to_number[self.dad.genotypes[column][2]]
        else:
            new_dad_genotype += "0"
        self.dad.genotypes[column] = new_dad_genotype
        # Convert children's genotypes
        for child in self.children:
            if child.genotypes[column][0] in base_to_number:
                new_child_genotype = base_to_number[child.genotypes[column][0]] + " "
            else:
                new_child_genotype = "0 "
            if child.genotypes[column][2] in base_to_number:
                new_child_genotype += base_to_number[child.genotypes[column][2]]
            else:
                new_child_genotype += "0"
            child.genotypes[column] = new_child_genotype

