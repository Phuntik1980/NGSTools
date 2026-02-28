from typing import Union
from datetime import datetime
from pathlib import Path

from Bio import SeqIO
from Bio.SeqUtils import GC123

from ngs_tools.utils import *
from ngs_tools.constants import (
    DEFAULT_GC_BOUNDS,
    DEFAULT_LENGTH_BOUNDS,
    DEFAULT_QUALITY_THRESHOLD,
    FASTQ_FILTERED_PREFIX,
    FASTQ_EXTENSION,
    FASTQ_TIMESTAMP_FORMAT,
    MSG_NO_FASTQ_PASSED,
)


def filter_fastq(
    input_fastq: str,
    output_fastq: str,
    gc_bounds: Union[int, tuple[int, int]] = DEFAULT_GC_BOUNDS,
    length_bounds: Union[int, tuple[int, int]] = DEFAULT_LENGTH_BOUNDS,
    quality_threshold: int = DEFAULT_QUALITY_THRESHOLD,
):
    """Filter FASTQ reads by length, GC content and mean Phred quality.

    This function mirrors the filtering rules from the legacy `fastq_tools`
    implementation, but relies on Biopython `SeqIO`/`SeqRecord` for parsing.

    Output:
        A FASTQ file named `filtered_<YYYYmmddHHMMSS>.fastq` is written into the
        directory given by `output_fastq` (despite the name, it is expected to
        be a directory).

    Notes:
        If basic argument checks fail, the function returns `None` without
        raising.
    """

    if not _check_filter_fastq_args(
        input_fastq, output_fastq, gc_bounds, length_bounds, quality_threshold
    ):
        return None

    output_dir = Path(output_fastq)
    output_filename = (
        f"{FASTQ_FILTERED_PREFIX}"
        f"{datetime.now().strftime(FASTQ_TIMESTAMP_FORMAT)}"
        f"{FASTQ_EXTENSION}"
    )
    output_path = output_dir / output_filename

    passed = 0
    not_passed = 0
    passed_records = []

    for record in SeqIO.parse(input_fastq, "fastq"):
        seq_str = str(record.seq)
        gc_value, *_ = round(GC123(seq_str))
        length_value = len(record)
        mean_qual = _mean_quality_phred33(
            record.letter_annotations.get("phred_quality", [])
        )

        is_ok = (
            _value_in_bounds(gc_value, gc_bounds)
            and _value_in_bounds(length_value, length_bounds)
            and mean_qual >= quality_threshold
        )

        if is_ok:
            passed_records.append(record)
            passed += 1
        else:
            not_passed += 1

    if passed_records:
        SeqIO.write(passed_records, str(output_path), "fastq")

    print(f"Filtered {not_passed} sequences. Saved {passed} sequences.")
    if passed == 0:
        print(MSG_NO_FASTQ_PASSED)
