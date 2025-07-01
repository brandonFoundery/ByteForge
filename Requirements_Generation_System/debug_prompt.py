#!/usr/bin/env python3

from orchestrator import RequirementsOrchestrator, DocumentType
from pathlib import Path
import asyncio

async def debug_prompt():
    base_path = Path('project')
    config_path = base_path / 'Requirements_Generation_System' / 'config.yaml'
    orchestrator = RequirementsOrchestrator('LSOMigrator', base_path, config_path, 'openai')
    
    print('=== DEBUGGING UI/UX PROMPT ===')
    
    # Get the context that would be sent to the LLM
    context = await orchestrator.gather_context(DocumentType.UIUX_SPEC)
    
    print(f"Context keys: {list(context.keys())}")
    
    if 'frd' in context:
        frd_content = context['frd']
        print(f"\nFRD content length: {len(frd_content)} characters")
        
        # Check for CRM requirements in context
        crm_020_count = frd_content.count('REQ-FUNC-020')
        crm_021_count = frd_content.count('REQ-FUNC-021') 
        crm_022_count = frd_content.count('REQ-FUNC-022')
        
        print(f"REQ-FUNC-020 occurrences: {crm_020_count}")
        print(f"REQ-FUNC-021 occurrences: {crm_021_count}")
        print(f"REQ-FUNC-022 occurrences: {crm_022_count}")
        
        # Show some sample CRM content
        if 'REQ-FUNC-020' in frd_content:
            start_idx = frd_content.find('REQ-FUNC-020')
            sample = frd_content[start_idx:start_idx+500]
            print(f"\nSample CRM content:\n{sample}...")
    
    # Get the UI/UX prompt template
    doc = orchestrator.documents[DocumentType.UIUX_SPEC]
    if doc.prompt_template:
        print(f"\nPrompt template length: {len(doc.prompt_template)} characters")
        
        # Check if prompt template mentions requirements extraction
        if 'requirement' in doc.prompt_template.lower():
            print("✅ Prompt template mentions requirements")
        else:
            print("❌ Prompt template does NOT mention requirements")
            
        # Show first part of prompt template
        print(f"\nPrompt template start:\n{doc.prompt_template[:1000]}...")
    
    # Build the full prompt that would be sent to LLM
    prompt_parts = doc.prompt_template.split("```markdown")
    if len(prompt_parts) > 1:
        main_prompt = prompt_parts[1].split("```")[0]
    else:
        main_prompt = doc.prompt_template
    
    full_prompt = f"""Project: {context['project_name']}
Generation Date: {context['generation_date']}

{main_prompt}

"""
    
    # Add context documents
    for key, value in context.items():
        if key not in ['project_name', 'generation_date'] and value:
            # Use larger context limit for UI/UX generation to include all requirements
            context_limit = 50000  # Same as orchestrator for UIUX_SPEC
            content_preview = value[:context_limit]
            if len(value) > context_limit:
                content_preview += "...\n(content truncated for brevity)"

            full_prompt += f"\n### {key.upper().replace('_', ' ')} DOCUMENT:\n"
            full_prompt += f"{content_preview}\n"
    
    print(f"\nFull prompt length: {len(full_prompt)} characters")
    
    # Check if CRM requirements are in the truncated context
    crm_in_prompt = full_prompt.count('REQ-FUNC-020') + full_prompt.count('REQ-FUNC-021') + full_prompt.count('REQ-FUNC-022')
    print(f"CRM requirements in final prompt: {crm_in_prompt}")
    
    if crm_in_prompt == 0:
        print("❌ ISSUE: CRM requirements are being truncated out of the prompt!")
        
        # Find where FRD content starts and ends in prompt
        frd_start = full_prompt.find("### FRD DOCUMENT:")
        if frd_start >= 0:
            frd_section = full_prompt[frd_start:frd_start+16000]  # Show more of FRD section
            print(f"\nFRD section in prompt (first 1000 chars):\n{frd_section[:1000]}...")
            
            # Check if CRM requirements are in the FRD section
            if 'REQ-FUNC-020' in frd_section:
                print("✅ CRM requirements ARE in FRD section")
            else:
                print("❌ CRM requirements are NOT in FRD section")
    else:
        print("✅ CRM requirements are included in the final prompt")

if __name__ == "__main__":
    asyncio.run(debug_prompt())
