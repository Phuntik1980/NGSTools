import logging
import os

from ngs_tools.bioinf_tools.constants import (
    BLAST_AIM_COLUMN,
    BLAST_DESCRIPTION_WIDTH,
)
from ngs_tools.utils import parse_multiline_fasta, read_data, write_data
from ngs_tools.utils.serializers import Serializer


logger = logging.getLogger(__name__)


def convert_multiline_fasta_to_oneline_(
    input_fastq: str, output_fastq: str, serializer: Serializer
) -> None:
    """Convert multi-line FASTA to one-line-per-sequence and write to file.

    Iterates over input records and writes them using provided serializer.

    Args:
        input_fastq (str): Path to input multi-line FASTA file.
        output_fastq (str): Path to output FASTA file.
        serializer (Serializer): Serializer to convert DTO into text.
    """
    output_dir, filename = os.path.split(output_fastq)
    logger.info(
        "Writing one-line FASTA to %s (input: %s)",
        output_fastq,
        input_fastq,
    )
    for record in parse_multiline_fasta(input_fastq):
        serialized_data = serializer.serialize(record)

        write_data(
            output_dir=output_dir, filename=filename, _data=serialized_data
        )


def parse_blast_output_(input_file: str, output_file: str):
    """Parse BLAST output and collect unique values from Description column.

    Assumes a BLAST text-like output where the line starting with
    BLAST_AIM_COLUMN is followed by a string whose leading part holds the
    description text. Collected values are sorted and written to output.

    Args:
        input_file (str): Path to text BLAST output.
        output_file (str): Path to destination text file.
    """
    output_dir, filename = os.path.split(output_file)
    logger.info("Parsing BLAST output %s -> %s", input_file, output_file)
    collected_proteins = set()
    waiting_for_aim = False
    for line in read_data(input_file):
        if line.startswith(BLAST_AIM_COLUMN):
            waiting_for_aim = True
        elif waiting_for_aim:
            collected_proteins.add(line[:BLAST_DESCRIPTION_WIDTH].strip())
            waiting_for_aim = False
    collected_proteins = '\n'.join(sorted(collected_proteins))

    write_data(
        output_dir=output_dir, filename=filename, _data=collected_proteins
    )
