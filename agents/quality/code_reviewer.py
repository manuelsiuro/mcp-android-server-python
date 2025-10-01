"""CodeReviewer Agent - Reviews generated code for quality and correctness."""

from typing import Any, Dict, List

from ..base import SupportAgent
from ..models import (
    CodeReviewResult,
    Language,
    PerformanceIssue,
    SecurityIssue,
    StyleIssue,
)
from ..registry import register_agent


class CodeReviewerAgent(SupportAgent):
    """Review generated code for quality, correctness, and best practices."""

    def __init__(self):
        super().__init__("CodeReviewer")

    def _process(self, inputs: Dict[str, Any]) -> CodeReviewResult:
        """Review code and return findings."""
        code = inputs["code"]
        language = Language(inputs.get("language", "python"))
        inputs.get("review_checklist", [])

        # Perform reviews
        style_issues = self._check_style(code, language)
        security_issues = self._check_security(code, language)
        performance_issues = self._check_performance(code, language)

        # Collect all issues
        critical_issues = []
        warnings = []
        suggestions = []

        for issue in security_issues:
            if issue.severity.value == "critical":
                critical_issues.append(issue.message)
            else:
                warnings.append(issue.message)

        for issue in style_issues:
            if issue.severity.value == "critical":
                critical_issues.append(issue.message)
            else:
                suggestions.append(issue.message)

        for issue in performance_issues:
            suggestions.append(issue.message)

        # Calculate review score
        score = self._calculate_score(critical_issues, warnings, suggestions)

        return CodeReviewResult(
            review_score=score,
            critical_issues=critical_issues,
            warnings=warnings,
            suggestions=suggestions,
            approved=score >= 80 and len(critical_issues) == 0,
            style_issues=style_issues,
            security_issues=security_issues,
            performance_issues=performance_issues,
        )

    def _check_style(self, code: str, language: Language) -> List[StyleIssue]:
        """Check code style."""
        issues = []
        # In real implementation, would use linters
        return issues

    def _check_security(self, code: str, language: Language) -> List[SecurityIssue]:
        """Check for security issues."""
        issues = []
        # In real implementation, would use security scanners
        return issues

    def _check_performance(
        self, code: str, language: Language
    ) -> List[PerformanceIssue]:
        """Check for performance issues."""
        issues = []
        # In real implementation, would analyze complexity
        return issues

    def _calculate_score(
        self, critical_issues: List[str], warnings: List[str], suggestions: List[str]
    ) -> int:
        """Calculate review score (0-100)."""
        score = 100
        score -= len(critical_issues) * 20
        score -= len(warnings) * 5
        score -= len(suggestions) * 2
        return max(0, score)


register_agent("code-reviewer", CodeReviewerAgent)
