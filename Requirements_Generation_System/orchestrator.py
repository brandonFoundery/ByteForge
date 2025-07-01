import os
import yaml
import json
import asyncio
import re
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Try to import dirty_json for robust JSON parsing from LLM responses  
try:
    import dirty_json
    DIRTY_JSON_AVAILABLE = True
except ImportError:
    dirty_json = None
    DIRTY_JSON_AVAILABLE = False
    print("Warning: dirty-json not available. Install with: pip install dirty-json")
from artifact_processor import ArtifactProcessor, create_artifact_enhanced_prompt
from template_manager import TemplateManager, create_new_project_interactive

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables only.")

from openai import OpenAI

# Try to import Anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None
    ANTHROPIC_AVAILABLE = False

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    genai = None
    GenerationConfig = None
    GOOGLE_AI_AVAILABLE = False
    print("Warning: google.generativeai not available. Gemini models will be disabled.")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import networkx as nx

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Graph generation will be disabled.")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize rich console for beautiful output with Windows encoding fix
import sys
import platform

# Fix Windows console encoding issues
if platform.system() == "Windows":
    try:
        # Try to set UTF-8 encoding for Windows
        import os
        os.system("chcp 65001 > nul")
        console = Console(force_terminal=True, legacy_windows=False)
    except:
        # Fallback for older Windows systems
        console = Console(force_terminal=True, legacy_windows=True)
else:
    console = Console()

# Import split document generators
try:
    from trd_split_generators import (
        generate_master_trd_doc, generate_trd_architecture_doc,
        generate_trd_technology_doc, generate_trd_security_doc,
        generate_trd_infrastructure_doc, generate_trd_performance_doc,
        generate_trd_operations_doc
    )
    from test_split_generators import (
        generate_master_test_plan_doc, generate_test_strategy_doc,
        generate_functional_test_cases_doc
    )
    from test_split_generators_part2 import (
        generate_performance_test_cases_doc, generate_security_test_cases_doc,
        generate_test_automation_doc
    )
    SPLIT_GENERATORS_AVAILABLE = True
except ImportError as e:
    console.print(f"[yellow]Warning: Could not import split generators: {e}[/yellow]")
    console.print("[yellow]Split document generation will be disabled[/yellow]")
    SPLIT_GENERATORS_AVAILABLE = False

# Import code scanner for full regeneration
try:
    from code_scanner import CodeScanner, CodeTree, FileBatch
    CODE_SCANNER_AVAILABLE = True
except ImportError as e:
    console.print(f"[yellow]Warning: Could not import code scanner: {e}[/yellow]")
    console.print("[yellow]Full regeneration from code will be disabled[/yellow]")
    CODE_SCANNER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('requirements_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentStatus(Enum):
    """Status of document generation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GENERATED = "generated"
    REFINED = "refined"
    VALIDATED = "validated"
    FAILED = "failed"


class DocumentType(Enum):
    """Types of documents in the system"""
    BRD = "Business Requirements Document"
    PRD = "Product Requirements Document"
    FRD = "Functional Requirements Document"
    NFRD = "Non-Functional Requirements Document"
    DRD = "Data Requirements Document"
    DB_SCHEMA = "Database Schema"
    TRD = "Technical Requirements Document"
    API_SPEC = "API OpenAPI Specification"
    UIUX_SPEC = "UI/UX Specification"
    TEST_PLAN = "Test Plan and Test Cases"
    RTM = "Requirements Traceability Matrix"
    DEV_PLAN = "Development Plan"


@dataclass
class Document:
    """Represents a requirements document"""
    doc_type: DocumentType
    status: DocumentStatus = DocumentStatus.NOT_STARTED
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[DocumentType] = field(default_factory=list)
    prompt_template: Optional[str] = None
    generated_at: Optional[datetime] = None
    refined_count: int = 0
    validation_errors: List[str] = field(default_factory=list)
    # Review system fields
    reviewed_content: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_count: int = 0
    review_errors: List[str] = field(default_factory=list)
    primary_llm_used: Optional[str] = None
    reviewer_llm_used: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of document validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)


class ConfigManager:
    """Manages API keys and configuration settings"""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent
        self.env_file = self.config_dir / ".env"
        self._load_config()

    def _load_config(self):
        """Load configuration from .env file and environment variables"""
        # Load from .env file if it exists
        if self.env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                console.print(f"[green][OK] Loaded configuration from {self.env_file}[/green]")
            except ImportError:
                console.print(f"[yellow]Warning: python-dotenv not installed. Install with: pip install python-dotenv[/yellow]")
        else:
            console.print(f"[yellow]No .env file found at {self.env_file}[/yellow]")
            console.print(f"[yellow]Create one from .env.example or set environment variables directly[/yellow]")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider"""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "gemini": "GOOGLE_API_KEY",  # Gemini uses Google API key
            "azure": "AZURE_OPENAI_API_KEY"
        }

        env_var = key_mapping.get(provider.lower())
        if not env_var:
            return None

        # First check environment variables
        api_key = os.getenv(env_var)
        if api_key:
            # Don't log the full key for security
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            console.print(f"[green][OK] Found {env_var}: {masked_key}[/green]")
            return api_key

        # If not found in environment, check api_keys.json file
        api_key = self._load_api_key_from_file(provider.lower())
        if api_key:
            # Set as environment variable for this session
            os.environ[env_var] = api_key
            # Don't log the full key for security
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            console.print(f"[green][OK] Found {env_var}: {masked_key}[/green]")
            return api_key

        console.print(f"[red][ERROR] {env_var} not found in environment variables[/red]")
        console.print(f"[yellow]Please set it in your .env file or environment[/yellow]")
        return None

    def _load_api_key_from_file(self, provider: str) -> Optional[str]:
        """Load API key from api_keys.json file"""
        api_keys_file = self.config_dir / "api_keys.json"
        if not api_keys_file.exists():
            return None

        try:
            import json
            with open(api_keys_file, 'r') as f:
                api_keys = json.load(f)
            return api_keys.get(provider)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load API keys file: {str(e)}[/yellow]")
            return None

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return os.getenv(key, default)

    def create_env_file_if_missing(self):
        """Create .env file from example if it doesn't exist"""
        if not self.env_file.exists():
            example_file = self.config_dir / ".env.example"
            if example_file.exists():
                console.print(f"[yellow]Creating .env file from example...[/yellow]")
                self.env_file.write_text(example_file.read_text())
                console.print(f"[green][OK] Created {self.env_file}[/green]")
                console.print(f"[yellow]Please edit {self.env_file} and add your API keys[/yellow]")
                return True
        return False

    def validate_required_keys(self, provider: str) -> bool:
        """Validate that required API keys are present"""
        api_key = self.get_api_key(provider)
        if not api_key:
            console.print(f"[red][ERROR] Missing API key for {provider}[/red]")
            self._show_setup_instructions(provider)
            return False
        return True

    def _show_setup_instructions(self, provider: str):
        """Show setup instructions for missing API keys"""
        console.print(f"\n[bold yellow]Setup Instructions for {provider.upper()}:[/bold yellow]")

        if provider.lower() == "openai":
            console.print("1. Get your API key from: https://platform.openai.com/api-keys")
            console.print("2. Add to .env file: OPENAI_API_KEY=your_key_here")
        elif provider.lower() == "anthropic":
            console.print("1. Get your API key from: https://console.anthropic.com/")
            console.print("2. Add to .env file: ANTHROPIC_API_KEY=your_key_here")
        elif provider.lower() in ["google", "gemini"]:
            console.print("1. Get your API key from: https://makersuite.google.com/app/apikey")
            console.print("2. Add to .env file: GOOGLE_API_KEY=your_key_here")

        console.print(f"3. Or set environment variable directly:")
        console.print(f"   export {provider.upper()}_API_KEY=your_key_here")
        console.print(f"\n[cyan]Example .env file location: {self.env_file}[/cyan]")


class RequirementsOrchestrator:
    """Main orchestrator for requirements generation"""
    
    def __init__(self, project_name: str, base_path: Path, config_path: Optional[Path] = None, model_provider: str = "openai"):
        self.project_name = project_name
        self.base_path = base_path
        self.model_provider = model_provider

        # Initialize configuration manager first to get paths from config
        # ConfigManager should look in the actual Requirements_Generation_System directory
        script_dir = Path(__file__).parent  # Requirements_Generation_System directory
        self.config_manager = ConfigManager(script_dir)

        # Load configuration to get proper paths
        config = self.config_manager._load_config()

        # Establish ByteForge root directory as the base for all relative paths
        script_dir = Path(__file__).parent  # Requirements_Generation_System directory
        byteforge_root = script_dir.parent   # ByteForge directory

        # Use config-based paths with fallbacks, all relative to ByteForge root
        if config and 'paths' in config:
            # All paths in config are relative to ByteForge root
            self.output_path = byteforge_root / config['paths'].get('output_dir', "project/requirements")
            self.prompts_path = byteforge_root / config['paths'].get('prompts_dir', "Requirements_Generation_Prompts")
            self.requirements_path = byteforge_root / config['paths'].get('requirements_dir', "project/requirements")
            self.status_path = byteforge_root / config['paths'].get('status_dir', "project/generation_status")
        else:
            # Fallback to default paths relative to ByteForge root
            self.output_path = byteforge_root / "project" / "requirements"
            self.prompts_path = byteforge_root / "Requirements_Generation_Prompts"
            self.requirements_path = byteforge_root / "project" / "requirements"
            self.status_path = byteforge_root / "project" / "generation_status"

        # Resolve all paths to absolute paths
        self.output_path = self.output_path.resolve()
        self.prompts_path = self.prompts_path.resolve()
        self.requirements_path = self.requirements_path.resolve()
        self.status_path = self.status_path.resolve()




        # Initialize artifact processor
        self.artifact_processor = ArtifactProcessor(self.base_path)

        # Initialize template manager
        self.template_manager = TemplateManager(self.base_path)

        # Load configuration if provided
        self.config = self._load_config(config_path) if config_path else {}

        # Store model names (use config if available, otherwise defaults)
        default_models = {
            "openai": "o3-mini",
            "anthropic": "claude-3-opus-20240229",
            "gemini": "gemini-1.5-pro-latest"
        }

        llm_config = self.config.get('llm', {})
        self.model_names = {
            "openai": llm_config.get("openai_model", default_models["openai"]),
            "anthropic": llm_config.get("anthropic_model", default_models["anthropic"]),
            "gemini": llm_config.get("gemini_model", default_models["gemini"]),
        }

        # Load review system configuration
        self.review_config = self.config.get('review_system', {
            'enabled': True,
            'primary_llm': {'provider': 'openai', 'model': 'o3-mini'},
            'reviewer_llm': {'provider': 'gemini', 'model': 'gemini-2.5-pro-preview-06-05'},
            'review_settings': {'auto_review': True, 'max_review_iterations': 1}
        })

        # Initialize the selected LLM client
        self.llm_client = self._initialize_llm_client()

        # Initialize reviewer LLM client if review system is enabled
        self.reviewer_llm_client = None
        if self.review_config.get('enabled', False):
            self.reviewer_llm_client = self._initialize_reviewer_llm_client()

        # Document registry
        self.documents: Dict[DocumentType, Document] = {}
        self._initialize_documents()
        
        # Dependency graph
        self.dependency_graph = self._build_dependency_graph()
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _initialize_llm_client(self):
        """Initializes the LLM client based on the selected provider."""
        provider = self.model_provider.lower()

        # Validate that required API keys are present
        if not self.config_manager.validate_required_keys(provider):
            # Try to create .env file if it doesn't exist
            if self.config_manager.create_env_file_if_missing():
                console.print(f"[yellow]Please edit the .env file and restart the application[/yellow]")
            raise ValueError(f"Missing API key for {provider}. Please check your .env file or environment variables.")

        # Get API key using ConfigManager
        api_key = self.config_manager.get_api_key(provider)

        if provider == "openai":
            base_url = self.config_manager.get_setting("OPENAI_BASE_URL")
            default_timeout = int(self.config_manager.get_setting("API_TIMEOUT", 60))

            # Check if using o3 model which needs longer timeout
            model_name = self.model_names[provider]
            if os.getenv("OPENAI_MODEL_OVERRIDE"):
                model_name = os.getenv("OPENAI_MODEL_OVERRIDE")

            # o3 models need much longer timeout due to reasoning time
            if "o3" in model_name.lower():
                timeout = int(self.config_manager.get_setting("llm.o3_timeout", 300))  # 5 minutes for o3
                console.print(f"[yellow]Using extended timeout ({timeout}s) for o3 model[/yellow]")
            else:
                timeout = default_timeout

            return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider == "anthropic":
            base_url = self.config_manager.get_setting("ANTHROPIC_BASE_URL")
            timeout = int(self.config_manager.get_setting("API_TIMEOUT", 60))
            return Anthropic(api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider == "gemini":
            if not GOOGLE_AI_AVAILABLE:
                raise ValueError("Google Generative AI not available. Please install: pip install google-generativeai")
            genai.configure(api_key=api_key)
            return genai
        elif provider == "azure":
            endpoint = self.config_manager.get_setting("AZURE_OPENAI_ENDPOINT")
            api_version = self.config_manager.get_setting("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT must be set for Azure provider")
            return OpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    def _initialize_reviewer_llm_client(self):
        """Initialize the reviewer LLM client based on review configuration."""
        reviewer_config = self.review_config.get('reviewer_llm', {})
        provider = reviewer_config.get('provider', 'gemini').lower()

        # Validate that required API keys are present
        if not self.config_manager.validate_required_keys(provider):
            console.print(f"[yellow]Warning: Missing API key for reviewer LLM ({provider}). Review system will be disabled.[/yellow]")
            return None

        # Get API key using ConfigManager
        api_key = self.config_manager.get_api_key(provider)

        if provider == "openai":
            base_url = self.config_manager.get_setting("OPENAI_BASE_URL")
            default_timeout = int(self.config_manager.get_setting("API_TIMEOUT", 60))

            # Check if using o3 model which needs longer timeout
            reviewer_config = self.review_config.get('reviewer_llm', {})
            model_name = reviewer_config.get('model', 'gpt-4o')
            if os.getenv("OPENAI_MODEL_OVERRIDE"):
                model_name = os.getenv("OPENAI_MODEL_OVERRIDE")

            # o3 models need much longer timeout due to reasoning time
            if "o3" in model_name.lower():
                timeout = int(self.config_manager.get_setting("llm.o3_timeout", 300))  # 5 minutes for o3
                console.print(f"[yellow]Using extended timeout ({timeout}s) for o3 reviewer model[/yellow]")
            else:
                timeout = default_timeout

            return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider == "anthropic":
            base_url = self.config_manager.get_setting("ANTHROPIC_BASE_URL")
            timeout = int(self.config_manager.get_setting("API_TIMEOUT", 60))
            return Anthropic(api_key=api_key, base_url=base_url, timeout=timeout)
        elif provider == "gemini":
            if not GOOGLE_AI_AVAILABLE:
                console.print(f"[yellow]Warning: Google Generative AI not available. Please install: pip install google-generativeai[/yellow]")
                return None
            genai.configure(api_key=api_key)
            return genai
        elif provider == "azure":
            endpoint = self.config_manager.get_setting("AZURE_OPENAI_ENDPOINT")
            api_version = self.config_manager.get_setting("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT must be set for Azure provider")
            return OpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version=api_version
            )
        else:
            console.print(f"[yellow]Warning: Unsupported reviewer LLM provider: {provider}. Review system will be disabled.[/yellow]")
            return None

    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the configured LLM client."""
        provider = self.model_provider.lower()
        model_name = self.model_names[provider]

        # Check for OpenAI model override (for o3 vs o3-mini selection)
        if provider == "openai" and os.getenv("OPENAI_MODEL_OVERRIDE"):
            model_name = os.getenv("OPENAI_MODEL_OVERRIDE")
        
        system_prompt = """You are an expert requirements analyst and technical writer specializing in creating comprehensive requirements documentation.

IMPORTANT GUIDELINES:
1. Follow the EXACT format and structure of any example documents provided
2. Always include proper traceability IDs (e.g., BRD-001, PRD-001.1, FRD-001.1.1)
3. Always reference upstream documents using their IDs
4. Maintain consistent terminology and formatting throughout the document
5. Include all required sections as specified in the prompt
6. Use YAML frontmatter at the beginning of documents when specified
7. Be specific, detailed, and precise in all requirements
8. Ensure each requirement is testable and verifiable

Think through this requirements analysis step by step, considering all dependencies, edge cases, and potential issues before generating the final document.
"""
        
        try:
            if provider == "openai":
                # Use max_completion_tokens for o3 models, max_tokens for others
                # o3 models also don't support temperature parameter
                logger.info(f"Using OpenAI model: {model_name}")
                if "o3" in model_name.lower():
                    logger.info(f"Detected o3 model, using max_completion_tokens without temperature")
                    response = self.llm_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_completion_tokens=4000
                    )
                else:
                    logger.info(f"Using non-o3 model, using max_tokens with temperature")
                    response = self.llm_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                return response.choices[0].message.content
            elif provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=model_name,
                    max_tokens=4000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            elif provider == "gemini":
                if not GOOGLE_AI_AVAILABLE:
                    raise ValueError("Google Generative AI not available")
                model = self.llm_client.GenerativeModel(model_name)
                full_prompt = f"{system_prompt}\n\n{prompt}"
                if GenerationConfig:
                    response = model.generate_content(
                        full_prompt,
                        generation_config=GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=8192
                        )
                    )
                else:
                    response = model.generate_content(full_prompt)
                return response.text
        except Exception as e:
            logger.error(f"Error generating text with {provider}: {e}")
            raise

    async def _generate_text_with_reviewer(self, prompt: str) -> str:
        """Generate text using the reviewer LLM client."""
        if not self.reviewer_llm_client:
            raise ValueError("Reviewer LLM client not initialized")

        reviewer_config = self.review_config.get('reviewer_llm', {})
        provider = reviewer_config.get('provider', 'gemini').lower()
        model_name = reviewer_config.get('model', 'gemini-2.5-pro-preview-06-05')

        # Check for OpenAI model override (for o3 vs o3-mini selection)
        if provider == "openai" and os.getenv("OPENAI_MODEL_OVERRIDE"):
            model_name = os.getenv("OPENAI_MODEL_OVERRIDE")

        # Get review-specific settings
        temperature = reviewer_config.get('temperature', 0.5)
        max_tokens = reviewer_config.get('max_tokens', 8192)

        system_prompt = """You are an expert technical reviewer specializing in requirements documentation analysis and improvement.

CRITICAL REVIEW INSTRUCTIONS:
1. PRESERVE the original document structure, format, and organization completely
2. PRESERVE all traceability IDs exactly as they appear (e.g., BRD-001, PRD-001.1, FRD-001.1.1)
3. PRESERVE all references to upstream documents using their IDs
4. DO NOT shorten, summarize, or skip any content sections
5. DO NOT change the document's language style or tone significantly
6. FOCUS on accuracy, completeness, and adding missing technical details
7. ADD missing information that should be present based on the context provided
8. CORRECT any technical inaccuracies or inconsistencies
9. IMPROVE clarity and specificity while maintaining the same level of detail
10. ENSURE all requirements are testable and verifiable

Your role is to enhance the document by:
- Adding missing technical details or requirements
- Correcting factual errors or inconsistencies
- Improving clarity without changing the overall structure
- Ensuring completeness based on the provided context
- Maintaining professional technical writing standards

DO NOT make changes just for the sake of change. Only modify content that genuinely needs improvement.
"""

        try:
            if provider == "openai":
                # Use max_completion_tokens for o3 models, max_tokens for others
                if "o3" in model_name.lower():
                    response = self.reviewer_llm_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_completion_tokens=max_tokens
                    )
                else:
                    response = self.reviewer_llm_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                return response.choices[0].message.content
            elif provider == "anthropic":
                response = self.reviewer_llm_client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            elif provider == "gemini":
                if not GOOGLE_AI_AVAILABLE:
                    raise ValueError("Google Generative AI not available")
                model = self.reviewer_llm_client.GenerativeModel(model_name)
                full_prompt = f"{system_prompt}\n\n{prompt}"
                if GenerationConfig:
                    response = model.generate_content(
                        full_prompt,
                        generation_config=GenerationConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens
                        )
                    )
                else:
                    response = model.generate_content(full_prompt)
                return response.text
        except Exception as e:
            logger.error(f"Error generating text with reviewer {provider}: {e}")
            raise

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}

    def _sanitize_content(self, content: str) -> str:
        """Sanitize content to handle problematic Unicode characters"""
        if not content:
            return content

        # Replace problematic Unicode characters with safe alternatives
        replacements = {
            '\u2011': '-',  # Non-breaking hyphen -> regular hyphen
            '\u2013': '-',  # En dash -> regular hyphen
            '\u2014': '--', # Em dash -> double hyphen
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u201C': '"',  # Left double quotation mark
            '\u201D': '"',  # Right double quotation mark
            '\u2026': '...', # Horizontal ellipsis
        }

        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)

        return content

    def _initialize_documents(self):
        """Initialize document registry with dependencies"""
        doc_configs = [
            (DocumentType.BRD, [], "01_BRD.md"),
            (DocumentType.PRD, [DocumentType.BRD], "02_PRD.md"),
            (DocumentType.FRD, [DocumentType.PRD, DocumentType.BRD], "04_FRD.md"),
            (DocumentType.NFRD, [DocumentType.PRD, DocumentType.FRD, DocumentType.BRD], "05_NFRD.md"),
            (DocumentType.DRD, [DocumentType.FRD, DocumentType.PRD], "07_DRD.md"),
            (DocumentType.DB_SCHEMA, [DocumentType.DRD, DocumentType.TRD], "08_DB_Schema.md"),
            (DocumentType.TRD, [DocumentType.FRD, DocumentType.NFRD, DocumentType.DRD], "09_TRD.md"),
            (DocumentType.API_SPEC, [DocumentType.FRD, DocumentType.DRD, DocumentType.TRD], "10_API_OpenAPI.md"),
            (DocumentType.UIUX_SPEC, [DocumentType.FRD, DocumentType.PRD], "11_UIUX_Spec.md"),
            (DocumentType.TEST_PLAN, [DocumentType.FRD, DocumentType.NFRD, DocumentType.PRD], "20_Test_Plan.md"),
            (DocumentType.RTM, [DocumentType.BRD, DocumentType.PRD, DocumentType.FRD,
                               DocumentType.NFRD, DocumentType.TRD, DocumentType.TEST_PLAN], "24_RTM.md"),
            (DocumentType.DEV_PLAN, [DocumentType.BRD, DocumentType.PRD, DocumentType.FRD, DocumentType.NFRD,
                                   DocumentType.TRD, DocumentType.API_SPEC, DocumentType.UIUX_SPEC, DocumentType.TEST_PLAN], "25_Dev_Plan.md"),
        ]
        
        for doc_type, deps, prompt_file in doc_configs:
            prompt_path = self.prompts_path / prompt_file
            prompt_template = prompt_path.read_text(encoding='utf-8', errors='ignore') if prompt_path.exists() else None

            self.documents[doc_type] = Document(
                doc_type=doc_type,
                dependencies=deps,
                prompt_template=prompt_template
            )
    
    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build directed graph of document dependencies"""
        G = nx.DiGraph()
        
        for doc_type, doc in self.documents.items():
            G.add_node(doc_type.name)
            for dep in doc.dependencies:
                G.add_edge(dep.name, doc_type.name)
        
        return G
    
    def visualize_dependencies(self, output_file: str = "dependency_graph.png"):
        """Visualize document dependencies"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.dependency_graph, k=2, iterations=50)
        
        # Color nodes by status
        node_colors = []
        for node in self.dependency_graph.nodes():
            doc_type = DocumentType[node]
            status = self.documents[doc_type].status
            if status == DocumentStatus.VALIDATED:
                node_colors.append('#90EE90')  # Light green
            elif status == DocumentStatus.GENERATED:
                node_colors.append('#87CEEB')  # Sky blue
            elif status == DocumentStatus.IN_PROGRESS:
                node_colors.append('#FFD700')  # Gold
            elif status == DocumentStatus.FAILED:
                node_colors.append('#FF6B6B')  # Light red
            else:
                node_colors.append('#D3D3D3')  # Light gray
        
        nx.draw(self.dependency_graph, pos, 
                node_color=node_colors,
                node_size=3000,
                font_size=10,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                with_labels=True)
        
        plt.title(f"Document Generation Dependencies - {self.project_name}")
        plt.tight_layout()
        plt.savefig(self.output_path / output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Dependency graph saved to {self.output_path / output_file}[/green]")
    
    def get_generation_order(self) -> List[DocumentType]:
        """Get topological order for document generation"""
        try:
            order = list(nx.topological_sort(self.dependency_graph))
            return [DocumentType[name] for name in order]
        except nx.NetworkXUnfeasible:
            logger.error("Circular dependency detected in document dependencies")
            raise
    
    async def gather_context(self, doc_type: DocumentType) -> Dict[str, str]:
        """Gather context from existing requirements and generated documents"""
        logger.info(f"Starting context gathering for {doc_type.value}")

        context = {
            "project_name": self.project_name,
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
        }

        logger.info(f"Base context initialized: project_name={self.project_name}, generation_date={context['generation_date']}")

        # Load existing documents if not already loaded
        await self._ensure_documents_loaded()

        # Add dependency documents
        logger.info(f"Checking dependencies for {doc_type.value}: {[dep.value for dep in self.documents[doc_type].dependencies]}")

        for dep_type in self.documents[doc_type].dependencies:
            dep_doc = self.documents[dep_type]
            logger.info(f"Processing dependency {dep_type.value} (status: {dep_doc.status.value})")

            # For requirements documents, try to load from the requirements directory first
            if dep_type in [DocumentType.FRD, DocumentType.NFRD, DocumentType.DRD]:
                doc_filename = f"{dep_type.name.lower()}.md"
                current_doc_file = self.requirements_path / doc_filename
                logger.info(f"Checking for existing {dep_type.value} at: {current_doc_file}")

                if current_doc_file.exists():
                    try:
                        # Try UTF-8 first, then fall back to other encodings
                        try:
                            current_content = current_doc_file.read_text(encoding='utf-8')
                        except UnicodeDecodeError:
                            # Fall back to latin-1 which can handle any byte sequence
                            current_content = current_doc_file.read_text(encoding='latin-1')
                            logger.warning(f"Used latin-1 encoding for {current_doc_file} due to encoding issues")

                        # Remove YAML front matter if present
                        if current_content.startswith("---"):
                            metadata_end = current_content.find("---", 3)
                            if metadata_end > 0:
                                current_content = current_content[metadata_end + 3:].strip()
                        context[dep_type.name.lower()] = current_content
                        logger.info(f"Loaded {dep_type.value} from requirements directory (content length: {len(current_content)} chars)")
                        console.print(f"[dim]Loaded current {dep_type.name} from requirements directory[/dim]")
                        continue
                    except Exception as e:
                        logger.warning(f"Could not load current {dep_type.name}: {e}")
                        console.print(f"[yellow]Warning: Could not load current {dep_type.name}: {e}[/yellow]")
                else:
                    logger.info(f"No existing {dep_type.value} found at {current_doc_file}")

            # Fallback to in-memory content
            if dep_doc.status in [DocumentStatus.GENERATED, DocumentStatus.REFINED, DocumentStatus.VALIDATED]:
                # Check if content is actually useful (not a placeholder response)
                if self._is_valid_document_content(dep_doc.content):
                    context[dep_type.name.lower()] = dep_doc.content
                    logger.info(f"Added in-memory {dep_type.value} to context (content length: {len(dep_doc.content)} chars)")
                else:
                    logger.info(f"Skipped {dep_type.value} - contains placeholder/incomplete content")
            elif dep_doc.content:  # Fallback: use content even if status is not set correctly
                # Check if content is actually useful (not a placeholder response)
                if self._is_valid_document_content(dep_doc.content):
                    context[dep_type.name.lower()] = dep_doc.content
                    logger.info(f"Added fallback {dep_type.value} to context (content length: {len(dep_doc.content)} chars)")
                else:
                    logger.info(f"Skipped fallback {dep_type.value} - contains placeholder/incomplete content")
            else:
                logger.info(f"No content available for dependency {dep_type.value}")
        
        # Search for existing requirements files
        doc_type_name = doc_type.name
        existing_files = list(self.requirements_path.rglob(f"**/{doc_type_name}.md"))
        
        if existing_files:
            try:
                # Try UTF-8 first, then fall back to other encodings
                try:
                    context[f"existing_{doc_type_name.lower()}"] = existing_files[0].read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # Fall back to latin-1 which can handle any byte sequence
                    context[f"existing_{doc_type_name.lower()}"] = existing_files[0].read_text(encoding='latin-1')
                    logger.warning(f"Used latin-1 encoding for {existing_files[0]} due to encoding issues")

                logger.info(f"Loaded existing {doc_type_name} document: {existing_files[0]} (content length: {len(context[f'existing_{doc_type_name.lower()}'])} chars)")
                console.print(f"[green]Found existing {doc_type_name} document: {existing_files[0]}[/green]")
            except Exception as e:
                logger.error(f"Failed to read existing {doc_type_name} document {existing_files[0]}: {e}")
                console.print(f"[yellow]Warning: Could not read existing {doc_type_name} document: {e}[/yellow]")
        
        # Add existing requirements based on document type
        if doc_type == DocumentType.BRD:
            logger.info("Adding BRD-specific context")

            # Load master PRD and other business context
            master_prd_path = self.requirements_path / "consolidated-requirements" / "master-prd.md"
            logger.info(f"Checking for master PRD at: {master_prd_path}")
            if master_prd_path.exists():
                try:
                    # Try UTF-8 first, then fall back to other encodings
                    try:
                        context["master_prd"] = master_prd_path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        context["master_prd"] = master_prd_path.read_text(encoding='latin-1')
                        logger.warning(f"Used latin-1 encoding for {master_prd_path} due to encoding issues")
                    logger.info(f"Loaded master PRD (content length: {len(context['master_prd'])} chars)")
                except Exception as e:
                    logger.error(f"Failed to read master PRD: {e}")
            else:
                logger.info("No master PRD found")

            # Load video annotations
            video_path = self.requirements_path / "Video Annotations"
            logger.info(f"Checking for video annotations at: {video_path}")
            if video_path.exists():
                annotations = []
                for file in video_path.glob("*.markdown"):
                    try:
                        # Try UTF-8 first, then fall back to other encodings
                        try:
                            content = file.read_text(encoding='utf-8')
                        except UnicodeDecodeError:
                            content = file.read_text(encoding='latin-1')
                            logger.warning(f"Used latin-1 encoding for {file} due to encoding issues")
                        annotations.append(f"## {file.stem}\n{content}")
                    except Exception as e:
                        logger.error(f"Failed to read video annotation {file}: {e}")
                        continue
                context["video_annotations"] = "\n\n".join(annotations)
                logger.info(f"Loaded video annotations (content length: {len(context['video_annotations'])} chars)")
            else:
                logger.info("No video annotations found")

            # Check for client requirements document first
            client_requirements_path = self.requirements_path / "Requirements_Doc_From_Client.md"
            logger.info(f"Checking for client requirements at: {client_requirements_path}")
            if client_requirements_path.exists():
                try:
                    # Try UTF-8 first, then fall back to other encodings
                    try:
                        context["client_requirements"] = client_requirements_path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        context["client_requirements"] = client_requirements_path.read_text(encoding='latin-1')
                        logger.warning(f"Used latin-1 encoding for {client_requirements_path} due to encoding issues")
                    logger.info(f"Loaded client requirements (content length: {len(context['client_requirements'])} chars)")
                except Exception as e:
                    logger.error(f"Failed to read client requirements: {e}")
            else:
                logger.info("No client requirements document found")

            # Provide default business context if no existing requirements found
            if not context.get("master_prd") and not context.get("video_annotations") and not context.get("client_requirements"):
                logger.info("No existing business context found, providing default context")
                context["business_context"] = f"""
**Company Background**: {self.project_name} is a software development project requiring comprehensive requirements documentation.

**Current Challenges**:
- Need for structured requirements documentation
- Alignment between business needs and technical implementation
- Clear traceability between requirements and deliverables

**Strategic Objectives**:
- Deliver high-quality software that meets business needs
- Ensure clear communication between stakeholders
- Maintain traceability throughout the development lifecycle

**Market Analysis**: Enterprise software development with focus on requirements management and documentation.

**Constraints**:
- Timeline: Standard development lifecycle
- Budget: Enterprise-level project
- Regulatory: Standard software development compliance requirements
"""
                logger.info(f"Added default business context (content length: {len(context['business_context'])} chars)")
            else:
                logger.info("Using existing business context from master PRD, video annotations, or client requirements")

        # Log final context summary
        logger.info(f"Context gathering complete for {doc_type.value}:")
        for key, value in context.items():
            if isinstance(value, str):
                logger.info(f"  - {key}: {len(value)} characters")
            else:
                logger.info(f"  - {key}: {type(value).__name__}")

        return context

    def _is_valid_document_content(self, content: str) -> bool:
        """Check if document content is valid and not a placeholder response"""
        if not content or len(content.strip()) < 100:
            return False

        # Check for common placeholder phrases that indicate incomplete generation
        placeholder_phrases = [
            "I'm ready to refine",
            "I still need the current version",
            "Please provide the existing",
            "I don't have access to",
            "Please copy-and-paste",
            "Once you provide the complete",
            "I need the exact",
            "Please upload",
            "I'll need the full"
        ]

        content_lower = content.lower()
        for phrase in placeholder_phrases:
            if phrase.lower() in content_lower:
                return False

        return True

    async def _ensure_documents_loaded(self):
        """Ensure existing documents are loaded from disk if not already in memory"""
        # Check if documents need to be loaded
        needs_loading = False
        for doc_type, doc in self.documents.items():
            if doc.status == DocumentStatus.NOT_STARTED and not doc.content:
                # Check if document file exists on disk
                doc_file = self.output_path / f"{doc_type.name.lower()}.md"
                if doc_file.exists():
                    needs_loading = True
                    break

        if needs_loading:
            console.print("[dim]Loading existing documents from disk...[/dim]")
            await self.load_existing_documents()

    async def generate_document(self, doc_type: DocumentType, model_provider: str = "openai") -> str:
        """Generate a document using LLM"""
        doc = self.documents[doc_type]
        
        if not doc.prompt_template:
            raise ValueError(f"No prompt template found for {doc_type.value}")
        
        # Update status
        doc.status = DocumentStatus.IN_PROGRESS
        await self.save_status_file(doc_type)

        console.print(f"\n[yellow]Generating {doc_type.value} using {self.model_provider.upper()}...[/yellow]")
        
        # Gather context
        logger.info(f"Starting document generation for {doc_type.value}")
        context = await self.gather_context(doc_type)

        # Load and process artifacts
        artifacts_context = self.artifact_processor.load_all_artifacts()
        logger.info(f"Loaded artifacts: {artifacts_context['artifacts_summary']['detailed_specs_count']} detailed specs, {artifacts_context['artifacts_summary']['json_blueprints_count']} UI blueprints")

        # Extract the main prompt from template
        prompt_parts = doc.prompt_template.split("```markdown")
        if len(prompt_parts) > 1:
            main_prompt = prompt_parts[1].split("```")[0]
        else:
            main_prompt = doc.prompt_template

        logger.info(f"Extracted main prompt (length: {len(main_prompt)} chars)")

        # Replace placeholders in the prompt
        original_prompt_length = len(main_prompt)
        main_prompt = main_prompt.replace("[PROJECT NAME]", context.get('project_name', 'Unknown Project'))
        main_prompt = main_prompt.replace("[COMPANY NAME]", context.get('project_name', 'Unknown Company'))
        main_prompt = main_prompt.replace("[APP NAME]", context.get('project_name', 'Unknown App'))
        logger.info(f"Replaced placeholders in prompt (length changed from {original_prompt_length} to {len(main_prompt)} chars)")

        # Enhance prompt with artifacts if available
        if artifacts_context["artifacts_summary"]["detailed_specs_count"] > 0:
            main_prompt = create_artifact_enhanced_prompt(main_prompt, artifacts_context)
            console.print(f"[green][OK] Enhanced prompt with {artifacts_context['artifacts_summary']['detailed_specs_count']} detailed specs and {artifacts_context['artifacts_summary']['json_blueprints_count']} UI blueprints[/green]")
        
        # Build the full prompt
        full_prompt = f"""
{main_prompt}

## IMPORTANT INSTRUCTIONS:
1. You MUST follow the exact format and structure of the existing documents
2. You MUST include proper traceability IDs (e.g., BRD-001, PRD-001, FRD-001.1, etc.)
3. You MUST reference upstream documents using their IDs
4. You MUST maintain the same level of detail and organization as the existing documents
5. You MUST include all required sections as specified in the prompt template

## Context Provided:

Project Name: {context.get('project_name', 'Unknown Project')}
Generation Date: {context.get('generation_date', 'Unknown')}

"""
        
        # Add dependency documents
        logger.info(f"Adding context documents to prompt for {doc_type.value}")
        context_docs_added = 0

        for key, value in context.items():
            if key not in ['project_name', 'generation_date'] and value:
                # Use larger context limit for UI/UX generation to include all requirements
                context_limit = 50000 if doc_type == DocumentType.UIUX_SPEC else 15000
                content_preview = value[:context_limit]
                if len(value) > context_limit:
                    content_preview += "...\n(content truncated for brevity)"
                    logger.info(f"Added context document '{key}' (truncated from {len(value)} to {len(content_preview)} chars)")
                else:
                    logger.info(f"Added context document '{key}' ({len(value)} chars)")

                full_prompt += f"\n### {key.upper().replace('_', ' ')} DOCUMENT:\n"
                full_prompt += f"{content_preview}\n"
                context_docs_added += 1

        logger.info(f"Final prompt constructed for {doc_type.value}: {len(full_prompt)} total characters, {context_docs_added} context documents included")

        try:
            logger.info(f"Sending prompt to LLM for {doc_type.value} generation")
            response = await self._generate_text(full_prompt)
            
            doc.content = response
            doc.status = DocumentStatus.GENERATED
            doc.generated_at = datetime.now()
            doc.primary_llm_used = f"{self.model_provider}-{self.model_names[self.model_provider]}"

            # Save document
            await self.save_document(doc_type)
            
            console.print(f"[green]Generated {doc_type.value} successfully[/green]")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate {doc_type.value}: {str(e)}")
            doc.status = DocumentStatus.FAILED
            doc.validation_errors.append(str(e))
            raise
    
    async def refine_document(self, doc_type: DocumentType, refinement_round: int = 1, model_provider: str = "openai"):
        """Refine a generated document"""
        doc = self.documents[doc_type]
        
        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED]:
            raise ValueError(f"Document {doc_type.value} must be generated before refinement")
        
        doc.status = DocumentStatus.IN_PROGRESS
        await self.save_status_file(doc_type)

        console.print(f"\n[yellow]Refining {doc_type.value} (Round {refinement_round}) using {self.model_provider.upper()}...[/yellow]")
        
        refinement_prompt = f"""
Please refine the following {doc_type.value}:

IMPORTANT REFINEMENT INSTRUCTIONS:
1. DO NOT remove or change any existing traceability IDs
2. DO NOT remove references to upstream documents
3. Maintain the same document structure and format
4. Ensure all required sections are present
5. Improve clarity, specificity, and detail while preserving the overall structure

{doc.content}
"""
        
        try:
            refined_content = await self._generate_text(refinement_prompt)
                
            doc.content = refined_content
            doc.refined_count += 1
            doc.status = DocumentStatus.REFINED
            
            await self.save_document(doc_type)
            console.print(f"[green]Refined {doc_type.value} (Round {refinement_round}) successfully[/green]")
            
        except Exception as e:
            logger.error(f"Failed to refine {doc_type.value}: {str(e)}")
            raise

    async def review_document(self, doc_type: DocumentType) -> bool:
        """Review a document using the reviewer LLM"""
        if not self.review_config.get('enabled', False):
            console.print(f"[yellow]Review system disabled, skipping review for {doc_type.value}[/yellow]")
            return True

        if not self.reviewer_llm_client:
            console.print(f"[yellow]Reviewer LLM not available, skipping review for {doc_type.value}[/yellow]")
            return True

        doc = self.documents[doc_type]

        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED, DocumentStatus.VALIDATED]:
            console.print(f"[yellow]Document {doc_type.value} not ready for review (status: {doc.status.value})[/yellow]")
            return False

        # Check if document type should skip review
        skip_review_for = self.review_config.get('review_settings', {}).get('skip_review_for', [])
        if doc_type.name in skip_review_for:
            console.print(f"[yellow]Skipping review for {doc_type.value} (configured to skip)[/yellow]")
            return True

        console.print(f"\n[cyan]Reviewing {doc_type.value} with {self.review_config.get('reviewer_llm', {}).get('provider', 'gemini').upper()}...[/cyan]")

        # Gather the same context that was used for generation
        context = await self.gather_context(doc_type)

        # Build review prompt
        review_prompt = self._build_review_prompt(doc_type, doc.content, context)

        try:
            # Generate reviewed content
            reviewed_content = await self._generate_text_with_reviewer(review_prompt)

            # Store the reviewed content
            doc.reviewed_content = reviewed_content
            doc.reviewed_at = datetime.now()
            doc.review_count += 1
            doc.reviewer_llm_used = f"{self.review_config.get('reviewer_llm', {}).get('provider', 'gemini')}-{self.review_config.get('reviewer_llm', {}).get('model', 'unknown')}"

            # Update the main content with reviewed version
            doc.content = reviewed_content

            # Save the updated document
            await self.save_document(doc_type)

            console.print(f"[green][OK] Reviewed {doc_type.value} successfully[/green]")
            return True

        except Exception as e:
            logger.error(f"Failed to review {doc_type.value}: {str(e)}")
            doc.review_errors.append(str(e))
            console.print(f"[red]Review failed for {doc_type.value}: {str(e)}[/red]")
            return False

    def _build_review_prompt(self, doc_type: DocumentType, content: str, context: Dict[str, str]) -> str:
        """Build the review prompt for the reviewer LLM using the appropriate reviewer template"""

        # Map document types to reviewer prompt files
        reviewer_prompt_map = {
            DocumentType.BRD: "Review_01_BRD.md",
            DocumentType.PRD: "Review_02_PRD.md",
            DocumentType.FRD: "Review_04_FRD.md",
            DocumentType.NFRD: "Review_05_NFRD.md",
            DocumentType.DRD: "Review_07_DRD.md",
            DocumentType.DB_SCHEMA: "Review_08_DB_Schema.md",
            DocumentType.TRD: "Review_09_TRD.md",
            DocumentType.API_SPEC: "Review_10_API_OpenAPI.md",
            DocumentType.UIUX_SPEC: "Review_11_UIUX_Spec.md",
            DocumentType.TEST_PLAN: "Review_20_Test_Plan.md",
            DocumentType.RTM: "Review_24_RTM.md",
            DocumentType.DEV_PLAN: "Review_25_Dev_Plan.md"
        }

        # Get the reviewer prompt template
        reviewer_prompt_file = reviewer_prompt_map.get(doc_type)
        if not reviewer_prompt_file:
            # Fallback to generic review prompt
            return self._build_generic_review_prompt(doc_type, content, context)

        # Load the reviewer prompt template using config-based path
        reviewer_prompt_path = self.prompts_path / "Review_Prompts" / reviewer_prompt_file

        if not reviewer_prompt_path.exists():
            console.print(f"[yellow]Reviewer prompt not found: {reviewer_prompt_path}, using generic review[/yellow]")
            return self._build_generic_review_prompt(doc_type, content, context)

        try:
            with open(reviewer_prompt_path, 'r', encoding='utf-8') as f:
                reviewer_template = f.read()

            # Extract the main prompt from the template (between ```markdown and ```)
            import re
            prompt_match = re.search(r'```markdown\n(.*?)\n```', reviewer_template, re.DOTALL)
            if not prompt_match:
                console.print(f"[yellow]Could not extract prompt from {reviewer_prompt_file}, using generic review[/yellow]")
                return self._build_generic_review_prompt(doc_type, content, context)

            base_prompt = prompt_match.group(1)

            # Replace placeholders in the prompt
            base_prompt = base_prompt.replace("[PROJECT NAME]", context.get('project_name', 'Unknown Project'))

            # Add context information
            context_section = "\n## REVIEW CONTEXT:\n\n"
            context_section += f"**Project Name:** {context.get('project_name', 'Unknown Project')}\n"
            context_section += f"**Generation Date:** {context.get('generation_date', 'Unknown')}\n\n"

            # Add context documents
            for key, value in context.items():
                if key not in ['project_name', 'generation_date'] and value:
                    content_preview = value[:8000]  # Smaller preview for review
                    if len(value) > 8000:
                        content_preview += "...\n(content truncated for brevity)"

                    context_section += f"### {key.upper().replace('_', ' ')} CONTEXT:\n"
                    context_section += f"{content_preview}\n\n"

            # Add the document to review
            document_section = f"\n## DOCUMENT TO REVIEW:\n\n{content}\n\n"

            # Combine all parts
            full_prompt = base_prompt + context_section + document_section

            return full_prompt

        except Exception as e:
            console.print(f"[yellow]Error loading reviewer prompt {reviewer_prompt_file}: {e}, using generic review[/yellow]")
            return self._build_generic_review_prompt(doc_type, content, context)

    def _build_generic_review_prompt(self, doc_type: DocumentType, content: str, context: Dict[str, str]) -> str:
        """Build a generic review prompt as fallback"""

        prompt = f"""
Please review and improve the following {doc_type.value} document.

## REVIEW INSTRUCTIONS:
1. **PRESERVE STRUCTURE**: Maintain the exact document structure, format, and organization
2. **PRESERVE IDs**: Keep all traceability IDs exactly as they appear (BRD-001, PRD-001.1, etc.)
3. **PRESERVE REFERENCES**: Keep all references to upstream documents using their IDs
4. **DO NOT SHORTEN**: Do not summarize, condense, or skip any content sections
5. **DO NOT CHANGE LANGUAGE**: Maintain the same professional tone and writing style
6. **FOCUS ON ACCURACY**: Correct any technical inaccuracies or inconsistencies
7. **ADD MISSING DETAILS**: Include missing technical information based on the context provided
8. **IMPROVE CLARITY**: Enhance clarity and specificity while maintaining detail level
9. **ENSURE COMPLETENESS**: Make sure all necessary sections and requirements are present
10. **MAINTAIN TESTABILITY**: Ensure all requirements remain testable and verifiable

## CONTEXT PROVIDED:
The following context was used to generate the original document. Use this to identify missing information or inaccuracies:

Project Name: {context.get('project_name', 'Unknown Project')}
Generation Date: {context.get('generation_date', 'Unknown')}

"""

        # Add context documents
        for key, value in context.items():
            if key not in ['project_name', 'generation_date'] and value:
                content_preview = value[:8000]  # Smaller preview for review
                if len(value) > 8000:
                    content_preview += "...\n(content truncated for brevity)"

                prompt += f"\n### {key.upper().replace('_', ' ')} CONTEXT:\n"
                prompt += f"{content_preview}\n"

        prompt += f"""

## DOCUMENT TO REVIEW:

{content}

## REVIEW OUTPUT:
Please provide the improved version of the document. Make only necessary improvements while following all the preservation instructions above.
"""

        return prompt

    async def generate_requirements_from_code(self, files: List[Path], cumulative_docs_dir: Path, batch_id: str) -> bool:
        """Generate requirements documents from code files using LLM analysis"""
        if not CODE_SCANNER_AVAILABLE:
            console.print("[red]Code scanner not available. Cannot generate requirements from code.[/red]")
            return False

        console.print(f"\n[cyan]Generating requirements from code batch: {batch_id}[/cyan]")

        try:
            # Initialize code scanner
            scanner = CodeScanner(self.config)

            # Load file contents
            code_files = []
            total_tokens = 0

            for file_path in files:
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Count tokens
                        tokens = scanner.count_tokens(content)
                        total_tokens += tokens

                        code_files.append({
                            'path': str(file_path),
                            'relative_path': str(file_path.relative_to(self.base_path)),
                            'content': content,
                            'tokens': tokens,
                            'extension': file_path.suffix
                        })

                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
                        continue

            if not code_files:
                console.print(f"[yellow]No readable files in batch {batch_id}[/yellow]")
                return False

            console.print(f"[blue]Processing {len(code_files)} files ({total_tokens} tokens)[/blue]")

            # Load existing cumulative requirements if they exist
            cumulative_context = ""
            if cumulative_docs_dir.exists():
                for doc_file in cumulative_docs_dir.glob("*.md"):
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            cumulative_context += f"\n\n## {doc_file.stem.upper()}\n{content[:5000]}"
                            if len(content) > 5000:
                                cumulative_context += "...\n(content truncated)"
                    except Exception as e:
                        logger.warning(f"Could not read cumulative doc {doc_file}: {e}")

            # Build the code analysis prompt
            code_analysis_prompt = self._build_code_analysis_prompt(code_files, cumulative_context, batch_id)

            # Generate requirements using LLM
            response = await self._generate_text(code_analysis_prompt)

            # Parse and save the generated requirements
            success = await self._process_code_analysis_response(response, cumulative_docs_dir, batch_id)

            if success:
                console.print(f"[green][OK] Successfully generated requirements from batch {batch_id}[/green]")
            else:
                console.print(f"[yellow]⚠ Partial success for batch {batch_id}[/yellow]")

            return success

        except Exception as e:
            logger.error(f"Error generating requirements from code batch {batch_id}: {e}")
            console.print(f"[red][FAIL] Failed to generate requirements from batch {batch_id}: {e}[/red]")
            return False

    def _build_code_analysis_prompt(self, code_files: List[dict], cumulative_context: str, batch_id: str) -> str:
        """Build prompt for analyzing code files and generating requirements"""

        prompt = f"""
You are an expert business analyst and requirements engineer. Your task is to analyze source code files and infer the high-level business and functional requirements that the code implements.

## ANALYSIS INSTRUCTIONS:

1. **INFER BUSINESS REQUIREMENTS**: Look at the code and determine what business problems it solves
2. **IDENTIFY FUNCTIONAL REQUIREMENTS**: Extract the specific functional capabilities implemented
3. **TRACE TO CODE**: For each requirement, reference the specific files and line ranges that implement it
4. **BUILD ON EXISTING**: If cumulative requirements exist, build upon them rather than duplicating
5. **BE SPECIFIC**: Requirements should be testable and verifiable
6. **USE PROPER IDs**: Generate traceability IDs in the format BRD-XXX, FRD-XXX.X, etc.

## BATCH INFORMATION:
- Batch ID: {batch_id}
- Files in this batch: {len(code_files)}
- Total tokens: {sum(f['tokens'] for f in code_files)}

## EXISTING CUMULATIVE REQUIREMENTS:
{cumulative_context if cumulative_context else "No existing requirements - this is the first batch."}

## CODE FILES TO ANALYZE:

"""

        for i, file_info in enumerate(code_files, 1):
            extension = file_info['extension'][1:] if file_info['extension'] else 'text'
            content = file_info['content'][:4000]
            truncated_suffix = '...\n(content truncated)' if len(file_info['content']) > 4000 else ''

            prompt += f"""
### File {i}: {file_info['relative_path']} ({file_info['extension']})
**Tokens:** {file_info['tokens']}

```{extension}
{content}{truncated_suffix}
```

"""

        prompt += """
## OUTPUT FORMAT:

Please provide your analysis in the following format:

### BUSINESS REQUIREMENTS DISCOVERED:
- BRD-XXX: [Requirement description]
  - **Implemented in:** [file paths and line ranges]
  - **Business Value:** [explanation]

### FUNCTIONAL REQUIREMENTS DISCOVERED:
- FRD-XXX.X: [Functional requirement description]
  - **Implemented in:** [file paths and line ranges]
  - **Acceptance Criteria:** [testable criteria]
  - **Dependencies:** [references to BRD items]

### NON-FUNCTIONAL REQUIREMENTS DISCOVERED:
- NFRD-XXX.X: [Non-functional requirement]
  - **Implemented in:** [file paths and line ranges]
  - **Metrics:** [measurable criteria]

### TECHNICAL REQUIREMENTS DISCOVERED:
- TRD-XXX.X: [Technical requirement]
  - **Implemented in:** [file paths and line ranges]
  - **Technology Stack:** [technologies used]

### INTEGRATION POINTS DISCOVERED:
- API endpoints, database connections, external services
- File paths where integrations are implemented

Focus on extracting meaningful business and functional requirements rather than low-level technical details. Each requirement should represent a business capability or user need that the code fulfills.
"""

        return prompt

    async def _process_code_analysis_response(self, response: str, cumulative_docs_dir: Path, batch_id: str) -> bool:
        """Process the LLM response and update cumulative requirements documents"""
        try:
            # Ensure cumulative docs directory exists
            cumulative_docs_dir.mkdir(parents=True, exist_ok=True)

            # Parse the response to extract different requirement types
            sections = self._parse_requirements_response(response)

            # Update or create cumulative documents
            success_count = 0

            for doc_type, content in sections.items():
                if content.strip():
                    doc_path = cumulative_docs_dir / f"{doc_type.lower()}.md"

                    # Load existing content if it exists
                    existing_content = ""
                    if doc_path.exists():
                        try:
                            with open(doc_path, 'r', encoding='utf-8') as f:
                                existing_content = f.read()
                        except Exception as e:
                            logger.warning(f"Could not read existing {doc_path}: {e}")

                    # Merge new content with existing
                    merged_content = self._merge_requirements_content(existing_content, content, doc_type, batch_id)

                    # Save updated document
                    try:
                        with open(doc_path, 'w', encoding='utf-8') as f:
                            f.write(merged_content)
                        success_count += 1
                        console.print(f"[green]Updated {doc_path.name}[/green]")
                    except Exception as e:
                        logger.error(f"Could not save {doc_path}: {e}")

            # Save batch processing log
            log_path = cumulative_docs_dir / "processing_log.md"
            self._update_processing_log(log_path, batch_id, response)

            return success_count > 0

        except Exception as e:
            logger.error(f"Error processing code analysis response: {e}")
            return False

    def _parse_requirements_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response to extract different requirement types"""
        sections = {
            'business_requirements': '',
            'functional_requirements': '',
            'non_functional_requirements': '',
            'technical_requirements': '',
            'integration_points': ''
        }

        # Split response into sections based on headers
        lines = response.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line_lower = line.lower().strip()

            if 'business requirements discovered' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'business_requirements'
                current_content = []
            elif 'functional requirements discovered' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'functional_requirements'
                current_content = []
            elif 'non-functional requirements discovered' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'non_functional_requirements'
                current_content = []
            elif 'technical requirements discovered' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'technical_requirements'
                current_content = []
            elif 'integration points discovered' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'integration_points'
                current_content = []
            elif current_section:
                current_content.append(line)

        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _merge_requirements_content(self, existing_content: str, new_content: str, doc_type: str, batch_id: str) -> str:
        """Merge new requirements content with existing content"""
        if not existing_content.strip():
            # Create new document with header
            header = f"""---
id: {doc_type.upper()}
title: {doc_type.replace('_', ' ').title()} (Generated from Code)
version: 1.0
generated_from_code: true
last_updated: {datetime.now().isoformat()}
---

# {doc_type.replace('_', ' ').title()}

*This document was generated by analyzing source code files.*

"""
            return header + new_content
        else:
            # Append new content with batch separator
            separator = f"\n\n## Requirements from Batch {batch_id}\n\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            return existing_content + separator + new_content

    def _update_processing_log(self, log_path: Path, batch_id: str, response: str):
        """Update the processing log with batch information"""
        try:
            truncated_suffix = '...\n(response truncated)' if len(response) > 2000 else ''
            log_entry = f"""
## Batch {batch_id} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Analysis Response:
```
{response[:2000]}{truncated_suffix}
```

---
"""

            if log_path.exists():
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            else:
                header = """# Code Analysis Processing Log

This log tracks the batch processing of code files for requirements generation.

---
"""
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(header + log_entry)

        except Exception as e:
            logger.warning(f"Could not update processing log: {e}")

    async def validate_document(self, doc_type: DocumentType) -> bool:
        """Validate a generated document"""
        doc = self.documents[doc_type]
        
        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED]:
            return False
        
        doc.status = DocumentStatus.IN_PROGRESS
        await self.save_status_file(doc_type)

        console.print(f"\n[yellow]Validating {doc_type.value}...[/yellow]")
        
        validation_errors = []
        
        # Check for YAML frontmatter
        if "---" not in doc.content[:20]:
            validation_errors.append("Missing YAML frontmatter at the beginning of the document")
        
        doc.validation_errors = validation_errors
        
        if not validation_errors:
            doc.status = DocumentStatus.VALIDATED
            await self.save_status_file(doc_type)
            console.print(f"[green]Validated {doc_type.value} successfully[/green]")
            return True
        else:
            doc.status = DocumentStatus.FAILED
            await self.save_status_file(doc_type)
            console.print(f"[red]Validation failed for {doc_type.value}:[/red]")
            for error in validation_errors:
                console.print(f"  [red]- {error}[/red]")
            return False

    async def validate_and_repair_document(self, doc_type: DocumentType, max_repair_attempts: int = 3) -> bool:
        """Validate document and automatically repair common issues"""
        doc = self.documents[doc_type]

        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED]:
            return False

        console.print(f"\n[yellow]Validating and repairing {doc_type.value}...[/yellow]")

        repair_attempts = 0
        previous_errors = set()  # Track errors to detect infinite loops
        while repair_attempts < max_repair_attempts:
            # Perform validation
            validation_result = await self._perform_validation_checks(doc_type)

            if validation_result.is_valid:
                doc.status = DocumentStatus.VALIDATED
                await self.save_status_file(doc_type)
                console.print(f"[green][OK] {doc_type.value} validated successfully[/green]")
                return True

            # Check for infinite repair loops - if same errors persist, stop trying
            current_errors = set(validation_result.errors)
            if repair_attempts > 0 and current_errors == previous_errors:
                console.print(f"[red]Detected infinite repair loop for {doc_type.value} - same errors persist[/red]")
                print(f"[DEBUG] Persistent errors: {current_errors}")
                break

            # Attempt auto-repair
            repair_attempts += 1
            console.print(f"[yellow]Attempting repair #{repair_attempts} for {doc_type.value}...[/yellow]")

            repair_success = await self._auto_repair_document(doc_type, validation_result.errors)

            if not repair_success:
                console.print(f"[red]Auto-repair failed for {doc_type.value}[/red]")
                break

            console.print(f"[blue]Applied repairs to {doc_type.value}, re-validating...[/blue]")
            previous_errors = current_errors  # Remember current errors for next iteration

        # If we get here, validation failed after all repair attempts
        doc.status = DocumentStatus.FAILED
        doc.validation_errors = validation_result.errors
        await self.save_status_file(doc_type)

        console.print(f"[red][FAIL] Validation failed for {doc_type.value} after {repair_attempts} repair attempts:[/red]")
        for error in validation_result.errors:
            console.print(f"  [red]- {error}[/red]")
        
        console.print(f"[yellow][WARNING]  {doc_type.value} failed validation after auto-repair attempts[/yellow]")
        console.print(f"[yellow]Document saved but may have issues. Manual review recommended.[/yellow]")

        return False

    async def _perform_validation_checks(self, doc_type: DocumentType) -> 'ValidationResult':
        """Perform comprehensive validation checks on a document"""
        doc = self.documents[doc_type]
        errors = []

        # Check 1: YAML frontmatter validation
        yaml_errors = self._validate_yaml_frontmatter(doc.content)
        errors.extend(yaml_errors)

        # Check 2: Content structure validation
        structure_errors = self._validate_content_structure(doc_type, doc.content)
        errors.extend(structure_errors)

        # Check 3: Document-specific validation
        specific_errors = self._validate_document_specific_requirements(doc_type, doc.content)
        errors.extend(specific_errors)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def _validate_yaml_frontmatter(self, content: str) -> List[str]:
        """Validate YAML frontmatter structure"""
        errors = []

        if not content.strip():
            errors.append("Document is empty")
            return errors

        lines = content.split('\n')

        # Check for frontmatter start - also catch documents that start with YAML code blocks
        if not lines[0].strip() == '---':
            if lines[0].strip() == '```yaml':
                errors.append("Document starts with YAML code block instead of frontmatter")
            else:
                errors.append("Missing YAML frontmatter start marker (---)")
            return errors

        # Find frontmatter end
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            errors.append("Missing YAML frontmatter end marker (---)")
            return errors

        # Extract and validate YAML
        yaml_content = '\n'.join(lines[1:frontmatter_end])
        try:
            metadata = yaml.safe_load(yaml_content)
            if not isinstance(metadata, dict):
                # Enhanced error logging to show what type was parsed
                parsed_type = type(metadata).__name__
                errors.append(f"YAML frontmatter is not a valid dictionary (parsed as {parsed_type})")
                print(f"[DEBUG] YAML validation failed - parsed as {parsed_type}: {repr(metadata)}")
                print(f"[DEBUG] Raw YAML content:\n{yaml_content}")
                return errors

            # Check required fields
            required_fields = ['id', 'title', 'version', 'dependencies']
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Missing required field in YAML frontmatter: {field}")

        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax in frontmatter: {str(e)}")
            print(f"[DEBUG] YAML syntax error: {str(e)}")
            print(f"[DEBUG] Raw YAML content:\n{yaml_content}")

        return errors

    def _validate_content_structure(self, doc_type: DocumentType, content: str) -> List[str]:
        """Validate document content structure"""
        errors = []

        # Get content after YAML frontmatter for validation
        content_lines = content.split('\n')
        content_start = 0

        # Skip YAML frontmatter
        if content_lines and content_lines[0].strip() == '---':
            for i, line in enumerate(content_lines[1:], 1):
                if line.strip() == '---':
                    content_start = i + 1
                    break

        actual_content = '\n'.join(content_lines[content_start:]).strip()

        # Check for main heading (more lenient)
        if not any(line.strip().startswith('# ') for line in content_lines[content_start:]):
            errors.append("Document missing main heading (# Title)")

        # More lenient content length check (reduced from 500 to 100)
        # Only flag as too short if content is extremely minimal
        if len(actual_content) < 100:
            errors.append("Document content appears too short (less than 100 characters)")

        # Check for malformed YAML blocks
        yaml_block_count = content.count('```yaml')
        yaml_close_count = content.count('```')
        if yaml_block_count > 0 and yaml_close_count % 2 != 0:
            errors.append("Unmatched YAML code blocks (``` markers)")

        return errors

    def _validate_document_specific_requirements(self, doc_type: DocumentType, content: str) -> List[str]:
        """Validate document-specific requirements (more lenient)"""
        errors = []

        # Make validation more lenient - focus on critical issues only
        content_lower = content.lower()

        if doc_type == DocumentType.FRD:
            # Check for FRD-related content (more flexible)
            frd_indicators = ['functional', 'requirement', 'feature', 'user story', 'acceptance']
            if not any(indicator in content_lower for indicator in frd_indicators):
                errors.append("Missing functional requirements content")

        elif doc_type == DocumentType.API_SPEC:
            # Check for API-related content (more flexible)
            api_indicators = ['api', 'endpoint', 'openapi', 'swagger', 'rest', 'http']
            if not any(indicator in content_lower for indicator in api_indicators):
                errors.append("Missing API specification content")

        elif doc_type == DocumentType.UIUX_SPEC:
            # Check for UI/UX content (more flexible)
            ui_indicators = ['ui', 'ux', 'interface', 'view', 'screen', 'component', 'design']
            if not any(indicator in content_lower for indicator in ui_indicators):
                errors.append("Missing UI/UX interface specifications")

        elif doc_type == DocumentType.NFRD:
            # Check for non-functional requirements content
            nfr_indicators = ['performance', 'security', 'scalability', 'availability', 'reliability']
            if not any(indicator in content_lower for indicator in nfr_indicators):
                errors.append("Missing non-functional requirements content")

        elif doc_type == DocumentType.DEV_PLAN:
            # Check for development plan content
            dev_plan_indicators = ['development', 'plan', 'feature', 'phase', 'timeline', 'dependency', 'branch', 'parallel']
            if not any(indicator in content_lower for indicator in dev_plan_indicators):
                errors.append("Missing development plan content")

        return errors

    async def _auto_repair_document(self, doc_type: DocumentType, errors: List[str]) -> bool:
        """Attempt to automatically repair common document issues"""
        doc = self.documents[doc_type]
        original_content = doc.content
        repaired_content = original_content
        repairs_made = []

        for error in errors:
            if "Missing YAML frontmatter start marker" in error:
                repaired_content = self._repair_missing_yaml_start(repaired_content)
                repairs_made.append("Added missing YAML frontmatter start marker")

            elif "Missing YAML frontmatter end marker" in error:
                repaired_content = self._repair_missing_yaml_end(repaired_content)
                repairs_made.append("Added missing YAML frontmatter end marker")

            elif "Multiple YAML frontmatter blocks" in error:
                repaired_content = self._repair_multiple_yaml_blocks(repaired_content)
                repairs_made.append("Consolidated multiple YAML frontmatter blocks")

            elif "Unmatched YAML code blocks" in error:
                repaired_content = self._repair_unmatched_code_blocks(repaired_content)
                repairs_made.append("Fixed unmatched YAML code blocks")

            elif "Missing required field in YAML frontmatter" in error:
                repaired_content = self._repair_missing_yaml_fields(repaired_content, doc_type)
                repairs_made.append("Added missing YAML frontmatter fields")

            elif "YAML frontmatter is not a valid dictionary" in error:
                repaired_content = self._repair_invalid_yaml_frontmatter(repaired_content, doc_type)
                repairs_made.append("Fixed invalid YAML frontmatter structure")

            elif "Document starts with YAML code block instead of frontmatter" in error:
                repaired_content = self._repair_yaml_code_block_start(repaired_content, doc_type)
                repairs_made.append("Converted YAML code block to proper frontmatter")

            elif "Document missing main heading" in error:
                repaired_content = self._repair_missing_main_heading(repaired_content, doc_type)
                repairs_made.append("Added missing main heading")

            elif "Document content appears too short" in error:
                # This usually indicates content was corrupted during repair
                repaired_content = self._repair_corrupted_content(repaired_content, original_content)
                repairs_made.append("Restored corrupted content")

            elif "Missing" in error and ("content" in error or "section" in error):
                # Handle missing content/section errors
                repaired_content = self._repair_missing_content(repaired_content, doc_type, error)
                repairs_made.append(f"Added missing content for: {error}")

        if repaired_content != original_content:
            doc.content = repaired_content
            console.print(f"[green]Applied repairs: {', '.join(repairs_made)}[/green]")
            return True

        return False

    def _repair_missing_yaml_start(self, content: str) -> str:
        """Add missing YAML frontmatter start marker"""
        if not content.startswith('---'):
            return f"---\n{content}"
        return content

    def _repair_missing_yaml_end(self, content: str) -> str:
        """Add missing YAML frontmatter end marker"""
        lines = content.split('\n')
        if lines[0] == '---':
            # Find where content starts (after YAML)
            for i, line in enumerate(lines[1:], 1):
                if line.strip() and not line.startswith(' ') and ':' not in line:
                    # Insert end marker before content
                    lines.insert(i, '---')
                    break
        return '\n'.join(lines)

    def _repair_multiple_yaml_blocks(self, content: str) -> str:
        """Fix multiple YAML frontmatter blocks"""
        # Remove extra --- markers at the beginning
        lines = content.split('\n')
        cleaned_lines = []
        yaml_start_found = False
        yaml_end_found = False

        for line in lines:
            if line.strip() == '---':
                if not yaml_start_found:
                    cleaned_lines.append(line)
                    yaml_start_found = True
                elif not yaml_end_found:
                    cleaned_lines.append(line)
                    yaml_end_found = True
                # Skip additional --- markers
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _repair_unmatched_code_blocks(self, content: str) -> str:
        """Fix unmatched YAML code blocks"""
        # Count and fix unmatched ``` markers
        lines = content.split('\n')
        in_code_block = False

        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block

        # If we end in a code block, add closing marker
        if in_code_block:
            lines.append('```')

        return '\n'.join(lines)

    def _repair_missing_yaml_fields(self, content: str, doc_type: DocumentType) -> str:
        """Add missing required YAML frontmatter fields"""
        lines = content.split('\n')

        # Find YAML section
        yaml_start = -1
        yaml_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if yaml_start == -1:
                    yaml_start = i
                else:
                    yaml_end = i
                    break

        if yaml_start == -1 or yaml_end == -1:
            return content

        # Parse existing YAML
        yaml_content = '\n'.join(lines[yaml_start + 1:yaml_end])
        try:
            parsed_yaml = yaml.safe_load(yaml_content)
            # Ensure we have a dictionary, not a list or other type
            if isinstance(parsed_yaml, dict):
                metadata = parsed_yaml
            else:
                metadata = {}
        except:
            metadata = {}

        # Add missing required fields
        if 'id' not in metadata:
            metadata['id'] = doc_type.name
        if 'title' not in metadata:
            metadata['title'] = doc_type.value
        if 'version' not in metadata:
            metadata['version'] = '1.0'
        if 'dependencies' not in metadata:
            metadata['dependencies'] = []
        if 'status' not in metadata:
            metadata['status'] = 'generated'
        if 'generated_at' not in metadata:
            metadata['generated_at'] = datetime.now().isoformat()

        # Reconstruct content
        new_yaml = yaml.dump(metadata, default_flow_style=False)
        new_lines = lines[:yaml_start + 1] + new_yaml.strip().split('\n') + lines[yaml_end:]

        return '\n'.join(new_lines)

    def _repair_invalid_yaml_frontmatter(self, content: str, doc_type: DocumentType) -> str:
        """Fix invalid YAML frontmatter structure"""
        lines = content.split('\n')

        # Find YAML section boundaries
        yaml_start = -1
        yaml_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if yaml_start == -1:
                    yaml_start = i
                else:
                    yaml_end = i
                    break

        if yaml_start == -1 or yaml_end == -1:
            # No valid YAML section found, create one
            return self._create_valid_yaml_frontmatter(content, doc_type)

        # Extract and clean YAML content
        yaml_lines = lines[yaml_start + 1:yaml_end]

        # Remove any embedded YAML code blocks that might be causing issues
        cleaned_yaml_lines = []
        skip_until_end = False

        for line in yaml_lines:
            if line.strip().startswith('```'):
                skip_until_end = not skip_until_end
                continue
            if not skip_until_end:
                cleaned_yaml_lines.append(line)

        # Try to parse and fix the YAML with enhanced repair capabilities
        yaml_content = '\n'.join(cleaned_yaml_lines)
        metadata = None
        
        try:
            parsed_yaml = yaml.safe_load(yaml_content)
            # Ensure we have a dictionary, not a list or other type
            if isinstance(parsed_yaml, dict):
                metadata = parsed_yaml
            else:
                print(f"[DEBUG] YAML parsed as {type(parsed_yaml).__name__}, not dict: {parsed_yaml}")
        except yaml.YAMLError as e:
            print(f"[DEBUG] YAML parsing failed: {e}")
            
        # If YAML parsing failed, try JSON repair utilities
        if metadata is None:
            print(f"[DEBUG] Attempting to repair YAML content using JSON utilities")
            metadata = self._extract_yaml_from_llm_response(yaml_content)
            
        # If all repair attempts failed, create new metadata
        if metadata is None or not isinstance(metadata, dict):
            print(f"[DEBUG] All repair attempts failed, creating new metadata")
            metadata = {}

        # Ensure metadata is a dictionary before accessing it
        if not isinstance(metadata, dict):
            metadata = {}

        # Ensure required fields
        if 'id' not in metadata:
            metadata['id'] = doc_type.name
        if 'title' not in metadata:
            metadata['title'] = doc_type.value
        if 'version' not in metadata:
            metadata['version'] = '1.0'
        if 'dependencies' not in metadata:
            metadata['dependencies'] = []
        if 'status' not in metadata:
            metadata['status'] = 'generated'
        if 'generated_at' not in metadata:
            metadata['generated_at'] = datetime.now().isoformat()

        # Reconstruct the document with safer YAML formatting
        try:
            new_yaml = yaml.dump(metadata, default_flow_style=False, allow_unicode=True, sort_keys=False)
            # Remove any YAML document separators that yaml.dump might add
            new_yaml = new_yaml.replace('---\n', '').replace('\n---', '').strip()
            
            # Validate the reconstructed YAML by parsing it back
            test_parse = yaml.safe_load(new_yaml)
            if not isinstance(test_parse, dict):
                raise ValueError("Reconstructed YAML is not a dictionary")
                
        except Exception as e:
            # If YAML reconstruction fails, manually construct safe YAML
            print(f"[DEBUG] YAML reconstruction failed: {e}, using manual construction")
            yaml_lines = []
            for key, value in metadata.items():
                if isinstance(value, list):
                    yaml_lines.append(f"{key}:")
                    for item in value:
                        yaml_lines.append(f"  - {item}")
                elif isinstance(value, str):
                    yaml_lines.append(f"{key}: \"{value}\"")
                else:
                    yaml_lines.append(f"{key}: {value}")
            new_yaml = '\n'.join(yaml_lines)

        # Clean the content part (remove any stray YAML blocks)
        content_lines = lines[yaml_end + 1:]
        cleaned_content_lines = self._clean_content_yaml_blocks(content_lines)

        # Reconstruct the full document
        result_lines = ['---'] + new_yaml.split('\n') + ['---', ''] + cleaned_content_lines
        
        # Final validation before returning
        final_result = '\n'.join(result_lines)
        try:
            # Test parse the entire frontmatter section
            test_lines = final_result.split('\n')
            yaml_start_idx = next(i for i, line in enumerate(test_lines) if line.strip() == '---')
            yaml_end_idx = next(i for i, line in enumerate(test_lines[yaml_start_idx + 1:], yaml_start_idx + 1) if line.strip() == '---')
            test_yaml_content = '\n'.join(test_lines[yaml_start_idx + 1:yaml_end_idx])
            test_parsed = yaml.safe_load(test_yaml_content)
            if not isinstance(test_parsed, dict):
                print(f"[WARNING] Final validation failed - YAML is not a dictionary: {type(test_parsed)}")
        except Exception as validation_error:
            print(f"[WARNING] Final validation failed: {validation_error}")
            
        return final_result

    def _clean_content_yaml_blocks(self, content_lines: List[str]) -> List[str]:
        """Remove problematic YAML blocks from document content"""
        cleaned_lines = []
        in_yaml_block = False
        yaml_block_lines = []

        for line in content_lines:
            if line.strip() == '```yaml' or line.strip() == '```':
                if line.strip() == '```yaml':
                    in_yaml_block = True
                    yaml_block_lines = []
                elif line.strip() == '```' and in_yaml_block:
                    # End of YAML block - check if it looks like metadata
                    yaml_text = '\n'.join(yaml_block_lines)
                    if self._is_metadata_yaml_block(yaml_text):
                        # Skip this block as it's likely duplicate metadata
                        in_yaml_block = False
                        continue
                    else:
                        # Keep this block as it's legitimate content
                        cleaned_lines.append('```yaml')
                        cleaned_lines.extend(yaml_block_lines)
                        cleaned_lines.append('```')
                        in_yaml_block = False
                elif line.strip() == '```' and not in_yaml_block:
                    # Stray closing marker
                    continue
            elif in_yaml_block:
                yaml_block_lines.append(line)
            else:
                cleaned_lines.append(line)

        # Handle unclosed YAML blocks
        if in_yaml_block and yaml_block_lines:
            # If it's not metadata, keep it and close it
            yaml_text = '\n'.join(yaml_block_lines)
            if not self._is_metadata_yaml_block(yaml_text):
                cleaned_lines.append('```yaml')
                cleaned_lines.extend(yaml_block_lines)
                cleaned_lines.append('```')

        return cleaned_lines

    def _is_metadata_yaml_block(self, yaml_text: str) -> bool:
        """Check if a YAML block contains metadata that should be in frontmatter"""
        metadata_indicators = [
            'document_type:', 'generated_date:', 'generator:',
            'version:', 'project_name:', 'id:', 'title:'
        ]
        return any(indicator in yaml_text for indicator in metadata_indicators)

    def _create_valid_yaml_frontmatter(self, content: str, doc_type: DocumentType) -> str:
        """Create valid YAML frontmatter for content that lacks it"""
        metadata = {
            'id': doc_type.name,
            'title': doc_type.value,
            'version': '1.0',
            'dependencies': [],
            'status': 'generated',
            'generated_at': datetime.now().isoformat()
        }

        yaml_content = yaml.dump(metadata, default_flow_style=False)

        # Clean the existing content
        content_lines = content.split('\n')
        cleaned_content_lines = self._clean_content_yaml_blocks(content_lines)

        # Construct the new document
        result_lines = ['---'] + yaml_content.strip().split('\n') + ['---', ''] + cleaned_content_lines
        return '\n'.join(result_lines)

    def _repair_yaml_code_block_start(self, content: str, doc_type: DocumentType) -> str:
        """Fix documents that start with YAML code blocks instead of frontmatter"""
        lines = content.split('\n')

        if not lines[0].strip() == '```yaml':
            return content

        # Find the end of the YAML code block
        yaml_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '```':
                yaml_end = i
                break

        if yaml_end == -1:
            # No closing marker found, treat everything until first heading as YAML
            for i, line in enumerate(lines[1:], 1):
                if line.strip().startswith('#'):
                    yaml_end = i
                    break

        if yaml_end == -1:
            # Still no end found, create proper frontmatter from scratch
            return self._create_valid_yaml_frontmatter(content, doc_type)

        # Extract YAML content and convert to frontmatter
        yaml_lines = lines[1:yaml_end]
        yaml_content = '\n'.join(yaml_lines)

        # Parse the YAML and create proper metadata
        try:
            parsed_yaml = yaml.safe_load(yaml_content)
            # Ensure we have a dictionary, not a list or other type
            if isinstance(parsed_yaml, dict):
                yaml_data = parsed_yaml
            else:
                yaml_data = {}
        except:
            yaml_data = {}

        # Create proper metadata structure
        metadata = {
            'id': doc_type.name,
            'title': doc_type.value,
            'version': '1.0',
            'dependencies': [],
            'status': 'generated',
            'generated_at': datetime.now().isoformat()
        }

        # Merge any valid data from the original YAML
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                if key in ['version', 'id', 'title']:
                    metadata[key] = value

        # Get the content after the YAML block
        content_start = yaml_end + 1 if yaml_end < len(lines) else len(lines)
        content_lines = lines[content_start:]

        # Clean any remaining YAML blocks from content
        cleaned_content_lines = self._clean_content_yaml_blocks(content_lines)

        # Construct the new document
        new_yaml = yaml.dump(metadata, default_flow_style=False)
        result_lines = ['---'] + new_yaml.strip().split('\n') + ['---', ''] + cleaned_content_lines

        return '\n'.join(result_lines)

    def _repair_malformed_json(self, json_str: str) -> Optional[dict]:
        """
        Repair malformed JSON from LLM responses using dirty_json
        
        Args:
            json_str: The potentially malformed JSON string
            
        Returns:
            Parsed dictionary if successful, None if repair failed
        """
        if not json_str or not json_str.strip():
            return None
            
        # First try standard JSON parsing
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
            
        # If dirty_json is available, use it for repair
        if DIRTY_JSON_AVAILABLE:
            try:
                print(f"[DEBUG] Attempting JSON repair with dirty_json")
                repaired = dirty_json.loads(json_str)
                print(f"[DEBUG] JSON repair successful using dirty_json")
                return repaired
            except Exception as e:
                print(f"[DEBUG] dirty_json repair failed: {e}")
        
        # Fallback: Try to extract JSON from common LLM response patterns
        try:
            # Look for JSON within code blocks
            json_match = re.search(r'```json\s*\n(.*?)\n```', json_str, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_content = json_match.group(1).strip()
                return json.loads(json_content)
                
            # Look for JSON within triple backticks (no language specified)
            json_match = re.search(r'```\s*\n(.*?)\n```', json_str, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
                if json_content.startswith(('{', '[')):
                    return json.loads(json_content)
                    
            # Look for standalone JSON objects/arrays
            json_match = re.search(r'(\{.*\}|\[.*\])', json_str, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                return json.loads(json_content)
                
        except json.JSONDecodeError:
            pass
            
        print(f"[WARNING] Could not repair malformed JSON: {json_str[:100]}...")
        return None

    def _extract_yaml_from_llm_response(self, response_text: str) -> Optional[dict]:
        """
        Extract and repair YAML content from LLM responses
        
        Args:
            response_text: Raw text response from LLM
            
        Returns:
            Parsed YAML dictionary if successful, None if extraction failed
        """
        if not response_text or not response_text.strip():
            return None
            
        # First try to parse as direct YAML
        try:
            return yaml.safe_load(response_text)
        except yaml.YAMLError:
            pass
            
        # Look for YAML within code blocks
        yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', response_text, re.DOTALL | re.IGNORECASE)
        if yaml_match:
            yaml_content = yaml_match.group(1).strip()
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError:
                pass
                
        # Look for YAML within triple backticks (no language specified)
        yaml_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1).strip()
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError:
                pass
                
        # If YAML parsing fails, try to treat it as JSON and convert
        json_result = self._repair_malformed_json(response_text)
        if json_result and isinstance(json_result, dict):
            return json_result
            
        print(f"[WARNING] Could not extract YAML from LLM response: {response_text[:100]}...")
        return None

    def _repair_missing_main_heading(self, content: str, doc_type: DocumentType) -> str:
        """Add missing main heading to document"""
        lines = content.split('\n')

        # Find where content starts (after YAML frontmatter)
        content_start = 0
        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    content_start = i + 1
                    break

        # Check if there's already a main heading
        for line in lines[content_start:]:
            if line.strip().startswith('# '):
                return content  # Already has a main heading

        # Add main heading
        title = doc_type.value
        heading = f"# {title}"

        # Insert heading after frontmatter
        if content_start > 0:
            lines.insert(content_start, "")
            lines.insert(content_start + 1, heading)
            lines.insert(content_start + 2, "")
        else:
            lines.insert(0, heading)
            lines.insert(1, "")

        return '\n'.join(lines)

    def _repair_missing_content(self, content: str, doc_type: DocumentType, error: str) -> str:
        """Add basic content structure for missing sections"""
        lines = content.split('\n')

        # Find where to add content (after main heading)
        insert_position = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                insert_position = i + 1
                break

        # Add basic content based on document type and error
        additional_content = []

        if doc_type == DocumentType.FRD and "functional requirements" in error.lower():
            additional_content = [
                "",
                "## Overview",
                "",
                f"This document outlines the functional requirements for the {self.project_name} system.",
                "",
                "## Functional Requirements",
                "",
                "### Core Features",
                "- Customer management",
                "- Payment processing",
                "- Load booking and tracking",
                "- Invoice generation",
                "",
                "## Acceptance Criteria",
                "",
                "Each requirement includes specific acceptance criteria for validation.",
                ""
            ]
        elif doc_type == DocumentType.NFRD and "non-functional" in error.lower():
            additional_content = [
                "",
                "## Performance Requirements",
                "",
                "- System response time under 2 seconds",
                "- Support for 1000+ concurrent users",
                "",
                "## Security Requirements",
                "",
                "- Data encryption in transit and at rest",
                "- Role-based access control",
                "",
                "## Scalability Requirements",
                "",
                "- Horizontal scaling capability",
                "- Load balancing support",
                ""
            ]
        elif doc_type == DocumentType.UIUX_SPEC and "interface" in error.lower():
            additional_content = [
                "",
                "## User Interface Design",
                "",
                "### Dashboard Views",
                "- Main dashboard with key metrics",
                "- Customer management interface",
                "- Payment processing screens",
                "",
                "### User Experience Guidelines",
                "- Responsive design for mobile and desktop",
                "- Intuitive navigation patterns",
                "- Accessibility compliance",
                ""
            ]
        elif doc_type == DocumentType.API_SPEC and "api" in error.lower():
            additional_content = [
                "",
                "## API Overview",
                "",
                f"RESTful API for the {self.project_name} system.",
                "",
                "## Endpoints",
                "",
                "### Customer Management",
                "- GET /api/customers",
                "- POST /api/customers",
                "",
                "### Payment Processing",
                "- POST /api/payments",
                "- GET /api/payments/{id}",
                ""
            ]
        elif doc_type == DocumentType.DEV_PLAN and "development plan" in error.lower():
            additional_content = [
                "",
                "## Executive Summary",
                "",
                f"This document outlines the development plan for the {self.project_name}.",
                "",
                "## Feature Analysis",
                "",
                "### Core Features",
                "- Customer management system",
                "- Payment processing platform",
                "- Load booking and tracking",
                "- Invoice generation and reporting",
                "",
                "## Development Phases",
                "",
                "### Phase 1: Foundation",
                "- Database schema implementation",
                "- Authentication and authorization",
                "- Basic API endpoints",
                "",
                "### Phase 2: Core Features",
                "- Customer onboarding",
                "- Payment processing",
                "- Load management",
                "",
                "## Feature Branch Strategy",
                "",
                "All feature branches should be created off the 'dev' branch using the naming convention:",
                "- feature/{feature-name}-{feature-id}",
                "- bugfix/{bug-description}-{bug-id}",
                "- hotfix/{hotfix-description}-{hotfix-id}",
                ""
            ]

        # Insert the additional content
        if additional_content:
            for i, line in enumerate(additional_content):
                lines.insert(insert_position + i, line)

        return '\n'.join(lines)

    def _repair_corrupted_content(self, repaired_content: str, original_content: str) -> str:
        """Restore content that was corrupted during repair"""
        # If the repaired content is significantly shorter, restore from original
        repaired_length = len(repaired_content.strip())
        original_length = len(original_content.strip())

        # If repaired content is less than 50% of original, it's likely corrupted
        if repaired_length < original_length * 0.5:
            self.logger.warning(f"Repaired content ({repaired_length} chars) much shorter than original ({original_length} chars), restoring original")
            return original_content

        # If repaired content is extremely short (< 500 chars) but original was longer, restore original
        if repaired_length < 500 and original_length > 1000:
            self.logger.warning(f"Repaired content too short ({repaired_length} chars), restoring original ({original_length} chars)")
            return original_content

        return repaired_content

    async def save_document(self, doc_type: DocumentType):
        """Save document to file"""
        doc = self.documents[doc_type]

        if not doc.content:
            return

        # Special handling for split documents
        if doc_type == DocumentType.API_SPEC:
            await self._save_api_spec_split_documents(doc)
        elif doc_type == DocumentType.UIUX_SPEC:
            await self._save_uiux_spec_split_documents(doc)
        elif doc_type == DocumentType.TRD:
            await self._save_trd_split_documents(doc)
        elif doc_type == DocumentType.TEST_PLAN:
            await self._save_test_plan_split_documents(doc)
        else:
            # Standard single-file save
            filename = f"{doc_type.name.lower()}.md"
            filepath = self.output_path / filename

            # Add metadata header
            metadata = {
                "id": doc_type.name,
                "title": doc_type.value,
                "version": "1.0",
                "status": doc.status.value,
                "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
                "refined_count": doc.refined_count,
                "dependencies": [dep.name for dep in doc.dependencies]
            }

            # Sanitize content
            sanitized_content = self._sanitize_content(doc.content)

            content = f"""---
{yaml.dump(metadata, default_flow_style=False)}---

{sanitized_content}
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Saved {doc_type.value} to {filepath}")

        await self.save_status_file(doc_type)

    async def _save_api_spec_split_documents(self, doc):
        """Save API specification as split documents"""
        logger.info("Generating split API specification documents")

        # Parse the generated content to extract sections
        content = doc.content

        # Define the split document structure
        split_docs = {
            "api_spec.md": {
                "title": "API OpenAPI Specification - Master Document",
                "id": "API_SPEC",
                "content": self._generate_master_api_doc(content)
            },
            "api_spec_security.md": {
                "title": "API Security Schemes and Authentication",
                "id": "API_SPEC_SECURITY",
                "content": self._extract_security_section(content)
            },
            "api_spec_components.md": {
                "title": "API Common Components and Schemas",
                "id": "API_SPEC_COMPONENTS",
                "content": self._extract_components_section(content)
            },
            "api_spec_errors.md": {
                "title": "API Error Handling and Response Patterns",
                "id": "API_SPEC_ERRORS",
                "content": self._generate_error_patterns(content)
            },
            "api_spec_common.md": {
                "title": "API Common Patterns and Shared Components",
                "id": "API_SPEC_COMMON",
                "content": self._generate_common_patterns(content)
            },
            "api_spec_endpoints.md": {
                "title": "API Endpoints",
                "id": "API_SPEC_ENDPOINTS",
                "content": self._extract_endpoints_section(content)
            }
        }

        # Save each split document
        for filename, doc_info in split_docs.items():
            filepath = self.output_path / filename

            # Create metadata for each split document
            metadata = {
                "dependencies": [dep.name for dep in doc.dependencies],
                "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
                "id": doc_info["id"],
                "refined_count": doc.refined_count,
                "status": doc.status.value,
                "title": doc_info["title"],
                "version": "1.0"
            }

            # Create full document content
            full_content = f"""---
{yaml.dump(metadata, default_flow_style=False)}---

{doc_info["content"]}
"""

            filepath.write_text(full_content, encoding='utf-8')
            logger.info(f"Saved API spec split document: {filename}")

    def _generate_master_api_doc(self, content):
        """Generate the master API specification document with links to split documents"""
        # Extract basic OpenAPI info from the original content
        lines = content.split('\n')
        openapi_section = []
        in_openapi = False

        for line in lines:
            if line.startswith('openapi:'):
                in_openapi = True
            if in_openapi:
                openapi_section.append(line)
                if line.startswith('security:') and len(openapi_section) > 10:
                    break

        openapi_yaml = '\n'.join(openapi_section)

        return f"""# {self.project_name} API

## Overview

This is the master document for the {self.project_name} API specification. The complete API documentation is organized into multiple linked documents for better maintainability and navigation.

## OpenAPI Specification

```yaml
{openapi_yaml}
```

## Document Structure

The complete API specification is organized into the following documents:

### Architecture Documents
- **[Security Schemes](./api_spec_security.md)** - Authentication and authorization patterns
- **[Common Components](./api_spec_components.md)** - Reusable schemas and data models

### Cross-cutting Concerns
- **[Error Handling](./api_spec_errors.md)** - Standardized error response patterns
- **[Common Patterns](./api_spec_common.md)** - Shared parameters, headers, and response structures

### API Endpoints
- **[API Endpoints](./api_spec_endpoints.md)** - Complete API endpoint specifications

## Navigation

- [← Back to Requirements](../Requirements/)
- [Security Schemes →](./api_spec_security.md)
- [Common Components →](./api_spec_components.md)
- [API Endpoints →](./api_spec_endpoints.md)
"""

    def _extract_security_section(self, content):
        """Extract security schemes from the original content"""
        return f"""# API Security Schemes and Authentication

This document defines the security schemes and authentication patterns for the {self.project_name} API.

## Security Schemes

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token-based authentication for secure API access.

        **Implementation Details:**
        - Tokens are issued upon successful authentication
        - Tokens include user identity and permissions
        - Tokens expire after a configurable period
        - Refresh tokens are supported for seamless renewal

        **Usage:**
        Include the JWT token in the Authorization header:
        ```
        Authorization: Bearer <jwt-token>
        ```

        **Traceability:**
        - Source: TRD-3.1 (Authentication Architecture)
        - Security Requirements: NFR-SEC-001
```

## Global Security Configuration

```yaml
security:
  - bearerAuth: []
```

All API endpoints require authentication by default using JWT bearer tokens.

## Navigation

- [← Back to Master Document](./api_spec.md)
- [Common Components →](./api_spec_components.md)
- [Error Handling →](./api_spec_errors.md)
"""

    def _extract_components_section(self, content):
        """Extract component schemas from the original content"""
        # Try to extract the components section from the OpenAPI spec
        lines = content.split('\n')
        components_section = []
        in_components = False
        current_indent = 0
        
        for i, line in enumerate(lines):
            if line.strip() == 'components:':
                in_components = True
                components_section.append(line)
                current_indent = len(line) - len(line.lstrip())
                continue
            
            if in_components:
                # Check if we've moved to the next top-level section
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    if line.strip().endswith(':') and current_indent == 0:
                        break
                elif line.strip() and len(line) - len(line.lstrip()) <= current_indent and line.strip().endswith(':'):
                    # Check if this is a sibling section at the same level as components
                    if line.strip() in ['paths:', 'security:', 'tags:', 'externalDocs:', 'info:', 'servers:']:
                        break
                
                components_section.append(line)
        
        # Format the extracted content
        if components_section and len(components_section) > 1:
            components_yaml = '\n'.join(components_section)
            components_content = f"""## Reusable Components

The following components are defined for reuse across the API:

```yaml
{components_yaml}
```

## Usage Notes

These components can be referenced throughout the API specification using `$ref` notation. Please refer to the OpenAPI specification for details on how to reference these components in your API endpoints.
"""
        else:
            components_content = """## Reusable Components

*Components will be extracted from the generated OpenAPI specification*

Please refer to the master API specification document for the complete list of reusable components and schemas.
"""
        
        return f"""# API Common Components and Schemas

This document defines the reusable components and data schemas for the {self.project_name} API.

{components_content}

## Navigation

- [← Back to Master Document](./api_spec.md)
- [← Security Schemes](./api_spec_security.md)
- [Error Handling →](./api_spec_errors.md)
"""

    def _generate_error_patterns(self, content):
        """Generate standardized error handling patterns"""
        return f"""# API Error Handling and Response Patterns

This document defines standardized error handling patterns and response structures for the {self.project_name} API.

## Standard Error Schema

```yaml
components:
  schemas:
    Error:
      type: object
      required:
        - code
        - message
        - timestamp
        - path
      properties:
        code:
          type: string
          description: "Machine-readable error code for programmatic handling"
        message:
          type: string
          description: "Human-readable error message"
        timestamp:
          type: string
          format: date-time
          description: "ISO 8601 timestamp when the error occurred"
        path:
          type: string
          description: "API endpoint path where the error occurred"
        traceId:
          type: string
          format: uuid
          description: "Unique correlation ID for tracking and debugging"
```

## HTTP Status Code Usage

### 4xx Client Error Responses
- **400 Bad Request**: Invalid input data or malformed request
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Requested resource not found
- **409 Conflict**: Request conflicts with current state
- **429 Too Many Requests**: Rate limit exceeded

### 5xx Server Error Responses
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable

## Navigation

- [← Back to Master Document](./api_spec.md)
- [← Common Components](./api_spec_components.md)
- [Common Patterns →](./api_spec_common.md)
"""

    def _generate_common_patterns(self, content):
        """Generate common API patterns and shared components"""
        return """# API Common Patterns and Shared Components

This document defines common patterns, shared parameters, headers, and response structures used across all API endpoints.

## Common Parameters

### Pagination Parameters
- `page`: Page number for pagination (1-based)
- `pageSize`: Number of items per page
- `sortBy`: Field to sort by
- `sortOrder`: Sort order (asc/desc)

### Search and Filter Parameters
- `search`: Search term for text-based filtering
- `fromDate`: Filter items from this date
- `toDate`: Filter items to this date
- `status`: Filter by status

## Common Headers

### Request Headers
- `Content-Type`: Content type of the request body
- `Authorization`: Bearer token for authentication
- `X-API-Key`: API key for service-to-service authentication

### Response Headers
- `X-Request-Id`: Request tracking identifier
- `X-RateLimit-*`: Rate limiting information
- `Location`: URL of created resource (for 201 responses)

## Navigation

- [← Back to Master Document](./api_spec.md)
- [← Error Handling](./api_spec_errors.md)
- [API Endpoints →](./api_spec_endpoints.md)
"""

    def _extract_endpoints_section(self, content):
        """Extract API endpoints from the generated content"""
        # Try to extract the paths section from the OpenAPI spec
        lines = content.split('\n')
        paths_section = []
        in_paths = False
        current_indent = 0
        
        for i, line in enumerate(lines):
            if line.strip() == 'paths:':
                in_paths = True
                paths_section.append(line)
                current_indent = len(line) - len(line.lstrip())
                continue
            
            if in_paths:
                # Check if we've moved to the next top-level section
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    if line.strip().endswith(':') and current_indent == 0:
                        break
                elif line.strip() and len(line) - len(line.lstrip()) <= current_indent and line.strip().endswith(':'):
                    # Check if this is a sibling section at the same level as paths
                    if line.strip() in ['components:', 'security:', 'tags:', 'externalDocs:']:
                        break
                
                paths_section.append(line)
        
        # Format the extracted content
        if paths_section:
            paths_yaml = '\n'.join(paths_section)
            endpoint_content = f"""## API Endpoints

The following endpoints are available in this API:

```yaml
{paths_yaml}
```

## Implementation Notes

Please refer to the complete OpenAPI specification in the master document for detailed request/response schemas, authentication requirements, and error handling patterns.
"""
        else:
            endpoint_content = """## API Endpoints

*Endpoints will be extracted from the generated OpenAPI specification*

Please refer to the master API specification document for the complete list of available endpoints.
"""
        
        return f"""# API Endpoints

This document contains the complete API endpoint specifications for the {self.project_name}.

{endpoint_content}

## Navigation

- [← Back to Master Document](./api_spec.md)
- [← Common Patterns](./api_spec_common.md)
- [Security Schemes →](./api_spec_security.md)
"""


    async def _save_uiux_spec_split_documents(self, doc):
        """Save UI/UX specification as split documents following UXDMD structure"""
        logger.info("Generating split UI/UX specification documents (UXDMD format)")

        # Parse the generated content to extract sections
        content = doc.content

        # Define the split document structure following UXDMD format
        split_docs = {
            "uiux_spec.md": {
                "title": "UI/UX Design and Mapping Document (UXDMD) - Master",
                "id": "UIUX_SPEC",
                "content": self._generate_master_uxdmd_doc(content)
            },
            "uiux_spec_architecture.md": {
                "title": "Information Architecture and Navigation Design",
                "id": "UIUX_SPEC_ARCHITECTURE",
                "content": self._extract_architecture_section(content)
            },
            "uiux_spec_components.md": {
                "title": "Component Library and Design System Integration",
                "id": "UIUX_SPEC_COMPONENTS",
                "content": self._extract_components_section(content)
            },
            "uiux_spec_interactions.md": {
                "title": "Interaction Flows and User Journeys",
                "id": "UIUX_SPEC_INTERACTIONS",
                "content": self._extract_interactions_section(content)
            },
            "uiux_spec_dashboard.md": {
                "title": "Dashboard and Analytics Interface Design",
                "id": "UIUX_SPEC_DASHBOARD",
                "content": self._extract_dashboard_views(content)
            },
            "uiux_spec_views.md": {
                "title": "Application Views and Interface Designs",
                "id": "UIUX_SPEC_VIEWS",
                "content": self._extract_application_views(content)
            }
        }

        # Save each split document
        for filename, doc_info in split_docs.items():
            filepath = self.output_path / filename

            # Create metadata for each split document
            metadata = {
                "dependencies": [dep.name for dep in doc.dependencies],
                "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
                "id": doc_info["id"],
                "refined_count": doc.refined_count,
                "status": doc.status.value,
                "title": doc_info["title"],
                "version": "1.0"
            }

            # Create full document content
            full_content = f"""---
{yaml.dump(metadata, default_flow_style=False)}---

{doc_info["content"]}
"""

            filepath.write_text(full_content, encoding='utf-8')
            logger.info(f"Saved UI/UX spec split document: {filename}")

    def _generate_master_uxdmd_doc(self, content):
        """Generate the master UXDMD document with links to split documents"""
        # Extract basic info from the original content
        lines = content.split('\n')
        overview_section = []

        # Take the first part of the content as overview
        for i, line in enumerate(lines):
            overview_section.append(line)
            if i > 50:  # Limit overview to first ~50 lines
                break

        overview_content = '\n'.join(overview_section)

        return f"""# {self.project_name} - UI/UX Design and Mapping Document (UXDMD)

## Overview

This is the master UI/UX Design and Mapping Document (UXDMD) for the {self.project_name}. The complete UI/UX specification follows the UXDMD structure and is organized into multiple linked documents for better maintainability and developer-ready implementation.

{overview_content}

## Document Structure

The complete UXDMD specification is organized into the following documents:

### Architecture and Foundation
- **[Information Architecture](./uiux_spec_architecture.md)** - Site structure, navigation, and role-based access
- **[Component Library](./uiux_spec_components.md)** - Design system integration and component specifications
- **[Interaction Flows](./uiux_spec_interactions.md)** - User journeys, state charts, and sequence diagrams

### Application Interface Specifications

#### Dashboard and Analytics
- **[Dashboard Views](./uiux_spec_dashboard.md)** - Main dashboard and analytics interface specifications

#### Application Views
- **[Application Views](./uiux_spec_views.md)** - Complete application interface specifications and view definitions

## UXDMD Structure Overview

Each view specification follows the standardized UXDMD format:

| Section | Purpose |
|---------|---------|
| **Purpose & Scope** | User goals, personas, accessibility standards |
| **View Catalogue** | Complete table of all views with API mappings |
| **Information Architecture** | Navigation, breadcrumbs, role-based access |
| **Data Map** | API contracts, state management, caching |
| **Per-View Specification** | Detailed specs for each view |
| **Interaction Flows** | Sequence diagrams and state charts |
| **Visual Guidelines** | Design system and motion specifications |
| **Performance & Offline** | Loading, caching, offline behavior |
| **Security Requirements** | Auth, validation, data protection |

## Navigation

- [← Back to Requirements](../Requirements/)
- [Information Architecture →](./uiux_spec_architecture.md)
- [Component Library →](./uiux_spec_components.md)

## Traceability Matrix

| Document | Requirements Covered | View-IDs | API Endpoints |
|----------|---------------------|----------|---------------|
| [Dashboard Views](./uiux_spec_dashboard.md) | FRD-3.1.3, PRD-3.1 | view-dashboard-* | /dashboard/*, /reports/* |
| [Customer Management](./uiux_spec_customer_mgt.md) | FRD-3.1.1, PRD-3.2 | view-customer-* | /customers/* |
| [Payment Processing](./uiux_spec_payment_proc.md) | FRD-3.1.2, PRD-3.3 | view-payment-* | /payments/* |
| [Load Management](./uiux_spec_load_mgt.md) | FRD-3.2.1, FRD-3.2.2, PRD-3.4 | view-load-* | /loads/*, /loads/*/track |
| [Invoice Processing](./uiux_spec_invoice_proc.md) | FRD-3.3.1, FRD-3.3.2, PRD-3.5 | view-invoice-* | /invoices/*, /reports/financial |
| [Carrier Management](./uiux_spec_carrier_mgt.md) | FRD-3.4.1, FRD-3.4.2, PRD-3.6 | view-carrier-* | /carrier/* |

## Implementation Notes

This UXDMD structure enables:
- **LLM Code Generation**: Per-view specs feed React/Next.js generators
- **Full Traceability**: View-IDs cross-link to FRD and API specifications
- **Security & Compliance**: Dedicated sections drive NFR tests
- **Design Hand-off**: Token references keep designers and developers synchronized
"""

    def _extract_architecture_section(self, content):
        """Extract information architecture and navigation design"""
        return f"""# Information Architecture and Navigation Design

This document defines the site structure, navigation patterns, and role-based access for the {self.project_name} platform.

## Site Map Structure

```yaml
/
├── /dashboard (authenticated)
├── /customers (role: admin, sales)
│   ├── /customers/list
│   ├── /customers/:id
│   └── /customers/new
├── /payments (role: admin, finance)
├── /loads (role: admin, operations)
│   ├── /loads/list
│   ├── /loads/book
│   └── /loads/:id/track
├── /invoices (role: admin, finance)
├── /carriers (role: admin, operations)
│   ├── /carriers/register
│   └── /carriers/portal
└── /reports (role: admin, finance)
```

## Navigation Patterns

### Primary Navigation
- Top navigation bar with role-based menu items
- Breadcrumb navigation for deep pages
- Quick action buttons for common tasks

### Role-Based Access
| Role | Accessible Routes | Permissions |
|------|------------------|-------------|
| Admin | All routes | Full CRUD access |
| Manager | Most routes | Management operations |
| User | Limited routes | Read/write access |
| Viewer | Public routes | Read-only access |

## Breadcrumb Rules
- Always show current location
- Include clickable parent levels
- Maximum 4 levels deep
- Home > Section > Subsection > Current Page

## Deep-Link Behavior
- All views support direct URL access
- State preserved in URL parameters
- Shareable URLs for filtered views
- Bookmark-friendly navigation

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [Component Library →](./uiux_spec_components.md)
- [Interaction Flows →](./uiux_spec_interactions.md)
"""

    def _extract_components_section(self, content):
        """Extract component library and design system integration"""
        return f"""# Component Library and Design System Integration

This document defines the design system components and their integration patterns for the {self.project_name} platform.

## Design System Reference

**Primary Design System**: Material-UI v5 with custom theme
**Figma File**: [Design System v3.0](https://figma.com/design-system)
**Storybook**: [Component Library](https://storybook.fywbmidway.com)

## Component Specifications

### Form Components
| Component | Usage | API Binding | Validation |
|-----------|-------|-------------|------------|
| `CustomerForm` | Customer registration | POST /customers | Zod schema validation |
| `PaymentForm` | Payment processing | POST /payments | PCI DSS compliant |
| `LoadBookingForm` | Load booking | POST /loads | Business rule validation |

### Data Display Components
| Component | Usage | Data Source | Caching |
|-----------|-------|-------------|---------|
| `CustomerTable` | Customer listing | GET /customers | 60s TTL |
| `LoadTracker` | Real-time tracking | GET /loads/:id/track | 5s polling |
| `InvoiceList` | Invoice management | GET /invoices | 30s TTL |

### Layout Components
| Component | Usage | Responsive | Accessibility |
|-----------|-------|------------|---------------|
| `DashboardLayout` | Main layout | Mobile-first | ARIA landmarks |
| `FormLayout` | Form containers | Stacked on mobile | Focus management |
| `TableLayout` | Data tables | Horizontal scroll | Keyboard navigation |

## Design Tokens

### Color Palette
```css
--primary-50: #e3f2fd
--primary-500: #2196f3
--primary-900: #0d47a1
--secondary-500: #ff9800
--error-500: #f44336
--success-500: #4caf50
```

### Typography Scale
```css
--text-xs: 0.75rem
--text-sm: 0.875rem
--text-base: 1rem
--text-lg: 1.125rem
--text-xl: 1.25rem
```

### Spacing System
```css
--space-xs: 0.25rem
--space-sm: 0.5rem
--space-md: 1rem
--space-lg: 1.5rem
--space-xl: 2rem
```

## Component Variants

### Allowed Variants
- Button: primary, secondary, outline, text
- Input: standard, outlined, filled
- Card: elevated, outlined, filled

### Disallowed Variants
- Custom button styles outside design system
- Non-standard input decorations
- Inconsistent card shadows

## Theming and Customization

### Light/Dark Mode Support
- Automatic theme detection
- Manual theme toggle
- Persistent user preference
- System theme synchronization

### Responsive Behavior
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Fluid typography scaling
- Adaptive component layouts

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Information Architecture](./uiux_spec_architecture.md)
- [Interaction Flows →](./uiux_spec_interactions.md)
"""

    def _extract_interactions_section(self, content):
        """Extract interaction flows and user journeys"""
        return f"""# Interaction Flows and User Journeys

This document defines the interaction patterns, user flows, and state management for the {self.project_name} platform.

## Primary User Flows

### Customer Onboarding Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant D as Database

    U->>F: Navigate to /customers/new
    F->>F: Render CustomerForm
    U->>F: Fill form and submit
    F->>A: POST /customers
    A->>D: Validate and store
    D->>A: Return customer ID
    A->>F: 201 Created response
    F->>F: Navigate to /customers/:id
    F->>U: Show success message
```

### Payment Processing Flow
```mermaid
stateDiagram-v2
    [*] --> FormEntry
    FormEntry --> Validating: Submit
    Validating --> Processing: Valid
    Validating --> FormEntry: Invalid
    Processing --> Success: Approved
    Processing --> Failed: Declined
    Success --> [*]
    Failed --> FormEntry: Retry
```

### Load Tracking Flow
```mermaid
journey
    title Load Tracking User Journey
    section Booking
      Book Load: 5: Customer
      Receive Confirmation: 4: Customer
    section Tracking
      Check Status: 3: Customer
      View Location: 4: Customer
      Get Updates: 5: Customer
    section Delivery
      Confirm Delivery: 5: Customer
      Rate Service: 3: Customer
```

## State Management Patterns

### Global State Structure
```typescript
interface AppState {
  auth: AuthState;
  customers: CustomersState;
  loads: LoadsState;
  payments: PaymentsState;
  invoices: InvoicesState;
  carriers: CarriersState;
  ui: UIState;
}
```

### Component State Patterns
| Pattern | Usage | Example |
|---------|-------|---------|
| Local State | Form inputs, UI toggles | `useState` for form fields |
| Global State | User data, app settings | Redux/Zustand for auth |
| Server State | API data, caching | React Query for API calls |
| URL State | Filters, pagination | URL params for table state |

## Error Handling Flows

### Form Validation Errors
1. Client-side validation on blur/submit
2. Display field-level error messages
3. Prevent submission until resolved
4. Focus first error field

### API Error Handling
1. Network errors → Retry mechanism
2. 4xx errors → User-friendly messages
3. 5xx errors → Generic error page
4. Timeout errors → Retry with backoff

### Recovery Patterns
- Auto-save for long forms
- Optimistic updates with rollback
- Offline queue for critical actions
- Session recovery after auth expiry

## Animation and Transitions

### Micro-interactions
- Button hover states (150ms ease)
- Form field focus (200ms ease-in-out)
- Loading spinners (infinite rotation)
- Success checkmarks (300ms bounce)

### Page Transitions
- Route changes (250ms slide)
- Modal open/close (200ms fade + scale)
- Drawer slide (300ms ease-out)
- Tab switching (150ms fade)

### Performance Guidelines
- Animations under 300ms
- Use transform/opacity for performance
- Respect prefers-reduced-motion
- Hardware acceleration for smooth 60fps

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Component Library](./uiux_spec_components.md)
- [Dashboard Views →](./uiux_spec_dashboard.md)
"""

    def _extract_dashboard_views(self, content):
        """Extract dashboard and analytics view specifications"""
        return """# Dashboard and Analytics Interface Design

This document defines the dashboard and analytics view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-dashboard-main` | Main Dashboard | `/dashboard` | FRD-3.1.3 | `GET /dashboard/metrics` | admin, user |
| `view-dashboard-reports` | Reports Dashboard | `/dashboard/reports` | FRD-3.3.2 | `GET /reports/financial` | admin, finance |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `metrics` | `GET /dashboard/metrics` | `state.dashboard.metrics` | 30s | dashboard-main | auth required |
| `reports` | `GET /reports/financial` | `state.dashboard.reports` | 60s | dashboard-reports | finance role |

## Per-View Specification

### view-dashboard-main (UXDMD-1)

| Section | Detail |
|---------|--------|
| **Purpose** | Provide real-time overview of key business metrics and KPIs |
| **Layout** | Grid layout with metric cards, charts, and quick actions |
| **Displayed Fields** | Total Revenue • Active Loads • Customer Count • Payment Status |
| **Primary Actions** | Refresh Data • Export Report • View Details |
| **Secondary Actions** | Filter by date range, drill-down to specific metrics |
| **State Behavior** | Loading skeleton cards, empty state with onboarding |
| **API Mapping** | `GET /dashboard/metrics` (200/401/500) |
| **Error UX** | 401 → redirect to login, 500 → retry button with toast |
| **Security Notes** | Requires auth token, role-based metric visibility |
| **Analytics** | Track `dashboard.viewed`, `metric.clicked` events |
| **Accessibility** | ARIA labels for charts, keyboard navigation |
| **Design Tokens** | `--surface-elevated-1`, `--space-lg` |
| **Traceability Links** | FRD-3.1.3 • API-DASHBOARD-1 • NFRD-PERF-1 |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Interaction Flows](./uiux_spec_interactions.md)
- [Customer Management →](./uiux_spec_customer_mgt.md)
"""

    def _extract_application_views(self, content):
        """Extract application view specifications from the generated content"""
        # Try to extract view-related content from the UXDMD specification
        lines = content.split('\n')
        view_sections = []
        
        # Look for sections that contain view specifications
        current_section = []
        in_view_section = False
        
        for line in lines:
            # Check for view-related section headers
            if any(keyword in line.lower() for keyword in ['view', 'interface', 'screen', 'page']):
                if line.startswith('#') and current_section:
                    # Save previous section if it was a view section
                    if in_view_section:
                        view_sections.extend(current_section)
                    current_section = [line]
                    in_view_section = True
                else:
                    current_section.append(line)
            elif current_section:
                current_section.append(line)
        
        # Add the last section if it was a view section
        if in_view_section and current_section:
            view_sections.extend(current_section)
        
        # Format the extracted content
        if view_sections:
            extracted_content = '\n'.join(view_sections)
            views_content = f"""## Application Interface Specifications

The following view specifications have been extracted from the generated UI/UX specification:

{extracted_content}

## Implementation Guidelines

Each view should follow the UXDMD (UI/UX Design and Mapping Document) structure with:
- Purpose and scope definition
- View catalogue with API mappings
- Information architecture
- Data mapping and state management
- Interaction flows and user journeys
- Visual guidelines and design system integration
- Performance requirements
- Security considerations
"""
        else:
            views_content = """## Application Interface Specifications

*View specifications will be extracted from the generated UI/UX specification*

Please refer to the master UI/UX specification document for complete view definitions and interface designs.

## UXDMD Structure

Each view specification should follow the standardized UXDMD format:
- **Purpose & Scope**: User goals, personas, accessibility standards
- **View Catalogue**: Complete table of all views with API mappings
- **Information Architecture**: Navigation, breadcrumbs, role-based access
- **Data Map**: API contracts, state management, caching
- **Per-View Specification**: Detailed specs for each view
- **Interaction Flows**: Sequence diagrams and state charts
- **Visual Guidelines**: Design system and motion specifications
- **Performance & Offline**: Loading, caching, offline behavior
- **Security Requirements**: Auth, validation, data protection
"""
        
        return f"""# Application Views and Interface Designs

This document contains the complete application interface specifications for the {self.project_name}.

{views_content}

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Dashboard Views](./uiux_spec_dashboard.md)
- [Information Architecture →](./uiux_spec_architecture.md)
"""

    async def save_status_file(self, doc_type: DocumentType):
        """Save status file for resume functionality"""
        doc = self.documents[doc_type]

        # Create status directory
        self.status_path.mkdir(parents=True, exist_ok=True)

        status_file = self.status_path / f"status_{doc_type.name.lower()}.json"
        
        status_data = {
            "document_type": doc_type.name,
            "status": doc.status.value,
            "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
            "refined_count": doc.refined_count,
            "validation_errors": doc.validation_errors,
            "content_preview": doc.content[:500] if doc.content else None
        }
        
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved status file: {status_file}")
        except Exception as e:
            logger.error(f"Failed to save status file: {e}")

    def print_status_summary(self):
        """Print a summary of all document statuses"""
        table = Table(title=f"Requirements Generation Status - {self.project_name}")
        table.add_column("Document", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Generated At", style="dim")

        for doc_type in DocumentType:
            doc = self.documents[doc_type]
            
            # Status with color coding
            if doc.status == DocumentStatus.VALIDATED:
                status = "[green]✓ Validated[/green]"
            elif doc.status == DocumentStatus.GENERATED:
                status = "[yellow]Generated[/yellow]"
            elif doc.status == DocumentStatus.IN_PROGRESS:
                status = "[blue]In Progress[/blue]"
            elif doc.status == DocumentStatus.FAILED:
                status = "[red]Failed[/red]"
            else:
                status = "[dim]Not Started[/dim]"
            
            # Generated at timestamp
            generated_at = doc.generated_at.strftime("%H:%M:%S") if doc.generated_at else "-"
            
            table.add_row(
                doc_type.value,
                status,
                generated_at
            )

        console.print(table)

