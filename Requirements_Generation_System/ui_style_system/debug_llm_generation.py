#!/usr/bin/env python3
"""
Debug LLM Generation
Test a single LLM call to see what's actually being generated
"""

import asyncio
import base64
import os
from pathlib import Path
from rich.console import Console

console = Console()

async def test_single_llm_call():
    """Test a single LLM call to debug the generation issue"""
    
    # Get paths
    project_root = Path(__file__).parent.parent.parent
    examples_path = project_root / "Requirements_Generation_System" / "ui_style_examples"
    
    # Load and encode a reference image
    image_path = examples_path / "ui_style_1.png"
    if not image_path.exists():
        console.print(f"[red]Image not found: {image_path}[/red]")
        return
    
    with open(image_path, 'rb') as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create the prompt
    prompt = """
# UI Design Generation Task

You are an expert UI/UX designer tasked with creating a unique dashboard design for the FY.WB.Midway freight brokerage application.

## Reference Style Image: ui_style_1.png
I'm providing you with a reference style image that shows the aesthetic direction I want you to follow. Study this image carefully and create a design that captures its visual essence, color palette, typography choices, and overall design philosophy.

## Target Application: FY.WB.Midway Dashboard
This is a freight brokerage dashboard that needs to display:

### Key Data Points:
- Total Loads: 1,247 (↑12% from last month)
- Active Loads: 89 (↑8% from last month)
- Monthly Revenue: $285,750 (↑15% from last month)
- Load status indicators and recent activity

### Required Components:
1. **Header** with company name and user profile
2. **Welcome Section** with personalized greeting
3. **Stats Cards** showing the key metrics above with trend indicators
4. **Quick Actions Panel** with buttons for:
   - + New Load Entry
   - 📊 View Reports
   - 👥 Manage Carriers
5. **Recent Activity Feed** showing:
   - Load #12847 delivered successfully (2 hours ago)
   - New carrier application received (4 hours ago)
   - Invoice #INV-2024-0156 pending (6 hours ago)

## Design Requirements:

### Style Direction: Inspired by ui_style_1.png
- Interpret and expand on the visual style shown in the reference image
- Create your own unique take on this aesthetic
- Don't copy exactly - innovate within the style direction

### Technical Requirements:
- Use modern HTML5 and CSS3
- Implement with Tailwind CSS classes
- Ensure responsive design (mobile-first)
- Include hover states and micro-interactions
- Use semantic HTML structure
- Ensure accessibility (proper contrast, ARIA labels)

### Creative Freedom:
- Choose your own color palette inspired by the reference
- Select appropriate typography (Google Fonts recommended)
- Design unique card layouts and spacing
- Create distinctive visual hierarchy
- Add your own creative elements (icons, illustrations, patterns)

## Output Format:
Provide a complete HTML file with embedded CSS that I can save and view directly in a browser. Include:

1. **Complete HTML structure** with all required components
2. **Embedded CSS** (either in <style> tags or inline Tailwind classes)
3. **Responsive design** that works on desktop and mobile
4. **Interactive elements** with hover effects
5. **Professional typography** and spacing
6. **Unique visual identity** inspired by but not copying the reference

## Important Notes:
- Make it genuinely unique - your interpretation of the style, not a copy
- Focus on user experience and visual hierarchy
- Ensure all data is clearly readable and actionable
- Create a design that feels modern and professional
- The reference image is inspiration, not a template to copy exactly

Generate a complete, production-ready HTML file that showcases your unique interpretation of this UI style for the FY.WB.Midway freight brokerage dashboard.
"""
    
    # Test OpenAI API call
    console.print("[bold]Testing OpenAI API call...[/bold]")
    
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            console.print("[red]OpenAI API key not found[/red]")
            return
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000,
            temperature=0.8
        )
        
        raw_response = response.choices[0].message.content
        
        console.print(f"[green]✅ Got response from OpenAI[/green]")
        console.print(f"[yellow]Response length: {len(raw_response)} characters[/yellow]")
        
        # Save raw response for inspection
        debug_file = Path(__file__).parent / "debug_raw_response.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write("=== RAW LLM RESPONSE ===\n")
            f.write(raw_response)
            f.write("\n\n=== END RAW RESPONSE ===\n")
        
        console.print(f"[green]📄 Raw response saved to: {debug_file.name}[/green]")
        
        # Show first 500 characters
        console.print(f"\n[bold]First 500 characters of response:[/bold]")
        console.print(raw_response[:500] + "..." if len(raw_response) > 500 else raw_response)
        
        # Extract HTML and save
        html_content = extract_html_from_response(raw_response)
        
        debug_html_file = Path(__file__).parent / "debug_extracted.html"
        with open(debug_html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]📄 Extracted HTML saved to: {debug_html_file.name}[/green]")
        console.print(f"[yellow]Extracted HTML length: {len(html_content)} characters[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def extract_html_from_response(response: str) -> str:
    """Extract HTML content from LLM response (remove markdown formatting)"""
    
    # Remove markdown code blocks
    if '```html' in response:
        start = response.find('```html') + 7
        end = response.find('```', start)
        if end != -1:
            response = response[start:end].strip()
    elif '```' in response:
        start = response.find('```') + 3
        end = response.find('```', start)
        if end != -1:
            response = response[start:end].strip()
    
    # Ensure it starts with <!DOCTYPE html> or <html>
    if not response.strip().startswith(('<!DOCTYPE', '<html')):
        response = f"<!DOCTYPE html>\n{response}"
    
    return response

if __name__ == "__main__":
    asyncio.run(test_single_llm_call())
