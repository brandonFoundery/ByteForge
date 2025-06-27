#!/usr/bin/env python3
"""
LLM-Powered UI Style Generator
Sends prompts to different LLM models to generate unique UI designs
Each model gets a different style example image to mimic
"""

import os
import sys
import json
import asyncio
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

class LLMUIGenerator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_system_path = project_root / "Requirements_Generation_System" / "ui_style_system"
        self.examples_path = project_root / "Requirements_Generation_System" / "ui_style_examples"
        self.generated_path = self.ui_system_path / "llm_generated"
        self.screenshots_path = self.ui_system_path / "screenshots"
        
        # Ensure directories exist
        self.generated_path.mkdir(exist_ok=True)
        self.screenshots_path.mkdir(exist_ok=True)
        
        # LLM Model configurations
        self.llm_models = [
            {
                "name": "OpenAI GPT-4o",
                "id": "gpt-4o",
                "provider": "openai"
            },
            {
                "name": "OpenAI GPT-4o-mini",
                "id": "gpt-4o-mini",
                "provider": "openai"
            },
            {
                "name": "OpenAI o1-mini",
                "id": "o1-mini",
                "provider": "openai"
            },
            {
                "name": "Google Gemini 2.5",
                "id": "gemini-2.0-flash-exp",
                "provider": "google"
            },
            {
                "name": "Anthropic Claude 4",
                "id": "claude-3-5-sonnet-20241022",
                "provider": "anthropic"
            }
        ]

        # Get all reference images from the examples directory
        self.reference_images = self.get_reference_images()

        # Status file for live updates
        self.status_file = self.ui_system_path / "generation_status.json"

    def get_reference_images(self) -> List[str]:
        """Get all reference images from the examples directory"""
        if not self.examples_path.exists():
            console.print(f"[red]Examples directory not found: {self.examples_path}[/red]")
            return []

        # Get all PNG files in the examples directory
        image_files = list(self.examples_path.glob("*.png"))
        image_names = [img.name for img in sorted(image_files)]

        console.print(f"[green]Found {len(image_names)} reference images: {', '.join(image_names)}[/green]")
        return image_names

    def encode_image_to_base64(self, image_path: Path) -> Optional[str]:
        """Encode image to base64 for LLM vision models"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            console.print(f"[red]Error encoding image {image_path}: {e}[/red]")
            return None

    def log_prompt_details(self, model_name: str, image_name: str, prompt: str) -> None:
        """Log detailed prompt information for debugging"""

        # Create logs directory if it doesn't exist
        logs_dir = self.ui_system_path / "logs"
        logs_dir.mkdir(exist_ok=True)

        # Create a safe filename
        safe_model_name = model_name.replace(" ", "_").replace(".", "_")
        safe_image_name = image_name.replace(".png", "")
        log_filename = f"prompt_{safe_model_name}_{safe_image_name}.txt"
        log_file = logs_dir / log_filename

        # Console logging
        console.print(f"📝 [bold cyan]Prompt Details for {model_name} + {image_name}[/bold cyan]")
        console.print(f"   📄 Prompt length: {len(prompt)} characters")
        console.print(f"   📁 Saving to: {log_file}")

        # Show first few lines of prompt
        prompt_lines = prompt.split('\n')
        console.print(f"   🔍 First 5 lines of prompt:")
        for i, line in enumerate(prompt_lines[:5]):
            if line.strip():
                console.print(f"      {i+1}. {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")

        # Show key sections
        if "multi-tenant SaaS" in prompt.lower():
            console.print(f"   ✅ Multi-tenant SaaS requirements included")
        if "design tokens" in prompt.lower():
            console.print(f"   ✅ Design tokens system included")
        if "role-based" in prompt.lower():
            console.print(f"   ✅ Role-based styling included")

        # Save full prompt to file
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== PROMPT LOG ===\n")
                f.write(f"Model: {model_name}\n")
                f.write(f"Reference Image: {image_name}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Prompt Length: {len(prompt)} characters\n")
                f.write(f"{'='*50}\n\n")
                f.write(prompt)
                f.write(f"\n\n{'='*50}\n")
                f.write("=== END PROMPT ===\n")

            console.print(f"   ✅ Prompt logged successfully")

        except Exception as e:
            console.print(f"   ⚠️  Failed to save prompt log: {e}")

    def log_generation_summary(self, results: List[Dict[str, Any]], duration: float) -> None:
        """Log a summary of the entire generation process"""

        logs_dir = self.ui_system_path / "logs"
        logs_dir.mkdir(exist_ok=True)

        summary_file = logs_dir / f"generation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"=== LLM UI GENERATION SUMMARY ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Duration: {duration:.1f} seconds\n")
                f.write(f"Total Combinations: {len(results)}\n")
                f.write(f"Successful: {len([r for r in results if r.get('success')])}\n")
                f.write(f"Failed: {len([r for r in results if not r.get('success')])}\n")
                f.write(f"{'='*60}\n\n")

                # Group by model
                by_model = {}
                for result in results:
                    model = result.get('model', 'Unknown')
                    if model not in by_model:
                        by_model[model] = []
                    by_model[model].append(result)

                for model, model_results in by_model.items():
                    successful = [r for r in model_results if r.get('success')]
                    failed = [r for r in model_results if not r.get('success')]

                    f.write(f"MODEL: {model}\n")
                    f.write(f"  Success: {len(successful)}/{len(model_results)}\n")

                    if successful:
                        f.write(f"  Successful generations:\n")
                        for result in successful:
                            f.write(f"    ✅ {result.get('reference_image')} → {Path(result.get('output_file', '')).name}\n")

                    if failed:
                        f.write(f"  Failed generations:\n")
                        for result in failed:
                            error = result.get('error', 'Unknown error')
                            f.write(f"    ❌ {result.get('reference_image')} → {error}\n")

                    f.write(f"\n")

                f.write(f"{'='*60}\n")
                f.write(f"Individual prompt logs saved in: {logs_dir}/prompt_*.txt\n")
                f.write(f"=== END SUMMARY ===\n")

            console.print(f"📋 Generation summary saved to: {summary_file.name}")

        except Exception as e:
            console.print(f"⚠️  Failed to save generation summary: {e}")

    def create_ui_generation_prompt(self, image_name: str) -> str:
        """Create the prompt for UI generation"""

        base_prompt = f"""
You are a senior product designer and front-end engineer working on a **multi-tenant SaaS application**.

Your inputs are:
• A reference image ({image_name}) of an existing UI or wireframe (provided as image input).
• Target application: **FY.WB.Midway** - A freight brokerage dashboard for logistics management.

## Reference Image Analysis: {image_name}
Study the provided reference image carefully and analyze:
- Visual hierarchy and layout patterns
- Color palette and design tokens
- Typography choices and spacing
- Component organization and grid structure
- Interactive elements and navigation patterns
- Overall design philosophy and aesthetic direction

## Target Application: FY.WB.Midway Dashboard
This is a **multi-tenant freight brokerage SaaS** that needs to display:

### Key Data Points:
- Total Loads: 1,247 (↑12% from last month)
- Active Loads: 89 (↑8% from last month)
- Monthly Revenue: $285,750 (↑15% from last month)
- Load status indicators and recent activity

### Required Components:
1. **Header** with company name, tenant branding, and user profile
2. **Navigation** with role-based menu items
3. **Welcome Section** with personalized greeting and tenant context
4. **Stats Cards** showing key metrics with trend indicators
5. **Quick Actions Panel** with role-based buttons:
   - + New Load Entry
   - 📊 View Reports
   - 👥 Manage Carriers (admin only)
6. **Recent Activity Feed** showing:
   - Load #12847 delivered successfully (2 hours ago)
   - New carrier application received (4 hours ago)
   - Invoice #INV-2024-0156 pending (6 hours ago)

**Your goal** is to produce a **high-fidelity HTML/CSS design prototype** that:
- Implements semantic HTML structure matching the reference image's layout
- Uses CSS variables or classes to reference design tokens (e.g., `--color-primary-500`, `--spacing-md`)
- Adheres to SaaS partitioning rules (Tenant workspace vs Admin console) via HTML sections and role-based class toggles
- Reflects responsive behavior using CSS media queries at defined breakpoints
- Enforces role-based visibility by including conditional classes or data attributes

**Detailed Instructions**:
1. **Structure the HTML**: Create semantic `<header>`, `<nav>`, `<main>`, and `<footer>` as needed. Use `<section>`, `<article>`, `<aside>`, and `<div>` with meaningful `class` or `id` attributes.

2. **Apply CSS Design System**: Define CSS classes and variables for:
   - Colors: `--color-primary-500`, `--color-secondary-300`, `--color-neutral-100`
   - Spacing: `--spacing-xs`, `--spacing-sm`, `--spacing-md`, `--spacing-lg`
   - Typography: `--font-heading`, `--font-body`, `--text-sm`, `--text-lg`
   - Layout: `.grid-container`, `.card`, `.btn-primary`, `.btn-secondary`

3. **Responsive Design**: Include at least three breakpoints with `@media` rules:
   - Mobile: `@media (max-width: 768px)`
   - Tablet: `@media (min-width: 769px) and (max-width: 1024px)`
   - Desktop: `@media (min-width: 1025px)`

4. **Multi-Tenant & Role-Based Features**: Add HTML attributes and CSS rules:
   - `data-role="user|admin"` attributes
   - `.role-admin .admin-only {{ display: block; }}`
   - `.role-user .admin-only {{ display: none; }}`
   - `data-tenant="tenant-id"` for tenant-specific styling

5. **Design Token Integration**: Comment in CSS next to each rule which design token it maps:
   ```css
   .btn-primary {{
     background-color: var(--color-primary-500); /* token: color.primary.500 */
     padding: var(--spacing-md); /* token: spacing.md */
   }}
   ```

**Style Direction**:
- Interpret and expand on the visual style shown in the reference image
- Create your own unique take on this aesthetic while maintaining the design system approach
- Don't copy exactly - innovate within the style direction using proper design tokens

**Output Format**:
Provide a complete HTML file with embedded CSS that includes:

1. **Complete semantic HTML structure** with all required components
2. **CSS design system** with custom properties and token-based classes
3. **Responsive design** that works across all breakpoints
4. **Role-based conditional styling** with data attributes
5. **Multi-tenant considerations** with tenant-specific classes
6. **Professional typography and spacing** using design tokens
7. **Interactive elements** with hover states and micro-interactions

**Important Notes**:
- Make it genuinely unique - your interpretation of the reference style using a proper design system
- Focus on scalable, maintainable CSS architecture
- Ensure all data is clearly readable and actionable
- Create a design that feels modern, professional, and enterprise-ready
- The reference image is inspiration for visual direction, not a template to copy exactly
- Use semantic HTML and ensure accessibility (proper contrast, ARIA labels)

Generate a complete, production-ready HTML file that showcases your unique interpretation of the reference image style for the FY.WB.Midway freight brokerage dashboard using a proper design system approach.
"""

        return base_prompt.strip()
    
    async def call_openai_api(self, model_id: str, prompt: str, image_base64: str) -> Optional[str]:
        """Call OpenAI API with vision capabilities"""
        try:
            import openai
            
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                console.print("[red]OpenAI API key not found in environment variables[/red]")
                return None
            
            client = openai.OpenAI(api_key=api_key)

            # Handle different parameter requirements for different models
            if model_id.startswith('o1'):
                # o1 models use max_completion_tokens instead of max_tokens
                response = client.chat.completions.create(
                    model=model_id,
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
                    max_completion_tokens=4000
                    # Note: o1 models don't support temperature parameter
                )
            else:
                # Standard models use max_tokens
                response = client.chat.completions.create(
                    model=model_id,
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
                    temperature=0.8  # Higher temperature for more creativity
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]Error calling OpenAI API: {e}[/red]")
            return None
    
    async def call_google_api(self, model_id: str, prompt: str, image_base64: str) -> Optional[str]:
        """Call Google Gemini API with vision capabilities"""
        try:
            import google.generativeai as genai
            
            # Get API key from environment
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                console.print("[red]Google API key not found in environment variables[/red]")
                return None
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_id)
            
            # Create image part
            image_part = {
                "mime_type": "image/png",
                "data": base64.b64decode(image_base64)
            }
            
            response = model.generate_content([prompt, image_part])
            return response.text
            
        except Exception as e:
            console.print(f"[red]Error calling Google API: {e}[/red]")
            return None
    
    async def call_anthropic_api(self, model_id: str, prompt: str, image_base64: str) -> Optional[str]:
        """Call Anthropic Claude API with vision capabilities"""
        try:
            import anthropic
            
            # Get API key from environment
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                console.print("[red]Anthropic API key not found in environment variables[/red]")
                return None
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model_id,
                max_tokens=4000,
                temperature=0.8,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            console.print(f"[red]Error calling Anthropic API: {e}[/red]")
            return None

    def update_live_status(self, result: Dict[str, Any]) -> None:
        """Update the live status file for real-time updates"""
        try:
            # Read current status
            current_status = {}
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    current_status = json.load(f)

            # Initialize if needed
            if "results" not in current_status:
                current_status["results"] = []

            # Update or add this result
            updated = False
            for i, existing in enumerate(current_status["results"]):
                if (existing.get("model_id") == result.get("model_id") and
                    existing.get("reference_image") == result.get("reference_image")):
                    current_status["results"][i] = result
                    updated = True
                    break

            if not updated:
                current_status["results"].append(result)

            # Update metadata
            current_status["timestamp"] = datetime.now().isoformat()
            current_status["completed"] = len([r for r in current_status["results"] if r.get("success")])

            # Save updated status
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(current_status, f, indent=2)

        except Exception as e:
            console.print(f"[yellow]Warning: Could not update live status: {e}[/yellow]")

    async def generate_ui_with_llm(self, model_config: Dict[str, Any], image_name: str) -> Optional[Dict[str, Any]]:
        """Generate UI design using specified LLM model and reference image"""

        console.print(f"🤖 Generating {model_config['name']} + {image_name}...")

        # Load and encode the reference image
        image_path = self.examples_path / image_name
        if not image_path.exists():
            console.print(f"[red]Reference image not found: {image_path}[/red]")
            return None

        image_base64 = self.encode_image_to_base64(image_path)
        if not image_base64:
            return None

        # Create the prompt
        prompt = self.create_ui_generation_prompt(image_name)

        # Log the prompt being sent
        self.log_prompt_details(model_config['name'], image_name, prompt)

        # Call the appropriate API
        html_content = None
        if model_config['provider'] == 'openai':
            html_content = await self.call_openai_api(model_config['id'], prompt, image_base64)
        elif model_config['provider'] == 'google':
            html_content = await self.call_google_api(model_config['id'], prompt, image_base64)
        elif model_config['provider'] == 'anthropic':
            html_content = await self.call_anthropic_api(model_config['id'], prompt, image_base64)

        if not html_content:
            console.print(f"[red]Failed to generate content from {model_config['name']} + {image_name}[/red]")
            return None

        # Extract HTML from the response (LLMs often wrap it in markdown)
        html_content = self.extract_html_from_response(html_content)

        # Create unique filename for this model-image combination
        image_base = image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        output_file = self.generated_path / f"{model_config['id']}_{image_base}_dashboard.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        console.print(f"[green]✅ {model_config['name']} + {image_name} → {output_file.name}[/green]")

        result = {
            "model": model_config['name'],
            "model_id": model_config['id'],
            "provider": model_config['provider'],
            "reference_image": image_name,
            "output_file": str(output_file),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }

        # Update live status
        self.update_live_status(result)

        return result
    
    def extract_html_from_response(self, response: str) -> str:
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
    
    async def generate_all_llm_uis(self) -> List[Dict[str, Any]]:
        """Generate UI designs from all LLM models with all reference images in parallel"""

        total_combinations = len(self.llm_models) * len(self.reference_images)

        console.print(Panel.fit(
            f"[bold]🤖 LLM-Powered UI Generation[/bold]\n"
            f"Generating {total_combinations} unique designs:\n"
            f"• {len(self.llm_models)} AI models × {len(self.reference_images)} reference images\n"
            f"• All combinations generated in parallel",
            style="cyan"
        ))

        # Create tasks for all model-image combinations
        tasks = []
        task_info = []

        for model_config in self.llm_models:
            for image_name in self.reference_images:
                task = asyncio.create_task(
                    self.generate_ui_with_llm_safe(model_config, image_name),
                    name=f"generate_{model_config['id']}_{image_name}"
                )
                tasks.append(task)
                task_info.append({
                    "model": model_config['name'],
                    "model_id": model_config['id'],
                    "provider": model_config['provider'],
                    "image": image_name
                })

        # Execute all tasks in parallel with progress tracking
        console.print(f"\n🚀 Starting parallel generation of {len(tasks)} combinations...")
        start_time = datetime.now()

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            task_data = task_info[i]

            if isinstance(result, Exception):
                console.print(f"[red]❌ {task_data['model']} + {task_data['image']}: {str(result)}[/red]")
                processed_results.append({
                    "model": task_data['model'],
                    "model_id": task_data['model_id'],
                    "provider": task_data['provider'],
                    "reference_image": task_data['image'],
                    "success": False,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            elif result is None:
                console.print(f"[red]❌ {task_data['model']} + {task_data['image']}: Failed to generate[/red]")
                processed_results.append({
                    "model": task_data['model'],
                    "model_id": task_data['model_id'],
                    "provider": task_data['provider'],
                    "reference_image": task_data['image'],
                    "success": False,
                    "error": "Failed to generate content",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Save results
        results_file = self.ui_system_path / "llm_generation_results.json"
        successful_count = len([r for r in processed_results if r.get("success")])

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "generation_start": start_time.isoformat(),
                "generation_end": end_time.isoformat(),
                "duration_seconds": duration,
                "total_models": len(self.llm_models),
                "total_images": len(self.reference_images),
                "total_combinations": total_combinations,
                "successful": successful_count,
                "failed": len(processed_results) - successful_count,
                "results": processed_results
            }, f, indent=2)

        console.print(f"\n[green]🎉 Parallel LLM generation complete![/green]")
        console.print(f"⏱️  Total time: {duration:.1f} seconds")
        console.print(f"📊 Success rate: {successful_count}/{len(processed_results)} combinations")
        console.print(f"📄 Results saved to: {results_file.name}")

        # Log summary of all prompts sent
        self.log_generation_summary(processed_results, duration)

        return processed_results

    async def generate_ui_with_llm_safe(self, model_config: Dict[str, Any], image_name: str) -> Optional[Dict[str, Any]]:
        """Safe wrapper for generate_ui_with_llm that handles exceptions"""
        try:
            return await self.generate_ui_with_llm(model_config, image_name)
        except Exception as e:
            console.print(f"[red]Exception in {model_config['name']} + {image_name}: {e}[/red]")
            return None

async def main():
    """Main function to run LLM UI generation"""
    
    # Get the project root
    project_root = Path(__file__).parent.parent.parent
    
    generator = LLMUIGenerator(project_root)
    results = await generator.generate_all_llm_uis()
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
