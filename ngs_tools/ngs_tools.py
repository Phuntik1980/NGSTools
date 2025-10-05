from typing import Optional, Union

from ngs_tools.dna_rna_tools import (
    is_valid_seq,
    is_valid_instrument,
    NUCLEIC_ACID_TYPE,
    TOOLS_MAPPER,
    IS_NUCLEIC_ACID_TOOL,
    is_check_as_nucleic_acid,
    composite_error_message,
)
from ngs_tools.filter_fastq import fastq_tools, GC_MIN, GC_MAX


def run_dna_rna_tools(*args) -> Union[Optional[NUCLEIC_ACID_TYPE], bool]:
    """Run a DNA/RNA utility on one or more sequences.

    If tool is "is_nucleic_acid", validation is applied directly; otherwise
    each sequence is first checked to be a nucleic acid.

    Args:
        *nucleic_acids (NUCLEIC_ACID_TYPE): One or more sequences to process.
        tool (str): Tool name from TOOLS_MAPPER.

    Returns:
        Union[Optional[NUCLEIC_ACID_TYPE], bool]: For a single input: single
        result of the tool. For multiple inputs: list of results. Returns None
        if validation fails.
    """
    *nucleic_acids, tool = args
    conditions = is_valid_seq(*nucleic_acids) and is_valid_instrument(tool)
    if not conditions:
        print(composite_error_message.format(TOOLS_MAPPER.keys()))
        return None

    result = []

    for nucleic_acid in nucleic_acids:
        if tool == IS_NUCLEIC_ACID_TOOL:
            result.append(TOOLS_MAPPER[tool](nucleic_acid))
        else:
            if is_check_as_nucleic_acid(nucleic_acid):
                result.append(TOOLS_MAPPER[tool](nucleic_acid))
            return None

    return result[0] if len(result) == 1 else result


def filter_fastq(
    seqs: Optional[fastq_tools.FASTQ_TYPE],
    gc_bounds: Union[int, tuple[int, int]] = (0, 100),
    length_bounds: Union[int, tuple[int, int]] = (0, 2**32),
    quality_threshold: int = 0,
) -> Optional[fastq_tools.FASTQ_TYPE]:
    """Validate inputs and filter FASTQ records by GC, length, and quality.

    This is a thin wrapper over fastq_tools.fastq_filter with input checks.

    Args:
        seqs (Optional[FASTQ_TYPE]): Mapping from id to (sequence, quality)
            tuples.
        gc_bounds (Union[int, tuple[int, int]]): GC percent bound or (min,
            max) bounds.
        length_bounds (Union[int, tuple[int, int]]): Length bound or (min,
            max) bounds.
        quality_threshold (int): Minimal acceptable mean Phred score.

    Returns:
        Optional[FASTQ_TYPE]: Filtered dict of sequences or None if
        validation fails.
    """
    if not seqs:
        print("No sequences provided")
        return None

    if isinstance(gc_bounds, tuple):
        if gc_bounds[0] < GC_MIN or gc_bounds[1] > GC_MAX:
            print("GC bounds must be in range " f"{GC_MIN} - {GC_MAX}")
            return None
    elif gc_bounds < GC_MIN or gc_bounds > GC_MAX:
        print("GC bounds must be in range " f"{GC_MIN} - {GC_MAX}")
        return None

    if isinstance(length_bounds, tuple):
        if length_bounds[0] < 0:
            print("Length bounds must be >= 0")
            return None
    elif length_bounds < 0:
        print("Length bounds must be >= 0")
        return None

    if quality_threshold < 0:
        print("Quality threshold must be >= 0")
        return None

    return fastq_tools.fastq_filter(
        seqs, gc_bounds, length_bounds, quality_threshold
    )
