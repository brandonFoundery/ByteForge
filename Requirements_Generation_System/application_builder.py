"""
AI-Driven Application Builder System

This module implements a 4-pass AI workflow for automatically generating and building applications:
1. Pass 1: OpenAI o3 - Design Phase
2. Pass 2: Gemini 2.5 - Review Phase  
3. Pass 3: Claude Sonnet 4 - Implementation Phase
4. Pass 4: Build System - Code Generation and Compilation
"""

import asyncio
import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Try to import Git and GitHub libraries
try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    Repo = None
    GitCommandError = None
    GIT_AVAILABLE = False
    print("Warning: GitPython not available. Git operations will be disabled.")

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    Github = None
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not available. GitHub operations will be disabled.")
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import existing orchestrator components
from orchestrator import RequirementsOrchestrator, ConfigManager
from multi_terminal_logger import MultiTerminalLogger, LogLevel

console = Console()


class PassType(Enum):
    """Types of AI passes in the workflow"""
    DESIGN = "design"
    REVIEW = "review"
    IMPLEMENTATION = "implementation"
    BUILD = "build"


class PassStatus(Enum):
    """Status of individual passes"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class PassResult:
    """Result from an individual pass"""
    pass_type: PassType
    status: PassStatus
    output: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BuildResult:
    """Final result from the complete build workflow"""
    success: bool
    feature_branch: Optional[str] = None
    pr_url: Optional[str] = None
    pass_results: List[PassResult] = None
    total_execution_time: Optional[float] = None
    error_summary: Optional[str] = None

    def __post_init__(self):
        if self.pass_results is None:
            self.pass_results = []


class ApplicationBuilder:
    """
    Main class for the AI-driven application building system.
    
    Orchestrates a 4-pass workflow:
    1. Design (OpenAI o3)
    2. Review (Gemini 2.5)
    3. Implementation (Claude Sonnet 4)
    4. Build (Automated system)
    """

    def __init__(self, project_name: str, base_path: Path, config_path: Optional[Path] = None):
        self.project_name = project_name
        self.base_path = base_path
        self.frontend_path = base_path / "FrontEnd"
        self.backend_path = base_path / "BackEnd"
        self.requirements_path = base_path / "Requirements"
        self.output_path = base_path / "generated_applications"

        # Create output directory
        self.output_path.mkdir(exist_ok=True)

        # Initialize configuration
        self.config_manager = ConfigManager(base_path / "Requirements_Generation_System")
        self.config = self._load_config(config_path) if config_path else {}

        # Initialize Git repository
        if GIT_AVAILABLE:
            try:
                self.repo = Repo(base_path)
                console.print(f"[green]✓ Git repository found at {base_path}[/green]")
            except Exception as e:
                console.print(f"[red]Warning: Could not initialize Git repository: {e}[/red]")
                self.repo = None
        else:
            console.print("[yellow]Warning: GitPython not available. Git operations disabled.[/yellow]")
            self.repo = None

        # Initialize GitHub client
        if GITHUB_AVAILABLE:
            github_token = os.getenv('GITHUB_TOKEN')
            self.github_client = Github(github_token) if github_token else None
        else:
            console.print("[yellow]Warning: PyGithub not available. GitHub operations disabled.[/yellow]")
            self.github_client = None

        # Multi-terminal logger (will be initialized per workflow)
        self.multi_logger = None

        # Get application builder config
        self.app_config = self.config.get('application_builder', {})

        # Pass tracking
        self.current_workflow_id = None
        self.pass_results = []

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config from {config_path}: {e}[/yellow]")
            return {}



    async def run_full_workflow(self, feature_spec: str, feature_name: str = None) -> BuildResult:
        """
        Run the complete 4-pass workflow

        Args:
            feature_spec: Description of the feature to build
            feature_name: Optional name for the feature (auto-generated if not provided)

        Returns:
            BuildResult with complete workflow results
        """
        start_time = time.time()
        self.current_workflow_id = f"workflow_{int(start_time)}"

        if not feature_name:
            feature_name = f"ai_generated_feature_{int(start_time)}"

        # Initialize multi-terminal logger
        self.multi_logger = MultiTerminalLogger(self.base_path, self.current_workflow_id)

        console.print(f"\n[bold cyan]Starting AI-Driven Application Build Workflow[/bold cyan]")
        console.print(f"[cyan]Feature: {feature_name}[/cyan]")
        console.print(f"[cyan]Workflow ID: {self.current_workflow_id}[/cyan]")

        # Log workflow start
        self.multi_logger.log_workflow_start(feature_name, feature_spec)

        # Initialize result tracking
        self.pass_results = []
        feature_branch = None
        pr_url = None
        
        try:
            # Create feature branch
            if self.repo:
                feature_branch = self.create_feature_branch(feature_name)
                console.print(f"[green]Created feature branch: {feature_branch}[/green]")
            
            # Run each pass in sequence
            passes_to_run = [
                (PassType.DESIGN, feature_spec),
                (PassType.REVIEW, None),  # Will use output from design pass
                (PassType.IMPLEMENTATION, None),  # Will use output from review pass
                (PassType.BUILD, None)  # Will use output from implementation pass
            ]
            
            previous_output = feature_spec
            
            for pass_type, initial_input in passes_to_run:
                console.print(f"\n[yellow]Starting {pass_type.value.title()} Pass...[/yellow]")

                # Use previous pass output as input (except for first pass)
                pass_input = initial_input if initial_input else previous_output

                # Log pass start
                input_summary = pass_input[:100] if pass_input else "No input"
                self.multi_logger.log_pass_start(pass_type.value, input_summary)

                result = await self.run_pass(pass_type, pass_input)
                self.pass_results.append(result)

                if result.status == PassStatus.FAILED:
                    console.print(f"[red]❌ {pass_type.value.title()} Pass failed: {result.error_message}[/red]")
                    self.multi_logger.log_pass_error(pass_type.value, result.error_message, result.retry_count)
                    break
                else:
                    console.print(f"[green]✅ {pass_type.value.title()} Pass completed successfully[/green]")
                    output_summary = result.output[:100] if result.output else "No output"
                    self.multi_logger.log_pass_complete(pass_type.value, result.execution_time, output_summary)
                    previous_output = result.output
            
            # Check if all passes completed successfully
            success = all(result.status == PassStatus.COMPLETED for result in self.pass_results)
            
            if success and self.repo:
                # Create PR if build was successful
                pr_url = await self.create_pull_request(feature_branch, feature_name)
                if pr_url:
                    console.print(f"[green]🎉 Pull Request created: {pr_url}[/green]")
            
            total_time = time.time() - start_time

            # Log workflow completion
            self.multi_logger.log_workflow_complete(success, total_time, feature_branch, pr_url)

            # Cleanup logger
            if self.multi_logger:
                self.multi_logger.cleanup()

            return BuildResult(
                success=success,
                feature_branch=feature_branch,
                pr_url=pr_url,
                pass_results=self.pass_results,
                total_execution_time=total_time,
                error_summary=self._generate_error_summary() if not success else None
            )

        except Exception as e:
            console.print(f"[red]❌ Workflow failed with exception: {e}[/red]")
            total_time = time.time() - start_time

            # Log workflow failure
            if self.multi_logger:
                self.multi_logger.log_workflow_complete(False, total_time)
                self.multi_logger.cleanup()

            return BuildResult(
                success=False,
                feature_branch=feature_branch,
                pass_results=self.pass_results,
                total_execution_time=total_time,
                error_summary=str(e)
            )

    async def run_full_workflow_from_requirements(self, requirements_dir: Path, feature_name: str) -> BuildResult:
        """
        Run the full 4-pass workflow using existing requirements documents

        Args:
            requirements_dir: Path to directory containing requirements documents
            feature_name: Name for the feature branch and implementation

        Returns:
            BuildResult with success status and details
        """
        # Load and organize requirements documents
        requirements_docs = self._load_requirements_documents(requirements_dir)

        if not requirements_docs:
            return BuildResult(
                success=False,
                feature_branch=None,
                pr_url=None,
                pass_results=[],
                total_execution_time=0.0,
                error_summary="No requirements documents found"
            )

        # Create a comprehensive feature specification from requirements
        feature_spec = self._create_feature_spec_from_requirements(requirements_docs)

        # Run the standard workflow with the generated specification
        return await self.run_full_workflow(feature_spec, feature_name)

    async def run_pass(self, pass_type: PassType, input_data: Any) -> PassResult:
        """
        Run an individual pass

        Args:
            pass_type: Type of pass to run
            input_data: Input data for the pass

        Returns:
            PassResult with pass execution results
        """
        # Create pass-specific logger
        if self.multi_logger:
            logger = self.multi_logger.create_pass_logger(pass_type.value)
        else:
            logger = logging.getLogger(f"app_builder.{pass_type.value}")

        logger.info(f"Starting {pass_type.value} pass")

        start_time = time.time()
        max_retries = self.app_config.get('max_retries', 4)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} of {max_retries}")
                
                # Route to appropriate pass implementation
                if pass_type == PassType.DESIGN:
                    output = await self._run_design_pass(input_data)
                elif pass_type == PassType.REVIEW:
                    output = await self._run_review_pass(input_data)
                elif pass_type == PassType.IMPLEMENTATION:
                    output = await self._run_implementation_pass(input_data)
                elif pass_type == PassType.BUILD:
                    output = await self._run_build_pass(input_data)
                else:
                    raise ValueError(f"Unknown pass type: {pass_type}")
                
                execution_time = time.time() - start_time
                logger.info(f"Pass completed successfully in {execution_time:.2f} seconds")
                
                return PassResult(
                    pass_type=pass_type,
                    status=PassStatus.COMPLETED,
                    output=output,
                    execution_time=execution_time,
                    retry_count=attempt
                )
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    execution_time = time.time() - start_time
                    return PassResult(
                        pass_type=pass_type,
                        status=PassStatus.FAILED,
                        error_message=str(e),
                        execution_time=execution_time,
                        retry_count=attempt + 1
                    )
                else:
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

    # Pass implementation methods
    async def _run_design_pass(self, input_data: str) -> str:
        """Run the design pass using OpenAI o3"""
        try:
            from build_passes.design_pass import DesignPass

            design_pass = DesignPass(self.config, self.base_path)
            result = await design_pass.run(input_data)
            return result

        except ImportError as e:
            raise NotImplementedError(f"Design pass module not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Design pass failed: {e}")

    async def _run_review_pass(self, input_data: str) -> str:
        """Run the review pass using Gemini 2.5"""
        try:
            from build_passes.review_pass import ReviewPass

            review_pass = ReviewPass(self.config, self.base_path)
            result = await review_pass.run(input_data)
            return result

        except ImportError as e:
            raise NotImplementedError(f"Review pass module not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Review pass failed: {e}")

    async def _run_implementation_pass(self, input_data: str) -> str:
        """Run the implementation pass using Claude Sonnet 4"""
        try:
            from build_passes.implementation_pass import ImplementationPass

            implementation_pass = ImplementationPass(self.config, self.base_path)
            result = await implementation_pass.run(input_data)
            return result

        except ImportError as e:
            raise NotImplementedError(f"Implementation pass module not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Implementation pass failed: {e}")

    async def _run_build_pass(self, input_data: str) -> str:
        """Run the build pass using automated build system"""
        try:
            from build_passes.build_pass import BuildPass

            build_pass = BuildPass(self.config, self.base_path, self.repo)
            result = await build_pass.run(input_data)
            return result

        except ImportError as e:
            raise NotImplementedError(f"Build pass module not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Build pass failed: {e}")

    def create_feature_branch(self, feature_name: str) -> str:
        """Create a new feature branch for the build"""
        if not self.repo:
            raise RuntimeError("Git repository not available")
        
        branch_prefix = self.config.get('application_builder', {}).get('git', {}).get('branch_prefix', 'feature/ai-generated')
        branch_name = f"{branch_prefix}/{feature_name}"
        
        try:
            # Create and checkout new branch
            self.repo.git.checkout("-b", branch_name)
            return branch_name
        except GitCommandError as e:
            # Branch might already exist, try to checkout
            try:
                self.repo.git.checkout(branch_name)
                return branch_name
            except GitCommandError:
                raise RuntimeError(f"Could not create or checkout branch {branch_name}: {e}")

    async def create_pull_request(self, branch_name: str, feature_name: str) -> Optional[str]:
        """Create a pull request for the feature branch"""
        if not self.github_client:
            console.print("[yellow]GitHub token not available, skipping PR creation[/yellow]")
            return None

        try:
            # Get repository info from Git remote
            origin_url = self.repo.remote('origin').url

            # Extract owner/repo from URL
            if 'github.com' in origin_url:
                # Handle both SSH and HTTPS URLs
                if origin_url.startswith('git@'):
                    # SSH: git@github.com:owner/repo.git
                    repo_part = origin_url.split(':')[1].replace('.git', '')
                else:
                    # HTTPS: https://github.com/owner/repo.git
                    repo_part = origin_url.split('github.com/')[1].replace('.git', '')

                owner, repo_name = repo_part.split('/')

                # Get the repository
                github_repo = self.github_client.get_repo(f"{owner}/{repo_name}")

                # Create PR
                base_branch = self.app_config.get('git', {}).get('base_branch', 'master')
                pr_title = f"feat: {feature_name} - AI-generated implementation"
                pr_body = f"""# AI-Generated Feature Implementation

This pull request contains an automatically generated implementation of the **{feature_name}** feature.

## Generated by AI-Driven Application Builder

This implementation was created using a 4-pass AI workflow:

1. **Design Pass (OpenAI o3)**: System architecture and design
2. **Review Pass (Gemini 2.5)**: Design validation and improvements
3. **Implementation Pass (Claude Sonnet 4)**: Detailed implementation specifications
4. **Build Pass (Automated System)**: Code generation and compilation

## What's Included

- ✅ Backend API implementation
- ✅ Frontend components and pages
- ✅ Database migrations (if applicable)
- ✅ Unit and integration tests
- ✅ Documentation updates

## Testing

All automated tests have been run and are passing. Please review the implementation and test manually before merging.

## Review Notes

This is an AI-generated implementation. Please review carefully for:
- Code quality and adherence to project standards
- Security considerations
- Performance implications
- Integration with existing systems

---

*This PR was created automatically by the AI-Driven Application Builder system.*
"""

                pr = github_repo.create_pull(
                    title=pr_title,
                    body=pr_body,
                    head=branch_name,
                    base=base_branch
                )

                console.print(f"[green]✅ Pull request created: {pr.html_url}[/green]")
                return pr.html_url

            else:
                console.print("[yellow]Repository is not hosted on GitHub, skipping PR creation[/yellow]")
                return None

        except Exception as e:
            console.print(f"[red]Failed to create pull request: {e}[/red]")
            return None

    def _generate_error_summary(self) -> str:
        """Generate a summary of errors from failed passes"""
        failed_passes = [result for result in self.pass_results if result.status == PassStatus.FAILED]
        if not failed_passes:
            return "No specific errors recorded"
        
        summary = "Failed passes:\n"
        for result in failed_passes:
            summary += f"- {result.pass_type.value}: {result.error_message}\n"
        
        return summary

    def _load_requirements_documents(self, requirements_dir: Path) -> Dict[str, str]:
        """Load all requirements documents from the directory"""
        requirements_docs = {}

        # Define the order and types of documents to load
        doc_types = {
            'BRD': ['01_BRD.md', 'BRD.md', 'business_requirements.md'],
            'PRD': ['02_PRD.md', 'PRD.md', 'product_requirements.md'],
            'FRD': ['04_FRD.md', 'FRD.md', 'functional_requirements.md'],
            'NFRD': ['05_NFRD.md', 'NFRD.md', 'non_functional_requirements.md'],
            'DRD': ['07_DRD.md', 'DRD.md', 'data_requirements.md'],
            'TRD': ['09_TRD.md', 'TRD.md', 'technical_requirements.md'],
            'API': ['10_API_OpenAPI.md', 'API.md', 'api_specification.md'],
            'UIUX': ['11_UIUX_Spec.md', 'UIUX.md', 'ui_ux_specification.md'],
            'TEST': ['20_Test_Plan.md', 'test_plan.md', 'testing.md']
        }

        for doc_type, possible_names in doc_types.items():
            for name in possible_names:
                doc_path = requirements_dir / name
                if doc_path.exists():
                    try:
                        content = doc_path.read_text(encoding='utf-8')
                        requirements_docs[doc_type] = content
                        console.print(f"[green]✓ Loaded {doc_type}: {name}[/green]")
                        break  # Found the document, move to next type
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not read {name}: {e}[/yellow]")

        return requirements_docs

    def _create_feature_spec_from_requirements(self, requirements_docs: Dict[str, str]) -> str:
        """Create a comprehensive feature specification from requirements documents"""

        feature_spec = """# AI-Driven Application Implementation

This implementation is based on the following requirements documents:

"""

        # Add each document type with its content summary
        for doc_type, content in requirements_docs.items():
            feature_spec += f"## {doc_type} - {self._get_doc_type_name(doc_type)}\n\n"

            # Extract key sections from each document
            if doc_type == 'BRD':
                feature_spec += self._extract_business_requirements(content)
            elif doc_type == 'PRD':
                feature_spec += self._extract_product_requirements(content)
            elif doc_type == 'FRD':
                feature_spec += self._extract_functional_requirements(content)
            elif doc_type == 'NFRD':
                feature_spec += self._extract_non_functional_requirements(content)
            elif doc_type == 'TRD':
                feature_spec += self._extract_technical_requirements(content)
            elif doc_type == 'API':
                feature_spec += self._extract_api_specifications(content)
            elif doc_type == 'UIUX':
                feature_spec += self._extract_ui_specifications(content)
            else:
                # For other document types, include a summary
                feature_spec += self._extract_document_summary(content)

            feature_spec += "\n\n"

        feature_spec += """
## Implementation Guidelines

Based on the requirements documents above, implement a complete, production-ready system that:

1. **Follows Clean Architecture**: Implement using the existing Clean Architecture patterns
2. **Maintains Multi-tenancy**: Ensure all features respect tenant boundaries
3. **Integrates Seamlessly**: Use existing authentication, authorization, and data access patterns
4. **Includes Comprehensive Testing**: Unit tests, integration tests, and API tests
5. **Provides Complete Documentation**: Code comments, API documentation, and user guides
6. **Handles Errors Gracefully**: Proper error handling, validation, and user feedback
7. **Optimizes Performance**: Efficient queries, caching where appropriate, and scalable design
8. **Ensures Security**: Input validation, authorization checks, and secure data handling

The implementation should be ready for production deployment with minimal additional work.
"""

        return feature_spec

    def _get_doc_type_name(self, doc_type: str) -> str:
        """Get the full name for a document type"""
        names = {
            'BRD': 'Business Requirements Document',
            'PRD': 'Product Requirements Document',
            'FRD': 'Functional Requirements Document',
            'NFRD': 'Non-Functional Requirements Document',
            'DRD': 'Data Requirements Document',
            'TRD': 'Technical Requirements Document',
            'API': 'API Specification',
            'UIUX': 'UI/UX Specification',
            'TEST': 'Test Plan'
        }
        return names.get(doc_type, doc_type)

    def _extract_business_requirements(self, content: str) -> str:
        """Extract key business requirements"""
        # Look for business objectives, scope, and key requirements
        lines = content.split('\n')
        extracted = []

        in_objectives = False
        in_scope = False
        in_requirements = False

        for line in lines:
            line_lower = line.lower().strip()

            if 'business objective' in line_lower or 'business goal' in line_lower:
                in_objectives = True
                extracted.append(line)
            elif 'scope' in line_lower and ('project' in line_lower or 'business' in line_lower):
                in_scope = True
                extracted.append(line)
            elif 'requirement' in line_lower and ('business' in line_lower or 'key' in line_lower):
                in_requirements = True
                extracted.append(line)
            elif in_objectives or in_scope or in_requirements:
                if line.strip() and not line.startswith('#'):
                    extracted.append(line)
                elif line.startswith('#') and len(extracted) > 0:
                    # New section, stop extracting
                    break

        return '\n'.join(extracted[:20])  # Limit to first 20 relevant lines

    def _extract_product_requirements(self, content: str) -> str:
        """Extract key product requirements"""
        # Look for features, user stories, and product specifications
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['feature', 'user story', 'epic', 'requirement', 'functionality']):
                extracted.append(line)
                # Get next few lines for context
                idx = lines.index(line)
                for i in range(1, 4):
                    if idx + i < len(lines) and lines[idx + i].strip():
                        extracted.append(lines[idx + i])

        return '\n'.join(extracted[:25])  # Limit to first 25 relevant lines

    def _extract_functional_requirements(self, content: str) -> str:
        """Extract functional requirements"""
        # Look for specific functional requirements and use cases
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['shall', 'must', 'should', 'fr-', 'functional requirement']):
                extracted.append(line)

        return '\n'.join(extracted[:30])  # Limit to first 30 requirements

    def _extract_non_functional_requirements(self, content: str) -> str:
        """Extract non-functional requirements"""
        # Look for performance, security, scalability requirements
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['performance', 'security', 'scalability', 'availability', 'nfr-', 'non-functional']):
                extracted.append(line)

        return '\n'.join(extracted[:20])  # Limit to first 20 requirements

    def _extract_technical_requirements(self, content: str) -> str:
        """Extract technical requirements and architecture details"""
        # Look for technology stack, architecture, and technical constraints
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['technology', 'architecture', 'framework', 'database', 'api', 'technical']):
                extracted.append(line)

        return '\n'.join(extracted[:25])  # Limit to first 25 technical details

    def _extract_api_specifications(self, content: str) -> str:
        """Extract API specifications"""
        # Look for endpoints, data models, and API details
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['endpoint', 'api', 'get', 'post', 'put', 'delete', 'model', 'schema']):
                extracted.append(line)

        return '\n'.join(extracted[:30])  # Limit to first 30 API details

    def _extract_ui_specifications(self, content: str) -> str:
        """Extract UI/UX specifications"""
        # Look for UI components, user flows, and design requirements
        lines = content.split('\n')
        extracted = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(keyword in line_lower for keyword in ['component', 'page', 'screen', 'user interface', 'ui', 'ux', 'design']):
                extracted.append(line)

        return '\n'.join(extracted[:25])  # Limit to first 25 UI details

    def _extract_document_summary(self, content: str) -> str:
        """Extract a general summary from any document"""
        # Get first few paragraphs and any bullet points
        lines = content.split('\n')
        extracted = []

        for line in lines[:50]:  # Look at first 50 lines
            if line.strip() and (line.startswith('-') or line.startswith('*') or line.startswith('#') or len(line.split()) > 5):
                extracted.append(line)

        return '\n'.join(extracted[:15])  # Limit to first 15 relevant lines
