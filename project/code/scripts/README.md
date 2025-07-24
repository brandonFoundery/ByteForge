# Scripts Directory

This directory contains utility scripts for managing the Lead Processing application.

## Available Scripts

### Application Management

#### `restart-app.sh` / `restart-app.bat`
**Purpose**: Stops any running instances of the application and starts a fresh instance.

**Features**:
- Kills existing LeadProcessing processes
- Frees up ports 5000 and 7001
- Builds the application
- Updates the database
- Starts the application in development mode

**Usage**:
```bash
# Linux/macOS
./scripts/restart-app.sh

# Windows
scripts\restart-app.bat
```

**Endpoints after startup**:
- HTTP: http://localhost:5000
- HTTPS: https://localhost:7001
- Hangfire Dashboard: https://localhost:7001/hangfire

### Testing

#### `run-tests.sh` / `run-tests.bat`
**Purpose**: Comprehensive test runner with detailed results and options.

**Features**:
- Colored output for better readability
- Test result summaries with statistics
- Code coverage collection
- Test filtering capabilities
- Failed test details
- Pass rate calculation

**Usage**:
```bash
# Linux/macOS
./scripts/run-tests.sh [OPTIONS]

# Windows
scripts\run-tests.bat [OPTIONS]
```

**Options**:
- `-v, --verbose`: Enable verbose output
- `-c, --coverage`: Collect code coverage
- `-f, --filter`: Filter tests (e.g., 'Category=Unit' or 'Name~Lead')
- `--release`: Use Release configuration
- `-h, --help`: Show help message

**Examples**:
```bash
# Run all tests
./scripts/run-tests.sh

# Run tests with verbose output
./scripts/run-tests.sh -v

# Run tests with coverage
./scripts/run-tests.sh -c

# Run only unit tests
./scripts/run-tests.sh -f "Category=Unit"

# Run tests with 'Lead' in the name
./scripts/run-tests.sh -f "Name~Lead"
```

#### `quick-test.sh` / `quick-test.bat`
**Purpose**: Fast test execution with minimal output - perfect for quick validation.

**Features**:
- Runs all tests quietly
- Shows only pass/fail status
- Fast execution for CI/CD pipelines

**Usage**:
```bash
# Linux/macOS
./scripts/quick-test.sh

# Windows
scripts\quick-test.bat
```

### Build Management

#### `clean-build.sh` / `clean-build.bat`
**Purpose**: Clean and rebuild the entire solution from scratch.

**Features**:
- Cleans previous build artifacts
- Restores NuGet packages
- Rebuilds the solution
- Ensures a fresh build state

**Usage**:
```bash
# Linux/macOS
./scripts/clean-build.sh

# Windows
scripts\clean-build.bat
```

## Script Features

### Cross-Platform Support
- **Linux/macOS**: Use `.sh` scripts
- **Windows**: Use `.bat` scripts
- Identical functionality across platforms

### Color-Coded Output
- 🔵 **Blue**: Informational messages
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warning messages
- 🔴 **Red**: Error messages
- 🟣 **Magenta**: Headers and sections
- 🟦 **Cyan**: Section dividers

### Error Handling
- Proper exit codes for CI/CD integration
- Graceful error handling and reporting
- Cleanup of temporary files
- Process cleanup and port management

### Test Result Formatting
The test runner provides a comprehensive summary including:
- Total, passed, failed, and skipped test counts
- Execution time
- Pass rate percentage
- Failed test details
- Code coverage reports (when enabled)

### Example Output
```
========================================
     Lead Processing Test Runner
========================================

>>> Building solution
✓ Build completed successfully

>>> Running tests
[12:34:56] Starting test execution...

>>> Test Results Summary
┌─────────────────────────────────────┐
│           TEST SUMMARY              │
├─────────────────────────────────────┤
│ Total Tests:               42       │
│ Passed:                    42       │
│ Failed:                     0       │
│ Skipped:                    0       │
│ Execution Time:         2.34s       │
└─────────────────────────────────────┘

🎉 All tests passed! (100%)
🚀 Ready for deployment!
```

## Integration with Development Workflow

### Recommended Usage
1. **Development**: `./scripts/restart-app.sh` to start fresh
2. **Quick Check**: `./scripts/quick-test.sh` for fast validation
3. **Full Testing**: `./scripts/run-tests.sh -v` for detailed results
4. **Coverage**: `./scripts/run-tests.sh -c` before commits
5. **Clean State**: `./scripts/clean-build.sh` when needed

### CI/CD Integration
All scripts return proper exit codes:
- `0`: Success
- `1`: Failure

Perfect for use in automated pipelines and build systems.