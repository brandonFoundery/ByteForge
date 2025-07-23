# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ByteForge Frontend** is an AI-powered software development orchestration platform that automates the generation of comprehensive requirements documentation and code implementation. This is not a traditional web application, but rather a sophisticated meta-development system that generates other software projects using AI agents and multi-LLM coordination.

## Core Architecture

### Primary Technology Stack

**Requirements Generation Engine (Python)**
- **Core Framework**: Python 3.x with FastAPI for dashboards
- **AI Integration**: Multi-LLM support (OpenAI GPT-4o/o3, Anthropic Claude-4, Google Gemini, Grok)
- **Document Processing**: YAML, Markdown, JSON processing with Jinja2 templates
- **Dependencies**: See `/Requirements_Generation_System/requirements.txt`

**Monitoring Dashboard (React + FastAPI)**
- **Frontend**: React 19.1.0 + TypeScript 5.8.3 + Vite 6.3.5
- **UI Framework**: Material-UI 7.1.1 (@mui/material, @emotion/react)
- **Backend**: Python FastAPI with WebSocket support
- **HTTP Client**: Axios for API communication

**Containerized Application Stack (Generated Output)**
- **Backend**: ASP.NET Core 8.0 with Clean Architecture
- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Database**: SQL Server 2022 with Redis cache
- **Infrastructure**: Docker containers with nginx reverse proxy

## Development Commands

### Requirements Generation System
```bash
# Main generation system (interactive menu)
cd Requirements_Generation_System
python run_generation.py

# Direct orchestrator execution
python orchestrator.py --config config.yaml

# Real-time monitoring
python monitor.py

# API key setup
python setup_api_keys.py
```

### Dashboard System
```bash
# Start complete dashboard
cd dashboard
python run_dashboard.py

# Start simple HTML dashboard
python run_simple.py

# Set up demo data for testing
python setup_demo.py

# Test API connectivity
python test_api.py
```

### Dashboard Frontend (React)
```bash
cd dashboard/frontend
npm install          # Install dependencies
npm run dev          # Start development server (port 5173)
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Docker Deployment (Generated Applications)
```bash
# Full stack deployment
docker-compose up -d

# Backend only
docker-compose up backend sqlserver redis

# Frontend only  
docker-compose up frontend nginx

# View logs
docker-compose logs -f [service-name]
```

## Key Configuration Files

**Main System Configuration**
- `/Requirements_Generation_System/config.yaml` - Core orchestration settings
  - LLM provider configuration (OpenAI, Anthropic, Google)
  - Document generation parameters and dependencies
  - AI agent execution settings
  - Claude Code integration settings
  - File paths and directory structure

**Environment Setup**
- `.env.example` - Template for environment variables
- `/Requirements_Generation_System/api_keys.json` - Secure API key storage

**Dashboard Configuration**
- `/dashboard/frontend/package.json` - React app dependencies
- `/dashboard/frontend/vite.config.ts` - Vite build configuration

**Docker Configuration**
- `docker-compose.yml` - Full application stack
- `docker-compose.upload.yml` - Upload service variant
- `Dockerfile.backend`, `Dockerfile.frontend`, `Dockerfile.upload` - Individual service containers

## Project Structure & Organization

### Core Directories

**`/Requirements_Generation_System/`** - Main orchestration engine
- `orchestrator.py` - Core document generation engine
- `run_generation.py` - Interactive user interface
- `monitor.py` - Real-time progress monitoring
- `utils.py` - Traceability analysis and validation
- `config.yaml` - System configuration
- `claude_code_executor.py` - Claude Code integration
- `application_builder.py` - AI-driven app builder

**`/Requirements_Generation_Prompts/`** - LLM prompt templates
- Business Requirements (BRD), Product Requirements (PRD)
- Functional Requirements (FRD), Technical Requirements (TRD)
- Database schemas, API specifications, test plans
- Requirements traceability matrices (RTM)

**`/Development_Prompts/`** - Specialized development prompts
- System architecture and backend logic
- React component generation and UX design
- DevOps integration and testing verification
- `/claude_code_prompts/` - Claude Code specific instructions

**`/Application_Templates/`** - Reusable project templates
- CRM applications with metadata and guides
- Template structure for rapid project bootstrapping

**`/dashboard/`** - Real-time monitoring interface
- `backend/` - FastAPI monitoring service
- `frontend/` - React dashboard with Material-UI
- `simple_dashboard.html` - Standalone HTML dashboard

**`/design/`** - AI agent design specifications
- Backend, frontend, infrastructure agent designs
- Security and integration agent architectures

## AI Agent Architecture

### Multi-LLM Coordination System

**Primary Providers**
- **OpenAI GPT-4o/o3**: Reasoning and initial document generation
- **Anthropic Claude-4**: Code generation and technical implementation  
- **Google Gemini**: Document review and validation
- **Grok**: Alternative reasoning and generation via xAI's API

**Agent Specializations**
- **Backend Agent**: ASP.NET Core APIs, data models, business logic
- **Frontend Agent**: React/Next.js components and user interfaces
- **Security Agent**: Authentication, authorization, audit logging
- **Infrastructure Agent**: Azure resources, CI/CD, containerization
- **Integration Agent**: API integration, data sync, external services

### Code Generation Workflow

**Phase 1: Requirements Generation**
1. Load client requirements from source documents
2. Generate comprehensive documentation suite (BRD → PRD → FRD → TRD)
3. Create database schemas and API specifications
4. Build requirements traceability matrices

**Phase 2: AI-Driven Implementation**
1. Execute specialized AI agents in dependency order
2. Generate backend APIs with Clean Architecture
3. Create frontend components with modern React patterns
4. Implement security and infrastructure components
5. Integrate external services and APIs

**Phase 3: Validation & Deployment**
1. Run automated testing and validation
2. Deploy to containerized environments
3. Monitor and track implementation progress
4. Generate deployment documentation

## Key Features & Capabilities

### Requirements Generation
- **Automated Documentation**: Complete business, functional, and technical requirements
- **Traceability System**: Bidirectional linking with hierarchical ID generation
- **Multi-Model Support**: Failover and retry logic across LLM providers
- **Change Management**: Automated impact analysis and document updates
- **Real-time Monitoring**: Live progress tracking with web dashboard

### Code Generation
- **Clean Architecture**: Multi-tenant SaaS applications with CQRS patterns
- **Modern Tech Stack**: Next.js, ASP.NET Core, SQL Server, Redis
- **Security-First**: JWT authentication, multi-tenancy, audit trails
- **Container-Ready**: Docker composition with nginx reverse proxy
- **CI/CD Integration**: Automated build and deployment pipelines

### Monitoring & Validation
- **Real-time Dashboard**: Web-based progress tracking with WebSocket updates
- **Document Validation**: Structure, traceability, and completeness checks
- **Metrics Export**: Progress analytics and traceability analysis
- **Error Recovery**: Automatic retry and rollback capabilities

## Development Patterns

### Requirements Generation Workflow
1. **Setup**: Configure API keys and paths in `config.yaml`
2. **Template Selection**: Choose appropriate application template
3. **Document Generation**: Run interactive system via `run_generation.py`
4. **Monitoring**: Track progress via dashboard or console monitor
5. **Validation**: Use utilities to check traceability and completeness

### Code Implementation Workflow
1. **Requirements Input**: Use generated documentation as input
2. **Agent Orchestration**: Deploy AI agents via `application_builder.py`
3. **Progressive Development**: Implement in phases (MVP → Advanced → Production)
4. **Validation**: Run tests and builds at each phase
5. **Deployment**: Use Docker composition for staging/production

### Dashboard Development
1. **Backend First**: FastAPI service monitors file system changes
2. **API Design**: RESTful endpoints with WebSocket for real-time updates
3. **Frontend Options**: Choose between React app or simple HTML
4. **Testing**: Use `test_api.py` for backend validation

## Configuration Management

### LLM Provider Setup
```yaml
llm:
  provider: "openai"  # or "anthropic", "gemini", "grok"
  openai_model: "o3-mini"
  anthropic_model: "claude-sonnet-4-20250514"
  gemini_model: "gemini-2.5-pro-preview-06-05"
  grok_model: "grok-beta"
  temperature: 0.2
  max_tokens: 8000
  timeout: 240
```

### Document Generation Settings
```yaml
generation:
  refinement_rounds: 3
  parallel_processing: false
  validation_level: "high"
  save_drafts: true
  include_metadata: true
```

### Agent Execution Configuration
```yaml
claude_code_execution:
  agents:
    backend:
      name: "Backend Agent"
      directory: "BackEnd"
      estimated_duration: 45
    frontend:
      name: "Frontend Agent" 
      directory: "FrontEnd"
      estimated_duration: 40
```

## Testing & Validation

### Requirements System Testing
```bash
# Validate document structure
python utils.py validate path/to/document.md

# Analyze traceability relationships
python utils.py analyze generated_documents/

# Export traceability matrix
python utils.py export generated_documents/
```

### Dashboard Testing
```bash
# Test API connectivity
cd dashboard
python test_api.py

# Setup demo data
python setup_demo.py

# Run frontend tests
cd frontend
npm run lint
```

### Generated Application Testing
```bash
# Backend testing
cd BackEnd
dotnet test

# Frontend testing  
cd FrontEnd
npm test

# Integration testing
docker-compose up --build
```

## Troubleshooting

### Common Issues

**API Key Configuration**
```bash
# Set environment variables
export OPENAI_API_KEY=your-key-here
export ANTHROPIC_API_KEY=your-key-here
export GOOGLE_API_KEY=your-key-here
export GROK_API_KEY=your-key-here

# Or use setup script
python setup_api_keys.py
```

**Path Resolution**
- All paths in `config.yaml` are relative to `Requirements_Generation_System/`
- Use forward slashes for cross-platform compatibility
- Verify source requirements exist before generation

**Generation Failures**
- Check `generation_status/` directory for error logs
- Reduce `max_tokens` if hitting context limits
- Increase `timeout` for slow network connections
- Enable debug mode: `debug: true` in config

**Dashboard Issues**
- Use simple HTML dashboard if React setup fails
- Verify backend server is running on correct port
- Check browser console for JavaScript errors

### Debug Mode

Enable comprehensive logging:
```yaml
advanced:
  debug: true
  verbose: true
```

## Future Claude Code Instances

This system is specifically designed to support future Claude Code instances:

**Comprehensive Context**: Detailed architecture documentation and prompt libraries
**Agent Orchestration**: Pre-built agent designs for specialized development tasks
**Template System**: Reusable patterns for common application types
**Monitoring Integration**: Real-time feedback and progress tracking
**Modular Architecture**: Clear separation of concerns for maintainability

When working with this codebase, prioritize understanding the AI orchestration patterns and multi-LLM coordination strategies, as these represent the core innovation of the ByteForge platform.