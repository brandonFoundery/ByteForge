#!/usr/bin/env python3
"""
LLM UI Comparison Viewer
Creates a comprehensive comparison page showing all LLM-generated UIs
Waits for all generations to complete before displaying results
"""

import sys
import asyncio
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

class LLMComparisonViewer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_system_path = project_root / "Requirements_Generation_System" / "ui_style_system"
        self.generated_path = self.ui_system_path / "llm_generated"
        self.comparison_file = self.ui_system_path / "llm_comparison.html"
        
    def create_comparison_html(self, results: List[Dict[str, Any]]) -> str:
        """Create comprehensive HTML comparison page"""
        
        successful_results = [r for r in results if r.get("success")]
        failed_results = [r for r in results if not r.get("success")]
        
        # Group results by model and image
        results_by_model = {}
        for result in successful_results:
            model_name = result['model']
            if model_name not in results_by_model:
                results_by_model[model_name] = []
            results_by_model[model_name].append(result)

        total_combinations = len(results)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM UI Design Comparison - FY.WB.Midway ({total_combinations} Designs)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .iframe-container {{
            position: relative;
            width: 100%;
            height: 500px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}

        .iframe-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        .model-card {{
            transition: all 0.3s ease;
        }}

        .model-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}

        .design-card {{
            transition: all 0.2s ease;
            cursor: pointer;
        }}

        .design-card:hover {{
            transform: scale(1.02);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
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

        .error-card {{
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border-left: 4px solid #ef4444;
        }}

        .success-card {{
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left: 4px solid #22c55e;
        }}

        .grid-auto-fit {{
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">LLM UI Design Matrix</h1>
                    <p class="text-gray-600 mt-2">FY.WB.Midway Dashboard - {total_combinations} Unique Designs from 5 AI Models</p>
                </div>
                <div class="text-right">
                    <div class="text-sm text-gray-500">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    <div class="text-sm font-medium text-green-600">{len(successful_results)} Successful</div>
                    <div class="text-sm font-medium text-red-600">{len(failed_results)} Failed</div>
                </div>
            </div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex space-x-8">
                <button onclick="showTab('matrix')" class="tab-button active py-4 px-1 border-b-2 border-blue-500 font-medium text-sm text-blue-600">
                    Design Matrix
                </button>
                <button onclick="showTab('by-model')" class="tab-button py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">
                    By Model
                </button>
                <button onclick="showTab('by-style')" class="tab-button py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">
                    By Style
                </button>
                <button onclick="showTab('analysis')" class="tab-button py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300">
                    Analysis
                </button>
            </div>
        </div>
    </nav>

    <!-- Design Matrix Tab -->
    <div id="matrix" class="tab-content active">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="mb-6">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Complete Design Matrix</h2>
                <p class="text-gray-600">All {total_combinations} generated designs organized by model and reference style</p>
            </div>

            <div class="grid grid-auto-fit gap-4">
"""

        # Add all successful designs as cards
        for result in successful_results:
            model_name = result['model']
            provider = result['provider']
            reference_image = result.get('reference_image', 'Unknown')
            output_file = Path(result['output_file']).name

            html_content += f"""
                <div class="design-card bg-white rounded-lg shadow-sm border p-4" onclick="openDesign('{output_file}')">
                    <div class="mb-3">
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="font-semibold text-gray-900 text-sm">{model_name}</h3>
                            <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">{provider}</span>
                        </div>
                        <div class="text-xs text-gray-500 mb-2">Style: {reference_image}</div>
                    </div>

                    <div class="iframe-container mb-3" style="height: 200px;">
                        <iframe src="{output_file}" loading="lazy"></iframe>
                    </div>

                    <button class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded text-xs font-medium transition-colors">
                        View Full Design
                    </button>
                </div>
"""

        # Add failed model cards
        for result in failed_results:
            model_name = result['model']
            provider = result['provider']
            error = result.get('error', 'Unknown error')
            
            html_content += f"""
                <div class="model-card error-card p-6 rounded-lg">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900">{model_name}</h3>
                        <span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Failed</span>
                    </div>
                    <p class="text-sm text-red-600 mb-4">{error}</p>
                    <div class="text-xs text-gray-500">Provider: <span class="font-medium">{provider}</span></div>
                </div>
"""

        html_content += """
            </div>
        </div>
    </div>

    <!-- By Model Tab -->
    <div id="by-model" class="tab-content">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
"""

        # Group by model and display
        for model_name, model_results in results_by_model.items():
            html_content += f"""
            <div class="mb-8">
                <h2 class="text-xl font-bold text-gray-900 mb-4">{model_name} ({len(model_results)} designs)</h2>
                <div class="grid grid-auto-fit gap-4">
"""

            for result in model_results:
                output_file = Path(result['output_file']).name
                reference_image = result.get('reference_image', 'Unknown')

                html_content += f"""
                    <div class="design-card bg-white rounded-lg shadow-sm border p-4" onclick="openDesign('{output_file}')">
                        <div class="mb-3">
                            <div class="text-sm font-medium text-gray-900 mb-1">Style: {reference_image}</div>
                        </div>
                        <div class="iframe-container mb-3" style="height: 200px;">
                            <iframe src="{output_file}" loading="lazy"></iframe>
                        </div>
                        <button class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded text-xs font-medium transition-colors">
                            View Full Design
                        </button>
                    </div>
"""

            html_content += """
                </div>
            </div>
"""

        html_content += """
        </div>
    </div>

    <!-- By Style Tab -->
    <div id="by-style" class="tab-content">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p class="text-gray-600 mb-6">Designs grouped by reference style image</p>
"""

        # Group by reference image
        results_by_style = {}
        for result in successful_results:
            style = result.get('reference_image', 'Unknown')
            if style not in results_by_style:
                results_by_style[style] = []
            results_by_style[style].append(result)

        for style_name, style_results in results_by_style.items():
            html_content += f"""
            <div class="mb-8">
                <h2 class="text-xl font-bold text-gray-900 mb-4">{style_name} ({len(style_results)} designs)</h2>
                <div class="grid grid-auto-fit gap-4">
"""

            for result in style_results:
                output_file = Path(result['output_file']).name
                model_name = result['model']

                html_content += f"""
                    <div class="design-card bg-white rounded-lg shadow-sm border p-4" onclick="openDesign('{output_file}')">
                        <div class="mb-3">
                            <div class="text-sm font-medium text-gray-900 mb-1">{model_name}</div>
                        </div>
                        <div class="iframe-container mb-3" style="height: 200px;">
                            <iframe src="{output_file}" loading="lazy"></iframe>
                        </div>
                        <button class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded text-xs font-medium transition-colors">
                            View Full Design
                        </button>
                    </div>
"""

            html_content += """
                </div>
            </div>
"""

        html_content += """
        </div>
    </div>

    <!-- Analysis Tab -->
    <div id="analysis" class="tab-content">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="bg-white rounded-lg shadow-sm border p-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-6">Generation Analysis</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="text-center">
                        <div class="text-3xl font-bold text-blue-600">""" + str(len(results)) + """</div>
                        <div class="text-gray-600">Total Models</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-600">""" + str(len(successful_results)) + """</div>
                        <div class="text-gray-600">Successful</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-red-600">""" + str(len(failed_results)) + """</div>
                        <div class="text-gray-600">Failed</div>
                    </div>
                </div>

                <div class="space-y-6">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-3">Model Performance</h3>
                        <div class="space-y-2">
"""

        # Add performance analysis
        for result in results:
            status_color = "green" if result.get("success") else "red"
            status_text = "✅ Success" if result.get("success") else "❌ Failed"
            
            html_content += f"""
                            <div class="flex justify-between items-center py-2 px-4 bg-gray-50 rounded">
                                <span class="font-medium">{result['model']}</span>
                                <span class="text-{status_color}-600">{status_text}</span>
                            </div>
"""

        html_content += """
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));

            // Remove active class from all tab buttons
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {
                button.classList.remove('active', 'text-blue-600', 'border-blue-500');
                button.classList.add('text-gray-500', 'border-transparent');
            });

            // Show selected tab content
            document.getElementById(tabName).classList.add('active');

            // Activate selected tab button
            event.target.classList.add('active', 'text-blue-600', 'border-blue-500');
            event.target.classList.remove('text-gray-500', 'border-transparent');
        }

        function openDesign(filename) {
            window.open(filename, '_blank');
        }

        function openFullscreen(filename) {
            window.open(filename, '_blank');
        }

        // Auto-refresh iframes every 30 seconds to catch late-loading content
        setInterval(() => {
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                if (iframe.src && !iframe.src.includes('about:blank')) {
                    iframe.src = iframe.src;
                }
            });
        }, 30000);

        // Add click handlers for design cards
        document.addEventListener('DOMContentLoaded', function() {
            const designCards = document.querySelectorAll('.design-card');
            designCards.forEach(card => {
                card.style.cursor = 'pointer';
            });
        });
    </script>
</body>
</html>
"""
        
        return html_content
    
    def save_and_open_comparison(self, results: List[Dict[str, Any]]) -> None:
        """Save comparison HTML and open in browser"""
        
        html_content = self.create_comparison_html(results)
        
        # Save the comparison file
        with open(self.comparison_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"\n[green]✅ Comparison page created: {self.comparison_file.name}[/green]")
        
        # Open in browser
        try:
            webbrowser.open(f"file://{self.comparison_file.absolute()}")
            console.print("[green]🌐 Opened comparison page in browser[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not auto-open browser: {e}[/yellow]")
            console.print(f"[blue]📂 Manual open: file://{self.comparison_file.absolute()}[/blue]")

async def main():
    """Main function to run LLM generation and create comparison"""
    
    # Import the generator
    from llm_ui_generator import LLMUIGenerator
    
    project_root = Path(__file__).parent.parent.parent
    
    # Generate UIs with all LLMs in parallel
    generator = LLMUIGenerator(project_root)
    results = await generator.generate_all_llm_uis()
    
    # Create and display comparison
    viewer = LLMComparisonViewer(project_root)
    viewer.save_and_open_comparison(results)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
