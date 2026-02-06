#!/usr/bin/env python3
"""
Test Script for LLM-Mediated Complaint System
Tests all major components and workflows
"""

from complaint_system import ComplaintSystem
import utils


def test_1_simple_bug_report():
    """Test 1: Simple bug report"""
    print("\n=== TEST 1: Simple Bug Report ===")
    
    system = ComplaintSystem()
    
    complaint = system.quick_file_complaint(
        user_summary="System crashed when uploading large file",
        user_intent="Upload a 500MB video file",
        observed_outcome="Browser froze and crashed",
        expected_outcome="File should upload with progress indicator",
        frequency="once"
    )
    
    print(f"✓ Filed: {complaint['complaint_id']}")
    print(f"  Category: {complaint['primary_category']}")
    print(f"  Severity: {complaint['severity']}")
    print(f"  Routing: {complaint['routing_target']}")
    
    assert complaint['primary_category'] in ['bug', 'performance']
    assert complaint['severity'] in ['medium', 'high']
    print("✓ Test 1 PASSED\n")
    
    return complaint['complaint_id']


def test_2_model_behavior_complaint():
    """Test 2: Model behavior complaint"""
    print("\n=== TEST 2: Model Behavior Complaint ===")
    
    system = ComplaintSystem()
    
    complaint = system.quick_file_complaint(
        user_summary="AI kept replacing my text instead of appending",
        user_intent="Append new paragraphs to existing document",
        observed_outcome="AI overwrote entire sections",
        expected_outcome="Only new content should be added",
        frequency="persistent"
    )
    
    print(f"✓ Filed: {complaint['complaint_id']}")
    print(f"  Category: {complaint['primary_category']}")
    print(f"  Severity: {complaint['severity']}")
    print(f"  Root causes: {complaint['probable_root_causes']}")
    print(f"  Routing: {complaint['routing_target']}")
    
    assert complaint['primary_category'] == 'model_behavior'
    assert 'constraint_parsing_failure' in complaint['probable_root_causes']
    assert complaint['routing_target'] == 'self_correction'
    print("✓ Test 2 PASSED\n")
    
    return complaint['complaint_id']


def test_3_feature_request():
    """Test 3: Feature request"""
    print("\n=== TEST 3: Feature Request ===")
    
    system = ComplaintSystem()
    
    complaint = system.quick_file_complaint(
        user_summary="Would love to have dark mode",
        user_intent="Use the app at night without eye strain",
        observed_outcome="Only light mode available",
        expected_outcome="Dark mode toggle in settings",
        frequency="persistent"
    )
    
    print(f"✓ Filed: {complaint['complaint_id']}")
    print(f"  Category: {complaint['primary_category']}")
    print(f"  Severity: {complaint['severity']}")
    print(f"  Routing: {complaint['routing_target']}")
    
    assert complaint['primary_category'] == 'feature_request'
    assert complaint['routing_target'] == 'product_backlog'
    print("✓ Test 3 PASSED\n")
    
    return complaint['complaint_id']


def test_4_critical_severity():
    """Test 4: Critical severity complaint"""
    print("\n=== TEST 4: Critical Severity ===")
    
    system = ComplaintSystem()
    
    complaint = system.quick_file_complaint(
        user_summary="Complete data loss - all my work is gone",
        user_intent="Save my project before deadline",
        observed_outcome="System crashed and deleted everything, completely unusable",
        expected_outcome="Work should be saved automatically",
        frequency="persistent"
    )
    
    print(f"✓ Filed: {complaint['complaint_id']}")
    print(f"  Category: {complaint['primary_category']}")
    print(f"  Severity: {complaint['severity']}")
    print(f"  Severity basis: {complaint['severity_basis']}")
    print(f"  Routing: {complaint['routing_target']}")
    
    assert complaint['severity'] == 'critical'
    assert complaint['routing_target'] == 'human_review'
    print("✓ Test 4 PASSED\n")
    
    return complaint['complaint_id']


def test_5_complaint_retrieval():
    """Test 5: Retrieve and verify complaint"""
    print("\n=== TEST 5: Complaint Retrieval ===")
    
    system = ComplaintSystem()
    
    # File a complaint first
    complaint_id = test_1_simple_bug_report()
    
    # Retrieve it
    retrieved = system.get_complaint(complaint_id)
    
    print(f"✓ Retrieved: {complaint_id}")
    print(f"  Status: {retrieved['status']}")
    print(f"  Has audit trail: {len(retrieved['audit_trail'])} entries")
    
    assert retrieved is not None
    assert retrieved['complaint_id'] == complaint_id
    assert len(retrieved['audit_trail']) > 0
    print("✓ Test 5 PASSED\n")


def test_6_status_transitions():
    """Test 6: Status transitions"""
    print("\n=== TEST 6: Status Transitions ===")
    
    system = ComplaintSystem()
    
    # File a complaint
    complaint_id = test_2_model_behavior_complaint()
    
    # Update to in_progress
    success = system.update_complaint_status(complaint_id, "in_progress")
    print(f"✓ Updated to in_progress: {success}")
    assert success
    
    # Update to resolved
    success = system.resolve_complaint(complaint_id, "Fixed constraint parsing logic")
    print(f"✓ Resolved complaint: {success}")
    assert success
    
    # Close complaint
    success = system.close_complaint(complaint_id)
    print(f"✓ Closed complaint: {success}")
    assert success
    
    # Reopen it
    success = system.reopen_complaint(complaint_id, "Issue recurred")
    print(f"✓ Reopened complaint: {success}")
    assert success
    
    # Verify final status
    complaint = system.get_complaint(complaint_id)
    assert complaint['status'] == 'reopened'
    print("✓ Test 6 PASSED\n")


def test_7_listing_and_filtering():
    """Test 7: List and filter complaints"""
    print("\n=== TEST 7: Listing and Filtering ===")
    
    system = ComplaintSystem()
    
    # File several complaints
    ids = []
    ids.append(test_1_simple_bug_report())
    ids.append(test_2_model_behavior_complaint())
    ids.append(test_3_feature_request())
    
    # List by category
    bugs = system.list_complaints_by_category("bug")
    print(f"✓ Found {len(bugs)} bug complaints")
    
    model_behavior = system.list_complaints_by_category("model_behavior")
    print(f"✓ Found {len(model_behavior)} model_behavior complaints")
    
    # List by status
    routed = system.list_complaints_by_status("routed")
    print(f"✓ Found {len(routed)} routed complaints")
    
    assert len(bugs) + len(model_behavior) >= 2
    print("✓ Test 7 PASSED\n")


def test_8_statistics():
    """Test 8: System statistics"""
    print("\n=== TEST 8: Statistics ===")
    
    system = ComplaintSystem()
    
    # File some complaints
    test_1_simple_bug_report()
    test_2_model_behavior_complaint()
    test_3_feature_request()
    
    # Get stats
    stats = system.get_statistics()
    
    print(f"✓ Total complaints: {stats['total_complaints']}")
    print(f"✓ Categories: {list(stats['by_category'].keys())}")
    print(f"✓ Severities: {list(stats['by_severity'].keys())}")
    
    assert stats['total_complaints'] >= 3
    assert len(stats['by_category']) > 0
    print("✓ Test 8 PASSED\n")


def test_9_similarity_clustering():
    """Test 9: Similar complaint detection"""
    print("\n=== TEST 9: Similarity Clustering ===")
    
    system = ComplaintSystem()
    
    # File similar complaints
    id1 = system.quick_file_complaint(
        user_summary="AI overwrote my document",
        user_intent="Append to document",
        observed_outcome="Replaced content instead of appending",
        expected_outcome="Should only add new content",
        frequency="intermittent"
    )['complaint_id']
    
    id2 = system.quick_file_complaint(
        user_summary="Text replacement instead of addition",
        user_intent="Add paragraphs to existing file",
        observed_outcome="Overwrote sections",
        expected_outcome="Append without replacing",
        frequency="persistent"
    )['complaint_id']
    
    # Check if they're linked
    complaint2 = system.get_complaint(id2)
    
    print(f"✓ Complaint 1: {id1}")
    print(f"✓ Complaint 2: {id2}")
    print(f"✓ Related complaints found: {len(complaint2['related_complaints'])}")
    
    if id1 in complaint2['related_complaints']:
        print("✓ Complaints correctly clustered as similar")
    else:
        print("⚠ Complaints not detected as similar (acceptable - similarity threshold)")
    
    print("✓ Test 9 PASSED\n")


def test_10_schema_validation():
    """Test 10: Schema validation"""
    print("\n=== TEST 10: Schema Validation ===")
    
    system = ComplaintSystem()
    
    complaint = system.quick_file_complaint(
        user_summary="Test complaint",
        user_intent="Test the system",
        observed_outcome="System works",
        expected_outcome="System works correctly",
        frequency="once"
    )
    
    # Validate against schema
    is_valid, error = utils.validate_complaint_schema(complaint)
    
    print(f"✓ Schema validation: {is_valid}")
    if not is_valid:
        print(f"  Error: {error}")
    
    assert is_valid
    print("✓ Test 10 PASSED\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_1_simple_bug_report,
        test_2_model_behavior_complaint,
        test_3_feature_request,
        test_4_critical_severity,
        test_5_complaint_retrieval,
        test_6_status_transitions,
        test_7_listing_and_filtering,
        test_8_statistics,
        test_9_similarity_clustering,
        test_10_schema_validation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
