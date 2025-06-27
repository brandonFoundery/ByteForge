# Dual-LLM Review System

## Overview

The Requirements Generation System now includes a dual-LLM architecture with:
- **Primary LLM** (default: OpenAI o3-mini) - for initial document generation
- **Reviewer LLM** (default: Google Gemini 2.5 Pro) - for document review and improvement

## How It Works

### Document Generation Workflow

1. **Generation**: Primary LLM generates the initial document
2. **Refinement**: Primary LLM refines the document (multiple rounds)
3. **Validation**: System validates document structure and content
4. **Review**: Reviewer LLM reviews and improves the document
5. **Final Save**: Improved document is saved

### Review Process

The reviewer LLM receives:
- The original document content
- All context that was provided to the primary LLM
- Specific instructions to preserve structure and IDs
- Guidelines to focus on accuracy and completeness

The reviewer is instructed to:
- ✅ **PRESERVE** document structure, format, and traceability IDs
- ✅ **PRESERVE** all references to upstream documents
- ✅ **MAINTAIN** the same level of detail (no shortening)
- ✅ **CORRECT** technical inaccuracies or inconsistencies
- ✅ **ADD** missing technical details based on context
- ✅ **IMPROVE** clarity and specificity
- ❌ **DO NOT** change language style or tone significantly
- ❌ **DO NOT** summarize or skip content sections

## Configuration

### config.yaml

```yaml
# Dual-LLM Review System Configuration
review_system:
  # Enable dual-LLM review system
  enabled: true
  
  # Primary LLM configuration (for initial document generation)
  primary_llm:
    provider: "openai"
    model: "o3-mini"
    temperature: 0.7
    max_tokens: 4000
    
  # Reviewer LLM configuration (for document review and improvement)
  reviewer_llm:
    provider: "gemini"
    model: "gemini-2.5-pro-preview-06-05"
    temperature: 0.5  # Lower temperature for more consistent reviews
    max_tokens: 8192  # Higher token limit for comprehensive reviews
    
  # Review process settings
  review_settings:
    # Enable review step after validation
    auto_review: true
    
    # Maximum number of review iterations
    max_review_iterations: 1
    
    # Skip review for certain document types (if needed)
    skip_review_for: []
    
    # Review prompt customization
    preserve_structure: true
    preserve_length: true
    focus_on_accuracy: true
    add_missing_details: true
```

### Environment Variables

Add to your `.env` file:

```bash
# Primary LLM (OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Reviewer LLM (Google Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Anthropic (if using as primary or reviewer)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

### Command Line Options

```bash
# Run with dual-LLM system (default)
python orchestrator.py

# Disable review system
python orchestrator.py --no-review

# Use different primary LLM
python orchestrator.py --model anthropic

# Custom configuration
python orchestrator.py --config custom_config.yaml
```

### Programmatic Usage

```python
from orchestrator import RequirementsOrchestrator

# Create orchestrator with dual-LLM system
orchestrator = RequirementsOrchestrator(
    project_name="My Project",
    base_path=Path("/path/to/project"),
    config_path=Path("config.yaml"),
    model_provider="openai"
)

# Check if review system is enabled
if orchestrator.review_config.get('enabled', False):
    print("Review system is enabled")
    
# Run generation with review
await orchestrator.run()
```

## Status Reporting

The status report now includes review information:

- **Reviewed**: Number of times document was reviewed
- **LLMs Used**: Shows both primary and reviewer LLMs used
- **Errors**: Includes both validation and review errors

## Testing

Test the dual-LLM system:

```bash
cd Requirements_Generation_System
python test_dual_llm.py
```

## Benefits

1. **Quality Improvement**: Second LLM catches errors and adds missing details
2. **Consistency**: Different LLM perspectives improve overall quality
3. **Accuracy**: Reviewer focuses specifically on technical accuracy
4. **Completeness**: Ensures all necessary information is included
5. **Flexibility**: Can use different LLM strengths (e.g., OpenAI for generation, Gemini for review)

## Troubleshooting

### Review System Not Working

1. **Check API Keys**: Ensure both OPENAI_API_KEY and GOOGLE_API_KEY are set
2. **Check Configuration**: Verify `review_system.enabled: true` in config.yaml
3. **Check Logs**: Look for error messages in the console output

### Review Taking Too Long

1. **Reduce max_tokens**: Lower the `reviewer_llm.max_tokens` setting
2. **Skip Large Documents**: Add document types to `skip_review_for` list
3. **Disable for Testing**: Use `--no-review` flag

### API Rate Limits

1. **Add Delays**: The system includes automatic retry logic
2. **Use Different Models**: Switch to models with higher rate limits
3. **Batch Processing**: Process documents in smaller batches

## Future Enhancements

- Support for more LLM providers
- Configurable review prompts per document type
- Multi-round review iterations
- Review quality scoring
- Parallel review processing
