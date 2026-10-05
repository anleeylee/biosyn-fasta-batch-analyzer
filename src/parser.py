"""
FASTA file parser — handles single and multi-record FASTA files.

Supports: .fasta, .fa, .fna, .faa, .txt
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FASTARecord:
    """Represents a single FASTA record."""

    record_id: str
    description: str
    sequence: str
    source_file: str = ""

    @property
    def length(self) -> int:
        """Sequence length excluding whitespace."""
        return len(self.sequence.strip())


class FASTAParser:
    """Parser for FASTA-format files."""

    VALID_EXTENSIONS = {".fasta", ".fa", ".fna", ".faa", ".txt"}

    def parse_file(self, file_path: Path) -> List[FASTARecord]:
        """
        Parse a FASTA file and return all records.

        Args:
            file_path: Path to the FASTA file.

        Returns:
            List of FASTARecord objects.

        Raises:
            ValueError: If the file format is invalid.
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        records: List[FASTARecord] = []
        current_id: Optional[str] = None
        current_desc: str = ""
        current_seq_parts: List[str] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
                for line_no, raw_line in enumerate(fh, start=1):
                    line = raw_line.strip()

                    # Skip blank lines
                    if not line:
                        continue

                    # Header line
                    if line.startswith(">"):
                        # Save previous record
                        if current_id is not None:
                            records.append(FASTARecord(
                                record_id=current_id,
                                description=current_desc,
                                sequence="".join(current_seq_parts),
                                source_file=file_path.name,
                            ))

                        # Parse new header
                        header = line[1:].strip()
                        parts = header.split(maxsplit=1)
                        current_id = parts[0] if parts else f"seq_{len(records)+1}"
                        current_desc = parts[1] if len(parts) > 1 else ""
                        current_seq_parts = []
                    else:
                        # Sequence line
                        if current_id is None:
                            raise ValueError(
                                f"Line {line_no}: sequence data before any header. "
                                "FASTA files must start with a '>' header."
                            )
                        current_seq_parts.append(line.upper())

            # Save last record
            if current_id is not None:
                records.append(FASTARecord(
                    record_id=current_id,
                    description=current_desc,
                    sequence="".join(current_seq_parts),
                    source_file=file_path.name,
                ))

        except UnicodeDecodeError as exc:
            raise ValueError(
                f"Encoding error in {file_path}. File may be binary or use "
                f"an unsupported encoding. Original error: {exc}"
            ) from exc

        logger.debug("Parsed %d records from %s", len(records), file_path.name)
        return records
