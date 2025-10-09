import os
from logging import getLogger
from typing import Generator

from .constants import DEFAULT_FILTERED_DIR

logger = getLogger(__name__)


def read_data(input_path_to: str) -> Generator[str, None, None]:
    try:
        with open(input_path_to, "r") as _fastq:
            for line in _fastq:
                yield line
    except FileNotFoundError:
        logger.warning(f"Input file {input_path_to} does not exist")
        return None


def write_data(output_dir: str, filename: str, _data: str) -> None:
    filtered_dir = os.path.join(
        os.path.dirname(output_dir), DEFAULT_FILTERED_DIR
    )
    if not os.path.exists(filtered_dir):
        os.makedirs(filtered_dir)

    with open(os.path.join(filtered_dir, filename), "a") as f:
        f.write(_data)
