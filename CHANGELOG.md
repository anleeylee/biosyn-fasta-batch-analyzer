# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Batch FASTA file parsing (single file, multi-file, folder recursion)
- Automatic DNA / RNA / Protein sequence type detection with manual override
- DNA analysis: length, base composition, GC%, AT%, molecular weight, reverse complement
- RNA analysis: base composition, GC%, molecular weight
- Protein analysis: amino acid composition, molecular weight, estimated pI (Bjellqvist)
- Quality control: PASS / REVIEW / INVALID with configurable thresholds
- Export to CSV, multi-sheet XLSX, and standalone HTML report
- CLI interface with `analyze` and `about` commands
- Local-first / offline processing, no data upload
