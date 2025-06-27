#!/usr/bin/env python3
"""
Script to update existing requirements with development_status field
and mark recent requirements as "new" for development planning.
"""

import json
from pathlib import Path
from datetime import datetime

def update_requirements_with_development_status():
    """Update all requirements with development_status field."""
    
    # Load the requirements tracker
    tracker_path = Path('d:/Repository/@Clients/FY.WB.Midway/Requirements_Traceable/cross-cutting/requirements_tracker.json')
    
    print(f"Loading requirements from: {tracker_path}")
    
    with open(tracker_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get the recent requirements from the last commit (REQ-FUNC-020 onwards)
    # These are the Pipedrive CRM requirements that were just added
    recent_req_ids = [
        'REQ-FUNC-020', 'REQ-FUNC-021', 'REQ-NFR-007', 'REQ-FUNC-022', 'REQ-FUNC-023',
        'REQ-FUNC-024', 'REQ-FUNC-025', 'REQ-FUNC-026', 'REQ-FUNC-027', 'REQ-FUNC-028',
        'REQ-FUNC-029', 'REQ-FUNC-030', 'REQ-FUNC-031', 'REQ-NFR-008', 'REQ-NFR-009',
        'REQ-NFR-010', 'REQ-NFR-011', 'REQ-NFR-012', 'REQ-DATA-004', 'REQ-FUNC-032'
    ]

    updated_count = 0
    new_count = 0

    # Update traceability_requirements list
    if 'traceability_requirements' in data:
        for req in data['traceability_requirements']:
            req_id = req.get('id', '')
            
            # Add development_status field to all requirements
            if 'development_status' not in req:
                if req_id in recent_req_ids:
                    req['development_status'] = 'new'  # Mark recent requirements as new
                    req['last_planned'] = None
                    req['plan_version'] = None
                    print(f"✅ Marked {req_id} as NEW for development planning")
                    new_count += 1
                else:
                    req['development_status'] = 'planned'  # Mark older requirements as already planned
                    req['last_planned'] = '2025-06-01T00:00:00'  # Assume they were planned before
                    req['plan_version'] = 'v1.0'
                
                updated_count += 1

    # Save the updated data
    with open(tracker_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\n🎯 SUMMARY:")
    print(f"   • Updated {updated_count} requirements with development_status field")
    print(f"   • Marked {new_count} recent requirements as 'new' for development planning")
    print(f"   • Total requirements in tracker: {len(data.get('traceability_requirements', []))}")
    
    # Show the new requirements that need development planning
    if new_count > 0:
        print(f"\n📋 NEW REQUIREMENTS READY FOR DEVELOPMENT PLANNING:")
        for req_id in recent_req_ids:
            print(f"   • {req_id}")
    
    return new_count

if __name__ == "__main__":
    update_requirements_with_development_status()
