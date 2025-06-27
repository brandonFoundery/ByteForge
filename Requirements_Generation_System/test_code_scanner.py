"""
Unit tests for the code_scanner module
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules to test
from code_scanner import CodeScanner, CodeFile, FileBatch, CodeTree


class TestCodeScanner(unittest.TestCase):
    """Test cases for CodeScanner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'code_regeneration': {
                'batching': {
                    'max_files': 5,
                    'max_tokens': 1000,
                    'included_extensions': ['.py', '.js', '.ts', '.cs'],
                    'excluded_directories': ['node_modules', 'bin', 'obj'],
                    'excluded_files': ['package-lock.json', '*.min.js']
                }
            }
        }
        self.scanner = CodeScanner(self.config)
    
    def test_should_include_file(self):
        """Test file inclusion logic"""
        # Test included extensions
        self.assertTrue(self.scanner.should_include_file(Path('test.py')))
        self.assertTrue(self.scanner.should_include_file(Path('test.js')))
        self.assertTrue(self.scanner.should_include_file(Path('test.ts')))
        self.assertTrue(self.scanner.should_include_file(Path('test.cs')))
        
        # Test excluded extensions
        self.assertFalse(self.scanner.should_include_file(Path('test.txt')))
        self.assertFalse(self.scanner.should_include_file(Path('test.log')))
        
        # Test excluded files
        self.assertFalse(self.scanner.should_include_file(Path('package-lock.json')))
    
    def test_should_include_directory(self):
        """Test directory inclusion logic"""
        # Test included directories
        self.assertTrue(self.scanner.should_include_directory(Path('src')))
        self.assertTrue(self.scanner.should_include_directory(Path('components')))
        
        # Test excluded directories
        self.assertFalse(self.scanner.should_include_directory(Path('node_modules')))
        self.assertFalse(self.scanner.should_include_directory(Path('bin')))
        self.assertFalse(self.scanner.should_include_directory(Path('obj')))
    
    def test_count_tokens(self):
        """Test token counting functionality"""
        # Test with mock tokenizer
        with patch.object(self.scanner, 'tokenizer') as mock_tokenizer:
            mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
            result = self.scanner.count_tokens("test content")
            self.assertEqual(result, 5)
        
        # Test fallback when tokenizer is None
        self.scanner.tokenizer = None
        result = self.scanner.count_tokens("test content")  # 12 chars / 4 = 3 tokens
        self.assertEqual(result, 3)
    
    def test_categorize_directory(self):
        """Test directory categorization"""
        # Frontend categories
        self.assertEqual(self.scanner._categorize_directory("FrontEnd/src/components"), "frontend-components")
        self.assertEqual(self.scanner._categorize_directory("FrontEnd/src/pages"), "frontend-pages")
        self.assertEqual(self.scanner._categorize_directory("FrontEnd/src/services"), "frontend-services")
        self.assertEqual(self.scanner._categorize_directory("FrontEnd/src/utils"), "frontend-utilities")
        self.assertEqual(self.scanner._categorize_directory("FrontEnd/src"), "frontend-core")
        
        # Backend categories
        self.assertEqual(self.scanner._categorize_directory("BackEnd/Controllers"), "backend-controllers")
        self.assertEqual(self.scanner._categorize_directory("BackEnd/Services"), "backend-services")
        self.assertEqual(self.scanner._categorize_directory("BackEnd/Models"), "backend-models")
        self.assertEqual(self.scanner._categorize_directory("BackEnd/Data"), "backend-data")
        self.assertEqual(self.scanner._categorize_directory("BackEnd"), "backend-core")
        
        # Miscellaneous
        self.assertEqual(self.scanner._categorize_directory("docs"), "miscellaneous")


class TestCodeScannerIntegration(unittest.TestCase):
    """Integration tests for CodeScanner with temporary file system"""
    
    def setUp(self):
        """Set up test fixtures with temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        self.config = {
            'paths': {
                'base_dir': str(self.temp_path)
            },
            'code_regeneration': {
                'batching': {
                    'max_files': 3,
                    'max_tokens': 500,
                    'included_extensions': ['.py', '.js', '.ts'],
                    'excluded_directories': ['node_modules', 'bin'],
                    'excluded_files': ['package-lock.json']
                }
            }
        }
        self.scanner = CodeScanner(self.config)
        
        # Create test directory structure
        self.create_test_files()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self):
        """Create test file structure"""
        # Frontend files
        frontend_dir = self.temp_path / "frontend"
        frontend_dir.mkdir(parents=True)
        
        (frontend_dir / "app.js").write_text("console.log('Hello World');")
        (frontend_dir / "utils.js").write_text("function helper() { return true; }")
        
        components_dir = frontend_dir / "components"
        components_dir.mkdir()
        (components_dir / "Button.js").write_text("export default function Button() { return <button>Click</button>; }")
        
        # Backend files
        backend_dir = self.temp_path / "backend"
        backend_dir.mkdir(parents=True)
        
        (backend_dir / "server.py").write_text("from flask import Flask\napp = Flask(__name__)")
        (backend_dir / "models.py").write_text("class User:\n    def __init__(self, name):\n        self.name = name")
        
        # Excluded directory
        node_modules = frontend_dir / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").write_text("// This should be excluded")
        
        # Excluded file
        (frontend_dir / "package-lock.json").write_text('{"dependencies": {}}')
    
    def test_scan_directory(self):
        """Test directory scanning functionality"""
        frontend_dir = self.temp_path / "frontend"
        files = self.scanner.scan_directory(frontend_dir, frontend_dir)
        
        # Should find .js files but exclude node_modules and package-lock.json
        file_names = [f.relative_path for f in files]
        
        self.assertIn("app.js", file_names)
        self.assertIn("utils.js", file_names)
        # Handle both forward and backward slashes for cross-platform compatibility
        button_js_found = any("Button.js" in name and "components" in name for name in file_names)
        self.assertTrue(button_js_found, f"Button.js in components not found in {file_names}")

        # Check exclusions
        node_modules_found = any("node_modules" in name for name in file_names)
        self.assertFalse(node_modules_found, f"node_modules files should be excluded: {file_names}")
        self.assertNotIn("package-lock.json", file_names)
    
    def test_build_code_tree(self):
        """Test building complete code tree"""
        frontend_dir = self.temp_path / "frontend"
        backend_dir = self.temp_path / "backend"
        
        code_tree = self.scanner.build_code_tree(frontend_dir, backend_dir)
        
        # Check tree structure
        self.assertIsInstance(code_tree, CodeTree)
        self.assertGreater(code_tree.total_files, 0)
        self.assertIn("FrontEnd", code_tree.frontend_files)
        self.assertIn("BackEnd", code_tree.backend_files)
    
    def test_create_batches(self):
        """Test batch creation"""
        frontend_dir = self.temp_path / "frontend"
        backend_dir = self.temp_path / "backend"
        
        code_tree = self.scanner.build_code_tree(frontend_dir, backend_dir)
        batches = self.scanner.create_batches(code_tree)
        
        # Should create at least one batch
        self.assertGreater(len(batches), 0)
        
        # Check batch properties
        for batch in batches:
            self.assertIsInstance(batch, FileBatch)
            self.assertLessEqual(batch.total_files, self.config['code_regeneration']['batching']['max_files'])
            self.assertIsNotNone(batch.category)
    
    def test_save_code_tree(self):
        """Test saving code tree to JSON"""
        frontend_dir = self.temp_path / "frontend"
        backend_dir = self.temp_path / "backend"
        
        code_tree = self.scanner.build_code_tree(frontend_dir, backend_dir)
        output_path = self.temp_path / "code_tree.json"
        
        success = self.scanner.save_code_tree(code_tree, output_path)
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("frontend_files", data)
        self.assertIn("backend_files", data)
        self.assertIn("summary", data)


class TestCodeFile(unittest.TestCase):
    """Test cases for CodeFile dataclass"""
    
    def test_code_file_creation(self):
        """Test CodeFile creation and properties"""
        file_path = Path("test.py")
        code_file = CodeFile(
            path=file_path,
            relative_path="test.py",
            size_bytes=1024,
            extension=".py",
            content="print('hello')",
            token_count=10
        )
        
        self.assertEqual(code_file.path, file_path)
        self.assertEqual(code_file.relative_path, "test.py")
        self.assertEqual(code_file.size_bytes, 1024)
        self.assertEqual(code_file.extension, ".py")
        self.assertEqual(code_file.content, "print('hello')")
        self.assertEqual(code_file.token_count, 10)


class TestFileBatch(unittest.TestCase):
    """Test cases for FileBatch dataclass"""
    
    def test_file_batch_creation(self):
        """Test FileBatch creation and properties"""
        code_files = [
            CodeFile(Path("test1.py"), "test1.py", 100, ".py"),
            CodeFile(Path("test2.py"), "test2.py", 200, ".py")
        ]
        
        batch = FileBatch(
            batch_id="batch_001",
            files=code_files,
            total_tokens=500,
            total_files=2,
            category="backend-core"
        )
        
        self.assertEqual(batch.batch_id, "batch_001")
        self.assertEqual(len(batch.files), 2)
        self.assertEqual(batch.total_tokens, 500)
        self.assertEqual(batch.total_files, 2)
        self.assertEqual(batch.category, "backend-core")


if __name__ == '__main__':
    unittest.main()
