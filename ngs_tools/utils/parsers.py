from typing import Generator

from ngs_tools.filter_fastq.dto import FastqRecord

from .clients import read_fastq
from .constants import CRLF, DELIMITER, FastqSign, FastqStatus


def parse_fastq(input_fastq: str) -> Generator[FastqRecord]:
    # Parse FASTQ by streaming characters from read_fastq
    prev_newline = True  # True at start-of-file to detect header at SOL
    state = FastqStatus.waiting_for_header
    line_buf = ""
    record = None

    for char in read_fastq(input_fastq):
        # skip carriage returns if present (handle CRLF)
        if char == CRLF:
            continue

        if state == FastqStatus.waiting_for_header:
            # start of a new record only when '@' appears at the start of a line
            if prev_newline and char == FastqSign.head.value:
                record = FastqRecord()
                state = FastqStatus.main_header
                line_buf = char
                prev_newline = False
            else:
                prev_newline = char == DELIMITER
            continue

        # accumulate characters for the current logical line
        line_buf += char

        if char == DELIMITER:
            line = line_buf[:-1]  # drop newline
            if state == FastqStatus.main_header:
                # header line (including leading '@')
                record.name = line
                state = FastqStatus.sequence
            elif state == FastqStatus.sequence:
                # sequence line
                record.sequence = line
                state = FastqStatus.second_header
            elif state == FastqStatus.second_header:
                # '+' line (content ignored)
                state = FastqStatus.quality
            elif state == FastqStatus.quality:
                # quality line -> emit record
                record.quality = line
                yield record
                # reset for the next record
                state = FastqStatus.waiting_for_header
                record = None

            # reset buffer and mark new line
            line_buf = ""
            prev_newline = True
        else:
            prev_newline = False

    # finalize if file ended without a trailing newline on the quality line
    if state == FastqStatus.quality and line_buf and record is not None:
        record.quality = line_buf
        yield record
