#!/usr/bin/env python3
"""
Test script for the Design Document Generator
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from design_document_generator import DesignDocumentGenerator


async def test_design_generator():
    """Test the design document generator"""
    print("🧪 Testing Design Document Generator...")
    
    # Initialize the generator
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    generator = DesignDocumentGenerator(base_path)
    
    print(f"📁 Base path: {base_path}")
    print(f"📋 Design path: {generator.design_path}")
    
    # Check if dev_plan.md exists
    dev_plan_path = base_path / "generated_documents" / "dev_plan.md"
    if dev_plan_path.exists():
        print("✅ Development plan found")
    else:
        print("❌ Development plan not found")
        return
    
    # Test generating a single agent design document
    print("\n🤖 Testing Frontend Agent design generation...")
    
    try:
        result = await generator.generate_single_agent_design("frontend")
        
        if result.success:
            print(f"✅ Frontend Agent design generated successfully!")
            print(f"📄 Document path: {result.document_path}")
            print(f"⏱️  Generation time: {result.generation_time:.2f} seconds")
            
            # Check if file was created
            if result.document_path and Path(result.document_path).exists():
                file_size = Path(result.document_path).stat().st_size
                print(f"📊 File size: {file_size} bytes")
                
                # Show first few lines
                with open(result.document_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    print("\n📖 First 10 lines of generated document:")
                    for i, line in enumerate(lines, 1):
                        print(f"   {i:2d}: {line.rstrip()}")
            else:
                print("❌ Document file not found after generation")
        else:
            print(f"❌ Frontend Agent design generation failed: {result.error_message}")
    
    except Exception as e:
        print(f"❌ Exception during generation: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_design_generator())
