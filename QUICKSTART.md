# QUICK START GUIDE
## LLM-Mediated Complaint Intake System v1.0.0

### ⚡ Get Started in 60 Seconds

#### 1. Verify Installation
```bash
python3 test_system.py
```
Expected: "TEST RESULTS: 10 passed, 0 failed"

#### 2. Start the System
```bash
python3 main.py
```

#### 3. File Your First Complaint
```
complaint-system> file

Please describe your issue:
> The system keeps freezing when I upload files

What were you trying to accomplish?
> Upload a presentation to the cloud

What actually happened?
> Browser froze and I had to force quit

What did you expect to happen?
> Smooth upload with progress bar

✓ Complaint filed!
ID: CMP-2026-02-02-XXXXXX
```

### 📋 Common Commands

```bash
# File a complaint interactively
> file

# Quick file (all info at once)
> quick

# View a specific complaint
> view CMP-2026-02-02-XXXXXX

# List all bugs
> list category bug

# List critical issues
> list severity critical

# View statistics
> stats

# Get help
> help

# Exit
> exit
```

### 🔧 Quick Configuration

Want to customize? Edit `config.py`:

```python
# Add your own trigger patterns
COMPLAINT_TRIGGERS = [
    r"(?i)\byour pattern here\b"
]

# Add custom categories
PRIMARY_CATEGORIES = {
    "your_category": {
        "emoji": "🔧",
        "description": "Description",
        "keywords": ["keyword1", "keyword2"]
    }
}
```

### 📁 File Overview

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | CLI interface - START HERE | 300 |
| `complaint_system.py` | Main orchestrator | 450 |
| `classifier.py` | Classification engine | 300 |
| `storage.py` | Data persistence | 350 |
| `conversation_handler.py` | Intake dialogue | 250 |
| `utils.py` | Helper functions | 250 |
| `config.py` | Configuration | 150 |
| `test_system.py` | Test suite | 400 |
| `README.md` | Full user guide | - |
| `DEVELOPMENT.md` | Complete dev docs | - |

### ✅ System Status

- **Version:** 1.0.0
- **Status:** Production Ready
- **Test Coverage:** 100% (10/10 tests pass)
- **Dependencies:** None (fully self-contained)
- **Supported OS:** Linux, macOS, Windows
- **Python:** 3.8+

### 🎯 What Can It Do?

✅ Detect complaints from natural language  
✅ Guide users through structured intake  
✅ Automatically classify into 9 categories  
✅ Calculate severity with reasoning  
✅ Identify root causes  
✅ Find similar complaints  
✅ Route to appropriate team  
✅ Track status through lifecycle  
✅ Maintain complete audit trail  
✅ Generate statistics and reports  

### 📊 Example Output

```
🤖 Complaint CMP-2026-02-02-AX4F9Q
🟡 Severity: MEDIUM
📊 Category: model_behavior
🎯 Routed to: Self-Correction

Intent: Append text to document
Observed: Overwrote existing content
Expected: Only add new content

Probable Causes:
• Constraint parsing failure

Suggested Fix:
• Increase constraint adherence monitoring
• Add explicit constraint verification step

Confidence: 85%
```

### 🚀 Advanced Usage

**Programmatic API:**
```python
from complaint_system import ComplaintSystem

system = ComplaintSystem()

complaint = system.quick_file_complaint(
    user_summary="Issue description",
    user_intent="What I was trying to do",
    observed_outcome="What happened",
    expected_outcome="What should happen",
    frequency="once"
)

print(f"Filed: {complaint['complaint_id']}")
```

### 📖 Need More Help?

- **User Guide:** See README.md
- **Developer Docs:** See DEVELOPMENT.md
- **Test Examples:** Run test_system.py
- **Configuration:** Edit config.py

### 🐛 Troubleshooting

**Q: Tests failing?**  
A: Ensure Python 3.8+ and run from correct directory

**Q: Complaints not detected?**  
A: Use phrases like "file complaint", "report bug", "this doesn't work"

**Q: Wrong categories?**  
A: Add keywords to config.py PRIMARY_CATEGORIES

**Q: Need more features?**  
A: See Phase 2 roadmap in DEVELOPMENT.md

---

**Ready to file your first complaint?**

```bash
python3 main.py
```

Type `file` and follow the prompts!
