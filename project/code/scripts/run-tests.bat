@echo off
setlocal enabledelayedexpansion

REM Colors for Windows
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "NC=[0m"

REM Default values
set "VERBOSE=false"
set "COVERAGE=false"
set "FILTER="
set "CONFIG=Debug"

REM Parse command line arguments
:parse_args
if "%1"=="" goto args_done
if "%1"=="-v" (
    set "VERBOSE=true"
    shift
    goto parse_args
)
if "%1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto parse_args
)
if "%1"=="-c" (
    set "COVERAGE=true"
    shift
    goto parse_args
)
if "%1"=="--coverage" (
    set "COVERAGE=true"
    shift
    goto parse_args
)
if "%1"=="-f" (
    set "FILTER=%2"
    shift
    shift
    goto parse_args
)
if "%1"=="--filter" (
    set "FILTER=%2"
    shift
    shift
    goto parse_args
)
if "%1"=="--release" (
    set "CONFIG=Release"
    shift
    goto parse_args
)
if "%1"=="-h" goto show_help
if "%1"=="--help" goto show_help

echo %RED%Unknown option: %1%NC%
goto show_help

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -v, --verbose     Enable verbose output
echo   -c, --coverage    Collect code coverage
echo   -f, --filter      Filter tests (e.g., 'Category=Unit')
echo   --release         Use Release configuration
echo   -h, --help        Show this help message
echo.
echo Examples:
echo   %0                    # Run all tests
echo   %0 -v                 # Run tests with verbose output
echo   %0 -c                 # Run tests with coverage
echo   %0 -f "Name~Lead"     # Run tests with 'Lead' in the name
exit /b 0

:args_done

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

echo %MAGENTA%========================================%NC%
echo %MAGENTA%     Lead Processing Test Runner%NC%
echo %MAGENTA%========================================%NC%
echo.

echo %BLUE%[%time%]%NC% Project directory: %PROJECT_DIR%
echo %BLUE%[%time%]%NC% Test execution started at: %date% %time%
echo.

REM Change to project directory
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo %RED%✗%NC% Failed to change to project directory: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Clean previous test results
echo %CYAN%^>^>^> Cleaning previous test results%NC%
if exist TestResults rmdir /s /q TestResults >nul 2>&1
if exist LeadProcessing.Tests\TestResults rmdir /s /q LeadProcessing.Tests\TestResults >nul 2>&1
echo %GREEN%✓%NC% Test results cleaned

REM Build the solution
echo.
echo %CYAN%^>^>^> Building solution%NC%
echo %BLUE%[%time%]%NC% Building in %CONFIG% configuration...
dotnet build --configuration %CONFIG% --verbosity minimal --no-restore
if errorlevel 1 (
    echo %RED%✗%NC% Build failed!
    pause
    exit /b 1
)
echo %GREEN%✓%NC% Build completed successfully

REM Restore packages
echo.
echo %CYAN%^>^>^> Restoring NuGet packages%NC%
dotnet restore --verbosity minimal
if errorlevel 1 (
    echo %YELLOW%⚠%NC% Package restore had issues
) else (
    echo %GREEN%✓%NC% Package restore completed
)

REM Prepare test command
set "TEST_CMD=dotnet test --configuration %CONFIG% --no-build --logger console;verbosity=normal"

if "%VERBOSE%"=="true" (
    set "TEST_CMD=!TEST_CMD! --verbosity normal"
) else (
    set "TEST_CMD=!TEST_CMD! --verbosity minimal"
)

if "%COVERAGE%"=="true" (
    set "TEST_CMD=!TEST_CMD! --collect:\"XPlat Code Coverage\" --results-directory ./TestResults"
)

if not "%FILTER%"=="" (
    set "TEST_CMD=!TEST_CMD! --filter \"%FILTER%\""
)

REM Run tests
echo.
echo %CYAN%^>^>^> Running tests%NC%
echo %BLUE%[%time%]%NC% Test command: !TEST_CMD!
echo %BLUE%[%time%]%NC% Starting test execution...
echo.

REM Create temporary file for output
set "TEMP_OUTPUT=%TEMP%\test_output_%RANDOM%.txt"

REM Execute tests and capture output
!TEST_CMD! > "%TEMP_OUTPUT%" 2>&1
set "TEST_EXIT_CODE=!errorlevel!"

REM Display the output
type "%TEMP_OUTPUT%"
echo.

REM Parse test results
echo %CYAN%^>^>^> Test Results Summary%NC%

REM Extract information from test output (simplified for Windows)
for /f "tokens=*" %%i in ('findstr /c:"Total tests:" "%TEMP_OUTPUT%" 2^>nul') do (
    for /f "tokens=3" %%j in ("%%i") do set "TOTAL_TESTS=%%j"
)
for /f "tokens=*" %%i in ('findstr /c:"Passed:" "%TEMP_OUTPUT%" 2^>nul') do (
    for /f "tokens=2" %%j in ("%%i") do set "PASSED_TESTS=%%j"
)
for /f "tokens=*" %%i in ('findstr /c:"Failed:" "%TEMP_OUTPUT%" 2^>nul') do (
    for /f "tokens=2" %%j in ("%%i") do set "FAILED_TESTS=%%j"
)
for /f "tokens=*" %%i in ('findstr /c:"Skipped:" "%TEMP_OUTPUT%" 2^>nul') do (
    for /f "tokens=2" %%j in ("%%i") do set "SKIPPED_TESTS=%%j"
)

REM Set defaults if not found
if not defined TOTAL_TESTS set "TOTAL_TESTS=0"
if not defined PASSED_TESTS set "PASSED_TESTS=0"
if not defined FAILED_TESTS set "FAILED_TESTS=0"
if not defined SKIPPED_TESTS set "SKIPPED_TESTS=0"

REM Display summary
echo %BLUE%┌─────────────────────────────────────┐%NC%
echo %BLUE%│           TEST SUMMARY              │%NC%
echo %BLUE%├─────────────────────────────────────┤%NC%
echo %BLUE%│%NC% Total Tests:     %GREEN%!TOTAL_TESTS!%NC%                 %BLUE%│%NC%
echo %BLUE%│%NC% Passed:         %GREEN%!PASSED_TESTS!%NC%                 %BLUE%│%NC%

if !FAILED_TESTS! gtr 0 (
    echo %BLUE%│%NC% Failed:         %RED%!FAILED_TESTS!%NC%                 %BLUE%│%NC%
) else (
    echo %BLUE%│%NC% Failed:         %GREEN%!FAILED_TESTS!%NC%                 %BLUE%│%NC%
)

if !SKIPPED_TESTS! gtr 0 (
    echo %BLUE%│%NC% Skipped:        %YELLOW%!SKIPPED_TESTS!%NC%                 %BLUE%│%NC%
) else (
    echo %BLUE%│%NC% Skipped:        %GREEN%!SKIPPED_TESTS!%NC%                 %BLUE%│%NC%
)

echo %BLUE%└─────────────────────────────────────┘%NC%

REM Show pass rate
if !TOTAL_TESTS! gtr 0 (
    set /a PASS_RATE=!PASSED_TESTS! * 100 / !TOTAL_TESTS!
    if !PASS_RATE! equ 100 (
        echo.
        echo %GREEN%🎉 All tests passed! (!PASS_RATE!%%)%NC%
    ) else if !PASS_RATE! geq 90 (
        echo.
        echo %YELLOW%😐 Most tests passed (!PASS_RATE!%%)%NC%
    ) else (
        echo.
        echo %RED%😞 Many tests failed (!PASS_RATE!%%)%NC%
    )
)

REM Show failed test details if any
if !FAILED_TESTS! gtr 0 (
    echo.
    echo %CYAN%^>^>^> Failed Test Details%NC%
    findstr /c:"Failed" "%TEMP_OUTPUT%" 2>nul || echo %CYAN%ℹ%NC% Failed test details not available in this format
)

REM Coverage report
if "%COVERAGE%"=="true" (
    echo.
    echo %CYAN%^>^>^> Code Coverage%NC%
    if exist TestResults (
        echo %GREEN%✓%NC% Coverage reports generated in TestResults directory
        for /r TestResults %%f in (coverage.cobertura.xml) do (
            if exist "%%f" (
                echo %CYAN%ℹ%NC% Coverage file: %%f
            )
        )
    ) else (
        echo %YELLOW%⚠%NC% TestResults directory not found
    )
)

REM Final status
echo.
echo %CYAN%^>^>^> Final Status%NC%
if !TEST_EXIT_CODE! equ 0 (
    echo %GREEN%✓%NC% Test execution completed successfully!
    if !FAILED_TESTS! equ 0 (
        echo %GREEN%🚀 Ready for deployment!%NC%
    )
) else (
    echo %RED%✗%NC% Test execution failed!
    echo %RED%🔥 Fix failing tests before deployment!%NC%
)

REM Cleanup
del "%TEMP_OUTPUT%" >nul 2>&1

echo %BLUE%[%time%]%NC% Test execution finished at: %date% %time%

if !TEST_EXIT_CODE! neq 0 pause
exit /b !TEST_EXIT_CODE!