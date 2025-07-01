#!/usr/bin/env python3
"""
Test script for the enhanced auto-repair system
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

async def test_brd_repair():
    """Test the enhanced auto-repair on the BRD document"""
    
    print("="*60)
    print("TESTING ENHANCED AUTO-REPAIR SYSTEM")
    print("="*60)
    
    # Initialize orchestrator (set dummy API key to avoid initialization error)
    import os
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"

    project_name = "FY.WB.Midway"
    base_path = Path("project")
    orchestrator = RequirementsOrchestrator(project_name, base_path, model_provider="openai")
    
    # Load existing document states
    await orchestrator.load_existing_documents()
    
    # Get the BRD document
    brd_doc = orchestrator.documents[DocumentType.BRD]
    
    print(f"\n1. CURRENT BRD STATUS:")
    print(f"   Status: {brd_doc.status.value}")
    print(f"   Content Length: {len(brd_doc.content) if brd_doc.content else 0} characters")
    
    if not brd_doc.content:
        print("   ❌ No content found - loading from file...")
        brd_path = base_path / "generated_documents" / "brd.md"
        if brd_path.exists():
            brd_doc.content = brd_path.read_text(encoding='utf-8')
            print(f"   ✅ Loaded content: {len(brd_doc.content)} characters")
        else:
            print("   ❌ BRD file not found!")
            return
    
    print(f"\n2. TESTING VALIDATION AND REPAIR:")
    print("-" * 40)

    # First, let's manually test the validation to see what errors are detected
    validation_result = await orchestrator._perform_validation_checks(DocumentType.BRD)
    print(f"   Manual Validation Result:")
    print(f"     Is Valid: {validation_result.is_valid}")
    print(f"     Errors Found: {len(validation_result.errors)}")
    for i, error in enumerate(validation_result.errors, 1):
        print(f"       {i}. {error}")

    # Test individual repair methods
    print(f"\n   Testing Individual Repairs:")
    original_content = brd_doc.content

    # Test YAML code block start repair
    if "Document starts with YAML code block instead of frontmatter" in validation_result.errors:
        print(f"     Testing YAML code block start repair...")
        repaired_content = orchestrator._repair_yaml_code_block_start(original_content, DocumentType.BRD)
        print(f"     Original length: {len(original_content)}")
        print(f"     Repaired length: {len(repaired_content)}")
        print(f"     Content changed: {repaired_content != original_content}")
        if repaired_content != original_content:
            print(f"     First 5 lines of repaired content:")
            for i, line in enumerate(repaired_content.split('\n')[:5], 1):
                print(f"       {i}: {line}")

    # Test the enhanced validation and repair
    try:
        validation_success = await orchestrator.validate_and_repair_document(
            DocumentType.BRD,
            max_repair_attempts=5  # Give it more attempts
        )
        
        print(f"\n3. REPAIR RESULTS:")
        print(f"   Validation Success: {'✅ YES' if validation_success else '❌ NO'}")
        print(f"   Final Status: {brd_doc.status.value}")
        
        if brd_doc.validation_errors:
            print(f"   Remaining Errors:")
            for error in brd_doc.validation_errors:
                print(f"     - {error}")
        else:
            print(f"   ✅ No validation errors remaining!")
        
        # Show the first few lines of the repaired content
        print(f"\n4. REPAIRED CONTENT PREVIEW:")
        print("-" * 40)
        lines = brd_doc.content.split('\n')[:20]
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        
        if len(brd_doc.content.split('\n')) > 20:
            print("    ... (content continues)")
        
        # Save the repaired document
        if validation_success:
            await orchestrator.save_document(DocumentType.BRD)
            print(f"\n✅ REPAIRED DOCUMENT SAVED SUCCESSFULLY!")
        else:
            print(f"\n⚠️  Document has remaining issues but was saved for manual review")
            
    except Exception as e:
        print(f"\n❌ ERROR DURING REPAIR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_brd_repair())
