"""
Report generation for technical debt analysis.
"""
import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import TextIO
from models import AggregatedMetrics, DebtItem

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate various report formats for technical debt analysis."""
    
    @staticmethod
    def generate_markdown_report(
        metrics: AggregatedMetrics,
        output_path: str
    ) -> None:
        """
        Generate a markdown report.
        
        Args:
            metrics: AggregatedMetrics to report on
            output_path: Path to write the markdown file
        """
        logger.info(f"Generating markdown report: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            ReportGenerator._write_markdown_header(f)
            ReportGenerator._write_executive_summary(f, metrics)
            ReportGenerator._write_priority_items(f, metrics)
            ReportGenerator._write_category_breakdown(f, metrics)
            ReportGenerator._write_repository_rankings(f, metrics)
            ReportGenerator._write_severity_distribution(f, metrics)
            ReportGenerator._write_footer(f)
        
        logger.info(f"Markdown report written successfully to {output_path}")
    
    @staticmethod
    def generate_json_report(
        metrics: AggregatedMetrics,
        output_path: str
    ) -> None:
        """
        Generate a JSON report.
        
        Args:
            metrics: AggregatedMetrics to report on
            output_path: Path to write the JSON file
        """
        logger.info(f"Generating JSON report: {output_path}")
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_debt_items": metrics.total_debt_items,
                "total_repos": metrics.total_repos,
                "average_severity": metrics.average_severity,
                "average_priority": metrics.average_priority
            },
            "category_counts": metrics.category_counts,
            "severity_distribution": {
                str(k): v for k, v in metrics.severity_distribution.items()
            },
            "top_priority_items": [
                {
                    "repo_name": repo_name,
                    "id": item.id,
                    "category": item.category,
                    "title": item.title,
                    "severity": item.severity,
                    "urgency": item.urgency,
                    "effort": item.effort,
                    "priority_score": item.priority_score,
                    "description": item.description,
                    "root_cause": item.root_cause,
                    "impact": item.impact,
                    "suggested_actions": item.suggested_actions
                }
                for repo_name, item in metrics.top_priority_items
            ],
            "repos_by_priority": [
                {"repo_name": name, "total_priority_score": score}
                for name, score in metrics.repos_by_priority
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"JSON report written successfully to {output_path}")
    
    @staticmethod
    def generate_csv_report(
        metrics: AggregatedMetrics,
        output_path: str
    ) -> None:
        """
        Generate a CSV report of all priority items.
        
        Args:
            metrics: AggregatedMetrics to report on
            output_path: Path to write the CSV file
        """
        logger.info(f"Generating CSV report: {output_path}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Repo Name',
                'ID',
                'Category',
                'Title',
                'Severity',
                'Urgency',
                'Effort',
                'Priority Score',
                'Root Cause',
                'Impact',
                'Suggested Actions'
            ])
            
            # Rows
            for repo_name, item in metrics.top_priority_items:
                writer.writerow([
                    repo_name,
                    item.id,
                    item.category,
                    item.title,
                    item.severity,
                    item.urgency,
                    item.effort,
                    item.priority_score,
                    item.root_cause,
                    item.impact,
                    '; '.join(item.suggested_actions)
                ])
        
        logger.info(f"CSV report written successfully to {output_path}")
    
    # Markdown report helper methods
    
    @staticmethod
    def _write_markdown_header(f: TextIO) -> None:
        """Write markdown report header."""
        f.write("# Technical Debt Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
    
    @staticmethod
    def _write_executive_summary(f: TextIO, metrics: AggregatedMetrics) -> None:
        """Write executive summary section."""
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Repositories Analyzed:** {metrics.total_repos}\n")
        f.write(f"- **Total Debt Items Identified:** {metrics.total_debt_items}\n")
        f.write(f"- **Average Severity:** {metrics.average_severity:.2f} / 5.0\n")
        f.write(f"- **Average Priority Score:** {metrics.average_priority:.2f} / 100\n\n")
    
    @staticmethod
    def _write_priority_items(f: TextIO, metrics: AggregatedMetrics) -> None:
        """Write top priority items section."""
        f.write("## Top Priority Items\n\n")
        f.write("These items should be addressed first based on severity, urgency, and effort.\n\n")
        
        for idx, (repo_name, item) in enumerate(metrics.top_priority_items, 1):
            f.write(f"### {idx}. {item.title}\n\n")
            f.write(f"**Repository:** {repo_name}  \n")
            f.write(f"**Category:** {item.category}  \n")
            f.write(f"**Priority Score:** {item.priority_score:.2f} / 100  \n")
            f.write(f"**Severity:** {ReportGenerator._severity_badge(item.severity)}  \n")
            f.write(f"**Urgency:** {item.urgency}/5  \n")
            f.write(f"**Effort:** {item.effort}/5  \n\n")
            
            f.write(f"**Description:** {item.description}\n\n")
            
            if item.root_cause:
                f.write(f"**Root Cause:** {item.root_cause}\n\n")
            
            if item.impact:
                f.write(f"**Impact:** {item.impact}\n\n")
            
            if item.suggested_actions:
                f.write("**Suggested Actions:**\n")
                for action in item.suggested_actions:
                    f.write(f"- {action}\n")
                f.write("\n")
            
            f.write("---\n\n")
    
    @staticmethod
    def _write_category_breakdown(f: TextIO, metrics: AggregatedMetrics) -> None:
        """Write category breakdown section."""
        f.write("## Category Breakdown\n\n")
        
        if not metrics.category_counts:
            f.write("No categories found.\n\n")
            return
        
        # Sort by count descending
        sorted_categories = sorted(
            metrics.category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        f.write("| Category | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        
        for category, count in sorted_categories:
            percentage = (count / metrics.total_debt_items) * 100
            f.write(f"| {category} | {count} | {percentage:.1f}% |\n")
        
        f.write("\n")
    
    @staticmethod
    def _write_repository_rankings(f: TextIO, metrics: AggregatedMetrics) -> None:
        """Write repository rankings section."""
        f.write("## Repository Rankings\n\n")
        f.write("Repositories ranked by total priority score (higher = more urgent debt).\n\n")
        
        f.write("| Rank | Repository | Total Priority Score |\n")
        f.write("|------|------------|---------------------|\n")
        
        for rank, (repo_name, score) in enumerate(metrics.repos_by_priority, 1):
            f.write(f"| {rank} | {repo_name} | {score:.2f} |\n")
        
        f.write("\n")
    
    @staticmethod
    def _write_severity_distribution(f: TextIO, metrics: AggregatedMetrics) -> None:
        """Write severity distribution section."""
        f.write("## Severity Distribution\n\n")
        
        if not metrics.severity_distribution:
            f.write("No severity data available.\n\n")
            return
        
        f.write("| Severity | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        
        for severity in range(5, 0, -1):  # 5 to 1
            count = metrics.severity_distribution.get(severity, 0)
            percentage = (count / metrics.total_debt_items) * 100 if metrics.total_debt_items > 0 else 0
            severity_label = ReportGenerator._severity_label(severity)
            f.write(f"| {severity} - {severity_label} | {count} | {percentage:.1f}% |\n")
        
        f.write("\n")
    
    @staticmethod
    def _write_footer(f: TextIO) -> None:
        """Write markdown report footer."""
        f.write("---\n\n")
        f.write("*Report generated by Technical Debt Analyzer (Rule-Based)*\n")
    
    @staticmethod
    def _severity_badge(severity: int) -> str:
        """Generate a severity badge string."""
        badges = {
            5: "🔴 Critical (5/5)",
            4: "🟠 High (4/5)",
            3: "🟡 Medium (3/5)",
            2: "🟢 Low (2/5)",
            1: "⚪ Minimal (1/5)"
        }
        return badges.get(severity, f"{severity}/5")
    
    @staticmethod
    def _severity_label(severity: int) -> str:
        """Get severity label."""
        labels = {
            5: "Critical",
            4: "High",
            3: "Medium",
            2: "Low",
            1: "Minimal"
        }
        return labels.get(severity, "Unknown")
