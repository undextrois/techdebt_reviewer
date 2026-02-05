"""
CLI interface for technical debt analysis tool (Rule-Based version).
No LLM required - uses pattern matching and keyword analysis.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import List

from models import RepoDebtSummary
from rule_based_extractor import RuleBasedExtractor
from parser import MarkdownParser
from scoring import DebtScorer, DebtAggregator
from report import ReportGenerator


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Technical Debt Analyzer (Rule-Based) - No LLM required',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  td-analyze-rules --input-dir ./reviews
  
  # Specify custom output paths
  td-analyze-rules --input-dir ./reviews --output-md report.md --output-json report.json
  
  # Test with limited files
  td-analyze-rules --input-dir ./reviews --max-files 5
  
Note: This version uses pattern matching and does not require Ollama or any LLM.
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='Directory containing Markdown code review summaries'
    )
    
    # Output arguments
    parser.add_argument(
        '--output-md',
        type=str,
        default='technical_debt_report.md',
        help='Path for the Markdown report (default: technical_debt_report.md)'
    )
    
    parser.add_argument(
        '--output-json',
        type=str,
        default=None,
        help='Path for JSON export (optional)'
    )
    
    parser.add_argument(
        '--output-csv',
        type=str,
        default=None,
        help='Path for CSV export (optional)'
    )
    
    # Processing options
    parser.add_argument(
        '--max-files',
        type=int,
        default=None,
        help='Maximum number of files to process (for testing)'
    )
    
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top priority items to highlight (default: 10)'
    )
    
    # Flags
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse files but do not write output files'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='Continue processing even if some files fail'
    )
    
    return parser.parse_args()


def process_markdown_files(
    md_files: List[Path],
    extractor: RuleBasedExtractor,
    skip_errors: bool = False
) -> List[RepoDebtSummary]:
    """
    Process markdown files and extract debt summaries.
    
    Args:
        md_files: List of markdown file paths
        extractor: RuleBasedExtractor instance
        skip_errors: Continue processing if extraction fails
        
    Returns:
        List of RepoDebtSummary objects
    """
    logger = logging.getLogger(__name__)
    repo_summaries = []
    
    for idx, md_file in enumerate(md_files, 1):
        logger.info(f"Processing file {idx}/{len(md_files)}: {md_file.name}")
        
        try:
            # Read the file
            content, repo_name = MarkdownParser.read_markdown_file(md_file)
            
            if not content:
                logger.warning(f"Skipping empty file: {md_file}")
                continue
            
            # Extract debt summary using rule-based approach
            debt_summary = extractor.extract_debt_summary(content, repo_name)
            
            if debt_summary and debt_summary.debt_items:
                # Score the debt items
                DebtScorer.score_repo_summary(debt_summary)
                repo_summaries.append(debt_summary)
                logger.info(
                    f"Successfully extracted {len(debt_summary.debt_items)} "
                    f"debt items from {repo_name}"
                )
            else:
                logger.warning(f"No debt items found in {md_file}")
        
        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}")
            if not skip_errors:
                raise
    
    return repo_summaries


def main() -> int:
    """
    Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("Technical Debt Analyzer (Rule-Based - No LLM Required)")
    logger.info("=" * 80)
    
    try:
        # Discover markdown files
        logger.info(f"Scanning directory: {args.input_dir}")
        md_files = MarkdownParser.discover_markdown_files(args.input_dir, args.max_files)
        
        if not md_files:
            logger.error("No markdown files found to process")
            return 1
        
        logger.info(f"Found {len(md_files)} markdown files to process")
        
        # Initialize rule-based extractor
        logger.info("Using rule-based extraction (pattern matching + keywords)")
        extractor = RuleBasedExtractor()
        
        # Process files
        logger.info("Starting extraction and analysis...")
        repo_summaries = process_markdown_files(md_files, extractor, args.skip_errors)
        
        if not repo_summaries:
            logger.error("No debt summaries were successfully extracted")
            return 1
        
        logger.info(f"Successfully processed {len(repo_summaries)} repositories")
        
        # Aggregate metrics
        logger.info("Aggregating metrics...")
        metrics = DebtAggregator.aggregate_metrics(repo_summaries, top_n=args.top_n)
        
        logger.info(f"Total debt items identified: {metrics.total_debt_items}")
        logger.info(f"Categories: {', '.join(metrics.category_counts.keys())}")
        
        # Generate reports
        if args.dry_run:
            logger.info("DRY RUN: Skipping report generation")
            logger.info(f"Would write Markdown report to: {args.output_md}")
            if args.output_json:
                logger.info(f"Would write JSON report to: {args.output_json}")
            if args.output_csv:
                logger.info(f"Would write CSV report to: {args.output_csv}")
        else:
            # Markdown report (always generated)
            logger.info("Generating Markdown report...")
            ReportGenerator.generate_markdown_report(metrics, args.output_md)
            
            # JSON report (optional)
            if args.output_json:
                logger.info("Generating JSON report...")
                ReportGenerator.generate_json_report(metrics, args.output_json)
            
            # CSV report (optional)
            if args.output_csv:
                logger.info("Generating CSV report...")
                ReportGenerator.generate_csv_report(metrics, args.output_csv)
            
            logger.info("=" * 80)
            logger.info("Report generation complete!")
            logger.info(f"Markdown report: {args.output_md}")
            if args.output_json:
                logger.info(f"JSON report: {args.output_json}")
            if args.output_csv:
                logger.info(f"CSV report: {args.output_csv}")
            logger.info("=" * 80)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
