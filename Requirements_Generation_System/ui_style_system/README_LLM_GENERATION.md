# LLM UI Generation System

A powerful system that leverages multiple AI models to generate **45 unique dashboard designs** for the FY.WB.Midway freight brokerage application.

## 🎯 Overview

This system creates a **complete design matrix** by sending each of 5 LLM models prompts with each of 9 different UI style reference images. This results in **45 total unique designs** (9 styles × 5 models = 45 combinations).

### Supported Models (5 Total)
- **OpenAI GPT-4o** - Latest multimodal model
- **OpenAI GPT-4.1** - Enhanced reasoning capabilities
- **OpenAI o3** - Advanced problem-solving model
- **Google Gemini 2.5** - Google's flagship multimodal AI
- **Anthropic Claude 4** - Anthropic's most capable model

### Reference Styles (9 Total)
Each model interprets all 9 reference style images, creating unique variations:
- **ui_style_1.png** through **ui_style_9.png**
- Covers diverse design approaches: Material, Gradient, Dark, Earth tones, Corporate, etc.

## 🚀 Features

- **45 Unique Designs** - Complete matrix of 9 styles × 5 models = 45 total designs
- **Parallel Generation** - All 45 combinations generate simultaneously for maximum speed
- **Live Updating Interface** - Opens immediately with placeholders, updates as designs complete
- **Real-Time Progress** - See exactly which designs are generating, completed, or failed
- **Model-Based Tabs** - Organized interface with tabs for each AI model:
  - **OpenAI GPT-4o Tab** - Shows all 9 designs from this model
  - **OpenAI GPT-4.1 Tab** - Shows all 9 designs from this model
  - **OpenAI o3 Tab** - Shows all 9 designs from this model
  - **Google Gemini 2.5 Tab** - Shows all 9 designs from this model
  - **Anthropic Claude 4 Tab** - Shows all 9 designs from this model
- **Visual References** - Each model interprets all 9 different style reference images
- **Auto-Browser Launch** - Live page opens immediately, no waiting for completion
- **Error Handling** - Graceful handling of API failures with clear status indicators

## 📋 Prerequisites

### Required Python Packages
```bash
pip install Pillow rich openai google-generativeai anthropic
```

### API Keys (Environment Variables)
```bash
# Required for full functionality
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here  
ANTHROPIC_API_KEY=your_anthropic_key_here
```

**Note:** The system will run with partial API keys, but some models will fail to generate.

## 🎮 Usage

### Quick Start (Windows)
```bash
# Double-click the batch file
run_llm_ui_generation.bat
```

### Manual Execution
```bash
# Navigate to the ui_style_system directory
cd Requirements_Generation_System/ui_style_system

# Run the orchestrator
python run_llm_ui_generation.py
```

## 📁 File Structure

```
ui_style_system/
├── run_llm_ui_generation.py      # Main orchestrator
├── llm_ui_generator.py           # Core LLM generation logic
├── llm_comparison_viewer.py      # Comparison page creator
├── create_reference_images.py    # Reference image generator
├── run_llm_ui_generation.bat     # Windows batch launcher
├── README_LLM_GENERATION.md      # This file
├── llm_generated/                # Generated HTML files
│   ├── gpt-4o_dashboard.html
│   ├── gpt-4.1-preview_dashboard.html
│   ├── o3-mini_dashboard.html
│   ├── gemini-2.0-flash-exp_dashboard.html
│   └── claude-3-5-sonnet_dashboard.html
├── llm_comparison.html           # Comparison viewer page
└── llm_generation_results.json   # Generation metadata
```

## 🔄 Process Flow

1. **Reference Images** - Creates 5 unique UI style reference images
2. **API Key Check** - Validates available API keys
3. **Parallel Generation** - Sends prompts to all LLM models simultaneously
4. **Result Compilation** - Waits for all generations to complete
5. **Comparison Page** - Creates comprehensive comparison viewer
6. **Browser Launch** - Automatically opens results

## 📊 Comparison Viewer Features

### Overview Tab
- Model cards showing success/failure status
- Style descriptions and provider information
- Quick access to individual designs

### Side-by-Side Tab
- Compare designs two at a time
- Easy visual comparison of different approaches

### Individual Views Tab
- Full-screen view of each generated design
- Detailed model information
- Fullscreen launch buttons

### Analysis Tab
- Generation statistics and performance metrics
- Model success rates
- Timing information

## 🛠️ Customization

### Adding New Models
Edit `llm_ui_generator.py` and add to the `llm_models` list:

```python
{
    "name": "New Model Name",
    "id": "model-api-id", 
    "provider": "provider_name",
    "style_image": "ui_style_6.png",
    "style_description": "Your style description"
}
```

### Creating New Reference Images
Add new image generation functions to `create_reference_images.py`:

```python
def create_new_style_image(filepath: Path, width: int, height: int):
    # Your image generation code here
    pass
```

## 🔧 Troubleshooting

### Common Issues

**Missing Dependencies**
```bash
pip install Pillow rich openai google-generativeai anthropic
```

**API Key Errors**
- Ensure environment variables are set correctly
- Check API key validity and quotas
- Some models may fail while others succeed

**Generation Failures**
- Check internet connection
- Verify API quotas and limits
- Review console output for specific error messages

## 📈 Expected Results

Each model should generate a unique dashboard design featuring:
- **Header** with company branding
- **Welcome section** with personalized greeting  
- **Stats cards** showing key freight metrics
- **Quick action buttons** for common tasks
- **Recent activity feed** with freight updates

The designs will vary significantly in:
- Color schemes and palettes
- Typography choices
- Layout approaches
- Visual hierarchy
- Interactive elements

## 🎨 Style Inspirations

1. **Material Design** - Clean cards, subtle shadows, Google-inspired
2. **Vibrant Gradient** - Bold colors, modern gradients, energetic
3. **Dark Professional** - Dark theme, neon accents, futuristic
4. **Earth Tones** - Warm colors, organic feel, natural
5. **Corporate Blue** - Traditional business, conservative, professional

---

**Happy UI Generation!** 🎨✨
