"""
Artifact-Aware Requirements Processor

This module processes structured requirements artifacts and ensures they are
properly integrated into the AI generation pipeline with full fidelity.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)

class ArtifactProcessor:
    """Processes requirements artifacts and creates enhanced context for AI generation."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.artifacts_path = base_path / "Requirements_Artifacts"
        
    def load_all_artifacts(self) -> Dict[str, Any]:
        """Load all requirements artifacts and create comprehensive context."""
        artifacts = {
            "visual_references": self._load_visual_references(),
            "detailed_specs": self._load_detailed_specs(),
            "json_blueprints": self._load_json_blueprints(),
            "user_stories": self._load_user_stories(),
            "acceptance_criteria": self._load_acceptance_criteria()
        }
        
        # Create enhanced context
        enhanced_context = self._create_enhanced_context(artifacts)
        return enhanced_context
    
    def _load_visual_references(self) -> List[Dict[str, Any]]:
        """Load visual reference files and metadata."""
        visual_refs = []
        visual_path = self.artifacts_path / "visual_references"
        
        if not visual_path.exists():
            return visual_refs
            
        for file_path in visual_path.glob("*"):
            if file_path.is_file():
                ref = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "type": self._get_file_type(file_path),
                    "description": self._extract_description(file_path)
                }
                visual_refs.append(ref)
                
        return visual_refs
    
    def _load_detailed_specs(self) -> List[Dict[str, Any]]:
        """Load detailed specification documents."""
        specs = []
        specs_path = self.artifacts_path / "detailed_specs"
        
        if not specs_path.exists():
            return specs
            
        for file_path in specs_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                spec = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "functional_requirements": self._extract_functional_requirements(content),
                    "priority_requirements": self._extract_priority_requirements(content)
                }
                specs.append(spec)
                
            except Exception as e:
                logger.warning(f"Failed to load spec {file_path}: {e}")
                
        return specs
    
    def _load_json_blueprints(self) -> List[Dict[str, Any]]:
        """Load JSON UI/UX blueprints."""
        blueprints = []
        blueprints_path = self.artifacts_path / "json_blueprints"
        
        if not blueprints_path.exists():
            return blueprints
            
        for file_path in blueprints_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    blueprint_data = json.load(f)
                    
                blueprint = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "data": blueprint_data,
                    "screen_type": blueprint_data.get("screen", "unknown"),
                    "components": self._extract_components(blueprint_data)
                }
                blueprints.append(blueprint)
                
            except Exception as e:
                logger.warning(f"Failed to load blueprint {file_path}: {e}")
                
        return blueprints
    
    def _load_user_stories(self) -> List[Dict[str, Any]]:
        """Load user story documents."""
        stories = []
        stories_path = self.artifacts_path / "user_stories"
        
        if not stories_path.exists():
            return stories
            
        for file_path in stories_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                story = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "personas": self._extract_personas(content),
                    "scenarios": self._extract_scenarios(content)
                }
                stories.append(story)
                
            except Exception as e:
                logger.warning(f"Failed to load story {file_path}: {e}")
                
        return stories
    
    def _load_acceptance_criteria(self) -> List[Dict[str, Any]]:
        """Load acceptance criteria documents."""
        criteria = []
        criteria_path = self.artifacts_path / "acceptance_criteria"
        
        if not criteria_path.exists():
            return criteria
            
        for file_path in criteria_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                criterion = {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "test_cases": self._extract_test_cases(content)
                }
                criteria.append(criterion)
                
            except Exception as e:
                logger.warning(f"Failed to load criteria {file_path}: {e}")
                
        return criteria
    
    def _create_enhanced_context(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced context for AI generation."""
        context = {
            "artifacts_summary": {
                "visual_references_count": len(artifacts["visual_references"]),
                "detailed_specs_count": len(artifacts["detailed_specs"]),
                "json_blueprints_count": len(artifacts["json_blueprints"]),
                "user_stories_count": len(artifacts["user_stories"]),
                "acceptance_criteria_count": len(artifacts["acceptance_criteria"])
            },
            "priority_requirements": self._consolidate_priority_requirements(artifacts),
            "ui_specifications": self._consolidate_ui_specifications(artifacts),
            "functional_requirements": self._consolidate_functional_requirements(artifacts),
            "raw_artifacts": artifacts
        }
        
        return context
    
    def _extract_functional_requirements(self, content: str) -> List[Dict[str, Any]]:
        """Extract functional requirements from markdown content."""
        requirements = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '| FR-' in line or '| REQ-FUNC-' in line:
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 4:
                    req = {
                        "id": parts[1],
                        "title": parts[2],
                        "description": parts[3] if len(parts) > 3 else "",
                        "priority": self._extract_priority_from_line(line)
                    }
                    requirements.append(req)
                    
        return requirements
    
    def _extract_priority_requirements(self, content: str) -> List[str]:
        """Extract P0 (highest priority) requirements."""
        priority_reqs = []
        lines = content.split('\n')
        
        for line in lines:
            if 'P0' in line and ('| FR-' in line or '| REQ-FUNC-' in line):
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 2:
                    priority_reqs.append(parts[1])
                    
        return priority_reqs
    
    def _extract_components(self, blueprint_data: Dict[str, Any]) -> List[str]:
        """Extract component names from JSON blueprint."""
        components = []
        
        def extract_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "type" and isinstance(value, str):
                        components.append(f"{path}.{value}" if path else value)
                    extract_recursive(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_recursive(item, f"{path}[{i}]")
                    
        extract_recursive(blueprint_data)
        return list(set(components))
    
    def _consolidate_priority_requirements(self, artifacts: Dict[str, Any]) -> List[str]:
        """Consolidate all P0 requirements across artifacts."""
        priority_reqs = []
        
        for spec in artifacts["detailed_specs"]:
            priority_reqs.extend(spec["priority_requirements"])
            
        return list(set(priority_reqs))
    
    def _consolidate_ui_specifications(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate UI specifications from blueprints."""
        ui_specs = {
            "screens": [],
            "components": [],
            "interactions": []
        }
        
        for blueprint in artifacts["json_blueprints"]:
            ui_specs["screens"].append(blueprint["screen_type"])
            ui_specs["components"].extend(blueprint["components"])
            
            if "interactions" in blueprint["data"]:
                ui_specs["interactions"].append(blueprint["data"]["interactions"])
                
        return ui_specs
    
    def _consolidate_functional_requirements(self, artifacts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolidate all functional requirements."""
        all_reqs = []
        
        for spec in artifacts["detailed_specs"]:
            all_reqs.extend(spec["functional_requirements"])
            
        return all_reqs
    
    # Helper methods
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type from extension."""
        return file_path.suffix.lower()
    
    def _extract_description(self, file_path: Path) -> str:
        """Extract description from filename or metadata."""
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    def _extract_priority_from_line(self, line: str) -> str:
        """Extract priority from table line."""
        if 'P0' in line:
            return 'P0'
        elif 'P1' in line:
            return 'P1'
        elif 'P2' in line:
            return 'P2'
        return 'P3'
    
    def _extract_personas(self, content: str) -> List[str]:
        """Extract user personas from content."""
        # Simple implementation - can be enhanced
        personas = []
        if 'broker' in content.lower():
            personas.append('Broker')
        if 'manager' in content.lower():
            personas.append('Manager')
        return personas
    
    def _extract_scenarios(self, content: str) -> List[str]:
        """Extract user scenarios from content."""
        # Simple implementation - can be enhanced
        scenarios = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('- ') and 'scenario' in line.lower():
                scenarios.append(line.strip()[2:])
        return scenarios
    
    def _extract_test_cases(self, content: str) -> List[str]:
        """Extract test cases from content."""
        # Simple implementation - can be enhanced
        test_cases = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('- ') and ('test' in line.lower() or 'verify' in line.lower()):
                test_cases.append(line.strip()[2:])
        return test_cases

def create_artifact_enhanced_prompt(base_prompt: str, artifacts_context: Dict[str, Any]) -> str:
    """Create enhanced prompt with artifact context."""
    
    artifact_section = f"""
## 🎯 ARTIFACT-DRIVEN REQUIREMENTS

### Priority Requirements (MUST IMPLEMENT)
{chr(10).join(f"- {req}" for req in artifacts_context["priority_requirements"])}

### Functional Requirements Detail
{chr(10).join(f"- {req['id']}: {req['title']} - {req['description']}" for req in artifacts_context["functional_requirements"])}

### UI Specifications Available
- Screens: {', '.join(artifacts_context["ui_specifications"]["screens"])}
- Components: {', '.join(artifacts_context["ui_specifications"]["components"][:10])}...
- Interactive Elements: {len(artifacts_context["ui_specifications"]["interactions"])} interaction patterns defined

### Artifact Files Referenced
- Visual References: {artifacts_context["artifacts_summary"]["visual_references_count"]} files
- Detailed Specs: {artifacts_context["artifacts_summary"]["detailed_specs_count"]} files  
- JSON Blueprints: {artifacts_context["artifacts_summary"]["json_blueprints_count"]} files
- User Stories: {artifacts_context["artifacts_summary"]["user_stories_count"]} files
- Acceptance Criteria: {artifacts_context["artifacts_summary"]["acceptance_criteria_count"]} files

🚨 CRITICAL: You MUST implement ALL priority requirements (P0) with complete fidelity to the specifications provided in the artifacts. Do NOT use generic templates when specific requirements exist.
"""
    
    return f"{base_prompt}\n\n{artifact_section}"