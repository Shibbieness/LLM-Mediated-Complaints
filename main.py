#!/usr/bin/env python3
"""
Main CLI Entry Point for LLM-Mediated Complaint System
Provides interactive command-line interface
"""

import sys
from complaint_system import ComplaintSystem
import utils
import config


def print_banner():
    """Print system banner"""
    print("=" * 60)
    print(f"  {config.SYSTEM_NAME}")
    print(f"  Version {config.VERSION}")
    print("=" * 60)
    print()


def print_help():
    """Print help information"""
    print("""
Available Commands:
  file     - File a new complaint (interactive)
  quick    - Quick file a complaint (provide all info at once)
  view     - View a specific complaint by ID
  list     - List complaints (by category, severity, or status)
  stats    - View system statistics
  update   - Update complaint status
  help     - Show this help message
  exit     - Exit the program

Examples:
  > file
  > view CMP-2026-02-02-AX4F9Q
  > list category model_behavior
  > list severity critical
  > stats
""")


def handle_file_command(system: ComplaintSystem):
    """Handle interactive complaint filing"""
    print("\n--- Filing New Complaint ---")
    print("Please describe your issue:")
    initial_message = input("> ")
    
    if not initial_message.strip():
        print("Error: Please provide a description.")
        return
    
    # Start intake
    response = system.start_complaint_intake(initial_message)
    print(f"\n{response}")
    
    # Continue conversation
    while system.mode == "complaint_intake":
        user_input = input("> ")
        response = system.continue_conversation(user_input)
        print(f"\n{response}")
    
    print("\n✓ Complaint filed successfully!")


def handle_quick_file_command(system: ComplaintSystem):
    """Handle quick complaint filing"""
    print("\n--- Quick File Complaint ---")
    
    print("Brief summary:")
    summary = input("> ")
    
    print("What were you trying to do?")
    intent = input("> ")
    
    print("What actually happened?")
    observed = input("> ")
    
    print("What did you expect?")
    expected = input("> ")
    
    print("Frequency (once/intermittent/persistent)? [once]:")
    frequency = input("> ").strip() or "once"
    
    if frequency not in ["once", "intermittent", "persistent"]:
        frequency = "unknown"
    
    # File complaint
    complaint = system.quick_file_complaint(
        summary, intent, observed, expected, frequency
    )
    
    print(f"\n✓ Complaint filed!")
    print(f"ID: {complaint['complaint_id']}")
    print(f"Category: {complaint['primary_category']}")
    print(f"Severity: {complaint['severity']}")
    print(f"Routed to: {complaint['routing_target']}")


def handle_view_command(system: ComplaintSystem, args: list):
    """Handle view complaint command"""
    if len(args) < 2:
        print("Usage: view <complaint_id>")
        return
    
    complaint_id = args[1]
    complaint = system.get_complaint(complaint_id)
    
    if complaint:
        print("\n" + utils.format_complaint_summary(complaint))
        
        if complaint.get("related_complaints"):
            print(f"\nRelated: {len(complaint['related_complaints'])} similar complaints")
        
        if complaint.get("audit_trail"):
            print("\n--- Audit Trail ---")
            for entry in complaint["audit_trail"][-5:]:  # Last 5 entries
                print(f"  [{entry['timestamp']}] {entry['actor']}: {entry['action']}")
    else:
        print(f"Complaint {complaint_id} not found.")


def handle_list_command(system: ComplaintSystem, args: list):
    """Handle list complaints command"""
    if len(args) < 3:
        print("Usage: list <type> <value>")
        print("  Types: category, severity, status")
        print("  Example: list category bug")
        return
    
    list_type = args[1].lower()
    value = args[2].lower()
    
    if list_type == "category":
        complaints = system.list_complaints_by_category(value)
    elif list_type == "severity":
        complaints = system.list_complaints_by_severity(value)
    elif list_type == "status":
        complaints = system.list_complaints_by_status(value)
    else:
        print(f"Unknown list type: {list_type}")
        return
    
    if complaints:
        print(f"\nFound {len(complaints)} complaint(s):\n")
        for c in complaints:
            severity_emoji = utils.get_severity_emoji(c['severity'])
            print(f"{severity_emoji} {c['complaint_id']} - {c['primary_category']} "
                  f"({c['status']}) - {c['user_intent'][:50]}...")
    else:
        print(f"No complaints found for {list_type}={value}")


def handle_stats_command(system: ComplaintSystem):
    """Handle statistics command"""
    stats = system.get_statistics()
    
    print("\n--- System Statistics ---")
    print(f"Total Complaints: {stats['total_complaints']}")
    
    print("\nBy Category:")
    for category, count in stats['by_category'].items():
        emoji = config.PRIMARY_CATEGORIES.get(category, {}).get("emoji", "❓")
        print(f"  {emoji} {category}: {count}")
    
    print("\nBy Severity:")
    for severity, count in stats['by_severity'].items():
        emoji = utils.get_severity_emoji(severity)
        print(f"  {emoji} {severity}: {count}")
    
    print("\nBy Status:")
    for status, count in stats['by_status'].items():
        print(f"  • {status}: {count}")


def handle_update_command(system: ComplaintSystem, args: list):
    """Handle update status command"""
    if len(args) < 3:
        print("Usage: update <complaint_id> <new_status>")
        print("  Valid statuses: triaged, structured, clustered, routed,")
        print("                  in_progress, awaiting_user, resolved, closed, reopened")
        return
    
    complaint_id = args[1]
    new_status = args[2].lower()
    
    success = system.update_complaint_status(complaint_id, new_status)
    
    if success:
        print(f"✓ Updated {complaint_id} status to {new_status}")
    else:
        print(f"✗ Failed to update status (invalid transition or complaint not found)")


def main():
    """Main CLI loop"""
    print_banner()
    
    # Initialize system
    system = ComplaintSystem()
    
    print("Type 'help' for available commands or 'file' to submit a complaint.")
    print()
    
    while True:
        try:
            user_input = input("complaint-system> ").strip()
            
            if not user_input:
                continue
            
            args = user_input.split()
            command = args[0].lower()
            
            if command == "exit" or command == "quit":
                print("Goodbye!")
                break
            
            elif command == "help":
                print_help()
            
            elif command == "file":
                handle_file_command(system)
            
            elif command == "quick":
                handle_quick_file_command(system)
            
            elif command == "view":
                handle_view_command(system, args)
            
            elif command == "list":
                handle_list_command(system, args)
            
            elif command == "stats":
                handle_stats_command(system)
            
            elif command == "update":
                handle_update_command(system, args)
            
            else:
                # Check if it's a complaint trigger
                if system.detect_complaint(user_input):
                    print("\nComplaint detected. Starting intake process...")
                    response = system.start_complaint_intake(user_input)
                    print(f"\n{response}")
                    
                    while system.mode == "complaint_intake":
                        user_response = input("> ")
                        response = system.continue_conversation(user_response)
                        print(f"\n{response}")
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
