# API Keys Setup Guide

This guide explains how to securely configure API keys for the Requirements Generation System.

## 🚀 Quick Setup

### Option 1: Interactive Setup (Recommended)
```bash
cd Requirements_Generation_System
python setup_api_keys.py
```

### Option 2: Manual Setup
1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and add your API keys
3. Run the system: `python orchestrator.py`

## 🔑 Getting API Keys

### OpenAI
1. Visit: https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key and add to `.env`: `OPENAI_API_KEY=your_key_here`

### Anthropic (Claude)
1. Visit: https://console.anthropic.com/
2. Sign in to your Anthropic account
3. Go to "API Keys" section
4. Create a new key
5. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

### Google (Gemini)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create an API key
4. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

### Azure OpenAI
1. Set up Azure OpenAI resource in Azure Portal
2. Get your API key and endpoint
3. Add to `.env`:
   ```
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## 📁 File Structure

```
Requirements_Generation_System/
├── .env                 # Your API keys (DO NOT COMMIT)
├── .env.example         # Template file (safe to commit)
├── setup_api_keys.py    # Interactive setup script
└── orchestrator.py      # Main application
```

## 🔒 Security Best Practices

### ✅ DO:
- Keep your `.env` file private (it's in `.gitignore`)
- Use different API keys for different environments
- Rotate your API keys regularly
- Set spending limits on your API accounts

### ❌ DON'T:
- Commit API keys to version control
- Share API keys in chat/email
- Use production keys for development
- Store keys in code files

## 🛠️ Configuration Options

### Basic Configuration
```bash
# Required: At least one API key
OPENAI_API_KEY=your_openai_key_here

# Optional: Default provider
DEFAULT_MODEL_PROVIDER=openai
```

### Advanced Configuration
```bash
# Custom API endpoints
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Timeout and retry settings
API_TIMEOUT=60
MAX_RETRIES=3
```

## 🚨 Troubleshooting

### "Missing API key" Error
```
❌ OPENAI_API_KEY not found in environment variables
```

**Solutions:**
1. Check your `.env` file exists and has the correct key
2. Restart your terminal/IDE after adding keys
3. Run the setup script: `python setup_api_keys.py`

### "Invalid API key" Error
```
❌ Error: Incorrect API key provided
```

**Solutions:**
1. Verify the API key is correct (copy-paste from provider)
2. Check for extra spaces or characters
3. Ensure the key hasn't expired
4. Verify account has sufficient credits

### "Permission denied" Error
```
❌ Error: You don't have access to this model
```

**Solutions:**
1. Check your account tier/subscription
2. Verify the model name is correct
3. Some models require special access approval

## 🔄 Switching Providers

You can use different providers for different runs:

```bash
# Use OpenAI (default)
python orchestrator.py --model openai

# Use Anthropic
python orchestrator.py --model anthropic

# Use Google Gemini
python orchestrator.py --model google

# Use Azure OpenAI
python orchestrator.py --model azure
```

## 💰 Cost Management

### Estimated Costs (per document):
- **OpenAI GPT-4**: ~$0.50-2.00
- **Anthropic Claude**: ~$0.30-1.50
- **Google Gemini**: ~$0.20-1.00

### Cost Optimization Tips:
1. Use cheaper models for initial drafts
2. Set API spending limits
3. Monitor usage in provider dashboards
4. Use `--skip-existing` to avoid regenerating documents

## 🔧 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic API key | `sk-ant-...` |
| `GOOGLE_API_KEY` | For Google | Google API key | `AIza...` |
| `AZURE_OPENAI_API_KEY` | For Azure | Azure OpenAI key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | For Azure | Azure endpoint | `https://...` |
| `DEFAULT_MODEL_PROVIDER` | No | Default provider | `openai` |
| `API_TIMEOUT` | No | Request timeout | `60` |
| `MAX_RETRIES` | No | Max retry attempts | `3` |

## 📞 Support

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Verify your API keys** are correct and active
3. **Check provider status** pages for outages
4. **Review account limits** and billing status

### Provider Status Pages:
- OpenAI: https://status.openai.com/
- Anthropic: https://status.anthropic.com/
- Google: https://status.cloud.google.com/

## 🔄 Updating Configuration

To update your configuration:

1. **Edit `.env` file** directly, or
2. **Run setup again**: `python setup_api_keys.py`
3. **Restart the application** to load new settings

The system will automatically detect changes and use the new configuration.
