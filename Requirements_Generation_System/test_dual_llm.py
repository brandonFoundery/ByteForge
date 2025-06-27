#!/usr/bin/env python3
"""
Test script for the dual-LLM review system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

async def test_dual_llm_system():
    """Test the dual-LLM system with a simple document"""
    
    print("🧪 Testing Dual-LLM Review System")
    print("=" * 50)
    
    # Configuration
    project_name = "Test Project"
    base_path = Path(__file__).parent.parent
    config_path = Path(__file__).parent / "config.yaml"
    
    # Create orchestrator
    try:
        orchestrator = RequirementsOrchestrator(
            project_name=project_name,
            base_path=base_path,
            config_path=config_path,
            model_provider="openai"
        )
        
        print(f"✅ Orchestrator initialized successfully")
        print(f"   Primary LLM: {orchestrator.model_provider}")
        print(f"   Review system enabled: {orchestrator.review_config.get('enabled', False)}")
        
        if orchestrator.review_config.get('enabled', False):
            reviewer_config = orchestrator.review_config.get('reviewer_llm', {})
            print(f"   Reviewer LLM: {reviewer_config.get('provider', 'unknown')}")
            print(f"   Reviewer model: {reviewer_config.get('model', 'unknown')}")
            
            if orchestrator.reviewer_llm_client:
                print("   ✅ Reviewer LLM client initialized")
            else:
                print("   ❌ Reviewer LLM client not available")
        else:
            print("   ⚠️  Review system disabled")
            
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return False
    
    # Test document creation and review
    try:
        # Create a simple test document
        test_doc = orchestrator.documents.get(DocumentType.BRD)
        if test_doc:
            # Simulate a generated document
            test_doc.content = """---
id: BRD-TEST
title: Test Business Requirements Document
version: 1.0
dependencies: []
status: generated
generated_at: 2025-01-27T10:00:00
---

# Test Business Requirements Document

## 1. Overview (BRD-001)

This is a test business requirements document for validating the dual-LLM review system.

### 1.1 Purpose (BRD-001.1)

The purpose of this document is to test the review functionality.

### 1.2 Scope (BRD-001.2)

This document covers basic requirements for testing.

## 2. Business Requirements (BRD-002)

### 2.1 Functional Requirements (BRD-002.1)

- The system shall support user authentication
- The system shall provide data storage capabilities
- The system shall generate reports

### 2.2 Business Rules (BRD-002.2)

- Users must be authenticated before accessing the system
- Data must be validated before storage
- Reports must be generated in real-time
"""
            test_doc.status = orchestrator.documents[DocumentType.BRD].status.GENERATED
            test_doc.generated_at = orchestrator.documents[DocumentType.BRD].generated_at
            
            print("\n📄 Test document created")
            print(f"   Content length: {len(test_doc.content)} characters")
            
            # Test the review process
            print("\n🔍 Testing review process...")
            review_success = await orchestrator.review_document(DocumentType.BRD)
            
            if review_success:
                print("✅ Review completed successfully")
                print(f"   Review count: {test_doc.review_count}")
                print(f"   Reviewer LLM used: {test_doc.reviewer_llm_used}")
                
                if test_doc.reviewed_content:
                    print(f"   Reviewed content length: {len(test_doc.reviewed_content)} characters")
                    
                    # Show a snippet of the changes (if any)
                    if test_doc.reviewed_content != test_doc.content:
                        print("   📝 Content was modified during review")
                    else:
                        print("   📝 Content unchanged during review")
                else:
                    print("   ⚠️  No reviewed content available")
            else:
                print("❌ Review failed")
                if test_doc.review_errors:
                    print(f"   Errors: {test_doc.review_errors}")
                    
        else:
            print("❌ No BRD document found for testing")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Dual-LLM system test completed!")
    return True

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        sys.exit(1)
    
    # Run the test
    success = asyncio.run(test_dual_llm_system())
    sys.exit(0 if success else 1)
