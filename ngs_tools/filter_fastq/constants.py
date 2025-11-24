from enum import Enum

GC_MIN = 0
GC_MAX = 100


class Nucleotide(str, Enum):
    Adenine = "A"
    Cytosine = "C"
    Guanine = "G"
    Thymidine = "T"


PHRED_SCORE = 33
