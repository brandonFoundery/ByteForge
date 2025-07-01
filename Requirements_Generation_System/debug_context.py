#!/usr/bin/env python3

from orchestrator import RequirementsOrchestrator, DocumentType
from pathlib import Path
import asyncio

async def debug_context():
    base_path = Path('project')
    config_path = base_path / 'Requirements_Generation_System' / 'config.yaml'
    orchestrator = RequirementsOrchestrator('LSOMigrator', base_path, config_path, 'openai')
    
    # Get context for UI/UX generation
    context = await orchestrator.gather_context(DocumentType.UIUX_SPEC)
    
    print("=== CONTEXT KEYS ===")
    for key in context.keys():
        print(f"- {key}")
    
    print("\n=== FRD CONTENT (first 2000 chars) ===")
    if 'frd' in context:
        frd_content = context['frd']
        print(f"Length: {len(frd_content)} characters")
        print(frd_content[:2000])
        print("...")
        
        # Check if CRM requirements are in the context
        crm_count = frd_content.count('REQ-FUNC-020') + frd_content.count('REQ-FUNC-021') + frd_content.count('REQ-FUNC-022')
        print(f"\nCRM requirements found in context: {crm_count}")
        
        # Check specific CRM requirements
        if 'REQ-FUNC-020' in frd_content:
            print("✅ REQ-FUNC-020 found in context")
        else:
            print("❌ REQ-FUNC-020 NOT found in context")
            
        if 'REQ-FUNC-021' in frd_content:
            print("✅ REQ-FUNC-021 found in context")
        else:
            print("❌ REQ-FUNC-021 NOT found in context")
            
        if 'REQ-FUNC-022' in frd_content:
            print("✅ REQ-FUNC-022 found in context")
        else:
            print("❌ REQ-FUNC-022 NOT found in context")
    else:
        print("❌ FRD not found in context!")
    
    print("\n=== ACTUAL FRD FILE (first 2000 chars) ===")
    frd_file_path = base_path / 'Requirements_Generation_System' / 'fy-wb-midway-docs' / 'docs' / 'requirements' / 'frd.md'
    if frd_file_path.exists():
        frd_file_content = frd_file_path.read_text(encoding='utf-8')
        print(f"Length: {len(frd_file_content)} characters")
        print(frd_file_content[:2000])
        print("...")
        
        # Check if CRM requirements are in the file
        crm_count_file = frd_file_content.count('REQ-FUNC-020') + frd_file_content.count('REQ-FUNC-021') + frd_file_content.count('REQ-FUNC-022')
        print(f"\nCRM requirements found in file: {crm_count_file}")
        
        # Compare context vs file
        if 'frd' in context:
            if context['frd'] == frd_file_content:
                print("✅ Context FRD matches file FRD")
            else:
                print("❌ Context FRD DIFFERS from file FRD")
                print(f"Context length: {len(context['frd'])}")
                print(f"File length: {len(frd_file_content)}")
    else:
        print("❌ FRD file not found!")

if __name__ == "__main__":
    asyncio.run(debug_context())
