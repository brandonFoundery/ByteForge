#!/usr/bin/env python3
"""
Live LLM UI Comparison Viewer
Creates a live-updating comparison page that shows placeholders initially
and updates in real-time as each design is generated
"""

import os
import sys
import json
import asyncio
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

class LiveComparisonViewer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_system_path = project_root / "Requirements_Generation_System" / "ui_style_system"
        self.generated_path = self.ui_system_path / "llm_generated"
        self.live_comparison_file = self.ui_system_path / "live_comparison.html"
        self.status_file = self.ui_system_path / "generation_status.json"
        
        # Ensure directories exist
        self.generated_path.mkdir(exist_ok=True)
        
        # Models and images
        self.models = [
            {"name": "OpenAI GPT-4o", "id": "gpt-4o", "provider": "openai"},
            {"name": "OpenAI GPT-4.1", "id": "gpt-4.1-preview", "provider": "openai"},
            {"name": "OpenAI o3", "id": "o3-mini", "provider": "openai"},
            {"name": "Google Gemini 2.5", "id": "gemini-2.0-flash-exp", "provider": "google"},
            {"name": "Anthropic Claude 4", "id": "claude-3-5-sonnet-20241022", "provider": "anthropic"}
        ]
        
        self.reference_images = self.get_reference_images()
        
    def get_reference_images(self) -> List[str]:
        """Get all reference images from the examples directory"""
        # Try multiple possible paths
        possible_paths = [
            self.project_root / "Requirements_Generation_System" / "ui_style_examples",
            self.project_root / "ui_style_examples",
            Path("Requirements_Generation_System/ui_style_examples"),
            Path("ui_style_examples")
        ]

        examples_path = None
        for path in possible_paths:
            if path.exists():
                examples_path = path
                break

        if not examples_path:
            console.print(f"[red]Examples directory not found in any of: {[str(p) for p in possible_paths]}[/red]")
            return []

        image_files = list(examples_path.glob("*.png"))
        image_names = [img.name for img in sorted(image_files)]
        console.print(f"[green]Found {len(image_names)} reference images in {examples_path}: {', '.join(image_names)}[/green]")
        return image_names

    def load_current_status(self) -> dict:
        """Load current status data from the LLM generation results file"""

        # Try to load from the actual LLM generation results file first
        llm_results_file = self.ui_system_path / "llm_generation_results.json"

        try:
            if llm_results_file.exists():
                with open(llm_results_file, 'r', encoding='utf-8') as f:
                    llm_data = json.load(f)

                # Convert LLM results format to status format
                status_data = {
                    "timestamp": llm_data.get("timestamp", datetime.now().isoformat()),
                    "status": "completed" if llm_data.get("successful", 0) > 0 else "initializing",
                    "total_combinations": llm_data.get("total_combinations", len(self.models) * len(self.reference_images)),
                    "completed": llm_data.get("successful", 0),
                    "results": llm_data.get("results", [])
                }

                console.print(f"[green]✅ Loaded {len(status_data['results'])} results from LLM generation file[/green]")
                return status_data

        except Exception as e:
            console.print(f"[yellow]Warning: Could not load LLM results file: {e}[/yellow]")

        # Fallback to status file
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load status file: {e}[/yellow]")

        # Return default status if no files can be read
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "initializing",
            "total_combinations": len(self.models) * len(self.reference_images),
            "completed": 0,
            "results": []
        }

    def create_live_html(self) -> str:
        """Create the live comparison HTML page"""
        
        total_designs = len(self.models) * len(self.reference_images)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live LLM UI Generation - FY.WB.Midway ({total_designs} Designs)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .design-placeholder {{
            background: linear-gradient(45deg, #f3f4f6, #e5e7eb);
            background-size: 20px 20px;
            background-image: 
                linear-gradient(45deg, rgba(255,255,255,.2) 25%, transparent 25%), 
                linear-gradient(-45deg, rgba(255,255,255,.2) 25%, transparent 25%), 
                linear-gradient(45deg, transparent 75%, rgba(255,255,255,.2) 75%), 
                linear-gradient(-45deg, transparent 75%, rgba(255,255,255,.2) 75%);
            animation: pulse 2s infinite;
        }}
        
        .design-completed {{
            border: 2px solid #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }}
        
        .design-failed {{
            border: 2px solid #ef4444;
            background: #fee2e2;
        }}
        
        .iframe-container {{
            width: 100%;
            height: 300px;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        
        .iframe-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .tab-button {{
            transition: all 0.2s ease;
        }}
        
        .tab-button.active {{
            background-color: #3b82f6;
            color: white;
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .status-pending {{ background-color: #fbbf24; }}
        .status-generating {{ background-color: #3b82f6; animation: pulse 1s infinite; }}
        .status-completed {{ background-color: #10b981; }}
        .status-failed {{ background-color: #ef4444; }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">Live LLM UI Generation</h1>
                    <p class="text-gray-600">FY.WB.Midway Dashboard - {total_designs} Designs Generating</p>
                </div>
                <div class="text-right">
                    <div id="overall-status" class="text-sm font-medium mb-1">
                        <span class="status-indicator status-pending"></span>
                        <span id="status-text">Initializing...</span>
                    </div>
                    <div class="text-xs text-gray-500">
                        <span id="completed-count">0</span>/{total_designs} completed
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex space-x-8 overflow-x-auto">
"""

        # Add tab for each model
        for i, model in enumerate(self.models):
            active_class = "active border-blue-500 text-blue-600" if i == 0 else "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            html_content += f"""
                <button onclick="showTab('{model['id']}')" class="tab-button {active_class} py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap">
                    {model['name']} (<span id="count-{model['id']}">0</span>/{len(self.reference_images)})
                </button>
"""

        html_content += """
            </div>
        </div>
    </nav>

    <!-- Model Tabs Content -->
"""

        # Create tab content for each model
        for i, model in enumerate(self.models):
            active_class = "active" if i == 0 else ""
            html_content += f"""
    <div id="{model['id']}" class="tab-content {active_class}">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="mb-6">
                <h2 class="text-xl font-bold text-gray-900 mb-2">{model['name']}</h2>
                <p class="text-gray-600">Provider: {model['provider']} | Generating {len(self.reference_images)} designs</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
"""

            # Add placeholder for each reference image
            for image_name in self.reference_images:
                design_id = f"{model['id']}_{image_name.replace('.png', '')}"
                html_content += f"""
                <div id="design-{design_id}" class="design-placeholder bg-white rounded-lg shadow-sm border p-4">
                    <div class="mb-3">
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="font-semibold text-gray-900 text-sm">Style: {image_name}</h3>
                            <span id="status-{design_id}" class="status-indicator status-pending"></span>
                        </div>
                        <div class="text-xs text-gray-500 mb-2">
                            <span id="status-text-{design_id}">Waiting to generate...</span>
                        </div>
                    </div>
                    
                    <div class="iframe-container mb-3">
                        <div id="placeholder-{design_id}" class="w-full h-full flex items-center justify-center text-gray-400">
                            <div class="text-center">
                                <div class="text-4xl mb-2">⏳</div>
                                <div class="text-sm">Generating...</div>
                            </div>
                        </div>
                        <iframe id="iframe-{design_id}" src="" style="display: none;" loading="lazy"></iframe>
                    </div>
                    
                    <button onclick="openDesign('{design_id}')" class="w-full bg-gray-100 text-gray-400 py-2 px-3 rounded text-xs font-medium cursor-not-allowed" disabled>
                        Generating...
                    </button>
                </div>
"""

            html_content += """
            </div>
        </div>
    </div>
"""

        # Load current status data to embed
        embedded_status = self.load_current_status()

        # Add JavaScript for live updates
        html_content += f"""
    <script>
        let completedCount = 0;
        const totalDesigns = {total_designs};

        // Embedded status data (avoids CORS issues)
        const embeddedStatus = {json.dumps(embedded_status, indent=8)};
        
        function showTab(tabName) {{
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tab buttons
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {{
                button.classList.remove('active', 'text-blue-600', 'border-blue-500');
                button.classList.add('text-gray-500', 'border-transparent');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Activate selected tab button
            event.target.classList.add('active', 'text-blue-600', 'border-blue-500');
            event.target.classList.remove('text-gray-500', 'border-transparent');
        }}
        
        function openDesign(designId) {{
            const iframe = document.getElementById(`iframe-${{designId}}`);
            if (iframe && iframe.src) {{
                window.open(iframe.src, '_blank');
            }}
        }}
        
        function updateDesignStatus(designId, status, filename = null) {{
            console.log(`updateDesignStatus called: ${{designId}}, ${{status}}, ${{filename}}`);

            const designCard = document.getElementById(`design-${{designId}}`);
            const statusIndicator = document.getElementById(`status-${{designId}}`);
            const statusText = document.getElementById(`status-text-${{designId}}`);
            const placeholder = document.getElementById(`placeholder-${{designId}}`);
            const iframe = document.getElementById(`iframe-${{designId}}`);

            if (!designCard) {{
                console.log(`Design card not found for ID: design-${{designId}}`);
                return;
            }}

            const button = designCard.querySelector('button');
            console.log(`Found elements for ${{designId}}:`, {{
                designCard: !!designCard,
                statusIndicator: !!statusIndicator,
                statusText: !!statusText,
                placeholder: !!placeholder,
                iframe: !!iframe,
                button: !!button
            }});
            
            // Update status indicator
            statusIndicator.className = `status-indicator status-${{status}}`;
            
            if (status === 'generating') {{
                statusText.textContent = 'Generating design...';
                designCard.classList.remove('design-placeholder');
                designCard.classList.add('bg-blue-50', 'border-blue-200');
            }} else if (status === 'completed' && filename) {{
                statusText.textContent = 'Completed!';
                designCard.classList.remove('design-placeholder', 'bg-blue-50', 'border-blue-200');
                designCard.classList.add('design-completed');
                
                // Show the iframe and hide placeholder
                placeholder.style.display = 'none';
                iframe.src = filename;
                iframe.style.display = 'block';
                
                // Enable button
                button.textContent = 'View Full Design';
                button.classList.remove('bg-gray-100', 'text-gray-400', 'cursor-not-allowed');
                button.classList.add('bg-blue-600', 'text-white', 'hover:bg-blue-700', 'cursor-pointer');
                button.disabled = false;
                
                // Update counters
                completedCount++;
                updateCounters();
                
            }} else if (status === 'failed') {{
                statusText.textContent = 'Generation failed';
                designCard.classList.remove('design-placeholder', 'bg-blue-50', 'border-blue-200');
                designCard.classList.add('design-failed');
                
                placeholder.innerHTML = `
                    <div class="text-center text-red-500">
                        <div class="text-4xl mb-2">❌</div>
                        <div class="text-sm">Generation Failed</div>
                    </div>
                `;
                
                button.textContent = 'Failed';
                button.classList.remove('bg-gray-100', 'text-gray-400');
                button.classList.add('bg-red-100', 'text-red-600', 'cursor-not-allowed');
            }}
        }}
        
        function updateCounters() {{
            document.getElementById('completed-count').textContent = completedCount;
            
            // Update model-specific counters
            const models = {json.dumps([model['id'] for model in self.models])};
            models.forEach(modelId => {{
                // Escape dots in model ID for CSS selector
                const escapedModelId = modelId.replace(/\\./g, '\\\\.');
                const modelCompleted = document.querySelectorAll(`#${{escapedModelId}} .design-completed`).length;
                document.getElementById(`count-${{modelId}}`).textContent = modelCompleted;
            }});
            
            // Update overall status
            const statusText = document.getElementById('status-text');
            const overallStatus = document.getElementById('overall-status').querySelector('.status-indicator');
            
            if (completedCount === 0) {{
                statusText.textContent = 'Starting generation...';
                overallStatus.className = 'status-indicator status-generating';
            }} else if (completedCount < totalDesigns) {{
                statusText.textContent = `Generating... (${{completedCount}}/${{totalDesigns}})`;
                overallStatus.className = 'status-indicator status-generating';
            }} else {{
                statusText.textContent = 'All designs completed!';
                overallStatus.className = 'status-indicator status-completed';
            }}
        }}
        
        // Process embedded status data immediately
        function processStatusData(status) {{
            console.log('Processing status data:', status);

            // Update designs based on status
            if (status.results) {{
                        status.results.forEach(result => {{
                            const imageBase = result.reference_image ? result.reference_image.replace('.png', '') : 'unknown';
                            const designId = `${{result.model_id}}_${{imageBase}}`;

                            // Extract just the filename from the full path
                            let filename = null;
                            if (result.output_file) {{
                                // Handle both Windows and Unix paths
                                const pathParts = result.output_file.replace(/\\\\/g, '/').split('/');
                                filename = pathParts[pathParts.length - 1];
                            }}

                            console.log(`Processing result for ${{designId}}:`, result);
                            console.log(`Extracted filename: ${{filename}}`);

                            // Check if element exists with exact ID
                            let element = document.getElementById(`design-${{designId}}`);
                            if (!element) {{
                                console.log(`Element not found for ID: design-${{designId}}`);
                                // Try alternative ID patterns
                                const alternativeIds = [
                                    `design-${{result.model_id.replace(/[^a-zA-Z0-9]/g, '-')}}_${{imageBase}}`,
                                    `design-${{result.model_id}}_${{imageBase}}`,
                                ];

                                for (const altId of alternativeIds) {{
                                    element = document.getElementById(altId);
                                    if (element) {{
                                        console.log(`Found element with alternative ID: ${{altId}}`);
                                        break;
                                    }}
                                }}

                                if (!element) {{
                                    // List all available design elements for debugging
                                    const allDesigns = document.querySelectorAll('[id^="design-"]');
                                    console.log('Available design elements:', Array.from(allDesigns).map(el => el.id));
                                }}
                            }}

                            if (result.success && filename && element) {{
                                console.log(`Marking ${{designId}} as completed with file ${{filename}}`);
                                updateDesignStatus(designId, 'completed', `llm_generated/${{filename}}`);
                            }} else if (result.success === false && element) {{
                                console.log(`Marking ${{designId}} as failed`);
                                updateDesignStatus(designId, 'failed');
                            }} else if (result.status === 'generating' && element) {{
                                console.log(`Marking ${{designId}} as generating`);
                                updateDesignStatus(designId, 'generating');
                            }}
                        }});
                    }}
        }}

        // Start processing when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            updateCounters();

            // Process embedded status data immediately
            if (embeddedStatus && embeddedStatus.results) {{
                console.log('Processing embedded status data with', embeddedStatus.results.length, 'results');
                processStatusData(embeddedStatus);
            }} else {{
                console.log('No embedded status data found');
            }}
        }});
    </script>
</body>
</html>
"""
        
        return html_content
    
    def create_and_open_live_page(self):
        """Create the live comparison page and open it immediately"""
        
        console.print("🌐 Creating live comparison page...")
        
        # Create the HTML content
        html_content = self.create_live_html()
        
        # Save the live comparison file
        with open(self.live_comparison_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Initialize status file
        initial_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "initializing",
            "total_combinations": len(self.models) * len(self.reference_images),
            "completed": 0,
            "results": []
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(initial_status, f, indent=2)
        
        console.print(f"✅ Live comparison page created: {self.live_comparison_file.name}")
        
        # Open in browser immediately
        try:
            webbrowser.open(f"file://{self.live_comparison_file.absolute()}")
            console.print("🌐 Live comparison page opened in browser!")
            console.print("📱 The page will update automatically as designs are generated")
        except Exception as e:
            console.print(f"⚠️  Could not auto-open browser: {e}")
            console.print(f"📂 Manual open: file://{self.live_comparison_file.absolute()}")
        
        return str(self.live_comparison_file.absolute())

def main():
    """Create and open the live comparison page"""
    project_root = Path(__file__).parent.parent.parent
    viewer = LiveComparisonViewer(project_root)
    return viewer.create_and_open_live_page()

if __name__ == "__main__":
    main()
