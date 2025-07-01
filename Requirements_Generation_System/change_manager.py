import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from rich.console import Console

console = Console()

class ChangeType(Enum):
    """Type of change being introduced."""
    ADDITION = "Addition"
    MODIFICATION = "Modification"
    DELETION = "Deletion"

@dataclass
class ChangeRequest:
    """Represents a single request to change one or more requirements."""
    change_id: str
    change_type: ChangeType
    reason: str
    requestor: str
    target_requirement_id: Optional[str] = None # For MODIFICATION or DELETION
    new_requirement_details: Optional[Dict[str, Any]] = None # For ADDITION
    
    # Additional metadata
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "Pending"
    
    def to_dict(self):
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "reason": self.reason,
            "requestor": self.requestor,
            "target_requirement_id": self.target_requirement_id,
            "new_requirement_details": self.new_requirement_details,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }

class ChangeManager:
    """Handles the end-to-end process of managing and propagating requirement changes."""

    def __init__(self, base_path: Path, orchestrator):
        self.base_path = base_path
        self.orchestrator = orchestrator
        self.traceability_path = self.base_path / "Requirements_Traceable" / "cross-cutting"
        self.change_log_path = self.base_path / "Requirements_Traceable" / "CHANGE-LOG.md"
        self.change_matrix_path = self.base_path / "Requirements_Traceable" / "change_traceability_matrix.csv"

    def _generate_change_id(self) -> str:
        """Generates a unique ID for a new change request."""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        timestamp_str = str(int(now.timestamp()))[-6:] # Last 6 digits of timestamp for sequence
        return f"CHG-{date_str}-{timestamp_str}"

    def _generate_requirement_id(self, req_type: str, existing_ids: List[str]) -> str:
        """Generates a new, unique requirement ID."""
        prefix_map = {
            "Functional": "REQ-FUNC",
            "Non-Functional": "REQ-NFR",
            "Data": "REQ-DATA"
        }
        prefix = prefix_map.get(req_type, "REQ-MISC")
        
        max_num = 0
        for req_id in existing_ids:
            if req_id.startswith(prefix):
                try:
                    num = int(req_id.split('-')[-1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        
        new_id = f"{prefix}-{max_num + 1:03d}"
        return new_id

    def _load_traceability_data(self) -> Dict[str, Any]:
        """Loads the primary traceability data from requirements_tracker.json."""
        tracker_path = self.traceability_path / "requirements_tracker.json"
        if not tracker_path.exists():
            console.print(f"[bold red]Error: Traceability tracker not found at {tracker_path}[/bold red]")
            raise FileNotFoundError(f"Traceability tracker not found at {tracker_path}")
        
        with open(tracker_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _perform_impact_analysis(self, target_req_id: str, traceability_data: Dict[str, Any]) -> List[str]:
        """
        Performs impact analysis to find all affected requirement IDs.
        
        Args:
            target_req_id: The ID of the requirement that is being changed directly.
            traceability_data: The loaded data from requirements_tracker.json.

        Returns:
            A list of all affected requirement IDs, including the original target.
        """
        console.print(f"Analyzing impact of change to [bold magenta]{target_req_id}[/bold magenta]...")
        
        affected_ids = set([target_req_id])
        
        # Using the 'dependencies' map for traversal
        dependencies_map = traceability_data.get("dependencies", {})
        
        # Build a reverse map (dependents) for easier downstream traversal
        dependents_map = {req_id: [] for req_id in dependencies_map}
        for req_id, deps in dependencies_map.items():
            for dep_id in deps:
                if dep_id in dependents_map:
                    dependents_map[dep_id].append(req_id)

        # Queue for traversal
        queue = [target_req_id]
        visited = set([target_req_id])

        while queue:
            current_id = queue.pop(0)
            
            # Find downstream dependents
            downstream = dependents_map.get(current_id, [])
            for dep_id in downstream:
                if dep_id not in visited:
                    affected_ids.add(dep_id)
                    visited.add(dep_id)
                    queue.append(dep_id)

            # Find upstream dependencies
            upstream = dependencies_map.get(current_id, [])
            for dep_id in upstream:
                if dep_id not in visited:
                    affected_ids.add(dep_id)
                    visited.add(dep_id)
                    queue.append(dep_id)
        
        console.print(f"Found [bold yellow]{len(affected_ids)}[/bold yellow] affected requirements.")
        return list(affected_ids)

    def _find_document_for_requirement(self, req_id: str) -> Optional[Path]:
        """Finds the markdown file that contains a given requirement ID."""
        # This is a simplified search. A more robust implementation might use a pre-built index.
        docs_path = self.base_path / "generated_documents"
        for doc_file in docs_path.glob("*.md"):
            try:
                content = doc_file.read_text(encoding='utf-8')
                if f"id: {req_id}" in content or f"- {req_id}" in content:
                    return doc_file
            except Exception:
                continue
        return None

    async def _update_document_content(self, doc_path: Path, req_id: str, change_request: ChangeRequest) -> bool:
        """Uses an LLM to update the content of a document for a specific requirement."""
        console.print(f"  Updating [bold magenta]{doc_path.name}[/bold magenta] for requirement [bold magenta]{req_id}[/bold magenta]...")
        
        original_content = doc_path.read_text(encoding='utf-8')
        
        # Construct a focused prompt for the LLM
        prompt = f"""
You are an expert requirements analyst. Your task is to update a section of a requirements document based on a change request.

**Change Request Details:**
- **Change ID:** {change_request.change_id}
- **Requirement to Modify:** {req_id}
- **Reason for Change:** {change_request.reason}

**Instructions:**
1.  Carefully read the provided original document content.
2.  Locate the section related to the requirement ID: **{req_id}**.
3.  Rewrite ONLY that section to incorporate the change.
4.  **Crucially, maintain the existing format, structure, and all other traceability IDs.** Do not change any other part of the document.
5.  Ensure the updated section is coherent and professionally written.
6.  Return the FULL document content with the single section updated.

**Original Document Content:**
---
{original_content}
---
"""
        
        try:
            # Use the orchestrator's LLM generation capability
            updated_content = await self.orchestrator._generate_text(prompt)
            
            # Save a backup of the original file
            backup_path = doc_path.with_suffix(f".{change_request.change_id}.bak")
            doc_path.rename(backup_path)
            console.print(f"    [dim]Backup created at {backup_path.name}[/dim]")

            # Write the updated content
            doc_path.write_text(updated_content, encoding='utf-8')
            console.print(f"    [green]Successfully updated {doc_path.name}[/green]")
            return True
        except Exception as e:
            console.print(f"    [bold red]Error updating {doc_path.name}: {e}[/bold red]")
            # Restore from backup if something went wrong
            if backup_path.exists():
                backup_path.rename(doc_path)
            return False

    async def process_change_request(self, change_request: ChangeRequest):
        """
        Main entry point to process a change request.
        This will orchestrate the entire workflow:
        1. Impact Analysis
        2. Document Updates (LLM-powered)
        3. Traceability File Updates
        4. Change Log and Matrix Updates
        """
        console.print(f"[bold cyan]Processing Change Request: {change_request.change_id}[/bold cyan]")
        
        # Step 1: Impact Analysis
        console.print("\nStep 1: Performing Impact Analysis...")
        traceability_data = self._load_traceability_data()
        
        if not change_request.target_requirement_id:
            console.print("[bold red]Error: Target requirement ID is required for modification.[/bold red]")
            return

        affected_req_ids = self._perform_impact_analysis(
            change_request.target_requirement_id, 
            traceability_data
        )
        console.print(f"Affected IDs: {affected_req_ids}")
        
        # Step 2: Document Updates
        console.print("\nStep 2: Applying changes to documents...")
        for req_id in affected_req_ids:
            doc_path = self._find_document_for_requirement(req_id)
            if doc_path:
                await self._update_document_content(doc_path, req_id, change_request)
            else:
                console.print(f"  [yellow]Warning: Could not find source document for requirement ID: {req_id}[/yellow]")

        # Step 3: Update Traceability Files
        console.print("\nStep 3: Updating traceability files...")
        self._update_traceability_files(change_request, affected_req_ids)

        # Step 4: Log the Change
        console.print("\nStep 4: Logging the change...")
        self._log_change(change_request, affected_req_ids)

        change_request.status = "Completed"
        console.print(f"\n[bold green]Change Request {change_request.change_id} processed successfully.[/bold green]")

    def _update_traceability_files(self, change_request: ChangeRequest, affected_ids: List[str]):
        """Updates the requirements_tracker.json file for modifications."""
        tracker_path = self.traceability_path / "requirements_tracker.json"
        if not tracker_path.exists():
            console.print(f"  [yellow]Warning: {tracker_path} not found. Skipping update.[/yellow]")
            return

        try:
            with open(tracker_path, 'r', encoding='utf-8') as f:
                tracker_data = json.load(f)

            now_iso = datetime.now().isoformat()
            
            # Find and update the target requirement
            for req_list_name in ["traceability_requirements", "platform_requirements"]:
                if req_list_name in tracker_data:
                    for req in tracker_data[req_list_name]:
                        if req["id"] == change_request.target_requirement_id:
                            req["updated_date"] = now_iso
                            req["status"] = "Modified" # Example status update
                            console.print(f"  Updated [bold magenta]{req['id']}[/bold magenta] in {tracker_path.name}")
            
            tracker_data["project"]["last_updated"] = now_iso

            # Save the updated tracker data
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2)
            console.print(f"  [green]Successfully saved updated {tracker_path.name}[/green]")

        except Exception as e:
            console.print(f"  [bold red]Error updating {tracker_path.name}: {e}[/bold red]")

    def _log_change(self, change_request: ChangeRequest, affected_ids: List[str]):
        """Logs the completed change to the change log and traceability matrix."""
        # Log to CHANGE-LOG.md
        try:
            with open(self.change_log_path, 'a', encoding='utf-8') as f:
                log_entry = f"""
---

### Change ID: {change_request.change_id}
- **Date**: {change_request.created_at.strftime("%Y-%m-%d %H:%M:%S")}
- **Type**: {change_request.change_type.value}
- **Affected Requirements**: {', '.join(affected_ids)}
- **Requestor**: {change_request.requestor}
- **Approver**: N/A (Automated Process)
- **Reason**: {change_request.reason}
- **Impact Analysis**: Change propagated to {len(affected_ids)} requirements.
"""
                f.write(log_entry)
            console.print(f"  [green]Successfully appended to {self.change_log_path.name}[/green]")
        except Exception as e:
            console.print(f"  [bold red]Error updating {self.change_log_path.name}: {e}[/bold red]")

        # Log to change_traceability_matrix.csv
        try:
            # Create file with header if it doesn't exist
            if not self.change_matrix_path.exists():
                self.change_matrix_path.write_text("Change_ID,Timestamp,Requestor,Change_Type,Target_Requirement,Affected_Requirement\n", encoding='utf-8')

            with open(self.change_matrix_path, 'a', encoding='utf-8') as f:
                timestamp = change_request.created_at.isoformat()
                target_id = change_request.target_requirement_id or "N/A"
                for req_id in affected_ids:
                    f.write(f"{change_request.change_id},{timestamp},{change_request.requestor},{change_request.change_type.value},{target_id},{req_id}\n")
            console.print(f"  [green]Successfully appended to {self.change_matrix_path.name}[/green]")
        except Exception as e:
            console.print(f"  [bold red]Error updating {self.change_matrix_path.name}: {e}[/bold red]")

    async def _extract_requirements_from_text(self, raw_text: str) -> List[Dict[str, Any]]:
        """Uses an LLM to extract and structure requirements from raw text."""
        console.print("\n[cyan]Phase 1: Extracting and structuring requirements from text...[/cyan]")
        
        prompt = f"""
You are a senior requirements analyst. Your task is to analyze the following text and break it down into a structured list of individual requirements.

**Instructions:**
1.  Read the entire text provided below.
2.  Identify every distinct functional, non-functional, or data requirement.
3.  For each requirement, create a JSON object with the following fields:
    - `description`: A clear, concise statement of the requirement.
    - `type`: The type of requirement (e.g., "Functional", "Non-Functional", "Data").
    - `dependencies`: A list of any other requirements (by their description) that this one depends on, if any can be inferred from the text.
4.  Return a single JSON array containing all the requirement objects. Ensure the JSON is perfectly formatted.

**Raw Text to Analyze:**
---
{raw_text}
---

**Example Output Format:**
```json
[
  {{
    "description": "The system shall allow users to log in with a username and password.",
    "type": "Functional",
    "dependencies": []
  }},
  {{
    "description": "The login page must load in under 2 seconds.",
    "type": "Non-Functional",
    "dependencies": ["The system shall allow users to log in with a username and password."]
  }}
]
```
"""
        try:
            response_text = await self.orchestrator._generate_text(prompt)
            
            # Clean up the response to extract only the JSON
            json_match = re.search(r'```json\n(.*)\n```', response_text, re.DOTALL)
            if not json_match:
                # Fallback for when the LLM doesn't use markdown code blocks
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1).strip()
                requirements = json.loads(json_str)
                console.print(f"[green]✅ Successfully extracted {len(requirements)} requirements.[/green]")
                return requirements
            else:
                console.print("[bold red]Error: Could not find valid JSON in the LLM response.[/bold red]")
                return []
        except Exception as e:
            console.print(f"[bold red]Error during requirement extraction: {e}[/bold red]")
            return []

    async def _add_requirement_to_document(self, doc_path: Path, new_req_details: Dict[str, Any], new_req_id: str) -> bool:
        """Uses an LLM to add a new requirement to the correct place in a document."""
        console.print(f"  Updating [bold magenta]{doc_path.name}[/bold magenta] with new requirement [bold magenta]{new_req_id}[/bold magenta]...")
        original_content = doc_path.read_text(encoding='utf-8')

        prompt = f"""
You are an expert requirements analyst. Your task is to add a new requirement to a requirements document.

**New Requirement Details:**
- **ID:** {new_req_id}
- **Description:** {new_req_details['description']}
- **Type:** {new_req_details['type']}

**Instructions:**
1.  Carefully read the provided original document content to understand its structure.
2.  Find the most logical section to add this new requirement based on its type and content.
3.  Insert the new requirement, perfectly matching the existing markdown format, numbering, and heading structure.
4.  **Crucially, do not change any other part of the document.**
5.  Return the FULL document content with the new requirement added.

**Original Document Content:**
---
{original_content}
---
"""
        try:
            updated_content = await self.orchestrator._generate_text(prompt)
            
            # Create a backup before overwriting
            backup_path = doc_path.with_suffix(f".{new_req_id}.bak")
            doc_path.rename(backup_path)
            
            doc_path.write_text(updated_content, encoding='utf-8')
            console.print(f"    [green]Successfully added {new_req_id} to {doc_path.name}[/green]")
            return True
        except Exception as e:
            console.print(f"    [bold red]Error updating {doc_path.name}: {e}[/bold red]")
            if backup_path.exists():
                backup_path.rename(doc_path) # Restore from backup
            return False

    def _update_traceability_for_addition(self, new_req_id: str, req_details: Dict[str, Any], tracker_data: Dict[str, Any]):
        """Adds a new requirement to the traceability data."""
        console.print(f"  Updating traceability for new requirement {new_req_id}...")
        
        new_req_entry = {
            "id": new_req_id,
            "description": req_details["description"],
            "type": req_details["type"],
            "status": "New",
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat(),
            "dependencies": req_details.get("dependencies", [])
        }
        
        # Add to the correct list
        list_name = "traceability_requirements" # Default
        if "platform" in req_details.get("type", "").lower():
             list_name = "platform_requirements"
        
        if list_name not in tracker_data:
            tracker_data[list_name] = []
        tracker_data[list_name].append(new_req_entry)
        
        # Also add to the main dependencies map
        if "dependencies" not in tracker_data:
            tracker_data["dependencies"] = {}
        tracker_data["dependencies"][new_req_id] = req_details.get("dependencies", [])

        tracker_path = self.traceability_path / "requirements_tracker.json"
        try:
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2)
            console.print(f"    [green]Successfully updated {tracker_path.name}[/green]")
        except Exception as e:
            console.print(f"    [bold red]Error updating {tracker_path.name}: {e}[/bold red]")

    async def _process_addition_request(self, change_request: ChangeRequest, traceability_data: Dict[str, Any]):
        """Processes a single requirement addition."""
        req_details = change_request.new_requirement_details
        console.print(f"\n[bold cyan]Processing New Requirement: {req_details.get('description', 'N/A')}[/bold cyan]")
        
        # 1. Determine target document
        req_type = req_details.get("type", "Functional")
        doc_map = {
            "Functional": "FRD.md",
            "Non-Functional": "NFRD.md",
            "Data": "DRD.md"
        }
        target_doc_name = doc_map.get(req_type, "FRD.md")
        doc_path = self.base_path / "generated_documents" / target_doc_name

        if not doc_path.exists():
            console.print(f"  [yellow]Warning: Target document {target_doc_name} not found. Skipping.[/yellow]")
            return

        # 2. Generate a new requirement ID
        existing_ids = [req['id'] for req_list in traceability_data.values() if isinstance(req_list, list) for req in req_list]
        new_req_id = self._generate_requirement_id(req_type, existing_ids)
        console.print(f"  Generated new Requirement ID: [bold magenta]{new_req_id}[/bold magenta]")

        # 3. Add the new requirement to the document
        success = await self._add_requirement_to_document(doc_path, req_details, new_req_id)
        if not success:
            console.print(f"  [red]Failed to add requirement to document. Aborting this addition.[/red]")
            return

        # 4. Update traceability files
        self._update_traceability_for_addition(new_req_id, req_details, traceability_data)

        # 5. Log the change
        self._log_change(change_request, [new_req_id])

    async def process_new_requirements_from_text(self, raw_text: str, requestor: str):
        """
        Main entry point for processing new requirements from a block of text.
        Orchestrates the two-phase LLM process.
        """
        # Phase 1: Extract requirements from text
        extracted_reqs = await self._extract_requirements_from_text(raw_text)
        
        if not extracted_reqs:
            console.print("[yellow]No requirements were extracted. Aborting.[/yellow]")
            return

        # Phase 2: Process each extracted requirement
        console.print(f"\n[cyan]Phase 2: Processing {len(extracted_reqs)} new requirements individually...[/cyan]")
        
        # Load traceability data once for the whole batch
        traceability_data = self._load_traceability_data()

        for req_details in extracted_reqs:
            change_request = ChangeRequest(
                change_id=self._generate_change_id(),
                change_type=ChangeType.ADDITION,
                reason=f"New requirement extracted from text provided by {requestor}.",
                requestor=requestor,
                new_requirement_details=req_details
            )
            await self._process_addition_request(change_request, traceability_data)

if __name__ == '__main__':
    # Example Usage
    
    # This is a placeholder for how the ChangeManager might be used.
    # The actual integration will be in run_generation.py.
    
    # Mock orchestrator for standalone testing
    class MockOrchestrator:
        async def _generate_text(self, prompt):
            # In a real scenario, this would call the OpenAI API.
            # For this test, we'll just return a modified version of the content.
            console.print("\n[bold yellow]-- MOCK LLM CALL --[/bold yellow]")
            console.print(f"[dim]Prompt: {prompt[:200]}...[/dim]")
            
            # Simulate the two different prompt responses
            if "Raw Text to Analyze" in prompt:
                # Simulate the requirement extraction response
                mock_json_response = """
```json
[
  {
    "description": "The system must support multi-factor authentication (MFA) using an authenticator app.",
    "type": "Functional",
    "dependencies": []
  },
  {
    "description": "User profiles should include a profile picture and a short bio.",
    "type": "Functional",
    "dependencies": []
  },
  {
    "description": "All API endpoints must respond within 500ms under normal load.",
    "type": "Non-Functional",
    "dependencies": []
  }
]
```
"""
                return mock_json_response
            else:
                # Simulate a document update response
                return "This is a mock response for a document update."

    base_path = Path("project")
    mock_orchestrator = MockOrchestrator()
    
    manager = ChangeManager(base_path, mock_orchestrator)
    
    # Example of running the new requirement introduction flow
    raw_text_input = """
    We need to enhance our security by adding MFA support via authenticator apps.
    Also, let's improve user engagement by allowing them to add a profile picture and a bio to their profiles.
    Finally, performance is key, so all APIs need to be fast, responding in under 500ms.
    """
    
    async def run_test():
        await manager.process_new_requirements_from_text(raw_text_input, "Test User")

    asyncio.run(run_test())
