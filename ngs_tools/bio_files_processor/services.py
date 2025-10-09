def convert_multiline_fasta_to_oneline_(
    input_fastq: str, output_fastq: str
) -> None: ...


def parse_blast_output_(input_file: str, output_file: str): ...


def select_genes_from_gbk_to_fasta_(
    input_gbk: str,
    genes: str | list[str],
    output_fasta: str,
    n_before: int = 1,
    n_after: int = 1,
): ...
