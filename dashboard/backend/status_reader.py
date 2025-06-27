"""
Status file reader - reuses logic from monitor.py
"""
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from .models import DocumentInfo, DocumentStatus, GenerationSummary
import time


class StatusReader:
    """Reads and parses status files from the generation output directory"""
    
    def __init__(self, output_path: Path, status_path: Optional[Path] = None):
        self.output_path = Path(output_path)
        self.status_path = Path(status_path) if status_path else self.output_path
        self.start_time = None
        self._last_update = {}
        
    def read_document_status(self, doc_file: Path) -> Optional[DocumentInfo]:
        """Read status from a generated document file"""
        try:
            if not doc_file.exists():
                return None
                
            content = doc_file.read_text(encoding='utf-8')
            
            # Extract metadata from YAML front matter
            if content.startswith("---"):
                metadata_end = content.find("---", 3)
                if metadata_end > 0:
                    metadata = yaml.safe_load(content[3:metadata_end])
                    
                    # Map status strings to enum
                    status_str = metadata.get("status", "unknown")
                    status_map = {
                        "not_started": DocumentStatus.NOT_STARTED,
                        "in_progress": DocumentStatus.IN_PROGRESS,
                        "generated": DocumentStatus.GENERATED,
                        "refining": DocumentStatus.REFINING,
                        "refined": DocumentStatus.REFINED,
                        "validating": DocumentStatus.VALIDATING,
                        "validated": DocumentStatus.VALIDATED,
                        "failed": DocumentStatus.FAILED
                    }
                    
                    return DocumentInfo(
                        id=metadata.get("id", doc_file.stem),
                        title=metadata.get("title", "Unknown"),
                        status=status_map.get(status_str, DocumentStatus.NOT_STARTED),
                        file_size=doc_file.stat().st_size,
                        refined_count=metadata.get("refined_count", 0),
                        generated_at=metadata.get("generated_at"),
                        dependencies=metadata.get("dependencies", [])
                    )
        except Exception as e:
            print(f"Error reading {doc_file}: {e}")
            
        return None
    
    def read_status_files(self) -> Dict[str, DocumentInfo]:
        """Read all status files from the status directory"""
        documents = {}
        
        # Try JSON status files first
        for status_file in self.status_path.glob("status_*.json"):
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    doc_id = data.get("id", status_file.stem.replace("status_", ""))
                    
                    # Convert to DocumentInfo
                    documents[doc_id] = DocumentInfo(
                        id=doc_id,
                        title=data.get("title", doc_id),
                        status=DocumentStatus(data.get("status", "not_started")),
                        file_size=data.get("file_size", 0),
                        refined_count=data.get("refined_count", 0),
                        generated_at=data.get("generated_at"),
                        elapsed_time=data.get("elapsed_time"),
                        error_message=data.get("error_message"),
                        dependencies=data.get("dependencies", [])
                    )
            except Exception as e:
                print(f"Error reading status file {status_file}: {e}")
        
        # Also check markdown files in output directory
        for doc_file in self.output_path.glob("*.md"):
            if doc_file.stem not in documents:
                doc_info = self.read_document_status(doc_file)
                if doc_info:
                    documents[doc_info.id] = doc_info
        
        return documents
    
    def get_summary(self) -> GenerationSummary:
        """Get current generation summary"""
        documents = self.read_status_files()
        
        # Count statuses
        completed = sum(1 for doc in documents.values() 
                       if doc.status in [DocumentStatus.VALIDATED, DocumentStatus.REFINED, DocumentStatus.GENERATED])
        failed = sum(1 for doc in documents.values() if doc.status == DocumentStatus.FAILED)
        in_progress = sum(1 for doc in documents.values() 
                         if doc.status in [DocumentStatus.IN_PROGRESS, DocumentStatus.REFINING, DocumentStatus.VALIDATING])
        not_started = 10 - len(documents) + sum(1 for doc in documents.values() 
                                               if doc.status == DocumentStatus.NOT_STARTED)
        
        # Calculate progress
        overall_progress = (completed / 10) * 100 if 10 > 0 else 0
        
        # Calculate average time and ETA
        times = [doc.elapsed_time for doc in documents.values() if doc.elapsed_time]
        avg_time = sum(times) / len(times) if times else None
        eta = (10 - completed) * avg_time if avg_time and completed < 10 else None
        
        # Find start time
        start_times = [doc.generated_at for doc in documents.values() if doc.generated_at]
        start_time = min(start_times) if start_times else None
        
        # Check if completed
        completed_at = None
        if completed >= 10 or (completed + failed >= 10):
            completed_at = datetime.now()
        
        return GenerationSummary(
            total_documents=10,
            completed=completed,
            in_progress=in_progress,
            failed=failed,
            not_started=not_started,
            overall_progress=overall_progress,
            estimated_time_remaining=eta,
            average_document_time=avg_time,
            documents=documents,
            generation_started_at=start_time,
            generation_completed_at=completed_at
        )
    
    def has_changes(self) -> bool:
        """Check if there have been changes since last read"""
        current = self.read_status_files()
        
        # Compare with last update
        if current != self._last_update:
            self._last_update = current
            return True
            
        return False
    
    def read_logs(self, last_n_lines: int = 100) -> List[str]:
        """Read the last N lines from log files"""
        logs = []
        
        # Check for orchestrator log file
        log_file = self.status_path / "orchestrator.log"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    logs = lines[-last_n_lines:]
            except Exception as e:
                print(f"Error reading log file: {e}")
                
        return logs