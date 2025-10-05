# NGS Tools

Lightweight Python utilities for working with nucleic acid sequences (DNA/RNA) and filtering FASTQ reads by GC content, length, and mean quality.

- Validate DNA/RNA sequences
- Transcribe DNA to RNA, reverse, complement, and reverse-complement
- Filter FASTQ records by GC%, length, and mean Phred quality

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

This library exposes two main entry points: `run_dna_rna_tools` (sequence utilities) and `filter_fastq` (FASTQ filtering).

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

### 2) FASTQ filtering

`filter_fastq` validates inputs and delegates to the core FASTQ filter.

Arguments:
- `seqs`: dict[str, tuple[str, str]] mapping read id -> (sequence, quality_string)
- `gc_bounds`: either an `int` (upper bound) or a `(min, max)` tuple, in percent
- `length_bounds`: either an `int` (upper bound) or a `(min, max)` tuple
- `quality_threshold`: minimal acceptable mean Phred score (integer)

```python
from ngs_tools import filter_fastq

seqs = {
    "read1": ("ATGCATGC", "IIIIIIII"),  # 'I' (ASCII 73) ~ Q40 in this mapping
    "read2": ("AAAA", "!!!!"),           # '!' (ASCII 33) ~ Q0
    "read3": ("GCGC", "####"),           # '#' (ASCII 35) ~ Q2
}

filtered = filter_fastq(
    seqs,
    gc_bounds=(40, 60),       # keep reads with 40–60% GC
    length_bounds=(4, 100),   # keep reads length between 4 and 100
    quality_threshold=30,     # keep reads with mean Q >= 30
)

print(filtered)
# Example output (dict with reads that passed all filters)
```

Notes:
- Returns a dict (possibly empty) of the reads that passed filtering, or `None` if validation fails.
- Prints how many reads were filtered out.

## Project layout

```
ngs_tools/
  __init__.py                 # public API: run_dna_rna_tools, filter_fastq
  ngs_tools.py                # wrappers and validation for exposed functions
  dna_rna_tools/
    __init__.py
    dna_rna_tools.py          # core sequence utilities (transcribe, complement, ...)
    constants.py              # alphabets and mappings
    errors.py                 # user-facing messages
  filter_fastq/
    __init__.py
    fastq_tools.py            # GC/length/quality filtering logic
    constants.py              # thresholds and score map
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

