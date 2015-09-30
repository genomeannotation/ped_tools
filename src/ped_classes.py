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

class Family:
    """Stores a mom PedRow, a dad PedRow, and child PedRows"""
    def __init__(self):
        self.mom = None
        self.dad = None
        self.children = []

    def validate_genotypes(self, column):
        genotypes_corrected = 0
        mom_genotype = self.mom.genotypes[column]
        dad_genotype = self.dad.genotypes[column]
        child_genotypes = [c.genotypes[column] for c in self.children]
        for child_genotype in child_genotypes:
            if not valid_genotype(mom_genotype, dad_genotype, child_genotype):
                genotypes_corrected += 1
                child_genotype = "0 0"
        return genotypes_corrected

