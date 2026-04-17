import contextlib
import io
import sys
from typing import Optional

import click

from bio_seq import AminoAcidSequence, DNASequence, RNASequence
from fastq_filter import filter_fastq
from ngs_tools.bioinf_tools import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
)
from ngs_tools.logging_config import init_logging
from ngs_tools.utils.serializers import Serializer


class _GlobalOptions:
    def __init__(self, verbose: bool, silent: bool, log_path: str):
        self.verbose = verbose
        self.silent = silent
        self.log_path = log_path


def _ctx_settings() -> dict:
    return {"help_option_names": ["-h", "--help"]}


@contextlib.contextmanager
def _maybe_silence_stdout(silent: bool):
    if not silent:
        yield
        return

    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = original_stdout


def _parse_bounds(
    min_value: Optional[int], max_value: Optional[int], default: tuple[int, int]
) -> tuple[int, int]:
    if min_value is None and max_value is None:
        return default
    if min_value is None:
        min_value = default[0]
    if max_value is None:
        max_value = default[1]
    return min_value, max_value


@click.group(context_settings=_ctx_settings())
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Печатать подробные сообщения об ошибках.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    default=False,
    help="Подавлять обычный вывод (stdout).",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, silent: bool) -> None:
    if verbose and silent:
        raise click.UsageError(
            "Нельзя использовать одновременно --verbose и --silent"
        )
    log_path = init_logging(verbose=verbose, silent=silent)
    ctx.obj = _GlobalOptions(verbose=verbose, silent=silent, log_path=log_path)


@cli.group(context_settings=_ctx_settings())
def bio_seq() -> None:
    """Операции над биологическими последовательностями (DNA/RNA/Protein)."""


@bio_seq.command("dna", context_settings=_ctx_settings())
@click.option(
    "-q",
    "--sequence",
    required=True,
    type=str,
    help="DNA-последовательность (A/T/G/C).",
)
@click.option(
    "-a",
    "--action",
    type=click.Choice(
        [
            "validate",
            "complement",
            "reverse",
            "reverse-complement",
            "transcribe",
        ],
        case_sensitive=False,
    ),
    required=True,
    help="Действие над DNA.",
)
@click.pass_obj
def bio_seq_dna(opts: _GlobalOptions, sequence: str, action: str) -> None:
    try:
        dna = DNASequence(sequence)
        with _maybe_silence_stdout(opts.silent):
            if action.lower() == "validate":
                click.echo(str(dna.is_valid_alphabet()))
            elif action.lower() == "complement":
                click.echo(str(dna.complement()))
            elif action.lower() == "reverse":
                click.echo(str(dna.reverse()))
            elif action.lower() == "reverse-complement":
                click.echo(str(dna.reverse_complement()))
            elif action.lower() == "transcribe":
                click.echo(str(dna.transcribe()))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@bio_seq.command("rna", context_settings=_ctx_settings())
@click.option(
    "-q",
    "--sequence",
    required=True,
    type=str,
    help="RNA-последовательность (A/U/G/C).",
)
@click.option(
    "-a",
    "--action",
    type=click.Choice(
        ["validate", "complement", "reverse", "reverse-complement"],
        case_sensitive=False,
    ),
    required=True,
    help="Действие над RNA.",
)
@click.pass_obj
def bio_seq_rna(opts: _GlobalOptions, sequence: str, action: str) -> None:
    try:
        rna = RNASequence(sequence)
        with _maybe_silence_stdout(opts.silent):
            if action.lower() == "validate":
                click.echo(str(rna.is_valid_alphabet()))
            elif action.lower() == "complement":
                click.echo(str(rna.complement()))
            elif action.lower() == "reverse":
                click.echo(str(rna.reverse()))
            elif action.lower() == "reverse-complement":
                click.echo(str(rna.reverse_complement()))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@bio_seq.command("protein", context_settings=_ctx_settings())
@click.option(
    "-q",
    "--sequence",
    required=True,
    type=str,
    help="Аминокислотная последовательность.",
)
@click.option(
    "-a",
    "--action",
    type=click.Choice(["validate", "molecular-weight"], case_sensitive=False),
    required=True,
    help="Действие над белком.",
)
@click.pass_obj
def bio_seq_protein(opts: _GlobalOptions, sequence: str, action: str) -> None:
    try:
        protein = AminoAcidSequence(sequence)
        with _maybe_silence_stdout(opts.silent):
            if action.lower() == "validate":
                click.echo(str(protein.is_valid_alphabet()))
            elif action.lower() == "molecular-weight":
                click.echo(str(protein.compute_molecular_weight()))
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("fastq_filter", context_settings=_ctx_settings())
@click.option(
    "-i",
    "--input-fastq",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Входной FASTQ файл.",
)
@click.option(
    "-o",
    "--output-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Директория для результата.",
)
@click.option(
    "-g", "--gc-min", type=int, default=None, help="Минимальный GC%% (0..100)."
)
@click.option(
    "-G", "--gc-max", type=int, default=None, help="Максимальный GC%% (0..100)."
)
@click.option(
    "-l", "--len-min", type=int, default=None, help="Минимальная длина рида."
)
@click.option(
    "-L", "--len-max", type=int, default=None, help="Максимальная длина рида."
)
@click.option(
    "-q",
    "--quality-threshold",
    type=int,
    default=0,
    show_default=True,
    help="Порог среднего Phred качества.",
)
@click.pass_obj
def fastq_filter_cmd(
    opts: _GlobalOptions,
    input_fastq: str,
    output_dir: str,
    gc_min: Optional[int],
    gc_max: Optional[int],
    len_min: Optional[int],
    len_max: Optional[int],
    quality_threshold: int,
) -> None:
    try:
        gc_bounds = _parse_bounds(gc_min, gc_max, default=(0, 100))
        length_bounds = _parse_bounds(len_min, len_max, default=(0, 2**32))
        with _maybe_silence_stdout(opts.silent):
            filter_fastq(
                input_fastq=input_fastq,
                output_fastq=output_dir,
                gc_bounds=gc_bounds,
                length_bounds=length_bounds,
                quality_threshold=quality_threshold,
            )
    except Exception as exc:
        if opts.verbose:
            raise
        raise click.ClickException(str(exc)) from exc


@cli.group("bioinf_tools", context_settings=_ctx_settings())
def bioinf_tools_group() -> None:
    """Файловые био-информатические утилиты."""


@bioinf_tools_group.command("convert-fasta", context_settings=_ctx_settings())
@click.option(
    "-i",
    "--input-fasta",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Входной multi-line FASTA файл.",
)
@click.option(
    "-o",
    "--output-fasta",
    required=True,
    type=click.Path(dir_okay=False),
    help="Выходной one-line FASTA файл.",
)
@click.pass_obj
def convert_fasta_cmd(
    opts: _GlobalOptions, input_fasta: str, output_fasta: str
) -> None:
    try:
        with _maybe_silence_stdout(opts.silent):
            convert_multiline_fasta_to_oneline_(
                input_fastq=input_fasta,
                output_fastq=output_fasta,
                serializer=Serializer(),
            )
    except Exception as exc:
        if opts.verbose:
            raise
        raise click.ClickException(str(exc)) from exc


@bioinf_tools_group.command("parse-blast", context_settings=_ctx_settings())
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Входной BLAST output (txt).",
)
@click.option(
    "-o",
    "--output-file",
    required=True,
    type=click.Path(dir_okay=False),
    help="Выходной файл со списком Description.",
)
@click.pass_obj
def parse_blast_cmd(
    opts: _GlobalOptions, input_file: str, output_file: str
) -> None:
    try:
        with _maybe_silence_stdout(opts.silent):
            parse_blast_output_(input_file=input_file, output_file=output_file)
    except Exception as exc:
        if opts.verbose:
            raise
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
