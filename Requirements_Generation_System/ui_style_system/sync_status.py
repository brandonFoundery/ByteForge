#!/usr/bin/env python3
"""
Sync the LLM generation results to the status file for live page updates
"""

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

def main():
    """Sync results from llm_generation_results.json to generation_status.json"""
    
    console.print("🔄 Syncing LLM generation results to status file...")
    
    # Get file paths
    ui_system_path = Path(__file__).parent
    results_file = ui_system_path / "llm_generation_results.json"
    status_file = ui_system_path / "generation_status.json"
    
    # Check if results file exists
    if not results_file.exists():
        console.print(f"[red]❌ Results file not found: {results_file}[/red]")
        return False
    
    # Read the results
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    # Create status data in the format expected by the live page
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "total_combinations": results_data.get("total_combinations", 45),
        "completed": results_data.get("successful", 0),
        "results": results_data.get("results", [])
    }
    
    # Write to status file
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2)
    
    console.print(f"✅ Status file updated!")
    console.print(f"   📊 Total combinations: {status_data['total_combinations']}")
    console.print(f"   ✅ Successful: {status_data['completed']}")
    console.print(f"   ❌ Failed: {status_data['total_combinations'] - status_data['completed']}")
    console.print(f"   📄 Results: {len(status_data['results'])}")
    
    # Show breakdown by model
    model_counts = {}
    for result in status_data['results']:
        model_id = result.get('model_id', 'unknown')
        if model_id not in model_counts:
            model_counts[model_id] = {'success': 0, 'failed': 0}
        
        if result.get('success'):
            model_counts[model_id]['success'] += 1
        else:
            model_counts[model_id]['failed'] += 1
    
    console.print(f"\n📈 Breakdown by model:")
    for model_id, counts in model_counts.items():
        total = counts['success'] + counts['failed']
        console.print(f"   {model_id}: {counts['success']}/{total} successful")
    
    console.print(f"\n🌐 The live page should now show all completed designs!")
    return True

if __name__ == "__main__":
    main()
