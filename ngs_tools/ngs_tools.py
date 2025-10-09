from logging import getLogger
from typing import Optional, Union

from ngs_tools.dna_rna_tools import (
    IS_NUCLEIC_ACID_TOOL,
    NUCLEIC_ACID_TYPE,
    TOOLS_MAPPER,
    composite_error_message,
    is_check_as_nucleic_acid,
    is_valid_instrument,
    is_valid_seq,
)
from ngs_tools.filter_fastq import checking_conditions, fastq_tools
from ngs_tools.utils import Serializer

serializer = Serializer()

logger = getLogger(__name__)


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
    input_fastq: str,
    output_fastq: str,
    gc_bounds: Union[int, tuple[int, int]] = (0, 100),
    length_bounds: Union[int, tuple[int, int]] = (0, 2**32),
    quality_threshold: int = 0,
) -> None:
    """Validate inputs and filter FASTQ records by GC, length, and quality.

    This is a thin wrapper over fastq_tools.fastq_filter with input checks.

    Args:
        input_fastq (str): Path to an input FASTQ file.
        output_fastq (str): Path to an output directory.
        gc_bounds (Union[int, tuple[int, int]]): GC percent bound or (min,
            max) bounds.
        length_bounds (Union[int, tuple[int, int]]): Length bound or (min,
            max) bounds.
        quality_threshold (int): Minimal acceptable mean Phred score.

    Returns:
        None. Filtered sequences are written to output directory.
    """
    conditions = checking_conditions(
        input_fastq, output_fastq, gc_bounds, length_bounds, quality_threshold
    )
    if not conditions:
        return None

    fastq_tools.fastq_filter(
        input_fastq,
        output_fastq,
        gc_bounds,
        length_bounds,
        quality_threshold,
        serializer,
    )


def bio_files_processor(): ...
