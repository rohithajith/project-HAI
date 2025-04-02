from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
import re
from pathlib import Path
import json

class FilterRule(BaseModel):
    """Schema for content filtering rules."""
    category: str = Field(..., description="Category of content to filter")
    patterns: List[str] = Field(..., description="Regex patterns to match")
    context_words: List[str] = Field(..., description="Context words that indicate this category")
    severity: int = Field(..., description="Severity level (1-5)")
    languages: List[str] = Field(default=["en"], description="Languages this rule applies to")

class FilterResult(BaseModel):
    """Schema for content filter results."""
    is_harmful: bool = Field(..., description="Whether content is harmful")
    categories: List[str] = Field(default_factory=list, description="Categories of harmful content found")
    severity: int = Field(0, description="Highest severity level found")
    filtered_content: Optional[str] = Field(None, description="Content with harmful parts removed")
    matches: List[Dict[str, Any]] = Field(default_factory=list, description="Details of matches found")

class ContentFilter:
    """Sophisticated content filter for multi-agent system."""
    
    def __init__(self):
        self.rules: List[FilterRule] = []
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        self.load_rules()
        
    def load_rules(self):
        """Load filtering rules from configuration."""
        rules_file = Path("config/filter_rules.json")
        
        # Default rules if config file doesn't exist
        default_rules = [
            FilterRule(
                category="hate_speech",
                patterns=[
                    r"\b(hate|racial|ethnic)\s*(slur|insult|attack)",
                    r"\b(discriminat\w+)\b"
                ],
                context_words=["racist", "xenophobic", "prejudice"],
                severity=5,
                languages=["en"]
            ),
            FilterRule(
                category="violence",
                patterns=[
                    r"\b(kill|murder|attack|bomb|weapon|terror)",
                    r"\b(threat\w*|violen\w+)\b"
                ],
                context_words=["harm", "dangerous", "deadly"],
                severity=5,
                languages=["en"]
            ),
            FilterRule(
                category="adult_content",
                patterns=[
                    r"\b(explicit|nude|sex|porn)",
                    r"\b(adult|xxx|erotic)\b"
                ],
                context_words=["inappropriate", "mature", "nsfw"],
                severity=4,
                languages=["en"]
            ),
            FilterRule(
                category="personal_info",
                patterns=[
                    r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",  # SSN
                    r"\b\d{16}\b",  # Credit card
                    r"\b[A-Z]{2}\d{6}\b"  # Passport number
                ],
                context_words=["social security", "credit card", "passport"],
                severity=3,
                languages=["en"]
            ),
            FilterRule(
                category="harmful_topics",
                patterns=[
                    r"\b(lgbtq|rape|politics|drugs)\b",
                    r"\b(sensitive|controversial)\b"
                ],
                context_words=["inappropriate", "offensive", "sensitive"],
                severity=4,
                languages=["en"]
            ),
            FilterRule(
                category="profanity",
                patterns=[
                    r"\b(profanity patterns here)\b",
                    r"\b(curse|swear)\s*(word|term)\b"
                ],
                context_words=["rude", "offensive", "inappropriate"],
                severity=2,
                languages=["en"]
            ),
            FilterRule(
                category="spam",
                patterns=[
                    r"\b(buy|sell|discount|offer|click|win)\b.*https?://",
                    r"\b(lottery|prize|winner|congrats)\b"
                ],
                context_words=["advertisement", "marketing", "promotion"],
                severity=1,
                languages=["en"]
            )
        ]
        
        try:
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    self.rules = [FilterRule(**rule) for rule in rules_data]
            else:
                self.rules = default_rules
                
            # Compile regex patterns
            for rule in self.rules:
                self.compiled_patterns[rule.category] = [
                    re.compile(pattern, re.IGNORECASE) 
                    for pattern in rule.patterns
                ]
                
        except Exception as e:
            print(f"Error loading filter rules: {e}")
            self.rules = default_rules

    def check_content(self, 
                     content: str, 
                     language: str = "en",
                     context: Optional[List[Dict[str, Any]]] = None) -> FilterResult:
        """
        Check content for harmful material.
        
        Args:
            content: The content to check
            language: Content language (default: "en")
            context: Optional conversation context
            
        Returns:
            FilterResult with analysis details
        """
        matches = []
        max_severity = 0
        categories = set()
        
        # Check each rule
        for rule in self.rules:
            # Skip if rule doesn't apply to this language
            if language not in rule.languages:
                continue
                
            # Check patterns
            for pattern in self.compiled_patterns[rule.category]:
                found_matches = pattern.finditer(content)
                for match in found_matches:
                    categories.add(rule.category)
                    max_severity = max(max_severity, rule.severity)
                    matches.append({
                        "category": rule.category,
                        "severity": rule.severity,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end()
                    })
            
            # Check context words if context is provided
            if context:
                context_content = " ".join(
                    msg.get("content", "") 
                    for msg in context[-3:]  # Look at last 3 messages
                )
                if any(word in context_content.lower() for word in rule.context_words):
                    categories.add(rule.category)
                    max_severity = max(max_severity, rule.severity)
                    matches.append({
                        "category": rule.category,
                        "severity": rule.severity,
                        "match": "context",
                        "context_words": [
                            word for word in rule.context_words 
                            if word in context_content.lower()
                        ]
                    })

        # Create filtered version if needed
        filtered_content = None
        if matches:
            filtered_content = content
            # Replace matches with asterisks, working backwards to preserve indices
            for match in sorted(matches, key=lambda x: x.get("start", 0), reverse=True):
                if "start" in match and "end" in match:
                    filtered_content = (
                        filtered_content[:match["start"]] +
                        "*" * (match["end"] - match["start"]) +
                        filtered_content[match["end"]:]
                    )

        return FilterResult(
            is_harmful=bool(matches),
            categories=list(categories),
            severity=max_severity,
            filtered_content=filtered_content,
            matches=matches
        )

    def filter_harmful_content(self, 
                             content: str,
                             language: str = "en",
                             context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Filter out harmful content, replacing it with asterisks.
        
        Args:
            content: Content to filter
            language: Content language (default: "en")
            context: Optional conversation context
            
        Returns:
            Filtered content with harmful parts replaced by asterisks
        """
        result = self.check_content(content, language, context)
        return result.filtered_content if result.is_harmful else content

    def is_content_safe(self,
                       content: str,
                       language: str = "en",
                       context: Optional[List[Dict[str, Any]]] = None,
                       max_severity: int = 3) -> bool:
        """
        Check if content is safe (below maximum severity threshold).
        
        Args:
            content: Content to check
            language: Content language (default: "en")
            context: Optional conversation context
            max_severity: Maximum allowed severity (default: 3)
            
        Returns:
            True if content is safe, False otherwise
        """
        result = self.check_content(content, language, context)
        return result.severity <= max_severity

# Create singleton instance
content_filter = ContentFilter()