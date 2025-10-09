from dataclasses import dataclass


@dataclass
class FastqRecord:
    name: str = ''
    sequence: str = ''
    quality: str = ''
