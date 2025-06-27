#!/usr/bin/env python3

from orchestrator import RequirementsOrchestrator, DocumentType, DocumentStatus
from pathlib import Path
import asyncio

async def debug_status():
    base_path = Path('d:/Repository/@Clients/FY.WB.Midway')
    config_path = base_path / 'Requirements_Generation_System' / 'config.yaml'
    orchestrator = RequirementsOrchestrator('FY.WB.Midway', base_path, config_path, 'openai')
    
    print("=== DOCUMENT STATUSES ===")
    for doc_type, doc in orchestrator.documents.items():
        print(f"{doc_type.name}: Status={doc.status}, Content Length={len(doc.content) if doc.content else 0}")
    
    print("\n=== UIUX_SPEC DEPENDENCIES ===")
    uiux_doc = orchestrator.documents[DocumentType.UIUX_SPEC]
    print(f"Dependencies: {[dep.name for dep in uiux_doc.dependencies]}")
    
    for dep_type in uiux_doc.dependencies:
        dep_doc = orchestrator.documents[dep_type]
        print(f"  {dep_type.name}: Status={dep_doc.status}, Content Length={len(dep_doc.content) if dep_doc.content else 0}")
        
        # Check if this dependency would be included in context
        if dep_doc.status in [DocumentStatus.GENERATED, DocumentStatus.REFINED, DocumentStatus.VALIDATED]:
            print(f"    ✅ Would be included in context")
        else:
            print(f"    ❌ Would NOT be included in context (status: {dep_doc.status})")

if __name__ == "__main__":
    asyncio.run(debug_status())
