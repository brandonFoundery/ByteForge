#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "     Lead Processing App Restart"
echo "========================================="
echo ""

print_status "Project directory: $PROJECT_DIR"
print_status "Stopping any existing LeadProcessing processes..."

# Kill existing processes
if command -v pgrep > /dev/null; then
    # Use pgrep if available (Linux/macOS)
    PIDS=$(pgrep -f "LeadProcessing" || true)
    if [ ! -z "$PIDS" ]; then
        print_warning "Found running processes: $PIDS"
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        sleep 2
        
        # Check if processes are still running
        REMAINING=$(pgrep -f "LeadProcessing" || true)
        if [ ! -z "$REMAINING" ]; then
            print_error "Some processes are still running: $REMAINING"
            echo "$REMAINING" | xargs kill -KILL 2>/dev/null || true
        else
            print_success "All LeadProcessing processes stopped"
        fi
    else
        print_status "No running LeadProcessing processes found"
    fi
else
    # Fallback for systems without pgrep
    print_warning "pgrep not available, using alternative method"
    pkill -f "LeadProcessing" 2>/dev/null || true
    sleep 2
fi

# Kill any dotnet processes running our application
print_status "Checking for dotnet processes..."
if command -v pgrep > /dev/null; then
    DOTNET_PIDS=$(pgrep -f "dotnet.*LeadProcessing" || true)
    if [ ! -z "$DOTNET_PIDS" ]; then
        print_warning "Found dotnet processes: $DOTNET_PIDS"
        echo "$DOTNET_PIDS" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
fi

# Check for processes using the default ports
print_status "Checking for processes using ports 5000, 7001..."
for port in 5000 7001; do
    if command -v lsof > /dev/null; then
        PID=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PID" ]; then
            print_warning "Process $PID is using port $port, killing it..."
            kill -9 $PID 2>/dev/null || true
        fi
    elif command -v netstat > /dev/null; then
        # Alternative method using netstat (Windows/some Linux)
        PID=$(netstat -ano | grep ":$port " | awk '{print $5}' | head -1 || true)
        if [ ! -z "$PID" ] && [ "$PID" != "0" ]; then
            print_warning "Process $PID is using port $port, killing it..."
            kill -9 $PID 2>/dev/null || true
        fi
    fi
done

print_success "Process cleanup completed"
echo ""

# Change to project directory
cd "$PROJECT_DIR" || {
    print_error "Failed to change to project directory: $PROJECT_DIR"
    exit 1
}

# Build the application
print_status "Building the application..."
if dotnet build --configuration Debug --verbosity minimal; then
    print_success "Build completed successfully"
else
    print_error "Build failed!"
    exit 1
fi

echo ""

# Update database
print_status "Updating database..."
if dotnet ef database update --verbosity minimal; then
    print_success "Database updated successfully"
else
    print_warning "Database update failed or no migrations needed"
fi

echo ""

# Start the application
print_status "Starting the application..."
print_status "The application will be available at:"
print_status "  - HTTP:  http://localhost:5000"
print_status "  - HTTPS: https://localhost:7001"
print_status "  - Hangfire Dashboard: https://localhost:7001/hangfire"
print_status ""
print_status "Press Ctrl+C to stop the application"
print_status "Starting in 3 seconds..."

sleep 3

# Start the application
exec dotnet run --configuration Debug