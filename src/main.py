"""
BioSyn FASTA Batch Analyzer
A local-first batch FASTA sequence analysis tool for molecular biology researchers.

Supports DNA / RNA / Protein batch analysis with automatic sequence type detection,
quality control, and CSV / XLSX / HTML export.

Built by BioSyn Inc. — https://biosyn-inc.com/
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .parser import FASTAParser, FASTARecord
from .analyzer import SequenceAnalyzer, AnalysisResult
from .qc import QualityChecker, QCResult
from .exporter import export_results

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure application logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def discover_fasta_files(input_path: Path, recursive: bool = True) -> List[Path]:
    """
    Discover FASTA files from a file or directory path.

    Args:
        input_path: File or directory to scan.
        recursive: Whether to recursively scan subdirectories.

    Returns:
        List of discovered FASTA file paths.
    """
    extensions = {".fasta", ".fa", ".fna", ".faa", ".txt"}
    files: List[Path] = []

    if input_path.is_file():
        if input_path.suffix.lower() in extensions:
            files.append(input_path)
        else:
            logger.warning("Input file extension not recognized: %s", input_path)
    elif input_path.is_dir():
        pattern = "**/*" if recursive else "*"
        for f in input_path.glob(pattern):
            if f.is_file() and f.suffix.lower() in extensions:
                files.append(f)
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")

    logger.info("Discovered %d FASTA file(s)", len(files))
    return files


def run_analysis(
    input_path: Path,
    output_dir: Path,
    seq_type: str = "auto",
    recursive: bool = True,
) -> Dict[str, Any]:
    """
    Run the full batch analysis pipeline.

    Args:
        input_path: Input file or directory.
        output_dir: Output directory for reports.
        seq_type: Sequence type override ('auto', 'DNA', 'RNA', 'PROTEIN').
        recursive: Recursive directory scan.

    Returns:
        Summary dictionary with analysis statistics.
    """
    # Step 1: Discover files
    files = discover_fasta_files(input_path, recursive=recursive)
    if not files:
        raise ValueError("No FASTA files found in the input path.")

    # Step 2: Parse all records
    parser = FASTAParser()
    records: List[FASTARecord] = []
    parse_errors: List[Dict[str, str]] = []

    for file_path in files:
        try:
            parsed = parser.parse_file(file_path)
            records.extend(parsed)
            logger.info("Parsed %d records from %s", len(parsed), file_path.name)
        except Exception as exc:
            logger.error("Failed to parse %s: %s", file_path, exc)
            parse_errors.append({"file": str(file_path), "error": str(exc)})

    logger.info("Total records parsed: %d", len(records))

    # Step 3: Analyze each sequence
    analyzer = SequenceAnalyzer(override_type=seq_type if seq_type != "auto" else None)
    results: List[AnalysisResult] = []

    for record in records:
        try:
            result = analyzer.analyze(record)
            results.append(result)
        except Exception as exc:
            logger.error("Analysis failed for %s: %s", record.record_id, exc)
            results.append(AnalysisResult(
                record_id=record.record_id,
                source_file=record.source_file,
                sequence_type="UNKNOWN",
                length=0,
                valid=False,
                error=str(exc),
            ))

    # Step 4: Quality control
    checker = QualityChecker()
    qc_results: List[QCResult] = []
    for result in results:
        qc = checker.check(result, records)
        qc_results.append(qc)

    # Step 5: Export
    output_dir.mkdir(parents=True, exist_ok=True)
    export_results(results, qc_results, parse_errors, output_dir)

    # Step 6: Summary
    summary = {
        "files_processed": len(files),
        "sequences_processed": len(records),
        "pass": sum(1 for q in qc_results if q.status == "PASS"),
        "review": sum(1 for q in qc_results if q.status == "REVIEW"),
        "invalid": sum(1 for q in qc_results if q.status == "INVALID"),
        "parse_errors": len(parse_errors),
    }
    logger.info("Analysis complete: %s", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="biosyn-fasta",
        description="BioSyn FASTA Batch Analyzer — local-first batch sequence analysis.",
        epilog="Built by BioSyn Inc. — https://biosyn-inc.com/",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze = subparsers.add_parser("analyze", help="Analyze FASTA files in batch")
    analyze.add_argument("input", type=Path, help="Input FASTA file or directory")
    analyze.add_argument(
        "--output", "-o", type=Path, default=Path("./results"),
        help="Output directory (default: ./results)",
    )
    analyze.add_argument(
        "--type", "-t", choices=["auto", "DNA", "RNA", "PROTEIN"], default="auto",
        help="Force sequence type (default: auto-detect)",
    )
    analyze.add_argument(
        "--no-recursive", action="store_true",
        help="Do not scan subdirectories recursively",
    )
    analyze.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    subparsers.add_parser("about", help="Show about / methods information")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    setup_logging(verbose=getattr(args, "verbose", False))

    if args.command == "about":
        print("BioSyn FASTA Batch Analyzer v1.0.0")
        print("Built by BioSyn Inc. — https://biosyn-inc.com/")
        print("Methods:")
        print("  - GC% = (G + C) / unambiguous bases × 100")
        print("  - Molecular weight: polymer approximation (single-stranded)")
        print("  - pI: Bjellqvist method (via Biopython ProteinAnalysis)")
        return 0

    if args.command == "analyze":
        try:
            summary = run_analysis(
                input_path=args.input,
                output_dir=args.output,
                seq_type=args.type,
                recursive=not args.no_recursive,
            )
            print(f"\nAnalysis complete: {summary}")
            print(f"Results saved to: {args.output.resolve()}")
            return 0
        except Exception as exc:
            logger.error("Fatal error: %s", exc)
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
