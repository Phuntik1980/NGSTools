import os
from typing import Optional

from ngs_tools.bioinf_tools import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
    FASTA_EXT,
    PREFIX,
)
from ngs_tools.utils import Serializer


def convert_multiline_fasta_to_oneline(
    input_fastq: str, output_fastq: Optional[str] = ''
) -> None:
    """Convert a multi-line FASTA file into a one-line-per-sequence FASTA.

    If output path is not provided, it will be created in the same directory
    as the input with prefix and extension from constants.

    Args:
        input_fastq (str): Path to source multi-line FASTA file.
        output_fastq (Optional[str]): Path to target one-line FASTA file. If
            None or empty, it will be inferred next to the input file.
    """
    if not input_fastq or not os.path.isfile(input_fastq):
        return None

    if not output_fastq:
        output_fastq = os.path.join(
            os.path.dirname(input_fastq),
            PREFIX + os.path.basename(input_fastq) + '.' + FASTA_EXT,
        )
        print(
            "Output file path was not provided. "
            f"Using default path: {output_fastq}"
        )

    convert_multiline_fasta_to_oneline_(input_fastq, output_fastq, Serializer())


def parse_blast_output(input_file: str, output_file: str) -> None:
    """Extract the 'Description' column values from BLAST output.

    This function scans a BLAST text output, collects unique values from the
    description column and writes a sorted list to the output file.

    Args:
        input_file (str): Path to a BLAST text output file.
        output_file (str): Path to a target text file to write results.
    """
    if not input_file or not os.path.isfile(input_file):
        print('You don\'t put path to input file')
        return None

    if not output_file:
        print('You don\'t put path to output file')
        return None

    parse_blast_output_(input_file, output_file)
