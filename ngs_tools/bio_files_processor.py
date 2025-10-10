import os
from typing import Optional

from ngs_tools.bio_files_processor import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
    select_genes_from_gbk_to_fasta_,
    Extension,
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
            PREFIX
            + os.path.basename(input_fastq)
            + '.'
            + Extension.FASTA.value,
        )
        print(
            f'You don\'t put path to output file. '
            f'Your output file is taken to {output_fastq}'
        )

    convert_multiline_fasta_to_oneline_(input_fastq, output_fastq)


def parse_blast_output(input_file: str, output_file: str) -> None:
    parse_blast_output_(input_file, output_file)


def select_genes_from_gbk_to_fasta(
    input_gbk: str,
    genes: str | list[str],
    output_fasta: str,
    n_before: int = 1,
    n_after: int = 1,
) -> None:
    select_genes_from_gbk_to_fasta_(
        input_gbk, genes, output_fasta, n_before, n_after
    )
