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


def write_data(
    output_dir: str, filename: str, _data: str, use_filtered: bool = False
) -> None:
    path_to_save = os.path.join(output_dir, filename)
    if use_filtered:
        path_to_save = os.path.join(
            os.path.dirname(output_dir), DEFAULT_FILTERED_DIR
        )
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

    with open(path_to_save, "a") as f:
        f.write(_data)
