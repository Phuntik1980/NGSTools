from dataclasses import dataclass
from typing import Any

from ngs_tools.filter_fastq.dto import FastqRecord


@dataclass
class Serializer:

    def __post_init__(self):
        self.mapper = {
            FastqRecord: self.fastq_serializer,
        }

    @staticmethod
    def fastq_serializer(fastq: FastqRecord) -> str:
        return (
            f"{fastq.name}\n{fastq.sequence}\n"
            f"+{fastq.name[1:]}\n{fastq.quality}\n"
        )

    def serialize(self, data: Any) -> str:
        return self.mapper[type(data)](data)
