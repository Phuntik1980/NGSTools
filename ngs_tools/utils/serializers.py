from ngs_tools.filter_fastq.dto import FastqRecord


def serialize_fastq(fastq: FastqRecord) -> str:
    return (
        f"{fastq.name}\n{fastq.sequence}\n+{fastq.name[1:]}\n{fastq.quality}\n"
    )
