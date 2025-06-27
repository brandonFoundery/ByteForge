# 🚀 Cofounder Prompts Library

This directory contains extracted prompts from the Cofounder system for generating comprehensive requirements documents and project artifacts.

## 📁 Directory Structure

### **Project Management Prompts**
- `01_PRD_Generation.md` - Product Requirements Document
- `02_FRD_Generation.md` - Features Requirements Document  
- `03_BRD_Generation.md` - Backend Requirements Document
- `04_DRD_Generation.md` - Database Requirements Document
- `05_FJMD_Generation.md` - Features Journey Maps Document
- `06_UXSMD_Generation.md` - UX Sitemap Document
- `07_UXDMD_Generation.md` - UX Data Map Document

### **UX/Design Prompts**
- `10_UX_Sitemap_Structure.md` - UX sitemap structure generation
- `11_UX_Datamap_Generation.md` - UX data mapping generation

### **Backend/Database Prompts**
- `20_Database_Schemas.md` - Database schema generation
- `21_PostgreSQL_Implementation.md` - PostgreSQL implementation
- `22_OpenAPI_Specification.md` - OpenAPI specification generation
- `23_AsyncAPI_Specification.md` - AsyncAPI specification generation
- `24_Backend_Server.md` - Backend server generation

### **Frontend/Webapp Prompts**
- `30_React_Root_Component.md` - React app root component generation
- `31_React_View_Component.md` - React view component generation
- `32_Redux_Store.md` - Redux store generation

### **Development Operations Prompts**
- `40_LLM_Operations.md` - LLM operation handling
- `41_Data_Conversion.md` - Data conversion utilities
- `42_Rendering_Operations.md` - Rendering operations

## 🎯 Usage

Each prompt file contains:
- **Purpose**: What the prompt generates
- **Input Requirements**: Required documents/data
- **System Prompt**: The core LLM instruction
- **User Message Templates**: How to structure input data
- **Output Format**: Expected response format
- **Model Recommendations**: Suggested LLM models

## 🔄 Integration

These prompts are designed to work in sequence:
1. Start with PRD generation from project description
2. Generate FRD from PRD
3. Create specialized documents (BRD, DRD, UX docs) from PRD+FRD
4. Generate technical specifications and implementations

## ✅ Extraction Status

### **Completed Extractions**
- ✅ `01_PRD_Generation.md` - Product Requirements Document
- ✅ `02_FRD_Generation.md` - Features Requirements Document
- ✅ `03_BRD_Generation.md` - Backend Requirements Document
- ✅ `04_DRD_Generation.md` - Database Requirements Document
- ✅ `06_UXSMD_Generation.md` - UX Sitemap Document
- ✅ `20_Database_Schemas.md` - Database schema generation
- ✅ `22_OpenAPI_Specification.md` - OpenAPI specification generation
- ✅ `30_React_Root_Component.md` - React app root component generation

### **Remaining Extractions** (Available in source)
- 📋 `05_FJMD_Generation.md` - Features Journey Maps Document
- 📋 `07_UXDMD_Generation.md` - UX Data Map Document
- 📋 `10_UX_Sitemap_Structure.md` - UX sitemap structure generation
- 📋 `11_UX_Datamap_Generation.md` - UX data mapping generation
- 📋 `21_PostgreSQL_Implementation.md` - PostgreSQL implementation
- 📋 `23_AsyncAPI_Specification.md` - AsyncAPI specification generation
- 📋 `24_Backend_Server.md` - Backend server generation
- 📋 `31_React_View_Component.md` - React view component generation
- 📋 `32_Redux_Store.md` - Redux store generation
- 📋 `40_LLM_Operations.md` - LLM operation handling
- 📋 `41_Data_Conversion.md` - Data conversion utilities
- 📋 `42_Rendering_Operations.md` - Rendering operations

## 📝 Notes

- All prompts are extracted from the Cofounder system
- Prompts are optimized for GPT-4 and similar models
- Output formats are typically Markdown or YAML
- Each prompt includes quality assurance instructions
- Source files located in: `cofounder/cofounder-main/cofounder-main/cofounder/api/system/functions/`
