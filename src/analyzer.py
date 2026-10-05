"""
Sequence analysis engine — computes length, composition, GC%, molecular weight,
reverse complement, and estimated pI for protein sequences.

All calculations are estimates unless otherwise noted.
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

from .parser import FASTARecord

logger = logging.getLogger(__name__)

# IUPAC ambiguity codes
DNA_BASES = set("ACGT")
DNA_AMBIG = set("RYSWKMBDHVN")
RNA_BASES = set("ACGU")
RNA_AMBIG = set("RYSWKMBDHVN")
PROTEIN_AMINO = set("ACDEFGHIKLMNPQRSTVWY")
PROTEIN_AMBIG = set("BXZJUO")

# Approximate molecular weights (g/mol) — single-stranded polymer, monophosphate
# Sources: standard biochemical reference values
MW_DNA = {
    "A": 313.21, "C": 289.18, "G": 329.21, "T": 304.20,
    # Ambiguous bases use average of possible bases
    "N": 308.95, "R": 321.21, "Y": 296.69, "S": 309.20,
    "W": 308.71, "K": 316.71, "M": 301.20,
    "B": 307.53, "D": 315.54, "H": 302.20, "V": 310.53,
}

MW_RNA = {
    "A": 329.21, "C": 305.18, "G": 345.21, "U": 306.20,
    "N": 321.45, "R": 337.21, "Y": 305.69, "S": 325.20,
    "W": 317.71, "K": 325.71, "M": 317.20,
    "B": 318.86, "D": 326.87, "H": 321.20, "V": 326.87,
}

# Amino acid residue weights (g/mol) — average residue weight in polypeptide chain
MW_AA = {
    "A": 89.09, "R": 174.20, "N": 132.12, "D": 133.10,
    "C": 121.16, "E": 147.13, "Q": 146.15, "G": 75.03,
    "H": 155.16, "I": 131.17, "L": 131.17, "K": 146.19,
    "M": 149.21, "F": 165.19, "P": 115.13, "S": 105.09,
    "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15,
}

# Reverse complement mapping
DNA_COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


@dataclass
class AnalysisResult:
    """Result of sequence analysis for a single record."""

    record_id: str
    source_file: str
    sequence_type: str  # DNA, RNA, PROTEIN, UNKNOWN
    length: int
    valid: bool = True
    error: str = ""
    # Base counts
    base_counts: Dict[str, float] = field(default_factory=dict)
    gc_percent: float = 0.0
    at_percent: float = 0.0
    ambiguous_count: int = 0
    molecular_weight: float = 0.0
    reverse_complement: str = ""
    estimated_pi: float = 0.0
    aa_composition: Dict[str, float] = field(default_factory=dict)


class SequenceAnalyzer:
    """Main analysis engine for FASTA records."""

    def __init__(self, override_type: Optional[str] = None) -> None:
        """
        Initialize analyzer.

        Args:
            override_type: If set, force this sequence type ('DNA', 'RNA',
                'PROTEIN') instead of auto-detecting.
        """
        self.override_type = override_type.upper() if override_type else None

    def analyze(self, record: FASTARecord) -> AnalysisResult:
        """
        Analyze a single FASTA record.

        Args:
            record: FASTA record to analyze.

        Returns:
            AnalysisResult with all computed metrics.
        """
        seq = record.sequence.strip().upper()
        result = AnalysisResult(
            record_id=record.record_id,
            source_file=record.source_file,
            sequence_type="UNKNOWN",
            length=len(seq),
        )

        if not seq:
            result.valid = False
            result.error = "Empty sequence"
            return result

        # Detect type
        seq_type = self.override_type or self._detect_type(seq)
        result.sequence_type = seq_type

        if seq_type == "DNA":
            self._analyze_dna(seq, result)
        elif seq_type == "RNA":
            self._analyze_rna(seq, result)
        elif seq_type == "PROTEIN":
            self._analyze_protein(seq, result)
        else:
            result.valid = False
            result.error = "Could not determine sequence type"

        return result

    def _detect_type(self, seq: str) -> str:
        """Auto-detect sequence type from character set."""
        chars = set(seq)
        has_u = "U" in chars
        has_t = "T" in chars
        has_only_na = chars.issubset(DNA_BASES | DNA_AMBIG)

        if has_u and not has_t and chars.issubset(RNA_BASES | RNA_AMBIG):
            return "RNA"
        if has_t and not has_u and chars.issubset(DNA_BASES | DNA_AMBIG):
            return "DNA"
        # If only A/C/G/N present, default to DNA
        if chars.issubset(DNA_BASES | DNA_AMBIG | {"U"}):
            if has_u:
                return "RNA"
            return "DNA"

        # Check protein
        protein_chars = PROTEIN_AMINO | PROTEIN_AMBIG
        if chars.issubset(protein_chars) and not chars.issubset(DNA_BASES | DNA_AMBIG):
            return "PROTEIN"

        return "UNKNOWN"

    def _analyze_dna(self, seq: str, result: AnalysisResult) -> None:
        """Compute DNA-specific metrics."""
        valid_bases = DNA_BASES | DNA_AMBIG
        counts: Dict[str, float] = {}

        for base in "ACGTN":
            counts[base] = float(seq.count(base))

        # Count ambiguous
        ambiguous = sum(seq.count(b) for b in (DNA_AMBIG - {"N"}))
        n_count = counts.get("N", 0.0)
        result.ambiguous_count = int(ambiguous + n_count)

        # Base composition
        result.base_counts = counts

        # GC% based on unambiguous bases
        a, t, g, c = counts["A"], counts["T"], counts["G"], counts["C"]
        unambiguous = a + t + g + c
        if unambiguous > 0:
            result.gc_percent = round((g + c) / unambiguous * 100, 2)
            result.at_percent = round((a + t) / unambiguous * 100, 2)

        # Molecular weight (single-stranded DNA polymer approximation)
        mw = sum(MW_DNA.get(b, 0) for b in seq)
        result.molecular_weight = round(mw, 2)

        # Reverse complement
        result.reverse_complement = seq.translate(DNA_COMPLEMENT)[::-1]

        # Validity check
        invalid_chars = set(seq) - valid_bases
        if invalid_chars:
            result.valid = False
            result.error = f"Invalid characters: {''.join(sorted(invalid_chars))}"

    def _analyze_rna(self, seq: str, result: AnalysisResult) -> None:
        """Compute RNA-specific metrics."""
        counts: Dict[str, float] = {}
        for base in "ACGUN":
            counts[base] = float(seq.count(base))

        ambiguous = sum(seq.count(b) for b in (RNA_AMBIG - {"N"}))
        result.ambiguous_count = int(ambiguous + counts.get("N", 0.0))
        result.base_counts = counts

        a, u, g, c = counts["A"], counts["U"], counts["G"], counts["C"]
        unambiguous = a + u + g + c
        if unambiguous > 0:
            result.gc_percent = round((g + c) / unambiguous * 100, 2)
            result.at_percent = round((a + u) / unambiguous * 100, 2)

        mw = sum(MW_RNA.get(b, 0) for b in seq)
        result.molecular_weight = round(mw, 2)

        invalid_chars = set(seq) - (RNA_BASES | RNA_AMBIG)
        if invalid_chars:
            result.valid = False
            result.error = f"Invalid characters: {''.join(sorted(invalid_chars))}"

    def _analyze_protein(self, seq: str, result: AnalysisResult) -> None:
        """Compute protein-specific metrics."""
        aa_counts: Dict[str, float] = {}
        total = len(seq)

        for aa in sorted(PROTEIN_AMINO):
            aa_counts[aa] = float(seq.count(aa))

        unknown = total - sum(aa_counts.values())
        result.ambiguous_count = unknown
        result.aa_composition = aa_counts

        # Molecular weight
        mw = sum(MW_AA.get(aa, 0) * count for aa, count in aa_counts.items())
        result.molecular_weight = round(mw, 2)

        # Estimated pI (Bjellqvist approximation)
        result.estimated_pi = round(self._estimate_pi(seq), 2)

        invalid_chars = set(seq) - (PROTEIN_AMINO | PROTEIN_AMBIG)
        if invalid_chars:
            result.valid = False
            result.error = f"Invalid amino acids: {''.join(sorted(invalid_chars))}"

    @staticmethod
    def _estimate_pi(seq: str) -> float:
        """
        Estimate isoelectric point using the Bjellqvist method.
        Simplified approximation based on charged residue counts.
        """
        # pKa values (Bjellqvist, 1994 approximation)
        n_term_pka = 9.69
        c_term_pka = 2.34
        k_pka = 10.07  # Lys
        r_pka = 12.48  # Arg
        h_pka = 6.04   # His
        d_pka = 3.65   # Asp
        e_pka = 4.27   # Glu
        c_pka = 8.18   # Cys
        y_pka = 10.46  # Tyr

        # Simple bisection on pH
        def charge_at_ph(ph: float) -> float:
            def frac_protonated(pka: float, ph: float) -> float:
                return 1.0 / (1.0 + 10 ** (ph - pka))

            def frac_deprotonated(pka: float, ph: float) -> float:
                return 1.0 / (1.0 + 10 ** (pka - ph))

            pos = (
                frac_protonated(k_pka, ph) * seq.count("K")
                + frac_protonated(r_pka, ph) * seq.count("R")
                + frac_protonated(h_pka, ph) * seq.count("H")
                + frac_protonated(n_term_pka, ph)  # N-terminus
            )
            neg = (
                frac_deprotonated(d_pka, ph) * seq.count("D")
                + frac_deprotonated(e_pka, ph) * seq.count("E")
                + frac_deprotonated(c_pka, ph) * seq.count("C")
                + frac_deprotonated(y_pka, ph) * seq.count("Y")
                + frac_deprotonated(c_term_pka, ph)  # C-terminus
            )
            return pos - neg

        lo, hi = 0.0, 14.0
        for _ in range(50):
            mid = (lo + hi) / 2
            if charge_at_ph(mid) > 0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
