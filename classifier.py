"""
Complaint Classifier Module
Handles categorization, severity assignment, and root cause analysis
"""

import re
from typing import Dict, Any, List, Tuple
import config
import utils


class ComplaintClassifier:
    """
    Classifies complaints by category, severity, and probable root causes
    """
    
    def __init__(self):
        self.categories = config.PRIMARY_CATEGORIES
        self.severity_indicators = config.SEVERITY_INDICATORS
        self.root_cause_patterns = config.ROOT_CAUSE_PATTERNS
    
    def classify_category(self, complaint_text: str, user_intent: str = "", 
                         observed_outcome: str = "") -> Tuple[str, List[str]]:
        """
        Classify complaint into primary and secondary categories
        
        Args:
            complaint_text: Full complaint description
            user_intent: What user was trying to do
            observed_outcome: What actually happened
            
        Returns:
            Tuple of (primary_category, secondary_categories)
        """
        # Combine all text for analysis
        full_text = f"{complaint_text} {user_intent} {observed_outcome}".lower()
        
        # Score each category
        category_scores = {}
        for category, info in self.categories.items():
            score = 0
            # Check each keyword
            for keyword in info["keywords"]:
                keyword_lower = keyword.lower()
                # Count occurrences
                count = full_text.count(keyword_lower)
                score += count
            category_scores[category] = score
        
        # Additional special case handling
        if any(word in full_text for word in ["append", "replace", "overwrite", "constraint"]):
            category_scores["model_behavior"] = category_scores.get("model_behavior", 0) + 5
        
        if any(word in full_text for word in ["dark mode", "feature", "add", "need", "want"]):
            category_scores["feature_request"] = category_scores.get("feature_request", 0) + 3
        
        # Get primary category (highest score)
        if max(category_scores.values()) == 0:
            primary = "other"
        else:
            primary = max(category_scores, key=category_scores.get)
        
        # Get secondary categories (any with score > 0, excluding primary)
        secondary = [cat for cat, score in category_scores.items() 
                     if score > 0 and cat != primary][:5]
        
        return primary, secondary
    
    def calculate_severity(self, complaint_data: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Calculate severity level and reasoning
        
        Args:
            complaint_data: Complaint dictionary
            
        Returns:
            Tuple of (severity_level, basis_reasons)
        """
        score = 0
        basis = []
        
        # Combine text for analysis
        text = f"{complaint_data.get('user_summary', '')} " \
               f"{complaint_data.get('user_intent', '')} " \
               f"{complaint_data.get('observed_outcome', '')}".lower()
        
        # Check severity indicators
        for severity_level, info in self.severity_indicators.items():
            for keyword in info["keywords"]:
                if keyword in text:
                    if severity_level == "critical":
                        score += 3
                    elif severity_level == "high":
                        score += 2
                    elif severity_level == "medium":
                        score += 1
                    basis.append(f"Contains '{keyword}' indicator")
        
        # Frequency multiplier
        frequency = complaint_data.get("frequency", "unknown")
        if frequency == "persistent":
            score += 2
            basis.append("Recurring issue (persistent)")
        elif frequency == "intermittent":
            score += 1
            basis.append("Recurring issue (intermittent)")
        
        # Impact on work
        if any(word in text for word in ["job", "work", "business", "project"]):
            score += 1
            basis.append("Impacts work/productivity")
        
        # Category-based adjustments
        primary_cat = complaint_data.get("primary_category", "other")
        if primary_cat in ["bug", "trust_safety"]:
            score += 1
            basis.append(f"Category: {primary_cat} (elevated priority)")
        
        # Map score to severity level
        if score >= 4:
            severity = "critical"
        elif score >= 3:
            severity = "high"
        elif score >= 1:
            severity = "medium"
        else:
            severity = "low"
        
        if not basis:
            basis = ["Default severity based on available information"]
        
        return severity, basis
    
    def identify_root_causes(self, complaint_data: Dict[str, Any]) -> List[str]:
        """
        Identify probable root causes
        
        Args:
            complaint_data: Complaint dictionary
            
        Returns:
            List of probable root cause identifiers
        """
        causes = []
        
        # Combine text for analysis
        text = f"{complaint_data.get('user_summary', '')} " \
               f"{complaint_data.get('user_intent', '')} " \
               f"{complaint_data.get('observed_outcome', '')} " \
               f"{complaint_data.get('context', '')}".lower()
        
        # Check patterns for each root cause
        for cause, patterns in self.root_cause_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    causes.append(cause)
                    break  # Only add each cause once
        
        # If no causes identified, mark as unknown
        if not causes:
            causes = ["unknown"]
        
        return causes
    
    def suggest_routing(self, complaint_data: Dict[str, Any]) -> str:
        """
        Suggest routing target based on complaint characteristics
        
        Args:
            complaint_data: Complaint dictionary
            
        Returns:
            str: Routing target identifier
        """
        severity = complaint_data.get("severity", "low")
        primary_cat = complaint_data.get("primary_category", "other")
        root_causes = complaint_data.get("probable_root_causes", [])
        frequency = complaint_data.get("frequency", "unknown")
        
        # Critical issues go to human review
        if severity == "critical":
            return "human_review"
        
        # Trust/safety escalation
        if primary_cat == "trust_safety" and severity in ["high", "critical"]:
            return "safety_escalation"
        
        # Bug reports go to human review if high severity
        if primary_cat == "bug" and severity in ["high", "critical"]:
            return "human_review"
        
        # Model behavior with constraint issues -> self-correction
        if primary_cat == "model_behavior" and "constraint_parsing_failure" in root_causes:
            return "self_correction"
        
        # Feature requests to product backlog
        if primary_cat == "feature_request":
            return "product_backlog"
        
        # Persistent misunderstandings -> documentation
        if primary_cat == "misunderstanding" and frequency == "persistent":
            return "documentation_update"
        
        # Performance issues go to human review if high severity
        if primary_cat == "performance" and severity in ["high", "critical"]:
            return "human_review"
        
        # Default to self-correction for model behavior
        if primary_cat == "model_behavior":
            return "self_correction"
        
        # Everything else to human review
        return "human_review"
    
    def suggest_fix(self, complaint_data: Dict[str, Any]) -> str:
        """
        Generate suggested fix based on complaint analysis
        
        Args:
            complaint_data: Complaint dictionary
            
        Returns:
            str: Suggested fix description
        """
        primary_cat = complaint_data.get("primary_category", "other")
        root_causes = complaint_data.get("probable_root_causes", [])
        
        suggestions = []
        
        # Category-specific suggestions
        if primary_cat == "model_behavior":
            if "constraint_parsing_failure" in root_causes:
                suggestions.append("Increase constraint adherence monitoring")
                suggestions.append("Add explicit constraint verification step")
            if "context_overload" in root_causes:
                suggestions.append("Implement conversation summarization")
                suggestions.append("Reduce context window usage")
        
        elif primary_cat == "bug":
            suggestions.append("Investigate technical root cause")
            suggestions.append("Review error logs and stack traces")
        
        elif primary_cat == "ux_ui":
            suggestions.append("Review UI/UX design for clarity")
            suggestions.append("Add user guidance or tooltips")
        
        elif primary_cat == "performance":
            suggestions.append("Optimize processing pipeline")
            suggestions.append("Investigate latency bottlenecks")
        
        elif primary_cat == "policy_friction":
            suggestions.append("Review policy application logic")
            suggestions.append("Improve refusal explanations")
        
        elif primary_cat == "misunderstanding":
            suggestions.append("Improve user documentation")
            suggestions.append("Add clarifying examples")
        
        if suggestions:
            return "; ".join(suggestions)
        else:
            return "Requires manual investigation and review"
    
    def classify_full(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform full classification on complaint data
        
        Args:
            complaint_data: Partial complaint dictionary
            
        Returns:
            Updated complaint dictionary with all classifications
        """
        # Get text components
        complaint_text = complaint_data.get("user_summary", "")
        user_intent = complaint_data.get("user_intent", "")
        observed_outcome = complaint_data.get("observed_outcome", "")
        
        # Classify category
        primary, secondary = self.classify_category(
            complaint_text, user_intent, observed_outcome
        )
        complaint_data["primary_category"] = primary
        complaint_data["secondary_categories"] = secondary
        
        # Calculate severity
        severity, basis = self.calculate_severity(complaint_data)
        complaint_data["severity"] = severity
        complaint_data["severity_basis"] = basis
        
        # Identify root causes
        root_causes = self.identify_root_causes(complaint_data)
        complaint_data["probable_root_causes"] = root_causes
        
        # Suggest routing
        routing = self.suggest_routing(complaint_data)
        complaint_data["routing_target"] = routing
        
        # Suggest fix
        fix = self.suggest_fix(complaint_data)
        complaint_data["suggested_fix"] = fix
        
        # Calculate confidence
        confidence = utils.calculate_confidence(complaint_data)
        complaint_data["confidence"] = confidence
        
        return complaint_data
