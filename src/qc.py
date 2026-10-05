"""
Quality Control engine — validates sequences and flags potential issues.

Status levels: PASS, REVIEW, INVALID
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Set

from .analyzer import AnalysisResult
from .parser import FASTARecord

logger = logging.getLogger(__name__)


@dataclass
class QCResult:
    """Quality control result for a single sequence."""

    record_id: str
    status: str  # PASS, REVIEW, INVALID
    flags: List[str] = field(default_factory=list)


class QualityChecker:
    """Runs QC checks on analysis results."""

    # Thresholds (can be configured)
    MAX_LENGTH = 100_000          # Flag sequences longer than this
    AMBIGUOUS_WARN_THRESHOLD = 0.10  # >10% ambiguous → REVIEW
    MIN_LENGTH = 1

    def __init__(
        self,
        max_length: int = MAX_LENGTH,
        ambiguous_warn_threshold: float = AMBIGUOUS_WARN_THRESHOLD,
    ) -> None:
        self.max_length = max_length
        self.ambiguous_warn_threshold = ambiguous_warn_threshold

    def check(
        self, result: AnalysisResult, all_records: List[FASTARecord]
    ) -> QCResult:
        """
        Run all QC checks on a single result.

        Args:
            result: Analysis result to check.
            all_records: All records in the batch (for duplicate ID detection).

        Returns:
            QCResult with status and flags.
        """
        flags: List[str] = []
        status = "PASS"

        # Check 1: Valid result
        if not result.valid:
            flags.append(f"INVALID: {result.error}")
            status = "INVALID"
            return QCResult(record_id=result.record_id, status=status, flags=flags)

        # Check 2: Empty sequence
        if result.length < self.MIN_LENGTH:
            flags.append("Empty sequence")
            status = "INVALID"

        # Check 3: Too long
        if result.length > self.max_length:
            flags.append(
                f"Sequence length {result.length:,} exceeds recommended "
                f"maximum of {self.max_length:,}"
            )
            if status == "PASS":
                status = "REVIEW"

        # Check 4: High ambiguity
        if result.length > 0:
            ambig_ratio = result.ambiguous_count / result.length
            if ambig_ratio > self.ambiguous_warn_threshold:
                flags.append(
                    f"High ambiguous content: {ambig_ratio:.1%} "
                    f"(threshold: {self.ambiguous_warn_threshold:.0%})"
                )
                if status == "PASS":
                    status = "REVIEW"

        # Check 5: Duplicate IDs
        dup_ids = self._find_duplicate_ids(all_records)
        if result.record_id in dup_ids:
            flags.append("Duplicate sequence ID detected")
            if status == "PASS":
                status = "REVIEW"

        # Check 6: Unknown type
        if result.sequence_type == "UNKNOWN":
            flags.append("Sequence type could not be determined")
            if status == "PASS":
                status = "REVIEW"

        return QCResult(record_id=result.record_id, status=status, flags=flags)

    @staticmethod
    def _find_duplicate_ids(records: List[FASTARecord]) -> Set[str]:
        """Find duplicate record IDs across the batch."""
        seen: Set[str] = set()
        duplicates: Set[str] = set()
        for rec in records:
            if rec.record_id in seen:
                duplicates.add(rec.record_id)
            seen.add(rec.record_id)
        return duplicates
