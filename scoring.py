"""
Scoring and aggregation for technical debt items.
"""
import logging
from typing import List
from models import DebtItem, RepoDebtSummary, AggregatedMetrics

logger = logging.getLogger(__name__)


class DebtScorer:
    """Score technical debt items based on multiple factors."""
    
    # Weights for priority calculation
    SEVERITY_WEIGHT = 0.5
    URGENCY_WEIGHT = 0.3
    EFFORT_WEIGHT = 0.2  # Lower effort = higher priority
    
    @classmethod
    def calculate_priority_score(
        cls,
        severity: int,
        urgency: int,
        effort: int
    ) -> float:
        """
        Calculate priority score from component scores.
        
        Higher scores mean higher priority. Effort is inverted so that
        lower effort items get higher priority (quick wins).
        
        Args:
            severity: Severity score (1-5)
            urgency: Urgency score (1-5)
            effort: Effort score (1-5)
            
        Returns:
            Priority score (0-100)
        """
        # Normalize to 0-1 scale
        norm_severity = severity / 5.0
        norm_urgency = urgency / 5.0
        norm_effort = (6 - effort) / 5.0  # Invert: lower effort = higher priority
        
        # Weighted sum
        score = (
            norm_severity * cls.SEVERITY_WEIGHT +
            norm_urgency * cls.URGENCY_WEIGHT +
            norm_effort * cls.EFFORT_WEIGHT
        )
        
        # Scale to 0-100
        return round(score * 100, 2)
    
    @classmethod
    def score_debt_item(cls, item: DebtItem) -> None:
        """
        Calculate and set the priority score for a debt item.
        
        Args:
            item: DebtItem to score (modified in place)
        """
        item.priority_score = cls.calculate_priority_score(
            item.severity,
            item.urgency,
            item.effort
        )
    
    @classmethod
    def score_repo_summary(cls, repo_summary: RepoDebtSummary) -> None:
        """
        Score all debt items in a repository summary.
        
        Args:
            repo_summary: RepoDebtSummary to score (modified in place)
        """
        for item in repo_summary.debt_items:
            cls.score_debt_item(item)
        
        # Update total priority score
        repo_summary.total_priority_score = sum(
            item.priority_score for item in repo_summary.debt_items
        )
        
        logger.debug(
            f"Scored {len(repo_summary.debt_items)} items for {repo_summary.repo_name}, "
            f"total priority: {repo_summary.total_priority_score:.2f}"
        )


class DebtAggregator:
    """Aggregate metrics across multiple repositories."""
    
    @staticmethod
    def aggregate_metrics(
        repo_summaries: List[RepoDebtSummary],
        top_n: int = 10
    ) -> AggregatedMetrics:
        """
        Aggregate metrics from multiple repository summaries.
        
        Args:
            repo_summaries: List of RepoDebtSummary objects
            top_n: Number of top priority items to include
            
        Returns:
            AggregatedMetrics object
        """
        logger.info(f"Aggregating metrics from {len(repo_summaries)} repositories")
        
        # Collect all debt items with repo context
        all_items_with_repo = [
            (repo.repo_name, item)
            for repo in repo_summaries
            for item in repo.debt_items
        ]
        
        total_items = len(all_items_with_repo)
        
        if total_items == 0:
            logger.warning("No debt items to aggregate")
            return AggregatedMetrics(
                total_debt_items=0,
                total_repos=len(repo_summaries)
            )
        
        # Category counts
        category_counts = {}
        for _, item in all_items_with_repo:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Severity distribution
        severity_distribution = {}
        for _, item in all_items_with_repo:
            severity_distribution[item.severity] = (
                severity_distribution.get(item.severity, 0) + 1
            )
        
        # Top priority items across all repos
        top_priority_items = sorted(
            all_items_with_repo,
            key=lambda x: x[1].priority_score,
            reverse=True
        )[:top_n]
        
        # Repos ranked by total priority score
        repos_by_priority = sorted(
            [
                (repo.repo_name, repo.total_priority_score)
                for repo in repo_summaries
            ],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate averages
        average_severity = sum(
            item.severity for _, item in all_items_with_repo
        ) / total_items
        
        average_priority = sum(
            item.priority_score for _, item in all_items_with_repo
        ) / total_items
        
        logger.info(
            f"Aggregated {total_items} items from {len(repo_summaries)} repos. "
            f"Avg severity: {average_severity:.2f}, Avg priority: {average_priority:.2f}"
        )
        
        return AggregatedMetrics(
            total_debt_items=total_items,
            total_repos=len(repo_summaries),
            category_counts=category_counts,
            severity_distribution=severity_distribution,
            top_priority_items=top_priority_items,
            repos_by_priority=repos_by_priority,
            average_severity=round(average_severity, 2),
            average_priority=round(average_priority, 2)
        )
