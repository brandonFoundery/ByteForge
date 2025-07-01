#!/usr/bin/env python3
"""
Check the final development status after incremental planning.
"""

import json
from pathlib import Path

def check_development_status():
    """Check the current development status of all requirements."""
    
    # Load the requirements tracker
    tracker_path = Path('project/Requirements_Traceable/cross-cutting/requirements_tracker.json')
    
    with open(tracker_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count by development status
    status_counts = {'new': 0, 'planned': 0, 'in_development': 0, 'completed': 0}

    if 'traceability_requirements' in data:
        for req in data['traceability_requirements']:
            status = req.get('development_status', 'unknown')
            if status in status_counts:
                status_counts[status] += 1

    print('📊 FINAL DEVELOPMENT STATUS SUMMARY:')
    print(f'   • New requirements needing planning: {status_counts["new"]}')
    print(f'   • Already planned: {status_counts["planned"]}')
    print(f'   • In development: {status_counts["in_development"]}')
    print(f'   • Completed: {status_counts["completed"]}')

    # Show some recent requirements that were planned
    recent_planned = []
    if 'traceability_requirements' in data:
        for req in data['traceability_requirements']:
            if req.get('development_status') == 'planned' and req.get('plan_version', '').startswith('incremental-'):
                recent_planned.append(req['id'])

    if recent_planned:
        print(f'\n✅ Recently planned requirements ({len(recent_planned)}):')
        for req_id in recent_planned[:10]:  # Show first 10
            print(f'   • {req_id}')
        if len(recent_planned) > 10:
            print(f'   ... and {len(recent_planned) - 10} more')
    else:
        print('\n⚠️  No requirements found with incremental plan version')

    return status_counts, recent_planned

if __name__ == "__main__":
    check_development_status()
