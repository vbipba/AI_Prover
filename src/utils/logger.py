"""
Logging utilities for AI_Prover.

Provides structured logging with metrics collection and performance tracking.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict

# Try to import rich for better formatting, fallback to standard logging
try:
    from rich.logging import RichHandler
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class Metrics:
    """Metrics for tracking AI_Prover performance."""
    timestamp: str
    problem_id: str
    problem_text: str
    formalization_time: float
    proof_generation_time: float
    total_time: float
    formalization_success: bool
    proof_success: bool
    lean_compilation_success: bool
    tokens_used: Dict[str, int]
    errors: List[str]
    lean_errors: List[str]

class AIProverLogger:
    """Enhanced logger for AI_Prover with metrics collection."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize AI_Prover logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup rich console for nice formatting (if available)
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Setup file logging
        self._setup_logging()
        
        # Metrics tracking
        self.metrics: List[Metrics] = []
        self.current_session = {}
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create logger
        self.logger = logging.getLogger('ai_prover')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Rich handler for console output (if available)
        if RICH_AVAILABLE and self.console:
            rich_handler = RichHandler(
                console=self.console,
                rich_tracebacks=True,
                show_time=True,
                show_path=True
            )
            rich_handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
            self.logger.addHandler(rich_handler)
        else:
            # Fallback to standard console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
            self.logger.addHandler(console_handler)
        
        # File handler for detailed logs
        log_file = self.log_dir / f"ai_prover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        self.logger.addHandler(file_handler)
    
    def start_problem_session(self, problem_id: str, problem_text: str):
        """Start a new problem solving session."""
        self.current_session = {
            'problem_id': problem_id,
            'problem_text': problem_text,
            'start_time': time.time(),
            'formalization_start': None,
            'proof_generation_start': None,
            'errors': [],
            'lean_errors': []
        }
        
        self.logger.info(f"Starting problem session: {problem_id}")
        self.logger.info(f"Problem: {problem_text[:100]}...")
    
    def start_formalization(self):
        """Mark start of formalization phase."""
        self.current_session['formalization_start'] = time.time()
        self.logger.info("Starting formalization phase...")
    
    def end_formalization(self, success: bool, lean_code: str = "", errors: List[str] = None):
        """Mark end of formalization phase."""
        if errors:
            self.current_session['errors'].extend(errors)
        
        formalization_time = 0
        if self.current_session['formalization_start']:
            formalization_time = time.time() - self.current_session['formalization_start']
        
        self.logger.info(f"Formalization completed in {formalization_time:.2f}s - Success: {success}")
        
        if lean_code:
            self._log_lean_code("Formalized Lean Code", lean_code)
    
    def start_proof_generation(self):
        """Mark start of proof generation phase."""
        self.current_session['proof_generation_start'] = time.time()
        self.logger.info("Starting proof generation phase...")
    
    def end_proof_generation(self, success: bool, lean_proof: str = "", errors: List[str] = None):
        """Mark end of proof generation phase."""
        if errors:
            self.current_session['errors'].extend(errors)
        
        proof_time = 0
        if self.current_session['proof_generation_start']:
            proof_time = time.time() - self.current_session['proof_generation_start']
        
        self.logger.info(f"Proof generation completed in {proof_time:.2f}s - Success: {success}")
        
        if lean_proof:
            self._log_lean_code("Generated Lean Proof", lean_proof)
    
    def log_lean_compilation(self, success: bool, errors: List[str] = None):
        """Log Lean compilation results."""
        if errors:
            self.current_session['lean_errors'].extend(errors)
        
        self.logger.info(f"Lean compilation - Success: {success}")
        if errors:
            for error in errors:
                self.logger.warning(f"Lean error: {error}")
    
    def log_tokens_used(self, tokens: Dict[str, int]):
        """Log tokens used by LLM calls."""
        self.current_session['tokens_used'] = tokens
        self.logger.info(f"Tokens used: {tokens}")
    
    def end_problem_session(self):
        """End the current problem session and save metrics."""
        if not self.current_session:
            return
        
        total_time = time.time() - self.current_session['start_time']
        
        # Create metrics record
        metrics = Metrics(
            timestamp=datetime.now().isoformat(),
            problem_id=self.current_session['problem_id'],
            problem_text=self.current_session['problem_text'],
            formalization_time=self._get_formalization_time(),
            proof_generation_time=self._get_proof_time(),
            total_time=total_time,
            formalization_success=len(self.current_session.get('errors', [])) == 0,
            proof_success=len(self.current_session.get('errors', [])) == 0,
            lean_compilation_success=len(self.current_session.get('lean_errors', [])) == 0,
            tokens_used=self.current_session.get('tokens_used', {}),
            errors=self.current_session.get('errors', []),
            lean_errors=self.current_session.get('lean_errors', [])
        )
        
        self.metrics.append(metrics)
        
        # Save metrics to file
        self._save_metrics()
        
        # Log summary
        self.logger.info(f"Problem session completed:")
        self.logger.info(f"  Total time: {total_time:.2f}s")
        self.logger.info(f"  Formalization: {'✓' if metrics.formalization_success else '✗'}")
        self.logger.info(f"  Proof generation: {'✓' if metrics.proof_success else '✗'}")
        self.logger.info(f"  Lean compilation: {'✓' if metrics.lean_compilation_success else '✗'}")
        
        # Clear current session
        self.current_session = {}
    
    def _get_formalization_time(self) -> float:
        """Get formalization time."""
        if not self.current_session.get('formalization_start'):
            return 0
        end_time = self.current_session.get('proof_generation_start') or time.time()
        return end_time - self.current_session['formalization_start']
    
    def _get_proof_time(self) -> float:
        """Get proof generation time."""
        if not self.current_session.get('proof_generation_start'):
            return 0
        return time.time() - self.current_session['proof_generation_start']
    
    def _log_lean_code(self, title: str, code: str):
        """Log Lean code with syntax highlighting."""
        self.logger.info(f"\n{title}:")
        if RICH_AVAILABLE and self.console:
            try:
                self.console.print(f"\n[bold]{title}:[/bold]")
                self.console.print(f"[green]{code}[/green]")
            except UnicodeEncodeError:
                # Fallback for encoding issues
                self.logger.info(f"Lean code:\n{code}")
        else:
            # Fallback to plain text logging
            self.logger.info(f"Lean code:\n{code}")
    
    def _save_metrics(self):
        """Save metrics to JSON file."""
        metrics_file = self.log_dir / "metrics.json"
        
        # Load existing metrics
        existing_metrics = []
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    existing_metrics = json.load(f)
            except:
                pass
        
        # Append new metrics
        existing_metrics.extend([asdict(metric) for metric in self.metrics])
        
        # Save updated metrics
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(existing_metrics, f, indent=2, ensure_ascii=False)
        
        # Clear in-memory metrics
        self.metrics = []
    
    def get_session_logger(self):
        """Get the logger instance."""
        return self.logger
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(message)