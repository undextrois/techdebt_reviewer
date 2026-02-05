# Technical Debt Analyzer (Rule-Based)

A lightweight technical debt analysis tool that uses pattern matching and keyword analysis to identify and prioritize technical debt from code review documents. **No LLM required.**

## Features

- **Rule-based extraction**: Uses pattern matching and keyword analysis
- **Multiple output formats**: Markdown, JSON, and CSV reports
- **Priority scoring**: Combines severity, urgency, and effort metrics
- **Category classification**: Automatically categorizes debt items
- **Aggregated metrics**: Cross-repository analysis and rankings
- **Zero external dependencies**: Uses only Python standard library

## Installation

```bash
# Clone or download the project
cd technical-debt-analyzer

# No dependencies to install! (optional: install dev dependencies)
pip install -r requirements.txt  # Only for development tools
```

## Usage

### Basic Usage

```bash
python cli_rules.py --input-dir ./reviews
```

This will:
- Scan `./reviews` for markdown files
- Extract technical debt items
- Generate `technical_debt_report.md`

### Advanced Usage

```bash
# Generate all report formats
python cli_rules.py \
  --input-dir ./reviews \
  --output-md report.md \
  --output-json report.json \
  --output-csv report.csv \
  --top-n 15

# Test with limited files
python cli_rules.py --input-dir ./reviews --max-files 5 --verbose

# Dry run (no output files)
python cli_rules.py --input-dir ./reviews --dry-run

# Continue on errors
python cli_rules.py --input-dir ./reviews --skip-errors
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-dir` | Directory containing markdown files | Required |
| `--output-md` | Path for markdown report | `technical_debt_report.md` |
| `--output-json` | Path for JSON report | None |
| `--output-csv` | Path for CSV report | None |
| `--max-files` | Limit number of files to process | None (all) |
| `--top-n` | Number of top priority items | 10 |
| `--dry-run` | Parse but don't write output | False |
| `--verbose` / `-v` | Enable debug logging | False |
| `--skip-errors` | Continue on file errors | False |

## Input Format

The tool expects markdown files containing code review summaries with sections like:

```markdown
# Project Code Review

## Security
- SQL injection vulnerability in user input handling
- Hardcoded API credentials in config file

## Performance
- N+1 query problem in data fetching loop
- Missing database indexes on frequently queried columns

## Testing
- No unit tests for core business logic
- Integration tests missing for API endpoints
```

## Output Reports

### Markdown Report

Human-readable report with:
- Executive summary
- Top priority items (detailed)
- Category breakdown
- Repository rankings
- Severity distribution

### JSON Report

Machine-readable format with:
- Summary metrics
- All top priority items with full details
- Category and severity distributions
- Repository rankings

### CSV Report

Spreadsheet-compatible format with one row per debt item.

## How It Works

1. **File Discovery**: Recursively finds all `.md` files in input directory
2. **Section Extraction**: Parses markdown structure and content
3. **Issue Detection**: Identifies bullet points and numbered items
4. **Categorization**: Maps issues to categories using keyword matching
5. **Scoring**: Calculates severity, urgency, and effort scores
6. **Prioritization**: Computes priority scores (0-100)
7. **Aggregation**: Combines data across all repositories
8. **Report Generation**: Creates formatted output files

## Categories

The tool recognizes these debt categories:

- **testing**: Missing tests, low coverage, test quality
- **security**: Vulnerabilities, auth issues, input validation
- **performance**: Bottlenecks, inefficiencies, resource usage
- **architecture**: Design issues, coupling, structure
- **docs**: Missing or outdated documentation
- **code_quality**: Code smells, maintainability, style
- **bugs**: Logic errors, edge cases, potential defects
- **tooling**: Build, CI/CD, automation, configuration

## Priority Scoring

Priority is calculated using weighted factors:

```
Priority = (Severity × 0.5) + (Urgency × 0.3) + (Inverted Effort × 0.2)
```

- **Severity** (1-5): Impact and consequences
- **Urgency** (1-5): Time sensitivity
- **Effort** (1-5): Implementation cost (inverted: lower effort = higher priority)

Result is scaled to 0-100 for easy interpretation.

## Project Structure

```
.
├── cli_rules.py              # Main CLI interface
├── rule_based_extractor.py   # Pattern matching & extraction logic
├── models.py                 # Data models
├── parser.py                 # Markdown parsing utilities
├── scoring.py                # Scoring and aggregation
├── report.py                 # Report generation
├── requirements.txt          # Dependencies (dev only)
└── README.md                 # This file
```

## Development

### Running Tests

```bash
pytest tests/ -v --cov
```

### Code Formatting

```bash
black *.py
flake8 *.py
mypy *.py
```

## Limitations

- Relies on structured markdown input
- Keyword-based categorization may miss nuanced cases
- Scoring is heuristic-based, not context-aware
- Cannot understand complex technical descriptions

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Please:
1. Keep changes simple and focused
2. Follow existing code style
3. Add tests for new features
4. Update documentation as needed
