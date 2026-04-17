import pytest

from bio_seq import (
    AminoAcidSequence,
    DNASequence,
    NucleicAcidSequence,
    RNASequence,
)
from ngs_tools.bioinf_tools import parse_blast_output_
from ngs_tools.utils import read_data, write_data


def _seq_to_str(seq_obj) -> str:
    return "".join(seq_obj[i] for i in range(len(seq_obj)))


def test_dna_complement_returns_expected_sequence():
    dna = DNASequence("ATGC")
    complement = dna.complement()
    assert _seq_to_str(complement) == "TACG"


def test_dna_transcribe_returns_rna_sequence_and_expected_content():
    dna = DNASequence("ATTGCC")
    rna = dna.transcribe()
    assert isinstance(rna, RNASequence)
    assert _seq_to_str(rna) == "AUUGCC"


def test_rna_reverse_complement_returns_expected_sequence():
    rna = RNASequence("AUGC")
    reverse_complement = rna.reverse_complement()
    assert _seq_to_str(reverse_complement) == "GCAU"


def test_amino_acid_molecular_weight_for_two_residues():
    protein = AminoAcidSequence("AC")
    assert protein.compute_molecular_weight() == 192.23


def test_dna_complement_raises_value_error_for_invalid_alphabet():
    invalid_dna = DNASequence("ATXG")
    with pytest.raises(ValueError):
        invalid_dna.complement()


def test_nucleic_acid_sequence_direct_instantiation_raises_error():
    with pytest.raises(NotImplementedError):
        NucleicAcidSequence("ATGC")


def test_write_data_and_read_data_roundtrip(tmp_path):
    output_dir = tmp_path / "io"
    output_dir.mkdir()
    filename = "sample.txt"

    write_data(str(output_dir), filename, "line1\n")
    write_data(str(output_dir), filename, "line2\n")

    file_path = output_dir / filename
    lines = list(read_data(str(file_path)))
    assert lines == ["line1\n", "line2\n"]


def test_parse_blast_output_writes_sorted_unique_descriptions(tmp_path):
    input_file = tmp_path / "blast_output.txt"
    output_file = tmp_path / "descriptions.txt"

    input_file.write_text(
        "Some header\n"
        "Description\n"
        "Protein B\n"
        "Description\n"
        "Protein A\n"
        "Description\n"
        "Protein B\n"
    )

    parse_blast_output_(str(input_file), str(output_file))

    assert output_file.read_text() == "Protein A\nProtein B"
