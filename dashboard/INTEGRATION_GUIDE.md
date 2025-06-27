# Integration Guide: Monitoring Real Requirements Generation

This guide explains how to integrate the dashboard with the actual requirements generation process for FY.WB.Midway.

## Overview

The dashboard is designed to monitor the requirements generation process by reading status files and logs produced by the orchestrator. To use it with the real requirements generation process, you need to:

1. Configure the orchestrator to write status files in the expected format
2. Point the dashboard to the correct directories
3. Run both the orchestrator and dashboard simultaneously

## Step 1: Configure the Orchestrator

The `orchestrator.py` script in the Requirements_Generation_System needs to write status files as it generates documents. Add the following code to the orchestrator:

```python
# In Requirements_Generation_System/orchestrator.py

def write_status_file(document_id, status, metadata=None):
    """Write status file for a document"""
    status_dir = Path(config['paths']['status_dir'])
    status_dir.mkdir(parents=True, exist_ok=True)
    
    status_file = status_dir / f"status_{document_id}.json"
    
    # Default metadata
    data = {
        "id": document_id,
        "title": f"{document_id} Document",
        "status": status,
        "file_size": 0,
        "refined_count": 0,
        "generated_at": datetime.now().isoformat(),
        "dependencies": []
    }
    
    # Update with provided metadata
    if metadata:
        data.update(metadata)
    
    # Write to file
    with open(status_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Status file updated: {status_file}")
```

Then call this function at key points in the generation process:

```python
# When starting generation of a document
write_status_file(doc_id, "in_progress", {
    "title": doc_title,
    "dependencies": dependencies
})

# When document is generated
write_status_file(doc_id, "generated", {
    "file_size": doc_file.stat().st_size,
    "generated_at": datetime.now().isoformat()
})

# When refining a document
write_status_file(doc_id, "refining", {
    "refined_count": refinement_count,
    "file_size": doc_file.stat().st_size
})

# When document is validated
write_status_file(doc_id, "validated", {
    "refined_count": refinement_count,
    "file_size": doc_file.stat().st_size
})

# If generation fails
write_status_file(doc_id, "failed", {
    "error_message": str(error)
})
```

## Step 2: Configure Logging

Ensure the orchestrator writes logs to a file that the dashboard can read:

```python
# In Requirements_Generation_System/orchestrator.py

import logging

def setup_logging():
    """Set up logging to file and console"""
    log_dir = Path(config['paths']['status_dir'])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "orchestrator.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger()

# Use the logger
logger = setup_logging()
logger.info("Starting requirements generation process")
```

## Step 3: Update Configuration

Update the `config.yaml` file to include the status directory:

```yaml
# In Requirements_Generation_System/config.yaml

paths:
  # Source requirements directory
  requirements_dir: "d:/Repository/@Clients/FY.WB.Midway/Requirements"
  
  # Prompt templates directory
  prompts_dir: "d:/Repository/@Clients/FY.WB.Midway/Requirements_Generation_Prompts"
  
  # Output directory for generated documents
  output_dir: "d:/Repository/@Clients/FY.WB.Midway/generated_documents"
  
  # Status tracking directory
  status_dir: "d:/Repository/@Clients/FY.WB.Midway/generation_status"
```

## Step 4: Run the Dashboard with Real Data

1. **Start the orchestrator**:
   ```bash
   cd Requirements_Generation_System
   python orchestrator.py --config config.yaml
   ```

2. **Start the dashboard backend**:
   ```bash
   python dashboard/run_simple.py
   ```

3. **Open the dashboard**:
   ```bash
   python dashboard/open_dashboard.py
   ```

## Customizing the Dashboard

You can customize the dashboard to match your specific requirements:

### Changing Directories

If your status files and documents are in different locations, update the paths in `run_simple.py`:

```python
# Default paths
OUTPUT_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
STATUS_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generation_status")
```

### Customizing Document Types

If you have different document types than the default ones, update the `simple_dashboard.html` file:

```javascript
// Sort documents by ID
const sortedDocuments = Object.values(documents).sort((a, b) => {
    const typeA = a.id.split('-')[0];
    const typeB = b.id.split('-')[0];
    if (typeA !== typeB) return typeA.localeCompare(typeB);
    
    const numA = parseInt(a.id.split('-')[1] || '0');
    const numB = parseInt(b.id.split('-')[1] || '0');
    return numA - numB;
});
```

## Troubleshooting

### Dashboard Shows No Data

1. Check that the status files are being written to the correct directory
2. Verify the format of the status files (should be JSON)
3. Check that the orchestrator log file is being written
4. Use the `test_api.py` script to test the API endpoints

### Dashboard Cannot Connect to Backend

1. Ensure the backend server is running
2. Check that the port (8001) is not being used by another application
3. Verify that the API endpoints are accessible in a browser

## Example Status File Format

```json
{
  "id": "BRD",
  "title": "Business Requirements Document",
  "status": "validated",
  "file_size": 15240,
  "refined_count": 3,
  "generated_at": "2025-06-10T20:30:00",
  "elapsed_time": 120.5,
  "dependencies": []
}