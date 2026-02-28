"""
Lean 4 Validator for syntax and proof validation.

Integrates with Lean 4 compiler to validate generated code.
"""

import os
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

class LeanValidator:
    """Validator for Lean 4 code using the Lean compiler."""
    
    def __init__(self, lean_path: Optional[str] = None):
        """
        Initialize Lean validator.
        
        Args:
            lean_path: Path to Lean 4 executable. If None, tries to find it in PATH.
        """
        self.lean_path = lean_path
        self.logger = logging.getLogger(__name__)
        
        # Try to find Lean executable
        if not self.lean_path:
            self.lean_path = self._find_lean_executable()
    
    def _find_lean_executable(self) -> str:
        """Find Lean 4 executable in system PATH."""
        try:
            # Try common locations
            common_paths = [
                'lean',  # In PATH
                'lean.exe',  # Windows
                '/usr/local/bin/lean',
                '/usr/bin/lean',
                'C:\\bin\\lean.exe',
                'C:\\Program Files\\lean\\bin\\lean.exe'
            ]
            
            for path in common_paths:
                try:
                    result = subprocess.run(
                        [path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        self.logger.info(f"Found Lean executable: {path}")
                        return path
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            raise FileNotFoundError("Lean 4 executable not found. Please install Lean 4 and ensure it's in your PATH.")
            
        except Exception as e:
            self.logger.error(f"Error finding Lean executable: {e}")
            raise
    
    def validate_syntax(self, lean_code: str) -> Dict[str, Any]:
        """
        Validate Lean 4 syntax using temporary file.
        
        Args:
            lean_code: Lean code to validate
            
        Returns:
            Dict with validation results
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': []
        }
        
        # Create temporary Lean file
        temp_file = Path('temp_validation.lean')
        
        try:
            # Write code to temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(lean_code)
            
            # Run Lean compiler on the file
            cmd = [self.lean_path, '--run', str(temp_file)]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output
            if process.returncode == 0:
                result['valid'] = True
            else:
                # Parse Lean compiler errors
                errors = self._parse_lean_output(process.stderr)
                result['errors'] = errors
            
        except subprocess.TimeoutExpired:
            result['errors'].append("Lean compilation timed out")
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
        
        return result
    
    def validate_proof(self, lean_proof: str) -> Dict[str, Any]:
        """
        Validate Lean 4 proof by compiling it.
        
        Args:
            lean_proof: Lean proof code to validate
            
        Returns:
            Dict with validation results
        """
        # Create a complete Lean file with the proof
        lean_file_content = f"""
import Mathlib

{lean_proof}
"""
        
        return self.validate_syntax(lean_file_content)
    
    def _parse_lean_output(self, output: str) -> List[str]:
        """Parse Lean compiler output for errors."""
        errors = []
        
        if not output:
            return errors
        
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('error:' in line.lower() or 'failed' in line.lower()):
                errors.append(line)
        
        return errors
    
    def check_lean_installation(self) -> bool:
        """Check if Lean 4 is properly installed."""
        try:
            result = subprocess.run(
                [self.lean_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False