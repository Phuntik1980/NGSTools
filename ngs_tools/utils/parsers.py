from typing import Generator

from ngs_tools.filter_fastq.dto import FastqRecord

from .clients import read_data
from .constants import DELIMITER, FastqSign, FastqStatus


def parse_fastq(input_fastq: str) -> Generator[FastqRecord, None, None]:
    status = FastqStatus.end

    record = FastqRecord()

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
            record = FastqRecord()
            status = FastqStatus.end
