from dataclasses import dataclass


@dataclass
class Fasta:
    name: str = ''
    sequence: str = ''

    @property
    def is_exists(self) -> bool:
        return bool(self.name and self.sequence)


@dataclass
class Fastq(Fasta):
    quality: str = ''
