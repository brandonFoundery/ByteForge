#!/usr/bin/env python3
"""
Security Manager for Claude Code Execution

This module provides security features, API key management, rate limiting,
and execution sandboxing for Claude Code operations.
"""

import os
import json
import time
import hashlib
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import threading

from rich.console import Console

console = Console()


@dataclass
class SecurityEvent:
    """Security event for logging and monitoring"""
    timestamp: str
    event_type: str
    severity: str  # low, medium, high, critical
    message: str
    context: Dict
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "context": self.context
        }


@dataclass
class RateLimitEntry:
    """Rate limit tracking entry"""
    requests: List[float]
    max_requests: int
    window_seconds: int
    
    def is_allowed(self) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [req for req in self.requests if req > now - self.window_seconds]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    def time_until_next_allowed(self) -> float:
        """Get seconds until next request is allowed"""
        if len(self.requests) < self.max_requests:
            return 0.0
        
        oldest_request = min(self.requests)
        return (oldest_request + self.window_seconds) - time.time()


class SecurityManager:
    """Comprehensive security management for Claude Code execution"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.security_path = base_path / "logs" / "security"
        self.security_path.mkdir(parents=True, exist_ok=True)
        
        # Security configuration
        self.config = self._load_security_config()
        
        # Rate limiting
        self.rate_limits: Dict[str, RateLimitEntry] = {}
        self.rate_limit_lock = threading.Lock()
        
        # Security event logging
        self.security_events: List[SecurityEvent] = []
        self.events_lock = threading.Lock()
        
        # Execution sandboxing
        self.allowed_commands: Set[str] = {
            'claude', 'cd', 'ls', 'cat', 'echo', 'mkdir', 'rm', 'cp', 'mv',
            'git', 'npm', 'dotnet', 'curl', 'wget', 'python', 'node'
        }
        
        # Blocked patterns
        self.blocked_patterns: Set[str] = {
            'sudo', 'su', 'chmod +x', 'rm -rf /', 'format', 'fdisk',
            'passwd', 'useradd', 'userdel', 'systemctl', 'service'
        }
        
        console.print("[green]🔒 Security Manager initialized[/green]")
    
    def _load_security_config(self) -> Dict:
        """Load security configuration"""
        return {
            "rate_limiting": {
                "enabled": True,
                "claude_api": {"max_requests": 60, "window_seconds": 60},
                "file_operations": {"max_requests": 100, "window_seconds": 60},
                "git_operations": {"max_requests": 20, "window_seconds": 60}
            },
            "command_filtering": {
                "enabled": True,
                "strict_mode": True,
                "log_blocked_commands": True
            },
            "file_access": {
                "restricted_paths": ["/etc", "/root", "/sys", "/proc"],
                "max_file_size_mb": 100,
                "allowed_extensions": [".md", ".ts", ".js", ".cs", ".json", ".yaml", ".txt"]
            },
            "api_key_security": {
                "encrypt_keys": True,
                "rotate_keys_days": 90,
                "log_key_usage": True
            }
        }
    
    def validate_api_key(self, provider: str, api_key: str) -> bool:
        """Validate and secure API key"""
        if not api_key or len(api_key) < 10:
            self._log_security_event(
                "api_key_validation",
                "medium",
                f"Invalid API key provided for {provider}",
                {"provider": provider}
            )
            return False
        
        # Check for common test/dummy keys
        dummy_patterns = ["test", "dummy", "fake", "example", "placeholder"]
        if any(pattern in api_key.lower() for pattern in dummy_patterns):
            self._log_security_event(
                "api_key_validation",
                "high",
                f"Potential dummy API key detected for {provider}",
                {"provider": provider}
            )
            return False
        
        # Log key usage (without exposing the key)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        self._log_security_event(
            "api_key_usage",
            "low",
            f"API key validated for {provider}",
            {"provider": provider, "key_hash": key_hash}
        )
        
        return True
    
    def check_rate_limit(self, operation_type: str, identifier: str = "default") -> bool:
        """Check if operation is within rate limits"""
        if not self.config.get("rate_limiting", {}).get("enabled", True):
            return True
        
        rate_config = self.config.get("rate_limiting", {}).get(operation_type)
        if not rate_config:
            return True  # No rate limit configured
        
        key = f"{operation_type}:{identifier}"
        
        with self.rate_limit_lock:
            if key not in self.rate_limits:
                self.rate_limits[key] = RateLimitEntry(
                    requests=[],
                    max_requests=rate_config["max_requests"],
                    window_seconds=rate_config["window_seconds"]
                )
            
            rate_limit = self.rate_limits[key]
            
            if not rate_limit.is_allowed():
                wait_time = rate_limit.time_until_next_allowed()
                self._log_security_event(
                    "rate_limit_exceeded",
                    "medium",
                    f"Rate limit exceeded for {operation_type}",
                    {
                        "operation_type": operation_type,
                        "identifier": identifier,
                        "wait_time": wait_time
                    }
                )
                return False
        
        return True
    
    def validate_command(self, command: str) -> bool:
        """Validate command for security compliance"""
        if not self.config.get("command_filtering", {}).get("enabled", True):
            return True
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command.lower():
                self._log_security_event(
                    "command_blocked",
                    "high",
                    f"Blocked command containing pattern: {pattern}",
                    {"command": command[:100], "pattern": pattern}
                )
                return False
        
        # Extract first command
        first_command = command.split()[0] if command.split() else ""
        
        # Check if command is in allowed list
        strict_mode = self.config.get("command_filtering", {}).get("strict_mode", True)
        if strict_mode and first_command not in self.allowed_commands:
            self._log_security_event(
                "command_blocked",
                "medium",
                f"Command not in allowed list: {first_command}",
                {"command": command[:100], "first_command": first_command}
            )
            return False
        
        return True
    
    def validate_file_access(self, file_path: str, operation: str = "read") -> bool:
        """Validate file access for security compliance"""
        path = Path(file_path)
        
        # Check restricted paths
        restricted_paths = self.config.get("file_access", {}).get("restricted_paths", [])
        for restricted in restricted_paths:
            if str(path).startswith(restricted):
                self._log_security_event(
                    "file_access_blocked",
                    "high",
                    f"Access to restricted path: {file_path}",
                    {"path": file_path, "operation": operation}
                )
                return False
        
        # Check file extension
        allowed_extensions = self.config.get("file_access", {}).get("allowed_extensions", [])
        if allowed_extensions and path.suffix not in allowed_extensions:
            self._log_security_event(
                "file_access_blocked",
                "medium",
                f"File extension not allowed: {path.suffix}",
                {"path": file_path, "extension": path.suffix, "operation": operation}
            )
            return False
        
        # Check file size for write operations
        if operation == "write" and path.exists():
            max_size_mb = self.config.get("file_access", {}).get("max_file_size_mb", 100)
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > max_size_mb:
                self._log_security_event(
                    "file_access_blocked",
                    "medium",
                    f"File too large: {file_size_mb:.1f}MB",
                    {"path": file_path, "size_mb": file_size_mb, "max_mb": max_size_mb}
                )
                return False
        
        return True
    
    def create_secure_temp_file(self, content: str, suffix: str = ".tmp") -> Optional[Path]:
        """Create a secure temporary file"""
        try:
            # Create temporary file with secure permissions
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=suffix,
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            
            # Set secure permissions (owner read/write only)
            os.chmod(tmp_path, 0o600)
            
            self._log_security_event(
                "temp_file_created",
                "low",
                f"Secure temporary file created",
                {"path": str(tmp_path), "size": len(content)}
            )
            
            return tmp_path
            
        except Exception as e:
            self._log_security_event(
                "temp_file_error",
                "medium",
                f"Failed to create secure temporary file: {e}",
                {"error": str(e)}
            )
            return None
    
    def sanitize_command_for_wsl(self, command: str) -> str:
        """Sanitize command for WSL execution"""
        # Remove potentially dangerous characters
        dangerous_chars = [';', '&&', '||', '|', '>', '<', '`', '$']
        sanitized = command
        
        for char in dangerous_chars:
            if char in sanitized and not self._is_safe_usage(sanitized, char):
                sanitized = sanitized.replace(char, f'\\{char}')
        
        return sanitized
    
    def _is_safe_usage(self, command: str, char: str) -> bool:
        """Check if special character usage is safe"""
        # Allow specific safe patterns
        safe_patterns = {
            '|': ['tee', 'grep', 'awk', 'sed'],  # Piping to safe commands
            '>': ['log', 'txt', 'md'],  # Redirecting to safe file types
            '&&': ['echo', 'cd']  # Chaining with safe commands
        }
        
        if char in safe_patterns:
            return any(pattern in command for pattern in safe_patterns[char])
        
        return False
    
    def get_security_summary(self) -> Dict:
        """Get security summary and statistics"""
        with self.events_lock:
            total_events = len(self.security_events)
            events_by_type = {}
            events_by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            
            for event in self.security_events:
                events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
                events_by_severity[event.severity] += 1
            
            recent_events = [
                event.to_dict() for event in self.security_events[-10:]
            ]
        
        return {
            "total_events": total_events,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "recent_events": recent_events,
            "config": self.config
        }
    
    def export_security_log(self) -> Path:
        """Export security log to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.security_path / f"security_log_{timestamp}.json"
        
        summary = self.get_security_summary()
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        console.print(f"[green]🔒 Security log exported: {log_file}[/green]")
        return log_file
    
    def _log_security_event(self, event_type: str, severity: str, message: str, context: Dict):
        """Log a security event"""
        event = SecurityEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            message=message,
            context=context
        )
        
        with self.events_lock:
            self.security_events.append(event)
        
        # Log to console for high severity events
        if severity in ["high", "critical"]:
            console.print(f"[red]🚨 SECURITY {severity.upper()}: {message}[/red]")
        
        # Save to file
        self._save_security_event(event)
    
    def _save_security_event(self, event: SecurityEvent):
        """Save security event to file"""
        event_file = self.security_path / f"events_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(event_file, 'a', encoding='utf-8') as f:
            json.dump(event.to_dict(), f)
            f.write('\n')


def main():
    """Test the security manager"""
    base_path = Path("project")
    security = SecurityManager(base_path)
    
    # Test API key validation
    console.print("[bold]Testing API key validation:[/bold]")
    security.validate_api_key("openai", "sk-test123")  # Should fail
    security.validate_api_key("openai", "sk-proj-abcd1234567890")  # Should pass
    
    # Test rate limiting
    console.print("\n[bold]Testing rate limiting:[/bold]")
    for i in range(5):
        allowed = security.check_rate_limit("claude_api", "user1")
        console.print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
    
    # Test command validation
    console.print("\n[bold]Testing command validation:[/bold]")
    commands = [
        "claude --help",
        "sudo rm -rf /",
        "npm install",
        "systemctl stop nginx"
    ]
    
    for cmd in commands:
        valid = security.validate_command(cmd)
        console.print(f"'{cmd}': {'✅ Valid' if valid else '❌ Blocked'}")
    
    # Export security log
    security.export_security_log()
    
    # Show summary
    summary = security.get_security_summary()
    console.print(f"\n[bold]Security Events: {summary['total_events']}[/bold]")
    for severity, count in summary['events_by_severity'].items():
        if count > 0:
            console.print(f"  {severity}: {count}")


if __name__ == "__main__":
    main()