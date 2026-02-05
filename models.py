"""
Data models for technical debt analysis.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DebtItem:
    """Represents a single technical debt item."""
    
    id: str
    category: str
    title: str
    description: str
    severity: int = 3  # 1-5 scale
    urgency: int = 3  # 1-5 scale
    effort: int = 3  # 1-5 scale
    priority_score: float = 0.0  # Calculated from severity, urgency, effort
    root_cause: str = ""
    impact: str = ""
    suggested_actions: List[str] = field(default_factory=list)
    file_location: Optional[str] = None
    
    def __post_init__(self):
        """Validate field values."""
        self.severity = max(1, min(5, self.severity))
        self.urgency = max(1, min(5, self.urgency))
        self.effort = max(1, min(5, self.effort))


@dataclass
class RepoDebtSummary:
    """Summary of technical debt for a single repository."""
    
    repo_name: str
    summary: str
    debt_items: List[DebtItem] = field(default_factory=list)
    total_priority_score: float = 0.0
    
    def __post_init__(self):
        """Calculate total priority score."""
        if self.debt_items:
            self.total_priority_score = sum(
                item.priority_score for item in self.debt_items
            )


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across all repositories."""
    
    total_debt_items: int
    total_repos: int
    category_counts: Dict[str, int] = field(default_factory=dict)
    severity_distribution: Dict[int, int] = field(default_factory=dict)
    top_priority_items: List[tuple] = field(default_factory=list)  # (repo_name, DebtItem)
    repos_by_priority: List[tuple] = field(default_factory=list)  # (repo_name, total_score)
    average_severity: float = 0.0
    average_priority: float = 0.0
