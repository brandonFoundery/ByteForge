# FY.WB.Midway Requirements Generation System

An automated system for generating comprehensive, traceable requirements documentation for the FY.WB.Midway enterprise logistics and payment platform.

## 🚀 Overview

This system automates the creation of 10+ interconnected requirements documents with full bidirectional traceability. It uses LLMs (OpenAI or Anthropic) to generate documents based on existing project requirements while maintaining consistency and traceability throughout.

## 📋 Generated Documents

1. **BRD** - Business Requirements Document
2. **PRD** - Product Requirements Document  
3. **FRD** - Functional Requirements Document
4. **NFRD** - Non-Functional Requirements Document
5. **DRD** - Design Requirements Document
6. **DB_SCHEMA** - Database Schema Document
7. **TRD** - Technical Requirements Document
8. **API_SPEC** - API Specification (OpenAPI)
9. **TEST_PLAN** - Comprehensive Test Plan
10. **RTM** - Requirements Traceability Matrix

## 🛠️ Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   # For OpenAI
   set OPENAI_API_KEY=your-api-key-here
   
   # For Anthropic
   set ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Configure paths in `config.yaml`:**
   - Update `requirements_dir` to point to your source requirements
   - Update `prompts_dir` to point to the prompt templates
   - Update `output_dir` for generated documents

## 🚦 Quick Start

### Option 1: Interactive Mode
```bash
python run_generation.py
```

This provides an interactive menu with options to:
- Run full generation
- Resume from checkpoint
- Generate specific documents
- Validate existing documents
- Generate traceability reports

### Option 2: Direct Orchestrator
```bash
python orchestrator.py --config config.yaml
```

### Option 3: With Live Monitoring
```bash
# Terminal 1: Run the orchestrator
python orchestrator.py

# Terminal 2: Run the monitor
python monitor.py d:/Repository/@Clients/FY.WB.Midway/generated_documents
```

## 📊 Monitoring Progress

The system provides multiple ways to track progress:

### Real-time Monitor
```bash
python monitor.py [output_directory]
```

Features:
- Live status updates for each document
- Progress bars and completion percentage
- File size tracking
- Refinement count display
- Automatic completion detection

### Progress Visualization
The orchestrator automatically generates:
- `document_dependencies.png` - Dependency graph
- `generation_progress.png` - Real-time progress graph
- Status reports in the output directory

## 🔧 Utilities

### Traceability Analysis
```bash
# Analyze traceability relationships
python utils.py analyze [documents_path]

# Export traceability matrix (CSV)
python utils.py export [documents_path]

# Generate visual traceability graph
python utils.py graph [documents_path]
```

### Document Validation
```bash
# Validate a single document
python utils.py validate path/to/document.md
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

- **LLM Settings**: Provider, model, temperature, tokens
- **Generation Settings**: Refinement rounds, validation level
- **Document Types**: Enable/disable specific documents
- **Traceability**: ID formats, validation rules
- **Monitoring**: Refresh rates, notifications

### Key Configuration Options

```yaml
llm:
  provider: "openai"  # or "anthropic"
  temperature: 0.7
  max_tokens: 4000

generation:
  refinement_rounds: 3
  validation_level: "high"
  
monitoring:
  enabled: true
  refresh_rate: 2
```

## 📁 Project Structure

```
Requirements_Generation_System/
├── orchestrator.py      # Main generation engine
├── monitor.py          # Real-time progress monitor
├── utils.py            # Traceability analysis tools
├── run_generation.py   # Interactive runner
├── config.yaml         # Configuration file
├── requirements.txt    # Python dependencies
└── README.md          # This file

Requirements_Generation_Prompts/
├── 01_BRD.md          # Business Requirements template
├── 02_PRD.md          # Product Requirements template
├── 04_FRD.md          # Functional Requirements template
├── 05_NFRD.md         # Non-Functional Requirements template
├── 07_DRD.md          # Design Requirements template
├── 08_DB_Schema.md    # Database Schema template
├── 09_TRD.md          # Technical Requirements template
├── 10_API_OpenAPI.md  # API Specification template
├── 20_Test_Plan.md    # Test Plan template
├── 24_RTM.md          # Traceability Matrix template
└── README.md          # Prompt documentation
```

## 🔄 Generation Process

1. **Context Gathering**: Loads existing requirements from source directory
2. **Dependency Resolution**: Determines generation order using topological sort
3. **Document Generation**: 
   - Generates each document with LLM
   - Includes upstream documents as context
   - Maintains traceability IDs
4. **Refinement**: Iteratively improves each document (3 rounds default)
5. **Validation**: Checks structure, traceability, and completeness
6. **Visualization**: Updates progress graphs and status reports

## 📈 Traceability System

The system implements hierarchical traceability:

```
BRD-001
  └─> PRD-001
      └─> FRD-001.1
          └─> TRD-001.1.1
              └─> TC-001.1.1.1
```

Features:
- Automatic ID generation
- Bidirectional linking
- Reference validation
- Visual traceability graphs
- Exportable traceability matrix

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   set OPENAI_API_KEY=your-key-here
   ```

2. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **Path Not Found**
   - Check paths in `config.yaml`
   - Ensure source requirements exist

4. **Generation Failures**
   - Check `generation_status/` for error logs
   - Reduce `max_tokens` if hitting limits
   - Increase `timeout` for slow connections

### Debug Mode

Enable debug mode in `config.yaml`:
```yaml
advanced:
  debug: true
  verbose: true
```

## 📝 Example Usage

### Full Generation with Monitoring
```bash
# Terminal 1
python run_generation.py
# Select option 1 for full generation

# Terminal 2 (auto-launched if monitoring enabled)
# Shows real-time progress
```

### Generate Traceability Report
```bash
python run_generation.py
# Select option 5

# Or directly:
python utils.py analyze generated_documents/
python utils.py graph generated_documents/
```

### Validate Generated Documents
```bash
python utils.py validate generated_documents/BRD.md
```

## 🚀 Advanced Features

- **Parallel Processing**: Enable in config for faster generation
- **Caching**: Reduces API calls for repeated generations
- **Context Strategies**: Choose between full, sliding, or summary context
- **Custom Prompts**: Modify templates in `Requirements_Generation_Prompts/`

## 📞 Support

For issues or questions:
1. Check error logs in `generation_status/`
2. Enable debug mode for detailed logging
3. Review generated status reports
4. Validate document structure with utilities

## 🎯 Next Steps

After generation:
1. Review generated documents in output directory
2. Analyze traceability with `utils.py analyze`
3. Export traceability matrix for stakeholders
4. Use generated documents for development planning

---

**Note**: This system generates draft documents that should be reviewed and refined by domain experts before final use.