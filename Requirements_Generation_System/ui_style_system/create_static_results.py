#!/usr/bin/env python3
"""
Create Static Results Page
Reads the generation_status.json and creates a static HTML page with all results
"""

import json
import webbrowser
from pathlib import Path
from datetime import datetime

def create_static_results():
    """Create a static results page from the current status"""
    
    ui_system_path = Path(__file__).parent
    status_file = ui_system_path / "generation_status.json"
    
    if not status_file.exists():
        print("❌ No generation_status.json found")
        return
    
    # Read status
    with open(status_file, 'r', encoding='utf-8') as f:
        status = json.load(f)
    
    print(f"📊 Found {status.get('completed', 0)}/{status.get('total_combinations', 0)} completed designs")
    
    # Group results by model
    models = {}
    for result in status.get('results', []):
        model_id = result.get('model_id', 'unknown')
        if model_id not in models:
            models[model_id] = []
        models[model_id].append(result)
    
    # Create HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM UI Generation Results - FY.WB.Midway</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .tab-button.active {{ background-color: #3b82f6; color: white; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">LLM UI Generation Results</h1>
                    <p class="text-gray-600 mt-1">FY.WB.Midway Dashboard • {status.get('total_combinations', 0)} Designs Generated</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold text-green-600">{status.get('completed', 0)}/{status.get('total_combinations', 0)} completed</div>
                    <div class="text-sm text-gray-500">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
        </div>
        
        <!-- Model Tabs -->
        <div class="bg-white rounded-lg shadow-sm border">
            <div class="border-b border-gray-200">
                <nav class="flex space-x-8 px-6" aria-label="Tabs">
"""
    
    # Add tabs
    model_names = {
        'gpt-4o': 'OpenAI GPT-4o',
        'gpt-4.1-preview': 'OpenAI GPT-4.1',
        'o3-mini': 'OpenAI o3',
        'gemini-2.0-flash-exp': 'Google Gemini 2.5',
        'claude-3-5-sonnet-20241022': 'Anthropic Claude 4'
    }
    
    for i, (model_id, results) in enumerate(models.items()):
        model_name = model_names.get(model_id, model_id)
        completed_count = len([r for r in results if r.get('success')])
        total_count = len(results)
        
        active_class = "active" if i == 0 else ""
        html_content += f"""
                    <button class="tab-button {active_class} py-4 px-1 border-b-2 font-medium text-sm focus:outline-none"
                            onclick="showTab('{model_id}')">
                        {model_name} ({completed_count}/{total_count})
                    </button>
"""
    
    html_content += """
                </nav>
            </div>
            
            <!-- Tab Contents -->
"""
    
    # Add tab contents
    for i, (model_id, results) in enumerate(models.items()):
        model_name = model_names.get(model_id, model_id)
        active_class = "active" if i == 0 else ""
        
        html_content += f"""
            <div id="{model_id}" class="tab-content {active_class} p-6">
                <div class="mb-4">
                    <h2 class="text-xl font-semibold text-gray-900">{model_name}</h2>
                    <p class="text-gray-600">Provider: {results[0].get('provider', 'unknown') if results else 'unknown'} | Generating {len(results)} designs</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
"""
        
        # Add design cards
        for result in sorted(results, key=lambda x: x.get('reference_image', '')):
            image_name = result.get('reference_image', 'unknown')
            success = result.get('success', False)
            output_file = result.get('output_file', '')
            
            if success and output_file:
                # Extract filename
                filename = output_file.split('\\')[-1] if '\\' in output_file else output_file.split('/')[-1]
                
                html_content += f"""
                    <div class="bg-white rounded-lg border shadow-sm overflow-hidden">
                        <div class="p-4">
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="font-semibold text-gray-900 text-sm">Style: {image_name}</h3>
                                <span class="text-green-500 text-xl">✅</span>
                            </div>
                            
                            <div class="mb-3">
                                <iframe src="llm_generated/{filename}" 
                                        style="width: 100%; height: 200px; border: 1px solid #ddd; border-radius: 4px;">
                                </iframe>
                            </div>
                            
                            <button onclick="window.open('llm_generated/{filename}', '_blank')"
                                    class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 text-sm">
                                View Full Design
                            </button>
                        </div>
                    </div>
"""
            else:
                html_content += f"""
                    <div class="bg-gray-50 rounded-lg border border-gray-200 p-4">
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="font-semibold text-gray-700 text-sm">Style: {image_name}</h3>
                            <span class="text-red-500 text-xl">❌</span>
                        </div>
                        <div class="text-center text-gray-500 py-8">
                            <div class="text-4xl mb-2">❌</div>
                            <div class="text-sm">Generation Failed</div>
                        </div>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
"""
    
    html_content += """
        </div>
    </div>
    
    <script>
        function showTab(modelId) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all buttons
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(modelId).classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    # Save static results page
    static_file = ui_system_path / "static_results.html"
    with open(static_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Static results page created: {static_file}")
    
    # Open in browser
    try:
        webbrowser.open(f"file://{static_file.absolute()}")
        print("🌐 Static results page opened in browser!")
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"📂 Manual open: file://{static_file.absolute()}")
    
    return str(static_file.absolute())

if __name__ == "__main__":
    create_static_results()
