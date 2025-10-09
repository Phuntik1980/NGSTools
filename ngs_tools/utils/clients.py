import os
from logging import getLogger
from typing import Generator

from ngs_tools.filter_fastq.dto import FastqRecord

from .constants import DEFAULT_FILTERED_DIR
from .serializers import serialize_fastq

logger = getLogger(__name__)


def read_fastq(input_fastq: str) -> Generator[str]:
    try:
        with open(input_fastq, "r") as f:
            for item in f.read():
                yield item
    except FileNotFoundError:
        logger.warning(f"Input file {input_fastq} does not exist")
        return None


def write_fastq(output_fastq: str, filename: str, fastq: FastqRecord):
    filtered_dir = os.path.join(
        os.path.dirname(output_fastq), DEFAULT_FILTERED_DIR
    )
    if not os.path.exists(filtered_dir):
        os.makedirs(filtered_dir)

    with open(os.path.join(filtered_dir, filename), "a") as f:
        f.write(serialize_fastq(fastq))
