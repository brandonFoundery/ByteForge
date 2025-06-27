# Directory Structure for Requirements Generation

This document explains the directory structure and data flow for the FY.WB.Midway requirements generation process.

## Directory Overview

The requirements generation process uses the following directories:

| Directory | Path | Purpose |
|-----------|------|---------|
| **Input: Requirements** | `d:/Repository/@Clients/FY.WB.Midway/Requirements/` | Source requirements files |
| **Input: Prompts** | `d:/Repository/@Clients/FY.WB.Midway/Requirements_Generation_Prompts/` | Prompt templates for generation |
| **Output: Documents** | `d:/Repository/@Clients/FY.WB.Midway/generated_documents/` | Generated requirement documents |
| **Output: Status** | `d:/Repository/@Clients/FY.WB.Midway/generation_status/` | Status files and logs |

## Input Directories

### Requirements Directory

**Path**: `d:/Repository/@Clients/FY.WB.Midway/Requirements/`

This directory contains the source requirements files that serve as input to the generation process. These files include:

- Consolidated requirements
- Cross-system analysis
- Invoice requirements
- Logistics requirements

The orchestrator reads these files to gather context for generating the new requirements documents.

### Prompts Directory

**Path**: `d:/Repository/@Clients/FY.WB.Midway/Requirements_Generation_Prompts/`

This directory contains the prompt templates used by the orchestrator to generate each type of document:

- `01_BRD.md` - Business Requirements Document template
- `02_PRD.md` - Product Requirements Document template
- `04_FRD.md` - Functional Requirements Document template
- `05_NFRD.md` - Non-Functional Requirements Document template
- `07_DRD.md` - Design Requirements Document template
- `08_DB_Schema.md` - Database Schema Document template
- `09_TRD.md` - Technical Requirements Document template
- `10_API_OpenAPI.md` - API Specification template
- `20_Test_Plan.md` - Test Plan template
- `24_RTM.md` - Requirements Traceability Matrix template

## Output Directories

### Generated Documents Directory

**Path**: `d:/Repository/@Clients/FY.WB.Midway/generated_documents/`

This directory is where the orchestrator writes the final generated documents:

- `BRD.md` - Business Requirements Document
- `PRD.md` - Product Requirements Document
- `FRD.md` - Functional Requirements Document
- `NFRD.md` - Non-Functional Requirements Document
- `DRD.md` - Design Requirements Document
- `DB_SCHEMA.md` - Database Schema Document
- `TRD.md` - Technical Requirements Document
- `API_SPEC.md` - API Specification
- `TEST_PLAN.md` - Test Plan
- `RTM.md` - Requirements Traceability Matrix

### Status Directory

**Path**: `d:/Repository/@Clients/FY.WB.Midway/generation_status/`

This directory contains status files and logs that track the progress of the generation process:

- `status_BRD.json` - Status of BRD generation
- `status_PRD.json` - Status of PRD generation
- `status_FRD.json` - Status of FRD generation
- ... (status files for each document)
- `orchestrator.log` - Log file with detailed generation progress

## Data Flow

1. The orchestrator reads source requirements from the **Requirements Directory**
2. It loads prompt templates from the **Prompts Directory**
3. It generates documents and writes them to the **Generated Documents Directory**
4. It writes status updates to the **Status Directory**
5. The dashboard reads from the **Status Directory** and **Generated Documents Directory** to display progress

## Configuration

These directories are configured in the `config.yaml` file:

```yaml
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

You can modify these paths in the config file if you need to use different directories.

## Dashboard Integration

The dashboard is configured to monitor the **Generated Documents Directory** and **Status Directory**. When you run the dashboard, it will automatically look for files in these directories.

If you need to change the directories that the dashboard monitors, you can update the paths in `dashboard/run_simple.py`:

```python
# Default paths
OUTPUT_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
STATUS_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generation_status")