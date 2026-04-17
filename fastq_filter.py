from datetime import datetime
import logging
from pathlib import Path
from typing import Union

from Bio import SeqIO
from Bio.SeqUtils import GC123

from ngs_tools.constants import (
    DEFAULT_GC_BOUNDS,
    DEFAULT_LENGTH_BOUNDS,
    DEFAULT_QUALITY_THRESHOLD,
    FASTQ_EXTENSION,
    FASTQ_FILTERED_PREFIX,
    FASTQ_TIMESTAMP_FORMAT,
    MSG_NO_FASTQ_PASSED,
)
from ngs_tools.utils import (
    check_filter_fastq_args,
    mean_quality_phred33,
    value_in_bounds,
)

logger = logging.getLogger(__name__)


def filter_fastq(
    input_fastq: str,
    output_fastq: str,
    gc_bounds: Union[int, tuple[int, int]] = DEFAULT_GC_BOUNDS,
    length_bounds: Union[int, tuple[int, int]] = DEFAULT_LENGTH_BOUNDS,
    quality_threshold: int = DEFAULT_QUALITY_THRESHOLD,
) -> None:
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

    if not check_filter_fastq_args(
        input_fastq, output_fastq, gc_bounds, length_bounds, quality_threshold
    ):
        logger.error(
            "Invalid arguments for filter_fastq: input_fastq=%s "
            "output_fastq=%s gc_bounds=%s length_bounds=%s "
            "quality_threshold=%s",
            input_fastq,
            output_fastq,
            gc_bounds,
            length_bounds,
            quality_threshold,
        )
        return None

    logger.info(
        "Starting FASTQ filtering: input=%s output_dir=%s "
        "gc_bounds=%s length_bounds=%s quality_threshold=%s",
        input_fastq,
        output_fastq,
        gc_bounds,
        length_bounds,
        quality_threshold,
    )

    output_dir = Path(output_fastq)
    output_filename = (
        f"{FASTQ_FILTERED_PREFIX}"
        f"{datetime.now().strftime(FASTQ_TIMESTAMP_FORMAT)}"
        f"{FASTQ_EXTENSION}"
    )
    output_path = output_dir / output_filename

    logger.info("Output FASTQ path: %s", output_path)

    passed = 0
    not_passed = 0
    passed_records = []

    total = 0

    for record in SeqIO.parse(input_fastq, "fastq"):
        total += 1
        seq_str = str(record.seq)
        gc_value, *_ = round(GC123(seq_str))
        length_value = len(record)
        mean_qual = mean_quality_phred33(
            record.letter_annotations.get("phred_quality", [])
        )

        is_ok = (
            value_in_bounds(gc_value, gc_bounds)
            and value_in_bounds(length_value, length_bounds)
            and mean_qual >= quality_threshold
        )

        if is_ok:
            passed_records.append(record)
            passed += 1
        else:
            not_passed += 1

    if passed_records:
        SeqIO.write(passed_records, str(output_path), "fastq")
        logger.info("Saved %s sequences to %s", passed, output_path)
    else:
        logger.warning(
            "No sequences passed the filter. Output file not written."
        )

    logger.info(
        "Finished FASTQ filtering: total=%s filtered_out=%s saved=%s",
        total,
        not_passed,
        passed,
    )

    if passed == 0:
        logger.warning(MSG_NO_FASTQ_PASSED)

    return None
