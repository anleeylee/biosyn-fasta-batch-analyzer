"""Tests for BioSyn FASTA Batch Analyzer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from parser import FASTAParser, FASTARecord
from analyzer import SequenceAnalyzer
from qc import QualityChecker


def test_parse_simple_fasta():
    rec = FASTARecord(record_id="test1", description="", sequence="ATCGATCG", source_file="t.fa")
    assert rec.length == 8


def test_detect_dna():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("dna1", "", "ATCGATCG", "test.fa"))
    assert r.sequence_type == "DNA"
    assert r.gc_percent == 50.0


def test_detect_rna():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("rna1", "", "AUCGAUCG", "test.fa"))
    assert r.sequence_type == "RNA"


def test_gc_percent():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("gc1", "", "GCGCGC", "t.fa"))
    assert r.gc_percent == 100.0


def test_reverse_complement():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("rc1", "", "ATCG", "t.fa"))
    assert r.reverse_complement == "CGAT"


def test_empty_sequence():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("empty", "", "", "t.fa"))
    assert not r.valid


def test_qc_pass():
    a = SequenceAnalyzer()
    c = QualityChecker()
    r = a.analyze(FASTARecord("ok", "", "ATCGATCGATCG", "t.fa"))
    qc = c.check(r, [FASTARecord("ok", "", "ATCGATCGATCG", "t.fa")])
    assert qc.status == "PASS"


def test_protein_analysis():
    a = SequenceAnalyzer()
    r = a.analyze(FASTARecord("p1", "", "MKWVTFISLLFLFSSAYS", "t.faa"))
    assert r.sequence_type == "PROTEIN"
    assert r.length == 18


if __name__ == "__main__":
    test_parse_simple_fasta(); test_detect_dna(); test_detect_rna()
    test_gc_percent(); test_reverse_complement(); test_empty_sequence()
    test_qc_pass(); test_protein_analysis()
    print("All tests passed!")
