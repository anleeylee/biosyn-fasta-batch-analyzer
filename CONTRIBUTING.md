# Contributing to BioSyn FASTA Batch Analyzer

We welcome contributions! Please follow these guidelines.

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Install dev dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Add or update tests
6. Run tests: `python -m pytest tests/`
7. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Add docstrings for public functions and classes
- Keep functions focused and small

## Adding a New Analysis Metric

1. Add the calculation to `src/analyzer.py`
2. Add the field to `AnalysisResult` dataclass
3. Update `src/exporter.py` to include it in CSV / XLSX / HTML
4. Add a test in `tests/test_analyzer.py`
5. Update the Methods section in the README

## Reporting Issues

Include:
- OS and Python version
- Input file format (sample if possible)
- Full error traceback
- Expected vs. actual behavior

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
