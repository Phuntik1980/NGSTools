"""Thin IO helpers used across the package.

- read_data: stream lines from a text file with graceful warning on missing
- write_data: append string data to a file path (optionally into 'filtered' dir)

"""

import os
from logging import getLogger
from typing import Generator

from .constants import DEFAULT_FILTERED_DIR

logger = getLogger(__name__)


def read_data(input_path_to: str) -> Generator[str, None, None]:
    """Yield file lines one-by-one.

    Args:
        input_path_to (str): Path to a readable text file.

    Yields:
        str: Next line including trailing newline characters.

    Notes:
        Logs a warning and returns if the file does not exist.
    """
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
    """Append string data to a target file, creating dirs if needed.

    Args:
        output_dir (str): Directory where the file resides (or will be created).
        filename (str): File name to append to.
        _data (str): Already-formatted text to write.
        use_filtered (bool): If True, write into sibling 'filtered' directory.
    """
    path_to_save = os.path.join(output_dir, filename)
    if use_filtered:
        filtered_dir = os.path.join(
            os.path.dirname(output_dir), DEFAULT_FILTERED_DIR
        )
        if not os.path.exists(filtered_dir):
            os.makedirs(filtered_dir)
        path_to_save = os.path.join(filtered_dir, filename)

    with open(path_to_save, "a") as f:
        f.write(_data)
