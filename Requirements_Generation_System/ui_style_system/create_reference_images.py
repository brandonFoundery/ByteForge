#!/usr/bin/env python3
"""
Create Reference UI Style Images
Generates 5 different UI style reference images for LLM models to mimic
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_reference_images():
    """Create 5 different UI style reference images"""

    # Create examples directory
    examples_dir = Path(__file__).parent.parent / "ui_style_examples"
    examples_dir.mkdir(exist_ok=True)

    # Image dimensions
    width, height = 800, 600

    # Style 1: Modern Material Design
    create_material_design_image(examples_dir / "ui_style_1.png", width, height)

    # Style 2: Vibrant Gradient Design
    create_gradient_design_image(examples_dir / "ui_style_2.png", width, height)

    # Style 3: Dark Professional Theme
    create_dark_professional_image(examples_dir / "ui_style_3.png", width, height)

    # Style 4: Warm Earth Tones
    create_earth_tones_image(examples_dir / "ui_style_4.png", width, height)

    # Style 5: Corporate Blue Theme
    create_corporate_blue_image(examples_dir / "ui_style_5.png", width, height)

    print(f"✅ Created 5 reference UI style images in {examples_dir}")

def create_material_design_image(filepath: Path, width: int, height: int):
    """Create Material Design style reference"""
    img = Image.new('RGB', (width, height), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, width, 80], fill='#2196F3')
    draw.text((20, 30), "Material Dashboard", fill='white', font=get_font(24))
    
    # Cards with shadows (simulated with gradients)
    card_positions = [(50, 120), (300, 120), (550, 120)]
    card_colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
    
    for i, (x, y) in enumerate(card_positions):
        # Shadow effect
        draw.rectangle([x+4, y+4, x+194, y+124], fill='#E0E0E0')
        # Card
        draw.rectangle([x, y, x+190, y+120], fill=card_colors[i])
        draw.text((x+20, y+20), f"Metric {i+1}", fill='#424242', font=get_font(16))
        draw.text((x+20, y+50), "1,247", fill='#2196F3', font=get_font(32))
        draw.text((x+20, y+85), "↑12% increase", fill='#4CAF50', font=get_font(12))
    
    # Action buttons
    draw.rectangle([50, 280, 200, 320], fill='#2196F3')
    draw.text((70, 295), "New Load", fill='white', font=get_font(14))
    
    draw.rectangle([220, 280, 370, 320], fill='#FF9800')
    draw.text((240, 295), "View Reports", fill='white', font=get_font(14))
    
    img.save(filepath)

def create_gradient_design_image(filepath: Path, width: int, height: int):
    """Create vibrant gradient design reference"""
    img = Image.new('RGB', (width, height), '#1A1A2E')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (simulated)
    for y in range(height):
        r = min(255, max(0, int(26 + (138 * y / height))))  # 1A -> 8A (clamped)
        g = min(255, max(0, int(26 + (43 * y / height))))   # 1A -> 2B (clamped)
        b = min(255, max(0, int(46 + (224 * y / height))))  # 2E -> E0 (clamped)
        color = f'#{r:02x}{g:02x}{b:02x}'
        draw.line([(0, y), (width, y)], fill=color)
    
    # Header with gradient
    draw.rectangle([0, 0, width, 80], fill='#FF6B6B')
    draw.text((20, 30), "Vibrant Dashboard", fill='white', font=get_font(24))
    
    # Colorful cards
    card_colors = ['#4ECDC4', '#45B7D1', '#96CEB4']
    card_positions = [(50, 120), (300, 120), (550, 120)]
    
    for i, (x, y) in enumerate(card_positions):
        draw.rectangle([x, y, x+190, y+120], fill=card_colors[i])
        draw.text((x+20, y+20), f"Active {i+1}", fill='white', font=get_font(16))
        draw.text((x+20, y+50), "89", fill='white', font=get_font(32))
        draw.text((x+20, y+85), "↑8% growth", fill='white', font=get_font(12))
    
    # Gradient buttons
    draw.rectangle([50, 280, 200, 320], fill='#FF6B6B')
    draw.text((70, 295), "+ New Entry", fill='white', font=get_font(14))
    
    img.save(filepath)

def create_dark_professional_image(filepath: Path, width: int, height: int):
    """Create dark professional theme reference"""
    img = Image.new('RGB', (width, height), '#0D1117')
    draw = ImageDraw.Draw(img)
    
    # Dark header
    draw.rectangle([0, 0, width, 80], fill='#161B22')
    draw.text((20, 30), "Professional Dark", fill='#F0F6FC', font=get_font(24))
    
    # Dark cards with neon accents
    card_positions = [(50, 120), (300, 120), (550, 120)]
    accent_colors = ['#00D9FF', '#00FF88', '#FF0080']
    
    for i, (x, y) in enumerate(card_positions):
        # Dark card background
        draw.rectangle([x, y, x+190, y+120], fill='#21262D')
        # Neon accent border
        draw.rectangle([x, y, x+190, y+4], fill=accent_colors[i])
        
        draw.text((x+20, y+20), f"Revenue", fill='#F0F6FC', font=get_font(16))
        draw.text((x+20, y+50), "$285K", fill=accent_colors[i], font=get_font(32))
        draw.text((x+20, y+85), "↑15% month", fill='#7D8590', font=get_font(12))
    
    # Neon buttons
    draw.rectangle([50, 280, 200, 320], fill='#00D9FF')
    draw.text((70, 295), "EXECUTE", fill='#0D1117', font=get_font(14))
    
    img.save(filepath)

def create_earth_tones_image(filepath: Path, width: int, height: int):
    """Create warm earth tones design reference"""
    img = Image.new('RGB', (width, height), '#F5F1EB')
    draw = ImageDraw.Draw(img)
    
    # Warm header
    draw.rectangle([0, 0, width, 80], fill='#8B4513')
    draw.text((20, 30), "Earth Dashboard", fill='#F5F1EB', font=get_font(24))
    
    # Earth tone cards
    card_colors = ['#DEB887', '#CD853F', '#A0522D']
    card_positions = [(50, 120), (300, 120), (550, 120)]
    
    for i, (x, y) in enumerate(card_positions):
        draw.rectangle([x, y, x+190, y+120], fill=card_colors[i])
        draw.text((x+20, y+20), f"Loads", fill='#3E2723', font=get_font(16))
        draw.text((x+20, y+50), "1,247", fill='#3E2723', font=get_font(32))
        draw.text((x+20, y+85), "organic growth", fill='#5D4037', font=get_font(12))
    
    # Natural buttons
    draw.rectangle([50, 280, 200, 320], fill='#8FBC8F')
    draw.text((70, 295), "Grow Business", fill='#2E7D32', font=get_font(14))
    
    img.save(filepath)

def create_corporate_blue_image(filepath: Path, width: int, height: int):
    """Create traditional corporate blue theme reference"""
    img = Image.new('RGB', (width, height), '#F8F9FA')
    draw = ImageDraw.Draw(img)
    
    # Corporate header
    draw.rectangle([0, 0, width, 80], fill='#003366')
    draw.text((20, 30), "Corporate Suite", fill='white', font=get_font(24))
    
    # Traditional blue cards
    card_positions = [(50, 120), (300, 120), (550, 120)]
    
    for i, (x, y) in enumerate(card_positions):
        draw.rectangle([x, y, x+190, y+120], fill='white')
        draw.rectangle([x, y, x+190, y+4], fill='#0066CC')  # Blue accent
        
        draw.text((x+20, y+20), f"KPI {i+1}", fill='#333333', font=get_font(16))
        draw.text((x+20, y+50), "89", fill='#0066CC', font=get_font(32))
        draw.text((x+20, y+85), "Target: 100", fill='#666666', font=get_font(12))
    
    # Corporate buttons
    draw.rectangle([50, 280, 200, 320], fill='#0066CC')
    draw.text((70, 295), "Generate Report", fill='white', font=get_font(14))
    
    draw.rectangle([220, 280, 370, 320], fill='#E6E6E6')
    draw.text((240, 295), "Export Data", fill='#333333', font=get_font(14))
    
    img.save(filepath)

def get_font(size: int):
    """Get font for text rendering"""
    try:
        # Try to use a system font
        return ImageFont.truetype("arial.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
        except:
            # Fallback to default font
            return ImageFont.load_default()

if __name__ == "__main__":
    create_reference_images()
