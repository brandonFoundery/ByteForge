#!/usr/bin/env python3
"""
Simple test to isolate the 'display' error
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

async def test_simple_openai():
    """Test a simple OpenAI call to isolate the display error"""
    
    print("Testing simple OpenAI call...")
    
    try:
        import openai
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("OpenAI API key not found")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Simple text-only call first
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "Say hello"
                }
            ],
            max_tokens=50
        )
        
        print(f"✅ OpenAI response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_simple_openai())
    print(f"Test result: {result}")
