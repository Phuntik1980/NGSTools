import os

from ngs_tools.constants import (
    DEFAULT_GC_BOUNDS,
    DEFAULT_LENGTH_BOUNDS,
    DEFAULT_QUALITY_THRESHOLD,
)


def check_filter_fastq_args(
    input_fastq: str,
    output_fastq: str,
    gc_bounds: int | tuple[int, int] = DEFAULT_GC_BOUNDS,
    length_bounds: int | tuple[int, int] = DEFAULT_LENGTH_BOUNDS,
    quality_threshold: int = DEFAULT_QUALITY_THRESHOLD,
) -> bool:
    """Run a minimal sanity-check for `filter_fastq` parameters.

    This helper is intentionally lightweight: it validates only filesystem
    preconditions and basic numeric bounds. The stricter, user-facing
    validation used to live in the legacy implementation and is not replicated
    here.

    Returns:
        `True` if the arguments look usable, otherwise `False`.
    """

    if not input_fastq or input_fastq == output_fastq:
        return False

    if not os.path.isfile(input_fastq):
        return False

    if not os.path.isdir(output_fastq):
        return False

    if isinstance(gc_bounds, tuple):
        if gc_bounds[0] < 0 or gc_bounds[1] > 100:
            return False
    elif gc_bounds < 0 or gc_bounds > 100:
        return False

    if isinstance(length_bounds, tuple):
        if length_bounds[0] < 0:
            return False
    elif length_bounds < 0:
        return False

    if quality_threshold < 0:
        return False

    return True


def value_in_bounds(value: int, bounds: int | tuple[int, int]) -> bool:
    """Return whether `value` satisfies an upper-bound or a `(min, max)` range.

    `bounds` may be either:
    - an `int`, interpreted as a maximum allowed value
    - a `(min, max)` tuple (both inclusive)
    """

    if isinstance(bounds, tuple):
        min_val, max_val = bounds
        return min_val <= value <= max_val
    return value <= bounds


def mean_quality_phred33(qualities: list[int]) -> int:
    """Compute mean per-read quality for Phred+33 encoded FASTQ.

    Biopython exposes FASTQ qualities as integers already decoded from
    the ASCII representation. For our use-case a simple arithmetic mean is
    sufficient.
    """

    if not qualities:
        return 0
    return round(sum(qualities) / len(qualities))
