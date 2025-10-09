from enum import Enum

DELIMITER = "\n"
CRLF = "\r"

DEFAULT_FILTERED_DIR = "filtered"


class FastqSign(Enum, str):
    head = "@"
    tail = "+"


class FastqStatus(Enum, str):
    waiting_for_header = "waiting_for_header"
    main_header = "main_header"
    sequence = "sequence"
    second_header = "second_header"
    quality = "quality"
