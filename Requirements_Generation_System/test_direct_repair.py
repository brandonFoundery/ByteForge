#!/usr/bin/env python3
"""
Direct test of the repair functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

async def test_direct_repair():
    """Test direct repair of the BRD document"""
    
    print("="*60)
    print("DIRECT REPAIR TEST")
    print("="*60)
    
    # Initialize orchestrator
    import os
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    project_name = "FY.WB.Midway"
    base_path = Path("d:/Repository/@Clients/FY.WB.Midway")
    orchestrator = RequirementsOrchestrator(project_name, base_path, model_provider="openai")
    
    # Load the BRD document directly
    brd_path = base_path / "generated_documents" / "brd.md"
    if not brd_path.exists():
        print("❌ BRD file not found!")
        return
    
    original_content = brd_path.read_text(encoding='utf-8')
    print(f"Original content length: {len(original_content)}")
    print(f"First 10 lines:")
    for i, line in enumerate(original_content.split('\n')[:10], 1):
        print(f"  {i:2d}: {line}")
    
    # Apply the unmatched code blocks repair
    print(f"\nApplying unmatched code blocks repair...")
    repaired_content = orchestrator._repair_unmatched_code_blocks(original_content)
    
    print(f"\nRepaired content length: {len(repaired_content)}")
    print(f"Content changed: {repaired_content != original_content}")
    print(f"First 10 lines of repaired content:")
    for i, line in enumerate(repaired_content.split('\n')[:10], 1):
        print(f"  {i:2d}: {line}")
    
    # Test validation on repaired content
    print(f"\nTesting validation on repaired content...")
    
    # Temporarily set the content for validation
    brd_doc = orchestrator.documents[DocumentType.BRD]
    brd_doc.content = repaired_content
    
    validation_result = await orchestrator._perform_validation_checks(DocumentType.BRD)
    print(f"Validation result:")
    print(f"  Is Valid: {validation_result.is_valid}")
    print(f"  Errors: {len(validation_result.errors)}")
    for error in validation_result.errors:
        print(f"    - {error}")
    
    # Save the repaired content
    if validation_result.is_valid:
        print(f"\n✅ REPAIR SUCCESSFUL! Saving repaired document...")
        repaired_path = base_path / "generated_documents" / "brd_repaired.md"
        repaired_path.write_text(repaired_content, encoding='utf-8')
        print(f"Saved to: {repaired_path}")
    else:
        print(f"\n⚠️  Repair partially successful but validation still has issues")
        # Save anyway for inspection
        repaired_path = base_path / "generated_documents" / "brd_partial_repair.md"
        repaired_path.write_text(repaired_content, encoding='utf-8')
        print(f"Saved partial repair to: {repaired_path}")

if __name__ == "__main__":
    asyncio.run(test_direct_repair())
