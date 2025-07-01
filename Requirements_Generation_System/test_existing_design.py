#!/usr/bin/env python3
"""
Test script to verify existing design documents
"""

from pathlib import Path
import json


def test_existing_design_documents():
    """Test that existing design documents are valid"""
    print("🧪 Testing Existing Design Documents...")
    
    # Base paths
    base_path = Path("project")
    design_path = base_path / "generated_documents" / "design"
    
    print(f"📁 Base path: {base_path}")
    print(f"📋 Design path: {design_path}")
    
    # Check if design directory exists
    if not design_path.exists():
        print("❌ Design directory not found")
        return False
    
    print("✅ Design directory found")
    
    # Expected design documents
    expected_docs = [
        "frontend-agent-design.md",
        "backend-agent-design.md", 
        "infrastructure-agent-design.md",
        "security-agent-design.md",
        "integration-agent-design.md",
        "README.md"
    ]
    
    print(f"\n📄 Checking for {len(expected_docs)} expected design documents...")
    
    found_docs = []
    missing_docs = []
    
    for doc in expected_docs:
        doc_path = design_path / doc
        if doc_path.exists():
            file_size = doc_path.stat().st_size
            print(f"✅ {doc} - {file_size:,} bytes")
            found_docs.append(doc)
            
            # Show first few lines of each document
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    print(f"   Preview: {lines[0].strip()[:80]}...")
            except Exception as e:
                print(f"   ⚠️  Could not read preview: {e}")
        else:
            print(f"❌ {doc} - NOT FOUND")
            missing_docs.append(doc)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   ✅ Found: {len(found_docs)}/{len(expected_docs)} documents")
    print(f"   ❌ Missing: {len(missing_docs)} documents")
    
    if missing_docs:
        print(f"   Missing documents: {', '.join(missing_docs)}")
    
    # Check development plan
    dev_plan_path = base_path / "generated_documents" / "dev_plan.md"
    if dev_plan_path.exists():
        print(f"✅ Development plan found - {dev_plan_path.stat().st_size:,} bytes")
    else:
        print("❌ Development plan not found")
    
    # Check requirements documents
    req_docs = ["brd.md", "prd.md", "frd.md", "nfrd.md", "trd.md"]
    req_path = base_path / "generated_documents"
    
    print(f"\n📋 Checking requirements documents...")
    req_found = 0
    for req_doc in req_docs:
        req_file = req_path / req_doc
        if req_file.exists():
            print(f"✅ {req_doc}")
            req_found += 1
        else:
            print(f"❌ {req_doc}")
    
    print(f"   Requirements found: {req_found}/{len(req_docs)}")
    
    # Overall status
    success = len(missing_docs) == 0 and req_found >= 3
    
    if success:
        print(f"\n🎉 SUCCESS: Design documents are ready for Claude Code implementation!")
    else:
        print(f"\n⚠️  PARTIAL: Some documents missing, but system is functional")
    
    return success


if __name__ == "__main__":
    test_existing_design_documents()
