@echo off
REM ============================================================================
REM Review Existing Documents with Dual-LLM System
REM ============================================================================
REM This script runs the reviewer LLM on existing documents without regenerating them
REM ============================================================================

title FY.WB.Midway Document Review System

echo.
echo ========================================================================
echo  FY.WB.Midway Document Review System
echo ========================================================================
echo.
echo  This will review existing documents using the Reviewer LLM
echo  (Gemini) to improve quality and generate validation questions.
echo.
echo  No documents will be regenerated - only reviewed and enhanced.
echo.

REM Check if we're in the correct directory
if not exist "orchestrator.py" (
    echo [ERROR] orchestrator.py not found!
    echo.
    echo Please ensure you're running this script from the Requirements_Generation_System directory.
    echo Expected file: orchestrator.py
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python and ensure it's added to your system PATH.
    echo Download from: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check for existing documents
if not exist "../generated_documents" (
    echo [ERROR] No generated_documents directory found!
    echo.
    echo Please run the main generation process first to create documents.
    echo Use: python orchestrator.py
    echo.
    pause
    exit /b 1
)

echo [INFO] Checking for existing documents to review...
echo.

REM Check for API keys
if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] OPENAI_API_KEY environment variable not set.
    echo This may be needed for the primary LLM operations.
    echo.
)

if "%GOOGLE_API_KEY%"=="" (
    echo [ERROR] GOOGLE_API_KEY environment variable not set!
    echo.
    echo The review system requires Google API key for Gemini.
    echo Please set GOOGLE_API_KEY in your environment or .env file.
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting document review process...
echo.
echo ========================================================================
echo  Review Process Starting
echo ========================================================================
echo.
echo  Primary LLM: OpenAI (for context)
echo  Reviewer LLM: Google Gemini (for review and validation)
echo.
echo  Process:
echo  1. Load existing documents
echo  2. Review each document with Gemini
echo  3. Generate enhanced versions
echo  4. Create validation questions
echo  5. Save improved documents
echo.
echo ========================================================================
echo.

REM Run the review-only mode
python orchestrator.py --review-only

REM Check the exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Review process failed!
    echo.
    echo Common issues:
    echo - Missing API keys (GOOGLE_API_KEY required)
    echo - No existing documents to review
    echo - Network connectivity issues
    echo - Invalid document format
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo  Review Process Complete
echo ========================================================================
echo.
echo The document review process has completed successfully.
echo.
echo Enhanced documents have been saved to: ../generated_documents/
echo.
echo Next steps:
echo 1. Review the enhanced documents
echo 2. Check the generated validation questions
echo 3. Present questions to stakeholders for answers
echo 4. Integrate answers back into requirements
echo.
echo To view the enhanced documents:
echo - Open the generated_documents folder
echo - Check the status report for review summary
echo - Use the documentation viewer: start_docs_viewer.bat
echo.
pause
