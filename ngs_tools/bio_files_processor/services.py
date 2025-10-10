import os

from ngs_tools.bio_files_processor.constants import (
    BLAST_AIM_COLUMN,
    BLAST_DESCRIPTION_WIDTH,
)
from ngs_tools.utils import parse_multiline_fasta, read_data, write_data
from ngs_tools.utils.serializers import Serializer


def convert_multiline_fasta_to_oneline_(
    input_fastq: str, output_fastq: str, serializer: Serializer
) -> None:
    output_dir, filename = os.path.split(output_fastq)
    for record in parse_multiline_fasta(input_fastq):
        serialized_data = serializer.serialize(record)

        write_data(
            output_dir=output_dir, filename=filename, _data=serialized_data
        )


def parse_blast_output_(input_file: str, output_file: str):
    output_dir, filename = os.path.split(output_file)
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
