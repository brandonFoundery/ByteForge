"""
Multi-Terminal Logging System for AI-Driven Application Builder

This module provides a logging system that creates separate terminal windows
for each AI pass, allowing real-time monitoring of the 4-pass workflow.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.logging import RichHandler

console = Console()


class LogLevel(Enum):
    """Log levels for the multi-terminal system"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class TerminalSession:
    """Represents a terminal session for a specific pass"""
    pass_name: str
    log_file: Path
    terminal_process: Optional[subprocess.Popen] = None
    logger: Optional[logging.Logger] = None
    is_active: bool = False


class MultiTerminalLogger:
    """
    Manages multiple terminal windows for logging different AI passes.
    
    Each pass gets its own terminal window with real-time log streaming.
    """

    def __init__(self, base_path: Path, workflow_id: str):
        self.base_path = base_path
        self.workflow_id = workflow_id
        self.log_dir = base_path / "logs" / workflow_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Terminal sessions for each pass
        self.sessions: Dict[str, TerminalSession] = {}
        
        # Main logger for the orchestrator
        self.main_logger = self._setup_main_logger()
        
        # Track active terminals
        self.active_terminals: List[subprocess.Popen] = []

    def _setup_main_logger(self) -> logging.Logger:
        """Set up the main orchestrator logger"""
        logger = logging.getLogger(f"app_builder.main.{self.workflow_id}")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # File handler
        main_log_file = self.log_dir / "main_orchestrator.log"
        file_handler = logging.FileHandler(main_log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler with Rich formatting
        console_handler = RichHandler(console=console, show_time=True, show_path=False)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def create_pass_logger(self, pass_name: str) -> logging.Logger:
        """
        Create a logger for a specific pass with its own terminal window
        
        Args:
            pass_name: Name of the pass (e.g., 'design', 'review', 'implementation', 'build')
            
        Returns:
            Logger instance for the pass
        """
        if pass_name in self.sessions:
            return self.sessions[pass_name].logger
        
        # Create log file for this pass
        log_file = self.log_dir / f"pass_{pass_name}.log"
        
        # Create logger
        logger = logging.getLogger(f"app_builder.{pass_name}.{self.workflow_id}")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add file handler
        logger.addHandler(file_handler)
        
        # Create terminal session
        session = TerminalSession(
            pass_name=pass_name,
            log_file=log_file,
            logger=logger
        )
        
        self.sessions[pass_name] = session
        
        # Launch terminal window for this pass
        self._launch_terminal_window(session)
        
        return logger

    def _launch_terminal_window(self, session: TerminalSession):
        """Launch a terminal window to monitor the log file for a pass"""
        try:
            if sys.platform == "win32":
                # Windows: Use PowerShell with Get-Content -Wait (equivalent to tail -f)
                cmd = [
                    "powershell", "-Command",
                    f"$Host.UI.RawUI.WindowTitle = 'AI Builder - {session.pass_name.title()} Pass'; "
                    f"Write-Host 'Monitoring {session.pass_name.title()} Pass Logs' -ForegroundColor Cyan; "
                    f"Write-Host 'Log file: {session.log_file}' -ForegroundColor Gray; "
                    f"Write-Host ''; "
                    f"Get-Content '{session.log_file}' -Wait -Tail 0"
                ]
                
                # Start terminal in new window
                terminal_process = subprocess.Popen(
                    ["start", "powershell", "-Command", " ".join(cmd[2:])],
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
                )
                
            elif sys.platform == "darwin":  # macOS
                # macOS: Use Terminal.app with tail -f
                script = f'''
                tell application "Terminal"
                    do script "echo 'Monitoring {session.pass_name.title()} Pass Logs'; echo 'Log file: {session.log_file}'; echo ''; tail -f '{session.log_file}'"
                    set custom title of front window to "AI Builder - {session.pass_name.title()} Pass"
                end tell
                '''
                
                terminal_process = subprocess.Popen([
                    "osascript", "-e", script
                ])
                
            else:  # Linux
                # Linux: Use gnome-terminal with tail -f
                terminal_process = subprocess.Popen([
                    "gnome-terminal",
                    "--title", f"AI Builder - {session.pass_name.title()} Pass",
                    "--",
                    "bash", "-c",
                    f"echo 'Monitoring {session.pass_name.title()} Pass Logs'; "
                    f"echo 'Log file: {session.log_file}'; "
                    f"echo ''; "
                    f"tail -f '{session.log_file}'; "
                    f"read -p 'Press Enter to close...'"
                ])
            
            session.terminal_process = terminal_process
            session.is_active = True
            self.active_terminals.append(terminal_process)
            
            self.main_logger.info(f"Launched terminal window for {session.pass_name} pass")
            
        except Exception as e:
            self.main_logger.error(f"Failed to launch terminal for {session.pass_name}: {e}")
            # Fallback: just log to file without terminal window
            session.is_active = False

    def log_pass_message(self, pass_name: str, level: LogLevel, message: str):
        """
        Log a message for a specific pass
        
        Args:
            pass_name: Name of the pass
            level: Log level
            message: Message to log
        """
        if pass_name not in self.sessions:
            logger = self.create_pass_logger(pass_name)
        else:
            logger = self.sessions[pass_name].logger
        
        # Log to the pass-specific logger
        if level == LogLevel.DEBUG:
            logger.debug(message)
        elif level == LogLevel.INFO:
            logger.info(message)
        elif level == LogLevel.WARNING:
            logger.warning(message)
        elif level == LogLevel.ERROR:
            logger.error(message)
        elif level == LogLevel.CRITICAL:
            logger.critical(message)
        
        # Also log to main logger for overview
        self.main_logger.info(f"[{pass_name.upper()}] {message}")

    def log_pass_start(self, pass_name: str, input_summary: str = ""):
        """Log the start of a pass"""
        message = f"Starting {pass_name.title()} Pass"
        if input_summary:
            message += f" - Input: {input_summary[:100]}..."
        
        self.log_pass_message(pass_name, LogLevel.INFO, "=" * 60)
        self.log_pass_message(pass_name, LogLevel.INFO, message)
        self.log_pass_message(pass_name, LogLevel.INFO, "=" * 60)

    def log_pass_complete(self, pass_name: str, execution_time: float, output_summary: str = ""):
        """Log the completion of a pass"""
        message = f"Completed {pass_name.title()} Pass in {execution_time:.2f} seconds"
        if output_summary:
            message += f" - Output: {output_summary[:100]}..."
        
        self.log_pass_message(pass_name, LogLevel.INFO, "-" * 60)
        self.log_pass_message(pass_name, LogLevel.INFO, message)
        self.log_pass_message(pass_name, LogLevel.INFO, "✅ PASS COMPLETED SUCCESSFULLY")
        self.log_pass_message(pass_name, LogLevel.INFO, "-" * 60)

    def log_pass_error(self, pass_name: str, error_message: str, retry_count: int = 0):
        """Log an error in a pass"""
        retry_info = f" (Retry {retry_count})" if retry_count > 0 else ""
        
        self.log_pass_message(pass_name, LogLevel.ERROR, "!" * 60)
        self.log_pass_message(pass_name, LogLevel.ERROR, f"❌ ERROR in {pass_name.title()} Pass{retry_info}")
        self.log_pass_message(pass_name, LogLevel.ERROR, f"Error: {error_message}")
        self.log_pass_message(pass_name, LogLevel.ERROR, "!" * 60)

    def log_workflow_start(self, feature_name: str, feature_spec: str):
        """Log the start of the complete workflow"""
        self.main_logger.info("🚀 Starting AI-Driven Application Build Workflow")
        self.main_logger.info(f"Feature: {feature_name}")
        self.main_logger.info(f"Workflow ID: {self.workflow_id}")
        self.main_logger.info(f"Log Directory: {self.log_dir}")
        self.main_logger.info(f"Feature Specification: {feature_spec[:200]}...")

    def log_workflow_complete(self, success: bool, total_time: float, feature_branch: str = None, pr_url: str = None):
        """Log the completion of the complete workflow"""
        if success:
            self.main_logger.info("🎉 Workflow completed successfully!")
            if feature_branch:
                self.main_logger.info(f"Feature branch: {feature_branch}")
            if pr_url:
                self.main_logger.info(f"Pull Request: {pr_url}")
        else:
            self.main_logger.error("❌ Workflow failed")
        
        self.main_logger.info(f"Total execution time: {total_time:.2f} seconds")

    def cleanup(self):
        """Clean up terminal processes and resources"""
        self.main_logger.info("Cleaning up terminal sessions...")
        
        for session in self.sessions.values():
            if session.terminal_process and session.is_active:
                try:
                    # Don't forcefully terminate - let user close terminals manually
                    # session.terminal_process.terminate()
                    pass
                except Exception as e:
                    self.main_logger.warning(f"Could not terminate terminal for {session.pass_name}: {e}")
        
        self.main_logger.info("Terminal cleanup completed")

    def get_log_files(self) -> Dict[str, Path]:
        """Get all log files created by this logger"""
        log_files = {"main": self.log_dir / "main_orchestrator.log"}
        
        for pass_name, session in self.sessions.items():
            log_files[pass_name] = session.log_file
        
        return log_files

    def get_active_sessions(self) -> List[str]:
        """Get list of active pass sessions"""
        return [name for name, session in self.sessions.items() if session.is_active]
