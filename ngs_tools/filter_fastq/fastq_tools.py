import os
from collections import Counter
from datetime import datetime
from logging import getLogger
from typing import Callable, Union

from ngs_tools.filter_fastq import GC_MAX, GC_MIN
from ngs_tools.filter_fastq.constants import PHRED_SCORE, Nucleotide
from ngs_tools.utils import Serializer, parse_fastq, write_data

logger = getLogger(__name__)


def checking_conditions(
    input_fastq: str,
    output_fastq: str,
    gc_bounds: Union[int, tuple[int, int]] = (0, 100),
    length_bounds: Union[int, tuple[int, int]] = (0, 2**32),
    quality_threshold: int = 0,
):
    """Validate inputs for FASTQ filtering.

    Checks that paths exist and bounds are within allowed ranges.

    Args:
        input_fastq (str): Path to an input FASTQ file.
        output_fastq (str): Path to an existing output directory.
        gc_bounds (Union[int, tuple[int, int]]): GC upper bound or (min, max).
        length_bounds (Union[int, tuple[int, int]]): Length upper bound
            or (min, max).
        quality_threshold (int): Minimal acceptable mean Phred score (>= 0).

    Returns:
        bool | None: True if all checks pass; otherwise None and logs a warning.
    """
    if not input_fastq:
        logger.warning("No sequences provided")
        return None

    if input_fastq == output_fastq:
        logger.warning("Input and output files must be different")
        return None

    if not os.path.isfile(input_fastq):
        logger.warning(f"Input file {input_fastq} does not exist")
        return None

    if not os.path.isdir(output_fastq):
        logger.warning(f"Output directory {output_fastq} does not exist")
        return None

    if isinstance(gc_bounds, tuple):
        if gc_bounds[0] < GC_MIN or gc_bounds[1] > GC_MAX:
            logger.warning("GC bounds must be in range " f"{GC_MIN} - {GC_MAX}")
            return None
    elif gc_bounds < GC_MIN or gc_bounds > GC_MAX:
        logger.warning("GC bounds must be in range " f"{GC_MIN} - {GC_MAX}")
        return None

    if isinstance(length_bounds, tuple):
        if length_bounds[0] < 0:
            logger.warning("Length bounds must be >= 0")
            return None
    elif length_bounds < 0:
        logger.warning("Length bounds must be >= 0")
        return None

    if quality_threshold < 0:
        logger.warning("Quality threshold must be >= 0")
        return None

    return True


def _count_gc(seq: str) -> int:
    """Calculate GC percentage for a nucleotide sequence.

    Args:
        seq (str): Nucleotide sequence (A/C/G/T).

    Returns:
        int: GC content as an integer percentage (0-100).
    """
    atgc_stat = Counter(seq.upper())
    gc_value = (
        atgc_stat[Nucleotide.Guanine.value]
        + atgc_stat[Nucleotide.Cytosine.value]
    )
    return round((gc_value / len(seq)) * 100)


def _is_filter_bounds(
    seq: str,
    _bounds: Union[int, tuple[int, int]],
    indicator: Callable,
) -> bool:
    """Check if an indicator value for a sequence fits within bounds.

    Args:
        seq (str): Sequence to evaluate.
        _bounds (Union[int, tuple[int, int]]): Either an upper bound (int) or
            (min, max) tuple.
        indicator (Callable[[str], int]): Function that maps the sequence to a
            numeric value.

    Returns:
        bool: True if the indicator value is within the bounds, otherwise
        False.
    """
    measurable_value = indicator(seq)
    if isinstance(_bounds, tuple):
        min_length, max_length = _bounds
        return min_length <= measurable_value <= max_length
    else:
        return measurable_value <= _bounds


def _count_quality(quality_seq: str) -> int:
    """Compute mean Phred quality score for a quality string.

    Args:
        quality_seq (str): FASTQ quality string (ASCII offset 33 mapping).

    Returns:
        int: Rounded mean Phred score.
    """
    mean_score = sum(
        map(lambda quality: ord(quality) - PHRED_SCORE, quality_seq)
    ) / len(quality_seq)
    return round(mean_score)


def _is_filter_quality(quality_seq: str, quality_threshold: int) -> bool:
    """Check if mean quality meets the threshold.

    Args:
        quality_seq (str): FASTQ quality string.
        quality_threshold (int): Minimal acceptable mean Phred score.

    Returns:
        bool: True if mean quality >= threshold, otherwise False.
    """
    return _count_quality(quality_seq) >= quality_threshold


def _is_filter_seq(
    sequence: str,
    quality_seq: str,
    gc_bounds: Union[int, tuple[int, int]],
    length_bounds: Union[int, tuple[int, int]],
    quality_threshold: int,
) -> bool:
    """Apply GC, length, and quality filters to a sequence record.

    Args:
        sequence (str): Nucleotide sequence.
        quality_seq (str): Corresponding quality string.
        gc_bounds (Union[int, tuple[int, int]]): GC percent upper bound or
            (min, max) bounds.
        length_bounds (Union[int, tuple[int, int]]): Length upper bound or
            (min, max) bounds.
        quality_threshold (int): Minimal acceptable mean Phred score.

    Returns:
        bool: True if the record passes all filters, otherwise False.
    """
    return all(
        [
            _is_filter_bounds(sequence, gc_bounds, _count_gc),
            _is_filter_bounds(sequence, length_bounds, len),
            _is_filter_quality(quality_seq, quality_threshold),
        ]
    )


def fastq_filter(
    input_fastq: str,
    output_fastq: str,
    gc_bounds: Union[int, tuple[int, int]],
    length_bounds: Union[int, tuple[int, int]],
    quality_threshold: int,
    serializer: Serializer,
):
    """Filter FASTQ sequences by GC content, length, and quality.

    Args:
        input_fastq (str): Path to an input FASTQ file.
        output_fastq (str): Path to an output directory.
        gc_bounds (Union[int, tuple[int, int]]): GC percent upper bound or
            (min, max) bounds.
        length_bounds (Union[int, tuple[int, int]]): Length upper bound or
            (min, max) bounds.
        quality_threshold (int): Minimal acceptable mean Phred score.
        serializer (Serializer): Serializer object.

    Returns:
        None
    """
    conditions = checking_conditions(
        input_fastq, output_fastq, gc_bounds, length_bounds, quality_threshold
    )
    if not conditions:
        return None

    not_passed, passed = 0, 0
    filename = f'filtered_{datetime.now().strftime("%Y%m%d%H%M%S")}.fastq'

    for seq_item in parse_fastq(input_fastq):
        is_passed = _is_filter_seq(
            seq_item.sequence,
            seq_item.quality,
            gc_bounds,
            length_bounds,
            quality_threshold,
        )
        if is_passed:
            _data = serializer.serialize(seq_item)
            if _data is None:
                continue
            write_data(
                output_dir=output_fastq,
                filename=filename,
                _data=_data,
                use_filtered=True,
            )
            passed += 1
        else:
            not_passed += 1
    print(f"Filtered {not_passed} sequences. Saved {passed} sequences.")
    if passed == 0:
        print("No sequences passed the filter.")
