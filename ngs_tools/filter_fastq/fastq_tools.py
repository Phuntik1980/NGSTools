from typing import Optional, Union, Callable
from collections import Counter
from ngs_tools.filter_fastq.constants import Nucleotide, QUALITY_SCORE

FASTQ_TYPE = dict[str, tuple[str, str]]


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


def _count_length(seq: str) -> int:
    """Return sequence length.

    Args:
        seq (str): Nucleotide sequence.

    Returns:
        int: Length of the sequence.
    """
    return len(seq)


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
        map(lambda quality: QUALITY_SCORE[ord(quality)], quality_seq)
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
            _is_filter_bounds(sequence, length_bounds, _count_length),
            _is_filter_quality(quality_seq, quality_threshold),
        ]
    )


def fastq_filter(
    seqs: FASTQ_TYPE,
    gc_bounds: Union[int, tuple[int, int]],
    length_bounds: Union[int, tuple[int, int]],
    quality_threshold: int,
) -> Optional[FASTQ_TYPE]:
    """Filter FASTQ sequences by GC content, length, and quality.

    Args:
        seqs (FASTQ_TYPE): Mapping from sequence id to (sequence, quality)
            tuple.
        gc_bounds (Union[int, tuple[int, int]]): GC percent upper bound or
            (min, max) bounds.
        length_bounds (Union[int, tuple[int, int]]): Length upper bound or
            (min, max) bounds.
        quality_threshold (int): Minimal acceptable mean Phred score.

    Returns:
        Optional[FASTQ_TYPE]: A dict of sequences that passed filters (might be
        empty). Prints the number of filtered-out sequences.
    """
    filtered = {}
    not_passed = 0
    for seq_id, (seq, quality_seq) in seqs.items():
        is_passed = _is_filter_seq(
            seq, quality_seq, gc_bounds, length_bounds, quality_threshold
        )
        if is_passed:
            filtered[seq_id] = (seq, quality_seq)
        else:
            not_passed += 1
    print(f"Filtered {not_passed} sequences")
    return filtered
