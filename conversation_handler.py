"""
Conversation Handler Module
Manages the interactive complaint intake conversation
"""

import random
from typing import Dict, Any, Optional, List
from datetime import datetime

import config
import utils


class ConversationHandler:
    """
    Manages conversational complaint intake flow
    """
    
    def __init__(self):
        self.questions = config.INTAKE_QUESTIONS
        self.max_rounds = config.MAX_CLARIFICATION_ROUNDS
        self.current_round = 0
        self.conversation_state = "idle"  # idle, active, complete
        self.complaint_data = {}
        self.missing_fields = []
    
    def start_intake(self, initial_message: str) -> str:
        """
        Start complaint intake process
        
        Args:
            initial_message: User's initial complaint message
            
        Returns:
            str: System response to begin intake
        """
        self.conversation_state = "active"
        self.current_round = 0
        
        # Initialize complaint data
        self.complaint_data = {
            "complaint_id": utils.generate_complaint_id(),
            "reported_at": utils.format_timestamp(),
            "incident_at": None,
            "status": "new",
            "user_summary": utils.sanitize_text(initial_message),
            "primary_category": None,
            "secondary_categories": [],
            "severity": None,
            "severity_basis": [],
            "frequency": "unknown",
            "user_intent": "",
            "observed_outcome": "",
            "expected_outcome": "",
            "context": None,
            "evidence": [],
            "probable_root_causes": [],
            "related_complaints": [],
            "routing_target": None,
            "suggested_fix": None,
            "confidence": 0.0,
            "audit_trail": []
        }
        
        # Add initial audit entry
        utils.add_audit_entry(
            self.complaint_data,
            actor="system",
            action="Complaint intake initiated"
        )
        
        # Identify missing required fields
        self._identify_missing_fields()
        
        # Generate initial response
        response = self._generate_initial_response()
        
        return response
    
    def _identify_missing_fields(self):
        """Identify which required fields are missing"""
        required_fields = [
            "user_intent",
            "observed_outcome",
            "expected_outcome"
        ]
        
        self.missing_fields = [
            field for field in required_fields
            if not self.complaint_data.get(field)
        ]
    
    def _generate_initial_response(self) -> str:
        """Generate initial intake response"""
        response = "I can help you file that complaint. "
        
        if self.missing_fields:
            response += "I'll need to ask you a few quick questions to complete the record.\n\n"
            response += self._ask_next_question()
        else:
            response += "I have enough information to proceed with filing."
            self.conversation_state = "complete"
        
        return response
    
    def _ask_next_question(self) -> str:
        """Ask the next question based on missing fields"""
        if not self.missing_fields:
            return ""
        
        field = self.missing_fields[0]
        questions = self.questions.get(field, ["Can you provide more details?"])
        question = random.choice(questions)
        
        return question
    
    def process_response(self, user_response: str) -> str:
        """
        Process user's response to a question
        
        Args:
            user_response: User's answer
            
        Returns:
            str: Next question or completion message
        """
        if self.conversation_state != "active":
            return "No active complaint intake session."
        
        self.current_round += 1
        
        if self.current_round > self.max_rounds:
            return self._finalize_with_partial_data()
        
        # Store response in appropriate field
        if self.missing_fields:
            current_field = self.missing_fields[0]
            self.complaint_data[current_field] = utils.sanitize_text(user_response)
            self.missing_fields.pop(0)
        
        # Check if we have all required fields
        if not self.missing_fields:
            return self._prepare_for_finalization()
        else:
            # Ask next question
            return self._ask_next_question()
    
    def _prepare_for_finalization(self) -> str:
        """Prepare complaint for finalization"""
        self.conversation_state = "complete"
        
        response = "\n✓ I have all the information I need.\n\n"
        response += "Let me structure this complaint for you...\n"
        
        return response
    
    def _finalize_with_partial_data(self) -> str:
        """Finalize complaint with whatever data we have"""
        self.conversation_state = "complete"
        
        # Fill in missing required fields with placeholder
        for field in self.missing_fields:
            if not self.complaint_data.get(field):
                self.complaint_data[field] = "Not provided"
        
        response = "\nI'll proceed with the information provided.\n"
        return response
    
    def ask_for_frequency(self) -> str:
        """Ask about frequency if not yet determined"""
        questions = self.questions.get("frequency", ["How often has this happened?"])
        return random.choice(questions)
    
    def ask_for_context(self) -> str:
        """Ask for additional context"""
        questions = self.questions.get("context", ["Any other details?"])
        return random.choice(questions)
    
    def ask_for_incident_time(self) -> str:
        """Ask when the incident occurred"""
        questions = self.questions.get("incident_at", ["When did this happen?"])
        return random.choice(questions)
    
    def set_frequency(self, frequency: str) -> bool:
        """Set frequency value"""
        valid_frequencies = ["once", "intermittent", "persistent", "unknown"]
        if frequency in valid_frequencies:
            self.complaint_data["frequency"] = frequency
            return True
        return False
    
    def set_context(self, context: str):
        """Set additional context"""
        self.complaint_data["context"] = utils.sanitize_text(context)
    
    def set_incident_time(self, time_str: str):
        """Set incident time"""
        # Try to parse as ISO format
        try:
            dt = datetime.fromisoformat(time_str)
            self.complaint_data["incident_at"] = utils.format_timestamp(dt)
        except:
            # Try to interpret relative time
            if "today" in time_str.lower():
                self.complaint_data["incident_at"] = utils.format_timestamp()
            elif "yesterday" in time_str.lower():
                from datetime import timedelta
                yesterday = datetime.now() - timedelta(days=1)
                self.complaint_data["incident_at"] = utils.format_timestamp(yesterday)
            else:
                # Store as-is in context
                if self.complaint_data.get("context"):
                    self.complaint_data["context"] += f" Time: {time_str}"
                else:
                    self.complaint_data["context"] = f"Time: {time_str}"
    
    def get_complaint_data(self) -> Dict[str, Any]:
        """Get current complaint data"""
        return self.complaint_data.copy()
    
    def is_complete(self) -> bool:
        """Check if intake is complete"""
        return self.conversation_state == "complete"
    
    def reset(self):
        """Reset conversation state"""
        self.conversation_state = "idle"
        self.current_round = 0
        self.complaint_data = {}
        self.missing_fields = []
    
    def add_evidence(self, evidence_type: str, content: str):
        """Add evidence to complaint"""
        if "evidence" not in self.complaint_data:
            self.complaint_data["evidence"] = []
        
        self.complaint_data["evidence"].append({
            "type": evidence_type,
            "content": content
        })
    
    def generate_summary(self) -> str:
        """Generate a summary of collected information"""
        summary = "=== Complaint Summary ===\n\n"
        
        if self.complaint_data.get("user_intent"):
            summary += f"Intent: {self.complaint_data['user_intent']}\n"
        
        if self.complaint_data.get("observed_outcome"):
            summary += f"Observed: {self.complaint_data['observed_outcome']}\n"
        
        if self.complaint_data.get("expected_outcome"):
            summary += f"Expected: {self.complaint_data['expected_outcome']}\n"
        
        if self.complaint_data.get("frequency") != "unknown":
            summary += f"Frequency: {self.complaint_data['frequency']}\n"
        
        if self.complaint_data.get("context"):
            summary += f"Context: {self.complaint_data['context']}\n"
        
        return summary
