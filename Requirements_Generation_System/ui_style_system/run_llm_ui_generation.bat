@echo off
echo.
echo ========================================
echo  LLM UI Generation System
echo ========================================
echo.
echo Generating unique dashboard designs using:
echo - OpenAI GPT-4o, GPT-4.1, o3
echo - Google Gemini 2.5  
echo - Anthropic Claude 4
echo.
echo Make sure you have set your API keys:
echo - OPENAI_API_KEY
echo - GOOGLE_API_KEY
echo - ANTHROPIC_API_KEY
echo.
pause

cd /d "%~dp0"
python run_llm_ui_generation.py

echo.
echo ========================================
echo Process Complete!
echo ========================================
pause
