from dataclasses import dataclass


@dataclass
class Fasta:
    """Simple container for a FASTA record (header and sequence)."""

    name: str = ''
    sequence: str = ''

    @property
    def is_exists(self) -> bool:
        """Return True if both header and sequence are present."""
        return bool(self.name and self.sequence)


@dataclass
class Fastq(Fasta):
    """FASTA plus quality line for FASTQ format."""

    quality: str = ''
