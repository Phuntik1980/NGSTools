from typing import Optional, Union
from ngs_tools.dna_rna_tools import errors, constants

NUCLEIC_ACID_TYPE = Union[Optional[str], list[Optional[str]]]


def is_nucleic_acid(seq: str) -> bool:
    """Check if a sequence consists only of valid nucleic acid letters.

    Args:
        seq (str): DNA or RNA sequence string.

    Returns:
        bool: True if the sequence contains only letters from
        NUCLEIC_ACID_LETTERS and is not composed solely of forbidden signs;
        otherwise False.
    """
    seq_letters = set(seq.upper())
    intersection = seq_letters.intersection(constants.NOT_NUCLEIC_ACID_SIGN)
    if len(intersection) == len(constants.NOT_NUCLEIC_ACID_SIGN):
        return False

    for letter in seq_letters:
        if letter not in constants.NUCLEIC_ACID_LETTERS:
            return False

    return True


def _convertor_symbols(seq: str, mapper: dict[str, str]) -> str:
    """Convert sequence symbols using a mapping while preserving case.

    Args:
        seq (str): Input sequence.
        mapper (dict[str, str]): Mapping of uppercase letter to replacement
            letter.

    Returns:
        str: Converted sequence with original character cases preserved.
    """
    converted_seq = ""
    for letter in seq:
        converted_letter = mapper[letter.upper()]
        converted_seq += (
            converted_letter if letter.isupper() else converted_letter.lower()
        )
    return converted_seq


def is_check_as_nucleic_acid(seq: str) -> bool:
    """Validate that a sequence is nucleic acid; print error if not.

    Args:
        seq (str): Sequence to validate.

    Returns:
        bool: True if the sequence is a valid nucleic acid; otherwise False
        (and prints an error message).
    """
    if not is_nucleic_acid(seq):
        print(errors.sequence_not_acid_message.format(seq))
        return False

    return True


def transcribe(seq: str):
    """Transcribe DNA to RNA (T->U). If RNA input, return None and warn.

    Args:
        seq (str): DNA sequence to transcribe.

    Returns:
        Optional[str]: Transcribed RNA sequence, or None if input appears to
        be RNA.
    """
    if constants.RNA_SIGN in set(seq.upper()):
        print(errors.sequence_not_transcribed.format(seq))
        return None

    return _convertor_symbols(seq, constants.TRANSCRIBE)


def reverse(seq: str):
    """Return the reverse of the sequence.

    Args:
        seq (str): Input sequence.

    Returns:
        str: Reversed sequence string.
    """
    return seq[::-1]


def complement(seq: str):
    """Return the complement of a DNA or RNA sequence.

    Chooses DNA or RNA complement rules based on presence of 'U'.

    Args:
        seq (str): Input DNA/RNA sequence.

    Returns:
        str: Complement sequence string.
    """
    if constants.RNA_SIGN in set(seq.upper()):
        complement_mapper = constants.RNA_COMPLEMENT
    else:
        complement_mapper = constants.DNA_COMPLEMENT

    return _convertor_symbols(seq, complement_mapper)


def reverse_complement(seq: str):
    """Return the reverse complement of a sequence.

    Args:
        seq (str): Input DNA/RNA sequence.

    Returns:
        Optional[str]: Reverse complement sequence, or None if complement
        failed.
    """
    complement_seq = complement(seq)

    return reverse(complement_seq) if complement_seq else None


TOOLS_MAPPER = {
    constants.IS_NUCLEIC_ACID_TOOL: is_nucleic_acid,
    "transcribe": transcribe,
    "reverse": reverse,
    "complement": complement,
    "reverse_complement": reverse_complement,
}


def is_valid_seq(*args: NUCLEIC_ACID_TYPE) -> bool:
    """Validate that at least one sequence argument is provided.

    Args:
        *args (NUCLEIC_ACID_TYPE): One or more sequences or lists of
            sequences.

    Returns:
        bool: True if any arguments are provided; otherwise False (and prints
        an error message).
    """
    if not args:
        print(errors.sequence_error_message)
        return False

    return True


def is_valid_instrument(tool: Optional[str]) -> bool:
    """Check that the tool name is provided and supported.

    Args:
        tool (Optional[str]): Name of the tool to execute.

    Returns:
        bool: True if the tool is known; otherwise False (and prints available
        tools).
    """
    if not tool or tool not in TOOLS_MAPPER:
        print(
            errors.tool_error_message.format(
                " \n".join([f'"{name}"' for name in TOOLS_MAPPER])
            ),
        )
        return False

    return True
