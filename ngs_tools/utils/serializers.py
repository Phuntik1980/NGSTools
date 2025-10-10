from dataclasses import dataclass
from typing import Any

from ngs_tools.common import Fastq, Fasta


@dataclass
class Serializer:
    """Generic serializer that converts DTOs to their textual form.

    The instance builds a simple type -> function mapper in __post_init__
    so that calling serialize(data) picks the right implementation by type.
    """

    def __post_init__(self):
        self.mapper = {
            Fastq: self.fastq_serializer,
            Fasta: self.fasta_serializer,
        }

    @staticmethod
    def fastq_serializer(fastq: Fastq) -> str:
        """Serialize a Fastq record to a 4-line FASTQ block.

        Returns a string with trailing newline suitable for appending to file.
        """
        return (
            f"{fastq.name}\n{fastq.sequence}\n"
            f"+{fastq.name[1:]}\n{fastq.quality}\n"
        )

    @staticmethod
    def fasta_serializer(fasta: Fasta) -> str:
        """Serialize a Fasta record to 2-line FASTA representation."""
        return f"{fasta.name}\n{fasta.sequence}\n"

    def serialize(self, data: Any) -> str:
        """Serialize DTO by its exact type using internal mapper."""
        return self.mapper[type(data)](data)
