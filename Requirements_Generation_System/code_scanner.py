"""
Code Scanner Module for Full Requirements Regeneration

This module provides functionality to scan source code directories,
build directory trees, and create batches of files for LLM processing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import tiktoken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeFile:
    """Represents a single code file with metadata"""
    path: Path
    relative_path: str
    size_bytes: int
    extension: str
    content: Optional[str] = None
    token_count: Optional[int] = None


@dataclass
class FileBatch:
    """Represents a batch of files to be processed together"""
    batch_id: str
    files: List[CodeFile]
    total_tokens: int
    total_files: int
    category: str  # e.g., "frontend-components", "backend-controllers"


@dataclass
class CodeTree:
    """Represents the complete code directory structure"""
    frontend_files: Dict[str, List[CodeFile]]
    backend_files: Dict[str, List[CodeFile]]
    total_files: int
    total_size_bytes: int
    file_extensions: Set[str]


class CodeScanner:
    """Main class for scanning and organizing code files"""
    
    def __init__(self, config: dict):
        self.config = config
        self.code_config = config.get('code_regeneration', {})
        self.batching_config = self.code_config.get('batching', {})
        
        # Configuration values with defaults
        self.max_files_per_batch = self.batching_config.get('max_files', 12)
        self.max_tokens_per_batch = self.batching_config.get('max_tokens', 8000)
        self.included_extensions = set(self.batching_config.get('included_extensions', [
            '.ts', '.tsx', '.js', '.jsx', '.cs', '.cshtml', '.sql', '.bicep', '.md', '.json'
        ]))
        self.excluded_directories = set(self.batching_config.get('excluded_directories', [
            'node_modules', 'bin', 'obj', 'dist', 'build', '.git', '.vs', '.vscode'
        ]))
        self.excluded_files = set(self.batching_config.get('excluded_files', [
            'package-lock.json', 'yarn.lock'
        ]))
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not initialize tokenizer: {e}")
            self.tokenizer = None
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in the scan"""
        # Check extension
        if file_path.suffix.lower() not in self.included_extensions:
            return False
        
        # Check excluded files
        if file_path.name in self.excluded_files:
            return False
        
        # Check for pattern matches in excluded files
        for pattern in self.excluded_files:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(file_path.name, pattern):
                    return False
        
        # Check if any parent directory is excluded
        for parent in file_path.parents:
            if parent.name in self.excluded_directories:
                return False
        
        return True
    
    def should_include_directory(self, dir_path: Path) -> bool:
        """Determine if a directory should be scanned"""
        return dir_path.name not in self.excluded_directories
    
    def count_tokens(self, content: str) -> int:
        """Count tokens in text content"""
        if not self.tokenizer:
            # Fallback: rough estimation (4 chars per token)
            return len(content) // 4
        
        try:
            return len(self.tokenizer.encode(content))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(content) // 4
    
    def scan_directory(self, directory: Path, base_path: Path) -> List[CodeFile]:
        """Scan a directory and return list of code files"""
        code_files = []
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return code_files
        
        logger.info(f"Scanning directory: {directory}")
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and self.should_include_file(file_path):
                    # Check if file is in an excluded directory
                    skip_file = False
                    for parent in file_path.parents:
                        if not self.should_include_directory(parent):
                            skip_file = True
                            break
                    
                    if skip_file:
                        continue
                    
                    try:
                        relative_path = str(file_path.relative_to(base_path))
                        size_bytes = file_path.stat().st_size
                        
                        # Skip very large files (>1MB)
                        if size_bytes > 1024 * 1024:
                            logger.warning(f"Skipping large file: {relative_path} ({size_bytes} bytes)")
                            continue
                        
                        code_file = CodeFile(
                            path=file_path,
                            relative_path=relative_path,
                            size_bytes=size_bytes,
                            extension=file_path.suffix.lower()
                        )
                        
                        code_files.append(code_file)
                        
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        logger.info(f"Found {len(code_files)} code files in {directory}")
        return code_files
    
    def build_code_tree(self, frontend_dir: Path, backend_dir: Path) -> CodeTree:
        """Build a complete tree structure of the codebase"""
        logger.info("Building code tree structure...")
        
        # Get base paths
        base_path = Path(self.config['paths']['base_dir'])
        
        # Resolve relative paths
        if not frontend_dir.is_absolute():
            frontend_dir = base_path / frontend_dir
        if not backend_dir.is_absolute():
            backend_dir = base_path / backend_dir
        
        # Scan directories
        frontend_files = self.scan_directory(frontend_dir, frontend_dir)
        backend_files = self.scan_directory(backend_dir, backend_dir)
        
        # Organize files by directory structure
        frontend_organized = self._organize_files_by_directory(frontend_files, "FrontEnd")
        backend_organized = self._organize_files_by_directory(backend_files, "BackEnd")
        
        # Calculate totals
        all_files = frontend_files + backend_files
        total_size = sum(f.size_bytes for f in all_files)
        extensions = set(f.extension for f in all_files)
        
        code_tree = CodeTree(
            frontend_files=frontend_organized,
            backend_files=backend_organized,
            total_files=len(all_files),
            total_size_bytes=total_size,
            file_extensions=extensions
        )
        
        logger.info(f"Code tree built: {code_tree.total_files} files, {len(extensions)} extensions")
        return code_tree
    
    def _organize_files_by_directory(self, files: List[CodeFile], root_name: str) -> Dict[str, List[CodeFile]]:
        """Organize files by their directory structure"""
        organized = defaultdict(list)
        
        for file in files:
            # Get the directory path relative to root
            dir_path = str(Path(file.relative_path).parent)
            if dir_path == '.':
                dir_path = root_name
            else:
                dir_path = f"{root_name}/{dir_path}"
            
            organized[dir_path].append(file)
        
        return dict(organized)

    def load_file_content(self, code_file: CodeFile) -> bool:
        """Load content for a code file and count tokens"""
        try:
            with open(code_file.path, 'r', encoding='utf-8', errors='ignore') as f:
                code_file.content = f.read()

            code_file.token_count = self.count_tokens(code_file.content)
            return True

        except Exception as e:
            logger.warning(f"Could not load content for {code_file.relative_path}: {e}")
            code_file.content = ""
            code_file.token_count = 0
            return False

    def create_batches(self, code_tree: CodeTree) -> List[FileBatch]:
        """Create batches of files for LLM processing"""
        logger.info("Creating file batches for processing...")

        batches = []
        batch_counter = 1

        # Process frontend files
        for directory, files in code_tree.frontend_files.items():
            directory_batches = self._create_batches_for_directory(
                files, directory, batch_counter
            )
            batches.extend(directory_batches)
            batch_counter += len(directory_batches)

        # Process backend files
        for directory, files in code_tree.backend_files.items():
            directory_batches = self._create_batches_for_directory(
                files, directory, batch_counter
            )
            batches.extend(directory_batches)
            batch_counter += len(directory_batches)

        logger.info(f"Created {len(batches)} batches for processing")
        return batches

    def _create_batches_for_directory(self, files: List[CodeFile], directory: str, start_counter: int) -> List[FileBatch]:
        """Create batches for files in a specific directory"""
        if not files:
            return []

        # Load content for all files
        for file in files:
            self.load_file_content(file)

        # Sort files by size (smaller first for better batching)
        files.sort(key=lambda f: f.token_count or 0)

        batches = []
        current_batch_files = []
        current_batch_tokens = 0
        batch_counter = start_counter

        for file in files:
            file_tokens = file.token_count or 0

            # Check if adding this file would exceed limits
            would_exceed_files = len(current_batch_files) >= self.max_files_per_batch
            would_exceed_tokens = (current_batch_tokens + file_tokens) > self.max_tokens_per_batch

            # If we would exceed limits and we have files in current batch, create a new batch
            if (would_exceed_files or would_exceed_tokens) and current_batch_files:
                batch = FileBatch(
                    batch_id=f"batch_{batch_counter:03d}",
                    files=current_batch_files.copy(),
                    total_tokens=current_batch_tokens,
                    total_files=len(current_batch_files),
                    category=self._categorize_directory(directory)
                )
                batches.append(batch)

                # Start new batch
                current_batch_files = []
                current_batch_tokens = 0
                batch_counter += 1

            # Add file to current batch
            current_batch_files.append(file)
            current_batch_tokens += file_tokens

        # Add remaining files as final batch
        if current_batch_files:
            batch = FileBatch(
                batch_id=f"batch_{batch_counter:03d}",
                files=current_batch_files,
                total_tokens=current_batch_tokens,
                total_files=len(current_batch_files),
                category=self._categorize_directory(directory)
            )
            batches.append(batch)

        return batches

    def _categorize_directory(self, directory: str) -> str:
        """Categorize a directory for better batch organization"""
        dir_lower = directory.lower()

        if 'frontend' in dir_lower or 'src' in dir_lower:
            if 'component' in dir_lower:
                return "frontend-components"
            elif 'page' in dir_lower or 'route' in dir_lower:
                return "frontend-pages"
            elif 'service' in dir_lower or 'api' in dir_lower:
                return "frontend-services"
            elif 'util' in dir_lower or 'helper' in dir_lower:
                return "frontend-utilities"
            else:
                return "frontend-core"

        elif 'backend' in dir_lower:
            if 'controller' in dir_lower:
                return "backend-controllers"
            elif 'service' in dir_lower:
                return "backend-services"
            elif 'model' in dir_lower or 'entity' in dir_lower:
                return "backend-models"
            elif 'data' in dir_lower or 'repository' in dir_lower:
                return "backend-data"
            else:
                return "backend-core"

        else:
            return "miscellaneous"

    def save_code_tree(self, code_tree: CodeTree, output_path: Path) -> bool:
        """Save the code tree structure to JSON file"""
        try:
            # Convert to serializable format
            tree_data = {
                "frontend_files": {
                    dir_name: [
                        {
                            "relative_path": f.relative_path,
                            "size_bytes": f.size_bytes,
                            "extension": f.extension,
                            "token_count": f.token_count
                        }
                        for f in files
                    ]
                    for dir_name, files in code_tree.frontend_files.items()
                },
                "backend_files": {
                    dir_name: [
                        {
                            "relative_path": f.relative_path,
                            "size_bytes": f.size_bytes,
                            "extension": f.extension,
                            "token_count": f.token_count
                        }
                        for f in files
                    ]
                    for dir_name, files in code_tree.backend_files.items()
                },
                "summary": {
                    "total_files": code_tree.total_files,
                    "total_size_bytes": code_tree.total_size_bytes,
                    "file_extensions": list(code_tree.file_extensions)
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Code tree saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save code tree: {e}")
            return False
