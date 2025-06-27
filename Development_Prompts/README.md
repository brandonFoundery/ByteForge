# 📘 Development Prompts Library

This directory contains the complete LLM prompt library for generating and maintaining traceable requirements documentation for the FY.WB.Midway project.

## 📁 Directory Structure

```
Development_Prompts/
├── README.md                    # This file - overview and usage guide
├── 00_system_primer.md         # Master orientation prompt for all agents
├── 01_product_requirements.md  # PRD generation prompts
├── 02_functional_requirements.md # FRD and NFRD generation prompts
├── 02b_project_planner.md        # WBS & development plan prompts
├── 03_data_design.md           # Data requirements and schema prompts
├── 04_backend_logic.md         # Backend services and API prompts
├── 05_ux_design.md             # UX design and mapping prompts
├── 06_struct_generators.md     # JSON structure generation prompts
├── 07_react_components.md      # React view and store generation prompts
├── 08_devops_integration.md    # Server setup and DevOps prompts
├── 09_testing_verification.md  # QA and testing prompts
├── 10_traceability_control.md  # RTM and change tracking prompts
└── 99_optional_artifacts.md    # Designer-led and optional prompts
```

## 🧭 Usage Guide

### Execution Order

The prompts should be executed in numerical order (00-10) to maintain proper traceability and dependencies:

1. **00_system_primer.md** - Initialize all agents with shared context
2. **01_product_requirements.md** - Generate PRD from user brief
3. **02_functional_requirements.md** - Create FRD and NFRD from PRD
4. **02b_project_planner.md** - Produce Work-Breakdown & Development Plan
5. **03_data_design.md** - Design data layer from FRD
6. **04_backend_logic.md** - Create backend services and APIs
7. **05_ux_design.md** - Design UX flows and mappings
8. **06_struct_generators.md** - Generate JSON structures
9. **07_react_components.md** - Create React components and stores
10. **08_devops_integration.md** - Setup deployment and infrastructure
11. **09_testing_verification.md** - Create test plans and verification
12. **10_traceability_control.md** - Maintain RTM and change logs

### Parallel Execution

Some steps can be executed in parallel:
- **Step 5**: Data Design (03), Backend Logic (04), and UX Design (05) can run concurrently
- **Step 8**: Struct Generators (06) and React Components (07) can run in parallel

### Integration with FY.WB.Midway

These prompts are specifically designed to work with:
- **Requirements/** directory structure
- **RTM.csv** traceability matrices
- **requirements_tracker.json** files
- **OpenAPI 3.0** specifications
- **React/Next.js** frontend architecture
- **ASP.NET Core** backend architecture

## 🔧 Customization

Each prompt file includes:
- **Input requirements** - What documents/data are needed
- **Output specifications** - Expected deliverables and formats
- **ID formatting rules** - Traceability identifier patterns
- **YAML front-matter** - Metadata requirements
- **Validation criteria** - Quality checks and acceptance criteria

## 📋 Document Types Covered

The prompt library generates all 23 document types used in the FY.WB.Midway project:

### Core Requirements
- PRD (Product Requirements Document)
- FRD (Functional Requirements Document)
- NFRD (Non-Functional Requirements Document)

### Technical Specifications
- DRD (Data Requirements Document)
- BRD (Business Requirements Document)
- API-OPEN (OpenAPI Specifications)
- API-ASYNC (Event/Message Specifications)
- DB-SCHEMA (Database Schema)

### UX/UI Design
- UXSMD (UX Site Map Document)
- UXDMD (UX Data Mapping Document)
- UX-SM-STRUCT (Site Map JSON Structure)
- UX-DM-STRUCT (Data Mapping JSON Structure)

### Implementation
- REACT-STORE (State Management)
- REACT-VIEW (Component Specifications)
- SERVER-GUIDE (Backend Implementation Guide)

### Quality Assurance
- TEST-PLAN (Testing Specifications)
- RTM (Requirements Traceability Matrix)
- CHANGE-LOG (Change Management)

### Optional/Designer-Led
- LAYOUT-DOC (Visual Design)
- LIB-INDEX (Component Library)
- REACT-VIEW-REDESIGN (Styled Components)

## 🚀 Getting Started

1. Start with `00_system_primer.md` to understand the overall approach
2. Follow the numbered sequence for your specific needs
3. Customize prompts based on your project requirements
4. Maintain traceability through consistent ID formatting
5. Update RTM and change logs after each generation cycle

## 📝 Notes

- All prompts are designed for LLM agents (GPT-4, Claude, etc.)
- Outputs integrate with existing FY.WB.Midway documentation structure
- Prompts can be exported as JSON/YAML for automation pipelines
- Templates are reusable across similar projects with modifications
