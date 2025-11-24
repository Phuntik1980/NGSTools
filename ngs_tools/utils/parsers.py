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
    """Stream-parse a FASTQ file and yield Fastq records.

    A minimal state machine that expects the typical 4-line per record FASTQ
    layout and emits Fastq dataclass instances as they complete.

    Args:
        input_fastq (str): Path to an input FASTQ file.

    Yields:
        Fastq: Dataclass with name, sequence, and quality fields filled.
    """
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
    """Stream-parse a multi-line FASTA file into one-line sequence records.

    Concatenates multi-line sequences until the next header ('>') or EOF and
    yields a Fasta dataclass with header and joined sequence.

    Args:
        input_fasta (str): Path to an input FASTA file.

    Yields:
        Fasta: Dataclass with name (header) and one-line sequence.
    """
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
