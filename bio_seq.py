from abc import ABC, abstractmethod

from ngs_tools.constants import (
    AMINO_ACID_WATER_LOSS,
    BIOSEQ_STR_ELLIPSIS,
    BIOSEQ_STR_MAX_LEN,
    BIOSEQ_STR_PREFIX_LEN,
)


class BiologicalSequence(ABC):
    """Abstract interface for biological sequences.

    Implementations must behave like a read-only sequence:
    - `__len__` returns the number of symbols
    - `__getitem__` supports indexing and slicing
    - `__str__` returns a user-facing representation
    - `is_valid_alphabet` checks that symbols belong to the allowed alphabet
    """

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def is_valid_alphabet(self):
        pass


class BioSeq(BiologicalSequence):
    """Base class for sequence-like objects backed by a string.

    The sequence is stored uppercased. Subclasses define `ALPHABET`.
    """

    __ALPHABET: set[str]

    def __init__(self, sequence: str):
        self._sequence = sequence.upper()

    def __len__(self):
        return len(self._sequence)

    def __getitem__(self, index):
        result = self._sequence[index]
        if isinstance(index, slice):
            return self.__class__(result)
        return result

    def __str__(self):
        class_name = self.__class__.__name__
        length = self.__len__()
        if length > BIOSEQ_STR_MAX_LEN:
            display_seq = (
                self._sequence[:BIOSEQ_STR_PREFIX_LEN] + BIOSEQ_STR_ELLIPSIS
            )
        else:
            display_seq = self._sequence
        return (
            f"{class_name}(\n"
            f"  sequence = {display_seq}\n"
            f"  length   = {length}\n"
            f"  valid    = {self.is_valid_alphabet()}\n"
            f")"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._sequence}')"

    def is_valid_alphabet(self) -> bool:
        """Return `True` if all symbols in the sequence belong to `ALPHABET`."""
        return set(self._sequence).issubset(self.__ALPHABET)


class NucleicAcidSequence(BioSeq):
    """Common functionality for DNA/RNA sequences.

    The class is intentionally non-instantiable. Concrete subclasses must
    provide:
    - `ALPHABET`
    - `COMPLEMENT_MAP`
    """

    __COMPLEMENT_MAP = {}
    __ALPHABET = set()

    def __init__(self, sequence: str):
        if self.__class__ is NucleicAcidSequence:
            raise NotImplementedError(
                "Cannot instantiate abstract class NucleicAcidSequence directly"
            )
        super().__init__(sequence)

    def complement(self) -> "NucleicAcidSequence":
        """Return the complementary strand.

        Raises:
            ValueError: If the sequence contains symbols outside `ALPHABET`.
        """
        if not self.is_valid_alphabet():
            raise ValueError(
                f"Invalid alphabet in sequence: "
                f"{set(self._sequence) - self.ALPHABET}"
            )
        complemented = "".join(
            self.__COMPLEMENT_MAP[base] for base in self._sequence
        )
        return self.__class__(complemented)

    def reverse(self) -> "NucleicAcidSequence":
        """Return the sequence reversed (5'->3' order is flipped)."""
        return self.__class__(self._sequence[::-1])

    def reverse_complement(self) -> "NucleicAcidSequence":
        """Return the reverse-complement of the sequence."""
        return self.complement().reverse()


class DNASequence(NucleicAcidSequence):
    """DNA sequence limited to the canonical alphabet A/T/G/C."""

    __ALPHABET = {"A", "T", "G", "C"}
    __COMPLEMENT_MAP = {"A": "T", "T": "A", "G": "C", "C": "G"}

    def transcribe(self) -> "RNASequence":
        """Transcribe DNA to RNA by replacing thymine (`T`) with uracil (`U`).

        Returns:
            RNASequence: The transcribed RNA sequence.

        Raises:
            ValueError: If the sequence contains symbols outside the DNA
                alphabet.
        """
        if not self.is_valid_alphabet():
            raise ValueError(
                f"Invalid alphabet in sequence: "
                f"{set(self._sequence) - self.ALPHABET}"
            )
        rna_sequence = self._sequence.replace("T", "U")
        return RNASequence(rna_sequence)


class RNASequence(NucleicAcidSequence):
    """RNA sequence limited to the canonical alphabet A/U/G/C."""

    __ALPHABET = {"A", "U", "G", "C"}
    __COMPLEMENT_MAP = {"A": "U", "U": "A", "G": "C", "C": "G"}


class AminoAcidSequence(BioSeq):
    """Protein sequence for the 20 standard amino acids.

    Provides a convenience method to compute the peptide molecular weight.
    """

    __ALPHABET = set("ACDEFGHIKLMNPQRSTVWY")

    MOLECULAR_WEIGHTS = {
        "A": 89.09,
        "C": 121.16,
        "D": 133.10,
        "E": 147.13,
        "F": 165.19,
        "G": 75.03,
        "H": 155.16,
        "I": 131.17,
        "K": 146.19,
        "L": 131.17,
        "M": 149.21,
        "N": 132.12,
        "P": 115.13,
        "Q": 146.15,
        "R": 174.20,
        "S": 105.09,
        "T": 119.12,
        "V": 117.15,
        "W": 204.23,
        "Y": 181.19,
    }

    def __init__(self, sequence: str):
        super().__init__(sequence)

    def compute_molecular_weight(self) -> float:
        """Compute molecular weight of the peptide in Dalton.

        Uses a simple residue-sum model and subtracts water loss for peptide
        bonds.

        Raises:
            ValueError: If the sequence contains symbols outside `ALPHABET`.
        """
        if not self.is_valid_alphabet():
            raise ValueError(
                f"Invalid amino acids in sequence: "
                f"{set(self._sequence) - self.__ALPHABET}"
            )
        weight = sum(self.MOLECULAR_WEIGHTS[aa] for aa in self._sequence)
        water_loss = (len(self._sequence) - 1) * AMINO_ACID_WATER_LOSS
        return round(weight - water_loss, 2)
