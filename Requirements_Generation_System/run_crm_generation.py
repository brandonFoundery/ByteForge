#!/usr/bin/env python3
"""
Direct CRM Generation Script
Runs the enhanced AI generation system specifically for CRM implementation.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator

async def generate_crm_design_documents():
    """Generate CRM design documents using enhanced artifact system."""
    
    print("Starting CRM Design Document Generation...")
    print("Using enhanced artifact-driven requirements pipeline")
    
    # Set up paths
    base_path = Path(__file__).parent.parent
    config_path = base_path / "Requirements_Generation_System" / "config.yaml"
    
    # Initialize orchestrator with artifact support
    orchestrator = RequirementsOrchestrator(
        project_name="FY.WB.Midway",
        base_path=base_path,
        config_path=config_path,
        model_provider="openai"
    )
    
    print("Orchestrator initialized with artifact processor")

    # Load artifacts and show what was found
    artifacts_context = orchestrator.artifact_processor.load_all_artifacts()

    print(f"Artifacts loaded:")
    print(f"   - Detailed specs: {artifacts_context['artifacts_summary']['detailed_specs_count']}")
    print(f"   - JSON blueprints: {artifacts_context['artifacts_summary']['json_blueprints_count']}")
    print(f"   - Priority requirements: {len(artifacts_context['priority_requirements'])}")

    if artifacts_context['priority_requirements']:
        print(f"Priority requirements found:")
        for req in artifacts_context['priority_requirements'][:5]:
            print(f"   - {req}")

    # Generate design documents
    print("\nGenerating AI agent design documents...")
    
    try:
        # This will use the enhanced prompt with your CRM artifacts
        await orchestrator.generate_design_documents()
        print("CRM design documents generated successfully!")

        # Show what was generated
        design_dir = base_path / "generated_documents" / "design"
        if design_dir.exists():
            generated_files = list(design_dir.glob("*.md"))
            print(f"\nGenerated {len(generated_files)} design documents:")
            for file in generated_files:
                print(f"   - {file.name}")

    except Exception as e:
        print(f"Error generating design documents: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("CRM Design Document Generation")
    print("Enhanced with Pipedrive-inspired requirements")
    print("=" * 60)
    
    # Check if artifacts exist
    base_path = Path(__file__).parent.parent
    artifacts_path = base_path / "Requirements_Artifacts"
    
    if not artifacts_path.exists():
        print("Requirements_Artifacts directory not found!")
        print("Please ensure your CRM requirements are in Requirements_Artifacts/")
        return 1

    crm_spec = artifacts_path / "detailed_specs" / "CRM_Functional_Requirements.md"
    if not crm_spec.exists():
        print("CRM_Functional_Requirements.md not found!")
        print("Please ensure your Pipedrive requirements are properly loaded.")
        return 1

    print("CRM requirements artifacts found")
    
    # Run the generation
    try:
        result = asyncio.run(generate_crm_design_documents())
        if result:
            print("\nCRM design generation completed successfully!")
            print("\nNext steps:")
            print("1. Review generated design documents in generated_documents/design/")
            print("2. Run Claude Code implementation to build the CRM")
            print("3. Test the broker dashboard functionality")
            return 0
        else:
            print("\nCRM design generation failed")
            return 1

    except KeyboardInterrupt:
        print("\nGeneration interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())