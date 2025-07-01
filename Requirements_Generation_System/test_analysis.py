#!/usr/bin/env python3

from downstream_resume_manager import DownstreamResumeManager
from orchestrator import RequirementsOrchestrator
from pathlib import Path
import asyncio

base_path = Path('project')
config_path = base_path / 'Requirements_Generation_System' / 'config.yaml'
orchestrator = RequirementsOrchestrator('LSOMigrator', base_path, config_path, 'openai')
manager = DownstreamResumeManager(base_path / 'Requirements_Generation_System', orchestrator)

analysis = manager.detect_incomplete_downstream_updates()
print('Analysis Results:')
print(f'Total requirements: {analysis["total_requirements"]}')
print(f'Missing in UI/UX: {len(analysis["missing_in_uiux"])} - {list(analysis["missing_in_uiux"])[:10]}')
print(f'Missing in testing: {len(analysis["missing_in_testing"])}')
print(f'Missing in RTM: {len(analysis["missing_in_rtm"])}')
print(f'Needs update: {analysis["needs_update"]}')
print(f'Source mod time: {analysis["source_mod_times"]}')
print(f'Downstream mod times: {analysis["downstream_mod_times"]}')

# Let's also check what requirements are actually in the FRD
print('\n--- FRD Requirements ---')
frd_reqs = manager._extract_requirement_ids_from_file(manager.requirements_path / "frd.md")
print(f'FRD requirements: {sorted(list(frd_reqs))}')

# And what's in the UI/UX files
print('\n--- UI/UX References ---')
uiux_refs = manager._extract_requirement_references_from_uiux()
print(f'UI/UX references: {sorted(list(uiux_refs))}')

# Check specific CRM requirements
crm_reqs = [req for req in frd_reqs if 'CRM' in req.upper() or 'BROKER' in req.upper() or 'SALES' in req.upper()]
print(f'\nCRM-related requirements in FRD: {crm_reqs}')

crm_in_uiux = [req for req in uiux_refs if 'CRM' in req.upper() or 'BROKER' in req.upper() or 'SALES' in req.upper()]
print(f'CRM-related requirements in UI/UX: {crm_in_uiux}')
