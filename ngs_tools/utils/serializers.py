from dataclasses import dataclass
from typing import Any

from ngs_tools.filter_fastq.dto import Fastq, Fasta


@dataclass
class Serializer:

    def __post_init__(self):
        self.mapper = {
            Fastq: self.fastq_serializer,
            Fasta: self.fasta_serializer,
        }

    @staticmethod
    def fastq_serializer(fastq: Fastq) -> str:
        return (
            f"{fastq.name}\n{fastq.sequence}\n"
            f"+{fastq.name[1:]}\n{fastq.quality}\n"
        )

    @staticmethod
    def fasta_serializer(fasta: Fasta) -> str:
        return f"{fasta.name}\n{fasta.sequence}\n"

    def serialize(self, data: Any) -> str:
        return self.mapper[type(data)](data)
