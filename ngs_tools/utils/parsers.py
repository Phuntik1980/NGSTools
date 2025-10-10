from typing import Generator

from ngs_tools.common import Fastq, Fasta

from .clients import read_data
from .constants import (
    DELIMITER,
    FastqSign,
    FastqStatus,
    FASTA_HEADER_PREFIX,
)


def parse_fastq(input_fastq: str) -> Generator[Fastq, None, None]:
    status = FastqStatus.end

    record = Fastq()

    for line in read_data(input_fastq):
        if line.startswith(FastqSign.header.value):
            if status == FastqStatus.end:
                status = FastqStatus.waiting_for_sequence
                record.name = line.rstrip(DELIMITER)

        elif status == FastqStatus.waiting_for_sequence:
            record.sequence = line.rstrip(DELIMITER)
            status = FastqStatus.waiting_for_quality

        elif status == FastqStatus.waiting_for_quality:
            if line.startswith(FastqSign.quality.value):
                continue
            record.quality = line.rstrip(DELIMITER)
            yield record
            record = Fastq()
            status = FastqStatus.end


def parse_multiline_fasta(input_fasta: str) -> Generator[Fasta, None, None]:
    record = Fasta()

    for line in read_data(input_fasta):
        if line.startswith(FASTA_HEADER_PREFIX):
            if record.is_exists:
                yield record
                record = Fasta()
            else:
                record.name = line.rstrip(DELIMITER)
        else:
            record.sequence += line.rstrip(DELIMITER)

    if record.is_exists:
        yield record
