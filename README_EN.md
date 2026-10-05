# BioSyn FASTA Batch Analyzer

> **Local-first batch FASTA sequence analysis** — process hundreds of DNA, RNA, and protein sequences at once with automatic QC and CSV/XLSX/HTML export.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Privacy-Offline%20First-orange.svg)](#privacy)

## What It Does

When you have hundreds or thousands of FASTA sequences to analyze, copying them one by one into a web tool is slow and error-prone. **BioSyn FASTA Batch Analyzer** brings the entire workflow to your desktop:

- Drop a folder → auto-scan all `.fasta` / `.fa` / `.fna` / `.faa` / `.txt` files
- Auto-detect DNA / RNA / Protein type (with manual override)
- Compute length, base composition, GC%, molecular weight, reverse complement, pI
- Run quality control (PASS / REVIEW / INVALID) on every sequence
- Export to CSV, multi-sheet XLSX, or a standalone HTML report

> For single-sequence quick calculations online, visit [BioSyn sequence analysis tools](https://biosyn-inc.com/tools/fasta-sequence-analyzer) — this desktop tool is the batch-powered companion.

## Tech Stack

- Python 3.12+
- pandas, openpyxl, matplotlib (optional)
- Standard library: `csv`, `dataclasses`, `argparse`

## Quick Start

```bash
git clone https://github.com/your-org/biosyn-fasta-batch-analyzer.git
cd biosyn-fasta-batch-analyzer
pip install -r requirements.txt

# Analyze a single file
python -m src.main analyze ./examples/sample_sequences.fasta --output ./results

# Scan a whole folder recursively
python -m src.main analyze ./sequences_folder --output ./results
```

## Key Outputs

| File | Content |
|------|---------|
| `fasta_analysis.csv` | One row per sequence: ID, type, length, GC%, MW, QC status |
| `fasta_analysis.xlsx` | Sheets: Summary, Sequence Results, Base Composition, QC, Methods |
| `fasta_qc_report.html` | Browser-openable QC report with stats and flags |
| `invalid_sequences.csv` | Only REVIEW / INVALID sequences for follow-up |

## Methods

| Metric | Formula / Method |
|--------|------------------|
| GC% | `(G + C) / (A + T + G + C) × 100`, unambiguous bases only |
| Molecular Weight | Single-stranded polymer approximation (estimate, not measured) |
| pI | Bjellqvist method, bisection solver |
| Reverse Complement | Standard Watson-Crick complement, 5'→3' reversal |

## Privacy

All processing is local. No sequences are uploaded. No cloud API calls. Your data never leaves your machine.

## Keywords

`FASTA batch analysis`, `DNA sequence analyzer`, `RNA sequence analyzer`, `protein sequence analyzer`, `batch sequence QC`, `GC content calculator`, `molecular weight estimation`, `reverse complement tool`, `local bioinformatics`

## About

Built by [BioSyn Inc.](https://biosyn-inc.com/) — explore more [online sequence analysis tools](https://biosyn-inc.com/tools/fasta-sequence-analyzer) and educational resources.

## License

[MIT](LICENSE)
