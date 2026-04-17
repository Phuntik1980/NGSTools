import logging
import os
from typing import Optional

from ngs_tools.bioinf_tools import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
    FASTA_EXT,
    PREFIX,
)
from ngs_tools.utils import Serializer

logger = logging.getLogger(__name__)


def convert_multiline_fasta_to_oneline(
    input_fastq: str, output_fastq: Optional[str] = ''
) -> None:
    """Convert a multi-line FASTA file into a one-line-per-sequence FASTA.

    If the output path is not provided, it is created next to the input file
    using the prefix and extension defined in the package constants.

    Args:
        input_fastq (str): Path to the source multi-line FASTA file.
        output_fastq (Optional[str]): Path to the target one-line FASTA file.
            If empty, it will be inferred next to the input file.
    """
    if not input_fastq or not os.path.isfile(input_fastq):
        logger.error("Input FASTA file does not exist: %s", input_fastq)
        return None

    if not output_fastq:
        output_fastq = os.path.join(
            os.path.dirname(input_fastq),
            PREFIX + os.path.basename(input_fastq) + '.' + FASTA_EXT,
        )
        logger.info(
            "Output file path was not provided. Using default path: %s",
            output_fastq,
        )

    logger.info(
        "Converting multi-line FASTA to one-line FASTA: %s -> %s",
        input_fastq,
        output_fastq,
    )
    convert_multiline_fasta_to_oneline_(input_fastq, output_fastq, Serializer())
    return None


def parse_blast_output(input_file: str, output_file: str) -> None:
    """Extract the 'Description' column values from BLAST output.

    The function scans a BLAST text report, collects unique values from the
    description column and writes them as a sorted list.

    Args:
        input_file (str): Path to a BLAST text output file.
        output_file (str): Path to a target text file to write results.
    """
    if not input_file or not os.path.isfile(input_file):
        logger.error("Input BLAST output file does not exist: %s", input_file)
        return None

    if not output_file:
        logger.error("Output file path was not provided")
        return None

    logger.info("Parsing BLAST output: %s -> %s", input_file, output_file)
    parse_blast_output_(input_file, output_file)
    return None
