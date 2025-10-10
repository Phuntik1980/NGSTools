import os
from typing import Optional

from ngs_tools.bio_files_processor import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
    FASTA_EXT,
    PREFIX,
)


def convert_multiline_fasta_to_oneline(
    input_fastq: str, output_fastq: Optional[str]
) -> None:
    if not input_fastq or not os.path.isfile(input_fastq):
        return None

    if not output_fastq or not os.path.isfile(output_fastq):
        output_fastq = os.path.join(
            os.path.dirname(input_fastq),
            PREFIX + os.path.basename(input_fastq) + '.' + FASTA_EXT,
        )
        print(
            f'You don\'t put path to output file. '
            f'Your output file is taken to {output_fastq}'
        )

    convert_multiline_fasta_to_oneline_(input_fastq, output_fastq)


def parse_blast_output(input_file: str, output_file: str) -> None:
    if not input_file or not os.path.isfile(input_file):
        print('You don\'t put path to input file')
        return None

    if not output_file or not os.path.isfile(output_file):
        print('You don\'t put path to output file')
        return None

    parse_blast_output_(input_file, output_file)
