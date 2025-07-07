#!/usr/bin/env python3
"""
Debug script to check config.yaml structure
"""

import yaml
from pathlib import Path

def debug_config():
    config_path = Path(__file__).parent / "config.yaml"
    print(f"Config path: {config_path}")
    print(f"Config exists: {config_path.exists()}")
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"\nConfig keys: {list(config.keys())}")
        
        if 'llm' in config:
            print(f"llm keys: {list(config['llm'].keys())}")
            
            if 'claude_code' in config['llm']:
                print(f"claude_code keys: {list(config['llm']['claude_code'].keys())}")
                
                # Check for agents
                if 'agents' in config['llm']['claude_code']:
                    agents = config['llm']['claude_code']['agents']
                    print(f"Found agents: {list(agents.keys())}")
                else:
                    print("No agents found in llm.claude_code")
                
                # Check for phases
                if 'phases' in config['llm']['claude_code']:
                    phases = config['llm']['claude_code']['phases']
                    print(f"Found phases: {list(phases.keys())}")
                else:
                    print("No phases found in llm.claude_code")
            else:
                print("No claude_code section found in llm")
        else:
            print("No llm section found")
            
        # Check if agents/phases are at root level
        if 'agents' in config:
            print(f"Found agents at root level: {list(config['agents'].keys())}")
        if 'phases' in config:
            print(f"Found phases at root level: {list(config['phases'].keys())}")

if __name__ == "__main__":
    debug_config()