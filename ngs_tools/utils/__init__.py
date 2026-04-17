"""Utility helpers for IO, parsing, and serialization.

Exposes a minimal, stable surface used across the package:
- read_data/write_data: lightweight file IO helpers
- parse_fastq/parse_multiline_fasta: streaming parsers
- Serializer: converts DTOs to on-disk text representation
"""

from .clients import read_data, write_data
from .parsers import (
    parse_fastq,
    parse_multiline_fasta,
)
from .serializers import Serializer
from .utils import (
    check_filter_fastq_args,
    mean_quality_phred33,
    value_in_bounds,
)
