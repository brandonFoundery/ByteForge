#!/usr/bin/env python3
"""
Test final validation of the repaired BRD document
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

async def test_final_validation():
    """Test validation of the repaired BRD document"""
    
    print("="*60)
    print("FINAL VALIDATION TEST")
    print("="*60)
    
    # Initialize orchestrator
    import os
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    project_name = "FY.WB.Midway"
    base_path = Path("project")
    orchestrator = RequirementsOrchestrator(project_name, base_path, model_provider="openai")
    
    # Load the repaired BRD document
    brd_path = base_path / "generated_documents" / "brd.md"
    if not brd_path.exists():
        print("❌ BRD file not found!")
        return
    
    content = brd_path.read_text(encoding='utf-8')
    print(f"Document length: {len(content)} characters")
    
    # Set the content for validation
    brd_doc = orchestrator.documents[DocumentType.BRD]
    brd_doc.content = content
    
    # Test validation
    print(f"\nTesting validation...")
    validation_result = await orchestrator._perform_validation_checks(DocumentType.BRD)
    
    print(f"\nValidation Results:")
    print(f"  ✅ Is Valid: {validation_result.is_valid}")
    print(f"  📊 Errors Found: {len(validation_result.errors)}")
    
    if validation_result.errors:
        print(f"  ❌ Remaining Issues:")
        for i, error in enumerate(validation_result.errors, 1):
            print(f"    {i}. {error}")
    else:
        print(f"  🎉 NO VALIDATION ERRORS - DOCUMENT IS PERFECT!")
    
    # Test the full validation and repair process
    print(f"\nTesting full validation and repair process...")
    try:
        validation_success = await orchestrator.validate_and_repair_document(DocumentType.BRD)
        
        if validation_success:
            print(f"  ✅ FULL VALIDATION SUCCESSFUL!")
            print(f"  📄 Document Status: {brd_doc.status.value}")
        else:
            print(f"  ⚠️  Full validation had issues")
            print(f"  📄 Document Status: {brd_doc.status.value}")
            if brd_doc.validation_errors:
                for error in brd_doc.validation_errors:
                    print(f"    - {error}")
    
    except Exception as e:
        print(f"  ❌ Error during validation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_final_validation())
