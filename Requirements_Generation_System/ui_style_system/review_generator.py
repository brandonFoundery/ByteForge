#!/usr/bin/env python3
"""
UI Style Review Interface Generator
Creates a professional HTML page showing all 9 UI style screenshots in a grid
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class ReviewInterfaceGenerator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_system_path = project_root / "Requirements_Generation_System" / "ui_style_system"
        self.screenshots_path = self.ui_system_path / "screenshots"
        self.review_path = self.ui_system_path / "review"
        
        # Ensure review directory exists
        self.review_path.mkdir(exist_ok=True)
        
        self.themes = [
            {"id": 1, "name": "Modern Minimal", "description": "Clean, professional design with subtle shadows", "category": "Professional"},
            {"id": 2, "name": "Vibrant Gradient", "description": "Colorful gradients with purple accents", "category": "Creative"},
            {"id": 3, "name": "Dark Professional", "description": "Dark theme with cyan highlights", "category": "Professional"},
            {"id": 4, "name": "Warm Earth Tones", "description": "Warm yellows and browns, organic feel", "category": "Organic"},
            {"id": 5, "name": "Cool Blue Corporate", "description": "Traditional corporate blue styling", "category": "Corporate"},
            {"id": 6, "name": "Nature Green", "description": "Fresh green theme with rounded corners", "category": "Organic"},
            {"id": 7, "name": "Elegant Monochrome", "description": "Sophisticated grayscale design", "category": "Minimal"},
            {"id": 8, "name": "Sunset Orange", "description": "Warm gradient with orange sunset colors", "category": "Creative"},
            {"id": 9, "name": "Tech Neon", "description": "Futuristic neon green on black", "category": "Tech"}
        ]
    
    def generate_review_html(self, results_data: Dict[str, Any] = None) -> Path:
        """Generate the main review HTML page"""
        
        # Load results if not provided
        if results_data is None:
            results_path = self.ui_system_path / "generation_results.json"
            if results_path.exists():
                with open(results_path, 'r') as f:
                    results_data = json.load(f)
            else:
                results_data = {"results": [], "timestamp": datetime.now().isoformat()}
        
        # Create the HTML content
        html_content = self._create_html_template(results_data)
        
        # Save the HTML file
        review_html_path = self.review_path / "ui_style_comparison.html"
        with open(review_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return review_html_path
    
    def _create_html_template(self, results_data: Dict[str, Any]) -> str:
        """Create the HTML template with all styles and content"""
        
        # Get screenshot paths
        screenshot_cards = self._generate_screenshot_cards(results_data.get("results", []))
        
        # Generate statistics
        stats = self._generate_statistics(results_data)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FY.WB.Midway - UI Style Comparison Review</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for the review interface */
        .screenshot-card {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .screenshot-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
        }}
        .category-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .category-professional {{ background-color: #dbeafe; color: #1e40af; }}
        .category-creative {{ background-color: #fce7f3; color: #be185d; }}
        .category-organic {{ background-color: #dcfce7; color: #166534; }}
        .category-corporate {{ background-color: #e0f2fe; color: #0369a1; }}
        .category-minimal {{ background-color: #f3f4f6; color: #374151; }}
        .category-tech {{ background-color: #0a0a0a; color: #00ff88; }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}
        .modal.active {{ display: flex; }}
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
        }}
        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .close:hover {{ color: #bbb; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">UI Style Comparison Review</h1>
                    <p class="mt-1 text-sm text-gray-600">FY.WB.Midway Dashboard - 9 Professional Themes</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-500">Generated: {datetime.fromisoformat(results_data.get("timestamp", datetime.now().isoformat())).strftime("%B %d, %Y at %I:%M %p")}</p>
                    <div class="mt-1 flex space-x-4 text-xs text-gray-400">
                        {stats}
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Instructions -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-blue-800">How to Review</h3>
                    <div class="mt-2 text-sm text-blue-700">
                        <ul class="list-disc list-inside space-y-1">
                            <li>Click on any screenshot to view it in full size</li>
                            <li>Compare the visual styles, colors, and overall feel</li>
                            <li>Consider which style best fits your brand and user experience goals</li>
                            <li>Note the category tags to understand the design approach</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Screenshot Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {screenshot_cards}
        </div>

        <!-- Footer -->
        <footer class="mt-16 pt-8 border-t border-gray-200">
            <div class="text-center text-sm text-gray-500">
                <p>UI Style Comparison System - FY.WB.Midway Project</p>
                <p class="mt-1">Generated using automated screenshot capture with Playwright</p>
            </div>
        </footer>
    </main>

    <!-- Modal for full-size image viewing -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
        <div id="modalCaption" class="text-center text-white mt-4"></div>
    </div>

    <script>
        // Modal functionality
        function openModal(imageSrc, caption) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalCaption = document.getElementById('modalCaption');
            
            modal.classList.add('active');
            modalImg.src = imageSrc;
            modalCaption.innerHTML = caption;
        }}

        function closeModal() {{
            const modal = document.getElementById('imageModal');
            modal.classList.remove('active');
        }}

        // Close modal when clicking outside the image
        document.getElementById('imageModal').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeModal();
            }}
        }});

        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeModal();
            }}
        }});

        // Add click handlers to all screenshot images
        document.querySelectorAll('.screenshot-img').forEach(img => {{
            img.addEventListener('click', function() {{
                const caption = this.getAttribute('data-caption');
                openModal(this.src, caption);
            }});
        }});
    </script>
</body>
</html>'''
    
    def _generate_screenshot_cards(self, results: List[Dict[str, Any]]) -> str:
        """Generate HTML cards for each screenshot"""
        
        cards = []
        
        for theme in self.themes:
            theme_id = theme["id"]
            
            # Find the result for this theme
            result = next((r for r in results if r.get("theme_id") == theme_id), None)
            
            # Determine screenshot path
            screenshot_path = None
            if result and result.get("success") and result.get("screenshot_path"):
                screenshot_path = Path(result["screenshot_path"])
                if not screenshot_path.exists():
                    # Try relative path from review directory
                    screenshot_path = Path("../screenshots") / f"ui_style_{theme_id}_screenshot.png"
            else:
                # Use placeholder or original example image
                example_path = self.ui_system_path.parent / "ui_style_examples" / f"ui_style_{theme_id}.png"
                if example_path.exists():
                    screenshot_path = Path("../ui_style_examples") / f"ui_style_{theme_id}.png"
            
            # Generate status indicator
            if result and result.get("success"):
                status_indicator = '<div class="absolute top-2 right-2 h-3 w-3 bg-green-500 rounded-full border-2 border-white"></div>'
                status_text = "Screenshot captured"
            else:
                status_indicator = '<div class="absolute top-2 right-2 h-3 w-3 bg-yellow-500 rounded-full border-2 border-white"></div>'
                status_text = "Using example image"
            
            # Category class
            category_class = f"category-{theme['category'].lower()}"
            
            card_html = f'''
            <div class="screenshot-card bg-white rounded-lg shadow-md overflow-hidden">
                <div class="relative">
                    {status_indicator}
                    <img 
                        src="{screenshot_path}" 
                        alt="{theme['name']} Theme Screenshot" 
                        class="screenshot-img w-full h-48 object-cover cursor-pointer hover:opacity-90 transition-opacity"
                        data-caption="Theme {theme_id}: {theme['name']} - {theme['description']}"
                        onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzZiNzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='"
                    >
                </div>
                <div class="p-6">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-lg font-semibold text-gray-900">Theme {theme_id}</h3>
                        <span class="category-badge {category_class}">{theme['category']}</span>
                    </div>
                    <h4 class="text-md font-medium text-gray-800 mb-2">{theme['name']}</h4>
                    <p class="text-sm text-gray-600 mb-4">{theme['description']}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xs text-gray-500">{status_text}</span>
                        <button 
                            onclick="openModal('{screenshot_path}', 'Theme {theme_id}: {theme['name']} - {theme['description']}')"
                            class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                        >
                            View Full Size
                        </button>
                    </div>
                </div>
            </div>'''
            
            cards.append(card_html)
        
        return '\n'.join(cards)
    
    def _generate_statistics(self, results_data: Dict[str, Any]) -> str:
        """Generate statistics HTML"""
        
        total = results_data.get("total_themes", 9)
        successful = results_data.get("successful", 0)
        failed = results_data.get("failed", 0)
        
        return f'''
        <span>Total Themes: {total}</span>
        <span>•</span>
        <span class="text-green-600">Captured: {successful}</span>
        <span>•</span>
        <span class="text-yellow-600">Examples: {failed}</span>
        '''

def main():
    """Main function to generate the review interface"""
    
    # Get the project root
    project_root = Path(__file__).parent.parent.parent
    
    generator = ReviewInterfaceGenerator(project_root)
    review_html_path = generator.generate_review_html()
    
    print(f"✅ Review interface generated: {review_html_path}")
    print(f"🌐 Open in browser: file://{review_html_path.absolute()}")
    
    return review_html_path

if __name__ == "__main__":
    main()
