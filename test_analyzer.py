"""
Tests for the technical debt analyzer.
"""
import pytest
from models import DebtItem, RepoDebtSummary
from scoring import DebtScorer, DebtAggregator


class TestDebtScorer:
    """Tests for DebtScorer class."""
    
    def test_calculate_priority_score_high_severity(self):
        """Test priority calculation with high severity."""
        score = DebtScorer.calculate_priority_score(
            severity=5,
            urgency=5,
            effort=1  # Low effort
        )
        assert score > 90  # Should be very high priority
    
    def test_calculate_priority_score_low_priority(self):
        """Test priority calculation with low priority."""
        score = DebtScorer.calculate_priority_score(
            severity=1,
            urgency=1,
            effort=5  # High effort
        )
        assert score < 20  # Should be very low priority
    
    def test_score_debt_item(self):
        """Test scoring a single debt item."""
        item = DebtItem(
            id="TEST-001",
            category="testing",
            title="Missing tests",
            description="No unit tests",
            severity=4,
            urgency=3,
            effort=2
        )
        
        DebtScorer.score_debt_item(item)
        assert item.priority_score > 0
        assert item.priority_score <= 100
    
    def test_score_repo_summary(self):
        """Test scoring all items in a repository."""
        items = [
            DebtItem(
                id=f"TEST-{i:03d}",
                category="testing",
                title=f"Issue {i}",
                description=f"Description {i}",
                severity=3,
                urgency=3,
                effort=3
            )
            for i in range(1, 4)
        ]
        
        repo = RepoDebtSummary(
            repo_name="test-repo",
            summary="Test summary",
            debt_items=items
        )
        
        DebtScorer.score_repo_summary(repo)
        
        assert all(item.priority_score > 0 for item in repo.debt_items)
        assert repo.total_priority_score > 0


class TestDebtAggregator:
    """Tests for DebtAggregator class."""
    
    def test_aggregate_metrics_empty(self):
        """Test aggregation with no repositories."""
        metrics = DebtAggregator.aggregate_metrics([], top_n=10)
        assert metrics.total_debt_items == 0
        assert metrics.total_repos == 0
    
    def test_aggregate_metrics_single_repo(self):
        """Test aggregation with one repository."""
        items = [
            DebtItem(
                id="TEST-001",
                category="testing",
                title="Issue 1",
                description="Desc 1",
                severity=3,
                urgency=3,
                effort=3,
                priority_score=50.0
            )
        ]
        
        repo = RepoDebtSummary(
            repo_name="test-repo",
            summary="Summary",
            debt_items=items
        )
        
        metrics = DebtAggregator.aggregate_metrics([repo], top_n=10)
        
        assert metrics.total_debt_items == 1
        assert metrics.total_repos == 1
        assert "testing" in metrics.category_counts
        assert metrics.category_counts["testing"] == 1
    
    def test_aggregate_metrics_multiple_repos(self):
        """Test aggregation across multiple repositories."""
        repos = []
        for i in range(3):
            items = [
                DebtItem(
                    id=f"TEST-{j:03d}",
                    category="testing",
                    title=f"Issue {j}",
                    description=f"Description {j}",
                    severity=3,
                    urgency=3,
                    effort=3,
                    priority_score=50.0
                )
                for j in range(1, 4)
            ]
            
            repo = RepoDebtSummary(
                repo_name=f"repo-{i}",
                summary=f"Summary {i}",
                debt_items=items
            )
            repos.append(repo)
        
        metrics = DebtAggregator.aggregate_metrics(repos, top_n=5)
        
        assert metrics.total_debt_items == 9  # 3 repos × 3 items
        assert metrics.total_repos == 3
        assert len(metrics.top_priority_items) == 5  # Limited by top_n


class TestDebtItem:
    """Tests for DebtItem model."""
    
    def test_debt_item_validation(self):
        """Test that scores are clamped to valid range."""
        item = DebtItem(
            id="TEST-001",
            category="testing",
            title="Test",
            description="Test",
            severity=10,  # Over max
            urgency=0,    # Under min
            effort=3
        )
        
        assert item.severity == 5  # Clamped to max
        assert item.urgency == 1   # Clamped to min


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
