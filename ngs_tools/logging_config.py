import logging
import os
from typing import Optional


def init_logging(
    *,
    verbose: bool = False,
    silent: bool = False,
    log_filename: str = "ngs_tools.log",
    log_dir: Optional[str] = None,
) -> str:
    level = logging.DEBUG if verbose else logging.INFO

    if log_dir is None:
        log_dir = os.getcwd()

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return log_path

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [file_handler]

    if not silent:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

    root_logger.setLevel(level)
    for handler in handlers:
        root_logger.addHandler(handler)

    return log_path
