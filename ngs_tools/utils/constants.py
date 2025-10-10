from enum import Enum

DELIMITER = "\n"
CRLF = "\r"

DEFAULT_FILTERED_DIR = "filtered"

FASTA_HEADER_PREFIX = ">"


class FastqSign(Enum):
    header = "@"
    quality = "+"


class FastqStatus(Enum):
    waiting_for_sequence = "waiting_for_sequence"
    waiting_for_quality = "waiting_for_quality"
    end = "end"


class FastaStatus(Enum):
    collecting_sequence = "collecting_sequence"
    end = "end"


class _FastqStatus(Enum):
    waiting_for_header = "waiting_for_header"
    main_header = "main_header"
    sequence = "sequence"
    second_header = "second_header"
    quality = "quality"
