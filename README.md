# NGS Tools

Small Python utilities for basic sequence handling and simple file-based helpers.

What is in this repo:
- Sequence classes (DNA/RNA/protein) with slicing and validation
- Simple FASTQ filtering by GC%, length and mean Phred quality
- Helpers for common text formats (FASTA normalization, BLAST text parsing)

Version: 0.0.1

## Requirements

- Python 3.12+

## Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install .
```

## Public API

This repo is not a single consolidated library API anymore. Use the modules
directly:

```python
from bio_seq import DNASequence, RNASequence, AminoAcidSequence
from fastq_filter import filter_fastq
from ngs_tools.bioinf_tools import (
    convert_multiline_fasta_to_oneline_,
    parse_blast_output_,
)
```

## Sequence classes

Sequence classes live in `bio_seq.py`.

Class tree:

```
BiologicalSequence (abstract)
  BioSeq
    NucleicAcidSequence (non-instantiable)
      DNASequence
      RNASequence
    AminoAcidSequence
```

Notes:
- The underlying sequence is stored uppercased.
- Indexing returns a single symbol, slicing returns an object of the same class.
- `NucleicAcidSequence` cannot be instantiated directly and raises `NotImplementedError`.

### DNA

```python
from bio_seq import DNASequence

dna = DNASequence("ATGCGATCG")
print(len(dna))
print(dna[0])
print(dna[0:3])
print(dna.complement())
print(dna.reverse())
print(dna.reverse_complement())
print(dna.transcribe())
```

### RNA

```python
from bio_seq import RNASequence

rna = RNASequence("AUGCGAUCG")
print(rna.complement())
print(rna.reverse_complement())
```

### Protein

```python
from bio_seq import AminoAcidSequence

protein = AminoAcidSequence("MKTAYIAKQRQISFVK")
print(protein.compute_molecular_weight())
```

## FASTQ filtering

`filter_fastq` (in `fastq_filter.py`) expects:
- `input_fastq`: a FASTQ file
- `output_fastq`: an existing directory

The function writes `filtered_<timestamp>.fastq` into that directory.

```python
from fastq_filter import filter_fastq

filter_fastq(
    input_fastq="reads.fastq",
    output_fastq="./out",
    gc_bounds=(40, 60),
    length_bounds=(50, 250),
    quality_threshold=30,
)
```

## Bio file helpers

### Convert multi-line FASTA to one-line FASTA

```python
from ngs_tools.bioinf_tools import convert_multiline_fasta_to_oneline_
from ngs_tools.utils.serializers import Serializer

convert_multiline_fasta_to_oneline_("input.fasta", "output.fasta", Serializer())
```

### Parse BLAST text output

```python
from ngs_tools.bioinf_tools import parse_blast_output_

parse_blast_output_("blast_output.txt", "descriptions.txt")
```

## Project layout (current)

```
ngs_tools/
  __init__.py
  bioinf_tools/
  common/
  utils/
bio_seq.py
fastq_filter.py
```

