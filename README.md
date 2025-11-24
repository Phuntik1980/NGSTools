# NGS Tools

Lightweight Python utilities for working with nucleic acid sequences (DNA/RNA) and filtering FASTQ reads by GC content, length, and mean quality.

- Validate DNA/RNA sequences
- Transcribe DNA to RNA, reverse, complement, and reverse-complement
- Filter FASTQ records by GC%, length, and mean Phred quality
- Process bioinformatics text files:
  - Convert multi-line FASTA to one-line-per-sequence FASTA
  - Parse BLAST output (collect unique values from Description column)

Version: 0.0.1

## Requirements

- Python 3.12+
- OS: Linux/macOS/Windows

## Installation

Recommended: use a virtual environment.

```bash
# create and activate a virtual environment (example with venv)
python3.12 -m venv .venv
source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate

# install the package
pip install .

# or for development (editable install with tooling)
pip install -e .[dev]
```

## Usage

This library exposes entry points for sequence utilities, FASTQ filtering, and bio-file processing.

### 1) DNA/RNA sequence utilities

```python
from ngs_tools import run_dna_rna_tools

# Available tools:
#  - "is_nucleic_acid"
#  - "transcribe"            # DNA -> RNA (T -> U)
#  - "reverse"
#  - "complement"            # DNA or RNA (auto-detected by presence of U)
#  - "reverse_complement"

# Usage with single sequence
print(run_dna_rna_tools("ATGC", "is_nucleic_acid"))  # True
print(run_dna_rna_tools("ATGC", "transcribe"))       # "UACG"
print(run_dna_rna_tools("ATGc", "reverse"))          # "cGTA"
print(run_dna_rna_tools("ATGC", "complement"))       # "TACG"
print(run_dna_rna_tools("ATGC", "reverse_complement"))  # "CGTA"

# Usage with multiple sequences -> returns a list in the same order
print(run_dna_rna_tools("ATGC", "AUGC", "is_nucleic_acid"))
# [True, True]
```

Notes:
- If you pass an unsupported tool name or no sequences, the function prints a hint and returns `None`.
- For tools other than `is_nucleic_acid`, inputs are validated to be nucleic acids first.

### 2) FASTQ filtering (file-based)

`filter_fastq` validates paths and delegates to the core FASTQ filter which streams input and writes filtered reads into an output directory.

Arguments:
- `input_fastq` (str): path to an input FASTQ file
- `output_fastq` (str): path to an existing output directory (filtered file will be created inside)
- `gc_bounds` (int | tuple[int, int]): GC% upper bound or (min, max)
- `length_bounds` (int | tuple[int, int]): length upper bound or (min, max)
- `quality_threshold` (int): minimal acceptable mean Phred score

```python
from ngs_tools import filter_fastq

filter_fastq(
    input_fastq="reads.fastq",
    output_fastq="./out",           # directory must exist
    gc_bounds=(40, 60),              # keep reads with 40–60% GC
    length_bounds=(50, 250),         # length between 50 and 250
    quality_threshold=30,            # mean Q >= 30
)

# Output: a file like ./out/filtered_YYYYMMDDhhmmss.fastq
# Console: prints how many sequences were filtered and saved
```

Notes:
- Returns `None`. Filtered reads are appended to a generated file in the output directory.
- If validation fails, a warning is printed and nothing is written.

### 3) Bio files processor

Helpers to post-process common bioinformatics text formats.

```python
from ngs_tools.bioinf_tools import FASTA_EXT, PREFIX
from ngs_tools import bioinf_tools as _  # namespace hint
```

Convert multi-line FASTA to one-line-per-sequence:

```python
from ngs_tools.bio_files_processor import convert_multiline_fasta_to_oneline

convert_multiline_fasta_to_oneline(
  input_fastq="input.fasta",
  output_fastq=None,
  # if None, file will be created next to input: f"{PREFIX}{basename}.{FASTA_EXT}"
)
```

Parse BLAST output (collect unique values in the Description column):

```python
from ngs_tools.bio_files_processor import parse_blast_output

parse_blast_output(
  input_file="blast_output.txt",
  output_file="descriptions.txt",
)
```

## Project layout

```
ngs_tools/
  __init__.py                 # public API: run_dna_rna_tools, filter_fastq
  ngs_tools.py                # wrappers and validation for exposed functions
  bio_files_processor/        # FASTA/BLAST helpers (services, constants)
    __init__.py
    services.py
    constants.py
  dna_rna_tools/
    __init__.py
    dna_rna_tools.py          # core sequence utilities (transcribe, complement, ...)
    constants.py              # alphabets and mappings
    errors.py                 # user-facing messages
  filter_fastq/
    __init__.py
    fastq_tools.py            # GC/length/quality filtering logic
    constants.py              # thresholds and score map
  utils/                      # IO, parsers, serializers
    __init__.py
    clients.py
    parsers.py
    serializers.py
  common/
    __init__.py               # simple DTOs: Fasta, Fastq
    dto.py
```

## Development

Install with dev extras and run linters/formatters:

```bash
pip install -e .[dev]
black .
flake8
```

## License

No license specified.

