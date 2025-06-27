"""
Integration tests for the full regeneration workflow
"""

import unittest
import tempfile
import yaml
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Import the modules to test
from run_generation import full_regeneration_workflow
from orchestrator import RequirementsOrchestrator


class TestFullRegenerationWorkflow(unittest.TestCase):
    """Integration tests for the full regeneration workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test configuration
        self.config = {
            'project': {'name': 'TestProject'},
            'paths': {
                'base_dir': str(self.temp_path),
                'frontend_dir': 'frontend',
                'backend_dir': 'backend',
                'output_dir': 'generated_documents',
                'status_dir': 'generation_status'
            },
            'code_regeneration': {
                'batching': {
                    'max_files': 3,
                    'max_tokens': 500,
                    'included_extensions': ['.py', '.js', '.ts'],
                    'excluded_directories': ['node_modules', 'bin'],
                    'excluded_files': ['package-lock.json']
                },
                'purge_directories': [
                    'generated_documents',
                    'generation_status'
                ]
            }
        }
        
        # Create config file
        self.config_path = self.temp_path / "config.yaml"
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)
        
        # Create test directory structure
        self.create_test_structure()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_structure(self):
        """Create test directory and file structure"""
        # Create frontend directory with test files
        frontend_dir = self.temp_path / "frontend"
        frontend_dir.mkdir(parents=True)
        
        (frontend_dir / "app.js").write_text("""
// Main application entry point
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UserProfile from './components/UserProfile';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/profile" element={<UserProfile />} />
      </Routes>
    </Router>
  );
}

export default App;
""")
        
        components_dir = frontend_dir / "components"
        components_dir.mkdir()
        
        (components_dir / "Dashboard.js").write_text("""
// Dashboard component for displaying user metrics
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      {loading ? <p>Loading...</p> : <MetricsDisplay metrics={metrics} />}
    </div>
  );
};

export default Dashboard;
""")
        
        # Create backend directory with test files
        backend_dir = self.temp_path / "backend"
        backend_dir.mkdir(parents=True)
        
        (backend_dir / "app.py").write_text("""
# Flask application for handling API requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import User, Metric
from database import db

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    \"\"\"Get user metrics for dashboard display\"\"\"
    try:
        user_id = request.args.get('user_id', 1)
        metrics = Metric.query.filter_by(user_id=user_id).all()
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    \"\"\"Get user profile information\"\"\"
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
""")
        
        (backend_dir / "models.py").write_text("""
# Database models for the application
from database import db
from datetime import datetime

class User(db.Model):
    \"\"\"User model for storing user information\"\"\"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Metric(db.Model):
    \"\"\"Metric model for storing user performance data\"\"\"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'metric_type': self.metric_type,
            'value': self.value,
            'timestamp': self.timestamp.isoformat()
        }
""")
        
        # Create some existing directories that should be purged
        old_output_dir = self.temp_path / "generated_documents"
        old_output_dir.mkdir(parents=True)
        (old_output_dir / "old_brd.md").write_text("Old BRD content")
        
        old_status_dir = self.temp_path / "generation_status"
        old_status_dir.mkdir(parents=True)
        (old_status_dir / "old_status.json").write_text('{"status": "old"}')
    
    @patch('run_generation.get_api_key')
    @patch('run_generation.get_api_key_info')
    @patch.object(RequirementsOrchestrator, 'generate_requirements_from_code')
    async def test_full_regeneration_workflow_success(self, mock_generate, mock_key_info, mock_get_key):
        """Test successful full regeneration workflow"""
        # Mock API key functions
        mock_key_info.return_value = {"env_var": "TEST_API_KEY", "name": "Test Provider"}
        mock_get_key.return_value = "test-api-key"
        
        # Mock the requirements generation
        mock_generate.return_value = True
        
        # Run the workflow
        result = await full_regeneration_workflow(self.config_path, "openai")
        
        # Verify success
        self.assertTrue(result)
        
        # Verify old directories were purged
        old_output_dir = self.temp_path / "generated_documents"
        old_status_dir = self.temp_path / "generation_status"
        
        # Directories should be recreated but old files should be gone
        self.assertTrue(old_output_dir.exists())
        self.assertTrue(old_status_dir.exists())
        self.assertFalse((old_output_dir / "old_brd.md").exists())
        self.assertFalse((old_status_dir / "old_status.json").exists())
        
        # Verify new directories were created
        cumulative_docs_dir = old_output_dir / "code_generated_requirements"
        self.assertTrue(cumulative_docs_dir.exists())
        
        # Verify code tree was saved
        code_tree_path = old_output_dir / "code_tree.json"
        self.assertTrue(code_tree_path.exists())
        
        # Verify status files were created
        status_files = list(old_status_dir.glob("status_batch_*.json"))
        self.assertGreater(len(status_files), 0)
        
        # Verify the generate_requirements_from_code was called
        self.assertTrue(mock_generate.called)
    
    @patch('run_generation.get_api_key')
    @patch('run_generation.get_api_key_info')
    async def test_full_regeneration_workflow_no_api_key(self, mock_key_info, mock_get_key):
        """Test workflow failure when no API key is available"""
        # Mock API key functions to return None
        mock_key_info.return_value = {"env_var": "TEST_API_KEY", "name": "Test Provider"}
        mock_get_key.return_value = None
        
        # Run the workflow
        result = await full_regeneration_workflow(self.config_path, "openai")
        
        # Verify failure
        self.assertFalse(result)
    
    @patch('run_generation.get_api_key')
    @patch('run_generation.get_api_key_info')
    @patch('code_scanner.CodeScanner')
    async def test_full_regeneration_workflow_scanner_error(self, mock_scanner_class, mock_key_info, mock_get_key):
        """Test workflow handling when code scanner fails"""
        # Mock API key functions
        mock_key_info.return_value = {"env_var": "TEST_API_KEY", "name": "Test Provider"}
        mock_get_key.return_value = "test-api-key"
        
        # Mock scanner to raise an exception
        mock_scanner = MagicMock()
        mock_scanner.build_code_tree.side_effect = Exception("Scanner failed")
        mock_scanner_class.return_value = mock_scanner
        
        # Run the workflow
        result = await full_regeneration_workflow(self.config_path, "openai")
        
        # Verify failure
        self.assertFalse(result)
    
    def test_config_loading(self):
        """Test that configuration is loaded correctly"""
        with open(self.config_path, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config['project']['name'], 'TestProject')
        self.assertEqual(loaded_config['paths']['frontend_dir'], 'frontend')
        self.assertEqual(loaded_config['paths']['backend_dir'], 'backend')
    
    def test_directory_structure_creation(self):
        """Test that test directory structure is created correctly"""
        # Check frontend files
        frontend_dir = self.temp_path / "frontend"
        self.assertTrue((frontend_dir / "app.js").exists())
        self.assertTrue((frontend_dir / "components" / "Dashboard.js").exists())
        
        # Check backend files
        backend_dir = self.temp_path / "backend"
        self.assertTrue((backend_dir / "app.py").exists())
        self.assertTrue((backend_dir / "models.py").exists())
        
        # Check old directories exist (before purging)
        self.assertTrue((self.temp_path / "generated_documents" / "old_brd.md").exists())
        self.assertTrue((self.temp_path / "generation_status" / "old_status.json").exists())


class TestFullRegenerationAsync(unittest.TestCase):
    """Test async functionality of full regeneration"""
    
    def test_async_workflow_execution(self):
        """Test that the workflow can be executed asynchronously"""
        # Create minimal test setup
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        config = {
            'project': {'name': 'AsyncTest'},
            'paths': {
                'base_dir': str(temp_path),
                'frontend_dir': 'frontend',
                'backend_dir': 'backend',
                'output_dir': 'output',
                'status_dir': 'status'
            },
            'code_regeneration': {
                'batching': {'max_files': 1, 'max_tokens': 100},
                'purge_directories': []
            }
        }
        
        config_path = temp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        # Create minimal directory structure
        (temp_path / "frontend").mkdir()
        (temp_path / "backend").mkdir()
        (temp_path / "frontend" / "test.js").write_text("console.log('test');")
        
        async def run_test():
            with patch('run_generation.get_api_key') as mock_get_key:
                with patch('run_generation.get_api_key_info') as mock_key_info:
                    mock_key_info.return_value = {"env_var": "TEST_KEY", "name": "Test"}
                    mock_get_key.return_value = None  # This will cause early failure
                    
                    result = await full_regeneration_workflow(config_path, "openai")
                    return result
        
        # Run the async test
        result = asyncio.run(run_test())
        
        # Should fail due to no API key
        self.assertFalse(result)
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
