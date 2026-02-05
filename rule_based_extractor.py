"""
Rule-based technical debt extractor (no LLM required).
"""
import re
import logging
from typing import List, Dict, Tuple
from models import RepoDebtSummary, DebtItem

logger = logging.getLogger(__name__)


class RuleBasedExtractor:
    """Extract technical debt using pattern matching and keyword analysis."""
    
    # Category keywords mapping - aligned with code review prompt
    CATEGORY_KEYWORDS = {
        'testing': [
            'test', 'testing', 'unit test', 'integration test', 'no tests',
            'missing tests', 'test coverage', 'untested', 'mock', 'stub',
            'test cases', 'coverage'
        ],
        'security': [
            'security', 'vulnerability', 'vulnerable', 'injection', 'xss',
            'csrf', 'authentication', 'authorization', 'access control',
            'input validation', 'sql injection', 'command injection',
            'data exposure', 'sensitive data', 'cryptography', 'hardcoded',
            'secrets', 'encryption', 'password', 'credential', 'token',
            'dependencies', 'vulnerable libraries'
        ],
        'performance': [
            'performance', 'slow', 'bottleneck', 'inefficient', 'optimization',
            'cache', 'memory leak', 'n+1', 'query', 'latency', 'timeout',
            'response time', 'load time', 'algorithm complexity', 'o(n)',
            'memory usage', 'allocation', 'i/o operations', 'blocking',
            'concurrency', 'database', 'indices', 'batch operations',
            'resource management', 'connection pooling', 'buffering'
        ],
        'architecture': [
            'architecture', 'design', 'coupling', 'cohesion', 'monolith',
            'refactor', 'structure', 'pattern', 'dependency', 'layering',
            'separation of concerns', 'solid', 'tight coupling', 'modularity',
            'design patterns', 'code structure', 'organization'
        ],
        'docs': [
            'documentation', 'docs', 'comment', 'readme', 'undocumented',
            'no documentation', 'missing docs', 'api docs', 'outdated docs',
            'maintainability documentation'
        ],
        'code_quality': [
            'code quality', 'clean code', 'readable', 'readability',
            'maintainability', 'technical debt', 'code smell', 'duplication',
            'complexity', 'spaghetti', 'messy', 'inconsistent', 'style',
            'linting', 'naming', 'formatting', 'god class', 'long method',
            'best practices'
        ],
        'bugs': [
            'bug', 'bugs', 'error', 'logic error', 'off-by-one', 'null safety',
            'null pointer', 'exception handling', 'resource leak', 'edge case',
            'boundary condition', 'type safety', 'casting', 'concurrency issue',
            'race condition', 'deadlock', 'potential bug'
        ],
        'tooling': [
            'tooling', 'build', 'ci/cd', 'pipeline', 'deployment', 'devops',
            'automation', 'script', 'configuration', 'environment'
        ]
    }
    
    # Severity indicators
    SEVERITY_HIGH = [
        'critical', 'severe', 'major', 'serious', 'urgent', 'blocker',
        'production', 'outage', 'crash', 'data loss', 'security breach'
    ]
    
    SEVERITY_MEDIUM = [
        'important', 'significant', 'notable', 'concerning', 'issue',
        'problem', 'bug', 'error'
    ]
    
    # Urgency indicators
    URGENCY_HIGH = [
        'urgent', 'immediate', 'asap', 'now', 'quickly', 'soon',
        'before release', 'must fix', 'should fix'
    ]
    
    # Effort indicators
    EFFORT_HIGH = [
        'large', 'big', 'massive', 'extensive', 'major refactor',
        'rewrite', 'redesign', 'significant effort', 'time-consuming'
    ]
    
    EFFORT_LOW = [
        'small', 'minor', 'quick', 'simple', 'easy', 'trivial',
        'straightforward', 'quick fix'
    ]
    
    def __init__(self):
        """Initialize the rule-based extractor."""
        # Compile regex patterns for efficiency
        self.section_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
        self.bullet_pattern = re.compile(r'^\s*[-*+]\s+(.+)$', re.MULTILINE)
        self.number_pattern = re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE)
        
    def extract_debt_summary(
        self,
        markdown_text: str,
        repo_name: str
    ) -> RepoDebtSummary:
        """
        Extract technical debt from markdown using rule-based approach.
        
        Args:
            markdown_text: Raw markdown content
            repo_name: Name of the repository
            
        Returns:
            RepoDebtSummary object
        """
        logger.info(f"Extracting debt from {repo_name} using rule-based approach")
        
        # Extract sections
        sections = self._extract_sections(markdown_text)
        
        # Find debt items
        debt_items = []
        debt_id_counter = 1
        
        for section_title, section_content in sections:
            # Determine category from section title
            category = self._categorize_section(section_title)
            
            # Extract issues from this section
            issues = self._extract_issues(section_content)
            
            for issue in issues:
                debt_item = self._create_debt_item(
                    f"DEBT-{debt_id_counter:03d}",
                    category,
                    issue,
                    section_title,
                    section_content
                )
                debt_items.append(debt_item)
                debt_id_counter += 1
        
        # Generate summary
        summary = self._generate_summary(debt_items, markdown_text)
        
        logger.info(f"Extracted {len(debt_items)} debt items from {repo_name}")
        
        return RepoDebtSummary(
            repo_name=repo_name,
            summary=summary,
            debt_items=debt_items
        )
    
    def _extract_sections(self, markdown_text: str) -> List[Tuple[str, str]]:
        """Extract sections from markdown."""
        sections = []
        lines = markdown_text.split('\n')
        
        current_title = "General"
        current_content = []
        
        for line in lines:
            header_match = self.section_pattern.match(line)
            if header_match:
                # Save previous section
                if current_content:
                    sections.append((current_title, '\n'.join(current_content)))
                
                # Start new section
                current_title = header_match.group(1).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))
        
        return sections
    
    def _categorize_section(self, section_title: str) -> str:
        """Determine category from section title."""
        title_lower = section_title.lower()
        
        # Direct mapping for code review sections
        section_mappings = {
            'code quality': 'code_quality',
            'potential bugs': 'bugs',
            'security': 'security',
            'performance': 'performance',
            'best practices': 'code_quality',
            'bugs': 'bugs',
            'quality': 'code_quality',
            'maintainability': 'code_quality'
        }
        
        # Check for exact matches first
        for key, category in section_mappings.items():
            if key in title_lower:
                return category
        
        # Check each category's keywords
        best_match = 'other'
        max_matches = 0
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in title_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = category
        
        return best_match
    
    def _extract_issues(self, content: str) -> List[str]:
        """Extract individual issues from section content."""
        issues = []
        
        # Pattern 1: Numbered items with bold headers (e.g., "1. **Input Validation**: description")
        numbered_bold_pattern = re.compile(r'^\s*\d+\.\s*\*\*([^*]+)\*\*:?\s*(.+?)(?=\n\s*\d+\.|$)', re.MULTILINE | re.DOTALL)
        numbered_bold_matches = numbered_bold_pattern.findall(content)
        for title, description in numbered_bold_matches:
            # Combine title and description
            issue_text = f"{title.strip()}: {description.strip()}"
            issues.append(issue_text)
        
        # If we found structured items, use those
        if issues:
            return issues[:15]  # Limit to top 15 per section
        
        # Pattern 2: Regular bullet points
        bullet_matches = self.bullet_pattern.findall(content)
        if bullet_matches:
            issues.extend(bullet_matches)
        
        # Pattern 3: Regular numbered lists
        number_matches = self.number_pattern.findall(content)
        if number_matches:
            issues.extend(number_matches)
        
        # If we found list items, use those
        if issues:
            issues = [self._clean_text(issue) for issue in issues]
            issues = [issue for issue in issues if len(issue) > 20]
            return issues[:15]
        
        # Pattern 4: Paragraphs (fallback)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        issues = [p for p in paragraphs if 30 < len(p) < 500]
        
        # Clean up issues
        issues = [self._clean_text(issue) for issue in issues]
        
        return issues[:10]  # Limit to top 10 per section
    
    def _create_debt_item(
        self,
        debt_id: str,
        category: str,
        issue: str,
        section_title: str,
        section_content: str
    ) -> DebtItem:
        """Create a DebtItem from extracted information."""
        
        # Analyze the issue text
        issue_lower = issue.lower()
        content_lower = section_content.lower()
        
        # Determine severity (1-5)
        severity = self._calculate_severity(issue_lower, content_lower)
        
        # Determine urgency (1-5)
        urgency = self._calculate_urgency(issue_lower, content_lower)
        
        # Determine effort (1-5)
        effort = self._calculate_effort(issue_lower, content_lower)
        
        # Extract root cause and impact
        root_cause = self._extract_root_cause(issue, content_lower)
        impact = self._extract_impact(issue, content_lower)
        
        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(category, issue)
        
        return DebtItem(
            id=debt_id,
            category=category,
            title=issue[:100],  # Use first 100 chars as title
            description=issue[:200],  # Truncate long descriptions
            root_cause=root_cause,
            impact=impact,
            severity=severity,
            urgency=urgency,
            effort=effort,
            suggested_actions=suggested_actions
        )
    
    def _calculate_severity(self, issue_text: str, context: str) -> int:
        """Calculate severity score (1-5)."""
        text = issue_text + ' ' + context
        
        # Check for high severity indicators
        high_count = sum(1 for keyword in self.SEVERITY_HIGH if keyword in text)
        if high_count >= 2:
            return 5
        elif high_count == 1:
            return 4
        
        # Check for medium severity indicators
        medium_count = sum(1 for keyword in self.SEVERITY_MEDIUM if keyword in text)
        if medium_count >= 2:
            return 3
        elif medium_count == 1:
            return 2
        
        return 2  # Default to low-medium
    
    def _calculate_urgency(self, issue_text: str, context: str) -> int:
        """Calculate urgency score (1-5)."""
        text = issue_text + ' ' + context
        
        # Check for urgency indicators
        urgency_count = sum(1 for keyword in self.URGENCY_HIGH if keyword in text)
        
        if urgency_count >= 2:
            return 5
        elif urgency_count == 1:
            return 4
        elif 'should' in text or 'needs' in text:
            return 3
        elif 'could' in text or 'consider' in text:
            return 2
        
        return 2  # Default
    
    def _calculate_effort(self, issue_text: str, context: str) -> int:
        """Calculate effort score (1-5)."""
        text = issue_text + ' ' + context
        
        # Check for high effort indicators
        high_count = sum(1 for keyword in self.EFFORT_HIGH if keyword in text)
        if high_count >= 1:
            return 5
        
        # Check for low effort indicators
        low_count = sum(1 for keyword in self.EFFORT_LOW if keyword in text)
        if low_count >= 1:
            return 2
        
        # Default based on category keywords
        if any(word in text for word in ['refactor', 'redesign', 'rewrite']):
            return 4
        
        return 3  # Default to medium
    
    def _extract_root_cause(self, issue: str, context: str) -> str:
        """Extract or infer root cause."""
        # Look for cause indicators
        cause_patterns = [
            r'because\s+(.+?)[\.\n]',
            r'due to\s+(.+?)[\.\n]',
            r'caused by\s+(.+?)[\.\n]',
            r'reason:\s+(.+?)[\.\n]'
        ]
        
        for pattern in cause_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        
        # Generic root cause based on issue type
        if 'no test' in issue.lower() or 'missing test' in issue.lower():
            return "Tests were not written or maintained alongside code development"
        elif 'security' in issue.lower():
            return "Security best practices not followed during implementation"
        elif 'performance' in issue.lower():
            return "Performance not considered in initial implementation"
        elif 'documentation' in issue.lower() or 'undocumented' in issue.lower():
            return "Documentation not prioritized or maintained"
        
        return "Technical shortcuts taken or requirements evolved over time"
    
    def _extract_impact(self, issue: str, context: str) -> str:
        """Extract or infer impact."""
        # Look for impact indicators
        impact_patterns = [
            r'impact[s]?:\s+(.+?)[\.\n]',
            r'consequence[s]?:\s+(.+?)[\.\n]',
            r'result[s]? in\s+(.+?)[\.\n]',
            r'leads to\s+(.+?)[\.\n]'
        ]
        
        for pattern in impact_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        
        # Generic impact based on issue type
        issue_lower = issue.lower()
        if 'test' in issue_lower:
            return "Increases risk of bugs in production, makes refactoring difficult"
        elif 'security' in issue_lower:
            return "Potential security breach or data compromise"
        elif 'performance' in issue_lower:
            return "Poor user experience, increased infrastructure costs"
        elif 'documentation' in issue_lower:
            return "Slows down onboarding, increases maintenance difficulty"
        elif 'architecture' in issue_lower:
            return "Reduces code maintainability and extensibility"
        
        return "Increases maintenance cost and development velocity"
    
    def _generate_suggested_actions(self, category: str, issue: str) -> List[str]:
        """Generate suggested actions based on category and issue."""
        actions = []
        issue_lower = issue.lower()
        
        if category == 'testing':
            actions.append("Write comprehensive unit tests for core functionality")
            actions.append("Set up CI/CD to enforce minimum test coverage")
            if 'integration' in issue_lower:
                actions.append("Add integration tests for critical paths")
        
        elif category == 'security':
            actions.append("Conduct security audit of affected components")
            actions.append("Implement security best practices and validation")
            actions.append("Add security scanning to CI/CD pipeline")
        
        elif category == 'performance':
            actions.append("Profile and identify performance bottlenecks")
            actions.append("Implement caching where appropriate")
            actions.append("Optimize database queries and indexes")
        
        elif category == 'architecture':
            actions.append("Create refactoring plan with clear milestones")
            actions.append("Introduce abstraction layers to reduce coupling")
            actions.append("Document architectural decisions (ADRs)")
        
        elif category == 'docs':
            actions.append("Update documentation to match current implementation")
            actions.append("Add inline code comments for complex logic")
            actions.append("Create/update README with setup instructions")
        
        elif category == 'code_quality':
            actions.append("Run linter and fix code style issues")
            actions.append("Refactor large functions into smaller units")
            actions.append("Remove dead code and unused dependencies")
        
        elif category == 'tooling':
            actions.append("Automate manual processes")
            actions.append("Update build and deployment scripts")
            actions.append("Document tooling setup and usage")
        
        else:
            actions.append("Prioritize and schedule time to address this issue")
            actions.append("Create detailed tickets for tracking")
        
        return actions[:3]  # Limit to top 3
    
    def _generate_summary(self, debt_items: List[DebtItem], markdown_text: str) -> str:
        """Generate a summary of the technical debt."""
        if not debt_items:
            return "No significant technical debt items identified in this review."
        
        # Count by category
        category_counts = {}
        for item in debt_items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        # Find most common categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate average severity
        avg_severity = sum(item.severity for item in debt_items) / len(debt_items)
        
        summary = f"Identified {len(debt_items)} technical debt items. "
        summary += f"Primary concerns are {', '.join(cat for cat, _ in top_categories)}. "
        
        if avg_severity >= 4:
            summary += "Overall severity is high and requires immediate attention."
        elif avg_severity >= 3:
            summary += "Overall severity is moderate and should be addressed soon."
        else:
            summary += "Overall severity is manageable with planned improvements."
        
        return summary
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)        # Code
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()