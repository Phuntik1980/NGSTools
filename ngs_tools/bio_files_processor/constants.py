from enum import Enum


class Extension(Enum):
    FASTA = "fasta"
    GBK = "gbk"
    TXT = "txt"


PREFIX = 'output_'

BLAST_AIM_COLUMN = 'Description'
BLAST_DESCRIPTION_WIDTH = 66
