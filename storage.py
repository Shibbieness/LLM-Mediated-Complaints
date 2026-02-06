"""
Storage Module for Complaint System
Handles persistence, retrieval, indexing, and clustering of complaints
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

import config
import utils


class ComplaintStorage:
    """
    Manages storage and retrieval of complaint records
    """
    
    def __init__(self):
        self.complaints_dir = config.COMPLAINTS_DIR
        self.indices_dir = config.INDICES_DIR
        self._ensure_directories()
        self._load_indices()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        self.complaints_dir.mkdir(parents=True, exist_ok=True)
        self.indices_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_indices(self):
        """Load all index files"""
        self.category_index = self._load_index("by_category.json")
        self.severity_index = self._load_index("by_severity.json")
        self.status_index = self._load_index("by_status.json")
    
    def _load_index(self, filename: str) -> Dict:
        """Load a specific index file"""
        path = self.indices_dir / filename
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self, filename: str, data: Dict):
        """Save a specific index file"""
        path = self.indices_dir / filename
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_indices(self, complaint_data: Dict[str, Any]):
        """Update all indices with new complaint"""
        complaint_id = complaint_data["complaint_id"]
        
        # Update category index
        category = complaint_data.get("primary_category", "other")
        if category not in self.category_index:
            self.category_index[category] = []
        if complaint_id not in self.category_index[category]:
            self.category_index[category].append(complaint_id)
        
        # Update severity index
        severity = complaint_data.get("severity", "low")
        if severity not in self.severity_index:
            self.severity_index[severity] = []
        if complaint_id not in self.severity_index[severity]:
            self.severity_index[severity].append(complaint_id)
        
        # Update status index
        status = complaint_data.get("status", "new")
        if status not in self.status_index:
            self.status_index[status] = []
        if complaint_id not in self.status_index[status]:
            self.status_index[status].append(complaint_id)
        
        # Save updated indices
        self._save_index("by_category.json", self.category_index)
        self._save_index("by_severity.json", self.severity_index)
        self._save_index("by_status.json", self.status_index)
    
    def save(self, complaint_data: Dict[str, Any]) -> bool:
        """
        Save complaint to storage
        
        Args:
            complaint_data: Complete complaint dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Validate schema
            is_valid, error = utils.validate_complaint_schema(complaint_data)
            if not is_valid:
                print(f"Schema validation error: {error}")
                return False
            
            # Get file path
            complaint_id = complaint_data["complaint_id"]
            file_path = utils.get_complaint_file_path(complaint_id)
            
            # Save complaint
            with open(file_path, 'w') as f:
                json.dump(complaint_data, f, indent=2)
            
            # Update indices
            self._update_indices(complaint_data)
            
            return True
        
        except Exception as e:
            print(f"Error saving complaint: {e}")
            return False
    
    def load(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load complaint by ID
        
        Args:
            complaint_id: Complaint identifier
            
        Returns:
            Complaint data or None if not found
        """
        try:
            file_path = utils.get_complaint_file_path(complaint_id)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading complaint {complaint_id}: {e}")
            return None
    
    def update(self, complaint_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing complaint
        
        Args:
            complaint_id: Complaint identifier
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        complaint_data = self.load(complaint_id)
        if complaint_data is None:
            return False
        
        # Apply updates
        complaint_data.update(updates)
        
        # Add audit entry
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action=f"Updated fields: {', '.join(updates.keys())}"
        )
        
        return self.save(complaint_data)
    
    def update_status(self, complaint_id: str, new_status: str) -> bool:
        """
        Update complaint status
        
        Args:
            complaint_id: Complaint identifier
            new_status: New status value
            
        Returns:
            bool: Success status
        """
        complaint_data = self.load(complaint_id)
        if complaint_data is None:
            return False
        
        old_status = complaint_data.get("status", "new")
        
        # Validate transition
        valid_transitions = config.VALID_STATUS_TRANSITIONS.get(old_status, [])
        if new_status not in valid_transitions and new_status != old_status:
            print(f"Invalid status transition: {old_status} -> {new_status}")
            return False
        
        # Update status
        complaint_data["status"] = new_status
        
        # Add audit entry
        utils.add_audit_entry(
            complaint_data,
            actor="system",
            action=f"Status changed: {old_status} -> {new_status}"
        )
        
        # Update indices (remove from old status, add to new)
        if old_status in self.status_index:
            if complaint_id in self.status_index[old_status]:
                self.status_index[old_status].remove(complaint_id)
        
        if new_status not in self.status_index:
            self.status_index[new_status] = []
        if complaint_id not in self.status_index[new_status]:
            self.status_index[new_status].append(complaint_id)
        
        self._save_index("by_status.json", self.status_index)
        
        return self.save(complaint_data)
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all complaints in a category"""
        complaint_ids = self.category_index.get(category, [])
        return [self.load(cid) for cid in complaint_ids if self.load(cid)]
    
    def search_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get all complaints with a severity level"""
        complaint_ids = self.severity_index.get(severity, [])
        return [self.load(cid) for cid in complaint_ids if self.load(cid)]
    
    def search_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all complaints with a status"""
        complaint_ids = self.status_index.get(status, [])
        return [self.load(cid) for cid in complaint_ids if self.load(cid)]
    
    def get_all_complaint_ids(self) -> List[str]:
        """Get list of all complaint IDs"""
        all_ids = set()
        for category_list in self.category_index.values():
            all_ids.update(category_list)
        return sorted(list(all_ids))
    
    def find_similar_complaints(self, complaint_data: Dict[str, Any], 
                                threshold: float = 0.75) -> List[str]:
        """
        Find similar complaints using simple text matching
        
        Args:
            complaint_data: Complaint to compare
            threshold: Similarity threshold (not used in simple implementation)
            
        Returns:
            List of similar complaint IDs
        """
        similar = []
        
        # Get complaints in same category
        category = complaint_data.get("primary_category", "other")
        same_category = self.search_by_category(category)
        
        # Extract key phrases from new complaint
        new_text = f"{complaint_data.get('user_intent', '')} " \
                   f"{complaint_data.get('observed_outcome', '')}".lower()
        new_keywords = set(utils.extract_keywords(new_text))
        
        # Compare with existing complaints
        for existing in same_category:
            if existing["complaint_id"] == complaint_data.get("complaint_id"):
                continue
            
            existing_text = f"{existing.get('user_intent', '')} " \
                          f"{existing.get('observed_outcome', '')}".lower()
            existing_keywords = set(utils.extract_keywords(existing_text))
            
            # Calculate simple keyword overlap
            if len(new_keywords) > 0:
                overlap = len(new_keywords & existing_keywords) / len(new_keywords)
                if overlap >= 0.5:  # 50% keyword overlap
                    similar.append(existing["complaint_id"])
        
        return similar
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            "total_complaints": len(self.get_all_complaint_ids()),
            "by_category": {k: len(v) for k, v in self.category_index.items()},
            "by_severity": {k: len(v) for k, v in self.severity_index.items()},
            "by_status": {k: len(v) for k, v in self.status_index.items()}
        }
