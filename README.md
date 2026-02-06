# LLM-Mediated Complaint Intake System v1.0.0

## Overview

A conversational complaint processor that converts free-form user grievances into structured, sortable, trackable records through intelligent conversation and automated classification.

## System Architecture

```
Human Complaint → LLM Understanding Layer → Structured Record → System of Action
```

### Core Functions
1. **Elicit** - Draw out what the user actually means through intelligent conversation
2. **Structure** - Convert into standardized data objects
3. **Route/Store/Sort** - File appropriately for action

## Features

### MVP (Phase 1) - ✅ Implemented
- ✅ Complaint detection and mode switching
- ✅ Conversational intake with guided questions
- ✅ Automatic classification (9 categories)
- ✅ Severity calculation with reasoning
- ✅ Root cause analysis
- ✅ File-based storage with indexing
- ✅ Status tracking and transitions
- ✅ Audit trail for all changes
- ✅ Basic similarity detection

### Categories Supported
- 🐞 **Bug / Malfunction** - System crashes, errors, technical failures
- 🤖 **Model Behavior** - AI not following constraints, hallucinations, tone issues
- 🖥 **UX / UI** - Interface confusion, accessibility problems
- 💡 **Feature Request** - New capability requests
- 📜 **Policy Friction** - Restriction or safety policy issues
- 🚀 **Performance** - Latency, timeouts, slow responses
- 🔐 **Trust / Safety** - Privacy or security concerns
- 🧠 **Misunderstanding** - Confusion about how features work
- ❓ **Other** - Uncategorized complaints

### Severity Levels
- 🔴 **Critical** - System completely unusable, data loss, urgent
- 🟠 **High** - Major functionality broken, blocks work
- 🟡 **Medium** - Frustrating issues, workarounds exist
- 🟢 **Low** - Minor inconveniences

## Installation

### Requirements
- Python 3.8+
- No external dependencies required (self-contained)

### Setup
```bash
# Clone or extract the system
cd complaint-system

# Run tests to verify installation
python3 test_system.py

# Start the CLI interface
python3 main.py
```

## Usage

### Interactive CLI

```bash
python3 main.py
```

**Available Commands:**
```
file     - File a new complaint (interactive conversation)
quick    - Quick file with all information at once
view     - View a specific complaint by ID
list     - List complaints by category/severity/status
stats    - View system statistics
update   - Update complaint status
help     - Show help
exit     - Exit program
```

### Examples

#### Filing a Complaint (Interactive)
```
complaint-system> file
Please describe your issue:
> The AI kept replacing my text instead of appending to it

I can help you file that complaint. I'll need to ask you a few quick questions...

What were you trying to accomplish?
> Add new sections to my document

What actually happened?
> It overwrote existing content

What did you expect to happen?
> It should only add new content without touching existing text

✓ Complaint filed!
ID: CMP-2026-02-02-AX4F9Q
Category: model_behavior
Severity: medium
Routed to: self_correction
```

#### Quick Filing
```
complaint-system> quick
Brief summary: System crashed when uploading files
What were you trying to do? Upload a large video
What actually happened? Browser froze and crashed
What did you expect? Smooth upload with progress
Frequency: once

✓ Complaint filed!
ID: CMP-2026-02-02-BK7H2M
Category: bug
Severity: medium
```

#### Viewing Complaints
```
complaint-system> view CMP-2026-02-02-AX4F9Q

🤖 Complaint CMP-2026-02-02-AX4F9Q
🟡 Severity: MEDIUM
📊 Category: model_behavior
📅 Reported: 2026-02-02T14:32:11
🔄 Status: routed

Intent: Add new sections to my document
Observed: It overwrote existing content
Expected: It should only add new content without touching existing text

Related: 2 similar complaints

--- Audit Trail ---
  [2026-02-02T14:32:11] system: Complaint intake initiated
  [2026-02-02T14:32:25] system: Complaint triaged
  [2026-02-02T14:32:25] system: Complaint structured and classified
  [2026-02-02T14:32:25] system: Clustered with 2 similar complaints
  [2026-02-02T14:32:25] system: Routed to self_correction
```

#### Listing and Filtering
```
complaint-system> list category bug
Found 5 complaint(s):
🟡 CMP-2026-02-02-XXXXXX - bug (routed) - Upload failed...
🔴 CMP-2026-02-02-YYYYYY - bug (in_progress) - Data loss...

complaint-system> list severity critical
Found 1 complaint(s):
🔴 CMP-2026-02-02-YYYYYY - bug (in_progress) - Complete data loss

complaint-system> stats
--- System Statistics ---
Total Complaints: 12

By Category:
  🐞 bug: 5
  🤖 model_behavior: 4
  💡 feature_request: 2
  ❓ other: 1

By Severity:
  🔴 critical: 1
  🟠 high: 3
  🟡 medium: 7
  🟢 low: 1

By Status:
  • routed: 8
  • in_progress: 3
  • resolved: 1
```

### Programmatic Usage

```python
from complaint_system import ComplaintSystem

# Initialize system
system = ComplaintSystem()

# Quick file a complaint
complaint = system.quick_file_complaint(
    user_summary="Button doesn't work",
    user_intent="Click the submit button",
    observed_outcome="Nothing happens",
    expected_outcome="Form should submit",
    frequency="persistent"
)

print(f"Filed: {complaint['complaint_id']}")
print(f"Category: {complaint['primary_category']}")
print(f"Severity: {complaint['severity']}")

# Retrieve complaint
complaint_data = system.get_complaint(complaint['complaint_id'])

# Update status
system.update_complaint_status(complaint['complaint_id'], "in_progress")

# Get statistics
stats = system.get_statistics()
print(f"Total complaints: {stats['total_complaints']}")
```

## File Structure

```
complaint-system/
├── complaint_schema.json     # JSON schema definition
├── config.py                 # Configuration and constants
├── utils.py                  # Utility functions
├── classifier.py             # Classification engine
├── storage.py                # Persistence layer
├── conversation_handler.py   # Conversation management
├── complaint_system.py       # Main orchestrator
├── main.py                   # CLI interface
├── test_system.py            # Test suite
├── complaint_data/           # Data storage (auto-created)
│   ├── complaints/           # Individual complaint files
│   │   └── YYYY/MM/          # Organized by date
│   └── indices/              # Indexing files
│       ├── by_category.json
│       ├── by_severity.json
│       └── by_status.json
└── README.md                 # This file
```

## Data Model

### Complaint Object
```json
{
  "complaint_id": "CMP-YYYY-MM-DD-XXXXXX",
  "reported_at": "ISO8601 timestamp",
  "incident_at": "ISO8601 timestamp or null",
  "status": "new|triaged|structured|clustered|routed|in_progress|awaiting_user|resolved|closed|reopened",
  "user_summary": "User's description",
  "primary_category": "Category identifier",
  "secondary_categories": ["Additional categories"],
  "severity": "low|medium|high|critical",
  "severity_basis": ["Reasons for severity"],
  "frequency": "once|intermittent|persistent|unknown",
  "user_intent": "What user was trying to do",
  "observed_outcome": "What actually happened",
  "expected_outcome": "What should have happened",
  "context": "Additional context",
  "evidence": [{"type": "text|screenshot|log|link", "content": "..."}],
  "probable_root_causes": ["Inferred causes"],
  "related_complaints": ["Similar complaint IDs"],
  "routing_target": "self_correction|human_review|product_backlog|...",
  "suggested_fix": "System suggestion",
  "confidence": 0.85,
  "audit_trail": [{"timestamp": "...", "actor": "...", "action": "..."}]
}
```

### Status Lifecycle
```
NEW → TRIAGED → STRUCTURED → CLUSTERED → ROUTED →
IN_PROGRESS → RESOLVED → CLOSED
               ↓
          REOPENED → (back to TRIAGED)
```

## Routing Logic

The system automatically routes complaints based on:

| Category | Severity | Root Cause | → Routing Target |
|----------|----------|------------|------------------|
| Any | Critical | Any | Human Review |
| Bug | High | Any | Human Review |
| Trust/Safety | High+ | Any | Safety Escalation |
| Model Behavior | Any | Constraint Failure | Self-Correction |
| Feature Request | Medium+ | Any | Product Backlog |
| Misunderstanding | Any | Persistent | Documentation Update |
| Performance | High+ | Any | Human Review |

## Testing

Run the comprehensive test suite:

```bash
python3 test_system.py
```

**Test Coverage:**
- ✅ Bug report filing
- ✅ Model behavior complaints
- ✅ Feature requests
- ✅ Critical severity escalation
- ✅ Complaint retrieval
- ✅ Status transitions
- ✅ Listing and filtering
- ✅ Statistics generation
- ✅ Similarity clustering
- ✅ Schema validation

All 10 tests pass successfully.

## Advanced Features (Planned)

### Phase 2 - Enhanced Version
- [ ] Embedding-based similarity (better clustering)
- [ ] Multi-language support
- [ ] Attachment handling
- [ ] Email notifications
- [ ] API endpoints (REST/GraphQL)
- [ ] Web dashboard
- [ ] Real-time analytics

### Phase 3 - Advanced Version
- [ ] Machine learning for classification
- [ ] Predictive routing
- [ ] Automated resolution suggestions
- [ ] Integration with ticketing systems
- [ ] User feedback loops
- [ ] Pattern detection across time
- [ ] Trend analysis and reporting

## Customization

### Adding New Categories

Edit `config.py`:

```python
PRIMARY_CATEGORIES = {
    "your_category": {
        "emoji": "🔧",
        "description": "Your category description",
        "keywords": ["keyword1", "keyword2"]
    }
}
```

### Modifying Routing Rules

Edit `config.py`:

```python
ROUTING_RULES = {
    "your_target": {
        "conditions": ["category_name"],
        "severity_min": "medium"
    }
}
```

### Adjusting Severity Calculation

Modify `classifier.py` → `calculate_severity()` method to change scoring logic.

## Troubleshooting

### Common Issues

**Q: Complaints not being detected**
A: Ensure your input contains trigger phrases like "file a complaint", "this doesn't work", "report a bug"

**Q: Wrong category assigned**
A: Add more specific keywords to `config.py` for your use case

**Q: Storage errors**
A: Check file permissions on `complaint_data/` directory

**Q: Tests failing**
A: Verify Python 3.8+ is installed and run from correct directory

## API Reference

### ComplaintSystem

**Main Methods:**

- `start_complaint_intake(initial_message: str) -> str`
  - Begin conversational intake
  
- `continue_conversation(user_response: str) -> str`
  - Process user responses during intake
  
- `quick_file_complaint(...) -> Dict`
  - File complaint with all information provided
  
- `get_complaint(complaint_id: str) -> Dict`
  - Retrieve complaint by ID
  
- `list_complaints_by_category(category: str) -> List[Dict]`
  - Get all complaints in category
  
- `update_complaint_status(complaint_id: str, new_status: str) -> bool`
  - Update complaint status
  
- `get_statistics() -> Dict`
  - Get system statistics

## License

This system is provided as-is for use and modification.

## Support

For issues, enhancements, or questions:
1. Check the documentation above
2. Run the test suite to verify functionality
3. Review the code comments for implementation details

## Version History

### v1.0.0 (2026-02-02)
- Initial release
- Full MVP implementation
- 9 complaint categories
- Automatic classification and routing
- File-based storage
- CLI interface
- Comprehensive test suite
