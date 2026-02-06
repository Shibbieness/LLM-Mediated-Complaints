"""
Main Complaint System Orchestrator
Coordinates all system components to process complaints end-to-end
"""

from typing import Dict, Any, Optional
from datetime import datetime

import config
import utils
from classifier import ComplaintClassifier
from storage import ComplaintStorage
from conversation_handler import ConversationHandler


class ComplaintSystem:
    """
    Main system class that orchestrates complaint processing
    """
    
    def __init__(self):
        self.classifier = ComplaintClassifier()
        self.storage = ComplaintStorage()
        self.conversation = ConversationHandler()
        self.mode = "normal"  # normal, complaint_intake
    
    def detect_complaint(self, user_input: str) -> bool:
        """
        Detect if user input is a complaint trigger
        
        Args:
            user_input: User's message
            
        Returns:
            bool: True if complaint detected
        """
        return utils.is_complaint_trigger(user_input)
    
    def start_complaint_intake(self, initial_message: str) -> str:
        """
        Begin complaint intake process
        
        Args:
            initial_message: User's initial complaint
            
        Returns:
            str: System response
        """
        self.mode = "complaint_intake"
        response = self.conversation.start_intake(initial_message)
        return response
    
    def continue_conversation(self, user_response: str) -> str:
        """
        Continue the complaint intake conversation
        
        Args:
            user_response: User's answer
            
        Returns:
            str: Next question or completion message
        """
        if self.mode != "complaint_intake":
            return "No active complaint intake."
        
        response = self.conversation.process_response(user_response)
        
        # Check if intake is complete
        if self.conversation.is_complete():
            # Process the complaint through full pipeline
            result = self._process_complaint()
            response += "\n\n" + result
            self.mode = "normal"
        
        return response
    
    def _process_complaint(self) -> str:
        """
        Process complaint through classification, storage, and routing pipeline
        
        Returns:
            str: Processing result message
        """
        # Get complaint data from conversation
        complaint_data = self.conversation.get_complaint_data()
        
        # Update status to triaged
        complaint_data["status"] = "triaged"
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action="Complaint triaged"
        )
        
        # Classify the complaint
        complaint_data = self.classifier.classify_full(complaint_data)
        
        # Update status to structured
        complaint_data["status"] = "structured"
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action="Complaint structured and classified"
        )
        
        # Find similar complaints
        similar = self.storage.find_similar_complaints(complaint_data)
        if similar:
            complaint_data["related_complaints"] = similar
        
        # Update status to clustered
        complaint_data["status"] = "clustered"
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action=f"Clustered with {len(similar)} similar complaints"
        )
        
        # Update status to routed
        complaint_data["status"] = "routed"
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action=f"Routed to {complaint_data['routing_target']}"
        )
        
        # Save to storage
        success = self.storage.save(complaint_data)
        
        if success:
            # Generate confirmation message
            result = self._generate_confirmation(complaint_data)
            
            # Reset conversation
            self.conversation.reset()
            
            return result
        else:
            return "Error: Failed to save complaint. Please try again."
    
    def _generate_confirmation(self, complaint_data: Dict[str, Any]) -> str:
        """
        Generate complaint confirmation message
        
        Args:
            complaint_data: Completed complaint
            
        Returns:
            str: Confirmation message
        """
        severity_emoji = utils.get_severity_emoji(complaint_data["severity"])
        category_emoji = config.PRIMARY_CATEGORIES[complaint_data["primary_category"]]["emoji"]
        
        message = f"""
✓ Your complaint has been filed and processed.

{category_emoji} **Complaint ID:** {complaint_data['complaint_id']}
{severity_emoji} **Severity:** {complaint_data['severity'].upper()}
📊 **Category:** {complaint_data['primary_category']}
🔄 **Status:** {complaint_data['status'].upper()}
🎯 **Routed to:** {complaint_data['routing_target'].replace('_', ' ').title()}

**Classification Details:**
"""
        
        if complaint_data.get("severity_basis"):
            message += f"\n*Severity reasoning:* {', '.join(complaint_data['severity_basis'][:2])}"
        
        if complaint_data.get("probable_root_causes"):
            causes = [c.replace('_', ' ').title() for c in complaint_data['probable_root_causes'][:2]]
            message += f"\n*Probable causes:* {', '.join(causes)}"
        
        if complaint_data.get("related_complaints"):
            message += f"\n*Related complaints:* {len(complaint_data['related_complaints'])} similar issue(s) found"
        
        if complaint_data.get("suggested_fix"):
            message += f"\n\n**Suggested Fix:**\n{complaint_data['suggested_fix']}"
        
        message += f"\n\n**Confidence:** {complaint_data['confidence']:.0%}"
        message += f"\n\n*If this issue recurs, reference ID: {complaint_data['complaint_id']}*"
        
        return message.strip()
    
    def get_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complaint by ID"""
        return self.storage.load(complaint_id)
    
    def list_complaints_by_category(self, category: str) -> list:
        """List all complaints in a category"""
        return self.storage.search_by_category(category)
    
    def list_complaints_by_severity(self, severity: str) -> list:
        """List all complaints by severity"""
        return self.storage.search_by_severity(severity)
    
    def list_complaints_by_status(self, status: str) -> list:
        """List all complaints by status"""
        return self.storage.search_by_status(status)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.storage.get_statistics()
    
    def update_complaint_status(self, complaint_id: str, new_status: str) -> bool:
        """Update complaint status"""
        return self.storage.update_status(complaint_id, new_status)
    
    def reopen_complaint(self, complaint_id: str, reason: str = "") -> bool:
        """
        Reopen a closed complaint
        
        Args:
            complaint_id: Complaint ID
            reason: Reason for reopening
            
        Returns:
            bool: Success status
        """
        complaint = self.storage.load(complaint_id)
        if not complaint:
            return False
        
        if complaint["status"] != "closed":
            return False
        
        success = self.storage.update_status(complaint_id, "reopened")
        
        if success and reason:
            # Add audit entry with reason
            complaint = self.storage.load(complaint_id)
            utils.add_audit_entry(
                complaint,
                actor="user",
                action=f"Reopened: {reason}"
            )
            self.storage.save(complaint)
        
        return success
    
    def resolve_complaint(self, complaint_id: str, resolution: str = "") -> bool:
        """
        Mark complaint as resolved
        
        Args:
            complaint_id: Complaint ID
            resolution: Resolution description
            
        Returns:
            bool: Success status
        """
        # Update status to resolved
        success = self.storage.update_status(complaint_id, "resolved")
        
        if success and resolution:
            # Add resolution to audit trail
            complaint = self.storage.load(complaint_id)
            utils.add_audit_entry(
                complaint,
                actor="system",
                action=f"Resolved: {resolution}"
            )
            self.storage.save(complaint)
        
        return success
    
    def close_complaint(self, complaint_id: str) -> bool:
        """
        Close a resolved complaint
        
        Args:
            complaint_id: Complaint ID
            
        Returns:
            bool: Success status
        """
        return self.storage.update_status(complaint_id, "closed")
    
    def quick_file_complaint(self, user_summary: str, user_intent: str,
                            observed_outcome: str, expected_outcome: str,
                            frequency: str = "unknown") -> Dict[str, Any]:
        """
        Quick complaint filing without conversation (for API/batch use)
        
        Args:
            user_summary: Brief description
            user_intent: What user was trying to do
            observed_outcome: What happened
            expected_outcome: What should have happened
            frequency: How often it occurs
            
        Returns:
            Filed complaint data
        """
        # Create complaint data
        complaint_data = {
            "complaint_id": utils.generate_complaint_id(),
            "reported_at": utils.format_timestamp(),
            "incident_at": utils.format_timestamp(),
            "status": "new",
            "user_summary": utils.sanitize_text(user_summary),
            "primary_category": None,
            "secondary_categories": [],
            "severity": None,
            "severity_basis": [],
            "frequency": frequency,
            "user_intent": utils.sanitize_text(user_intent),
            "observed_outcome": utils.sanitize_text(observed_outcome),
            "expected_outcome": utils.sanitize_text(expected_outcome),
            "context": None,
            "evidence": [],
            "probable_root_causes": [],
            "related_complaints": [],
            "routing_target": None,
            "suggested_fix": None,
            "confidence": 0.0,
            "audit_trail": []
        }
        
        # Add audit entry
        utils.add_audit_entry(
            complaint_data,
            actor="api",
            action="Quick complaint filed"
        )
        
        # Classify
        complaint_data = self.classifier.classify_full(complaint_data)
        
        # Find similar
        similar = self.storage.find_similar_complaints(complaint_data)
        if similar:
            complaint_data["related_complaints"] = similar
        
        # Update status
        complaint_data["status"] = "routed"
        
        # Save
        self.storage.save(complaint_data)
        
        return complaint_data
