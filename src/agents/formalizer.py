"""
Agent A1 - Formalizer Agent

Converts natural language math problems into formal Lean 4 syntax.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from ..utils.llm_client import LLMClient
from ..utils.lean_validator import LeanValidator

class FormalizerAgent:
    """Agent responsible for converting natural language math problems to Lean 4."""
    
    def __init__(self, llm_client: LLMClient, lean_validator: LeanValidator):
        self.llm_client = llm_client
        self.lean_validator = lean_validator
        self.logger = logging.getLogger(__name__)
        
    def formalize_problem(self, natural_language_problem: str) -> Dict[str, Any]:
        """
        Convert natural language problem to formal Lean 4 syntax.
        
        Args:
            natural_language_problem: Math problem in natural language
            
        Returns:
            Dict containing formalized problem, Lean code, and draft proof
        """
        self.logger.info(f"Formalizing problem: {natural_language_problem[:100]}...")
        
        # Create prompt for formalization
        prompt = self._create_formalization_prompt(natural_language_problem)
        
        # Get response from LLM
        response = self.llm_client.generate_response(prompt)
        
        # Parse and validate the response
        result = self._parse_formalization_response(response)
        
        # Validate Lean syntax
        if result.get('lean_code'):
            validation_result = self.lean_validator.validate_syntax(result['lean_code'])
            result['syntax_valid'] = validation_result['valid']
            result['syntax_errors'] = validation_result.get('errors', [])
        
        return result
    
    def _create_formalization_prompt(self, problem: str) -> str:
        """Create prompt for converting natural language to Lean 4."""
        return f"""Convert the following natural language math problem into formal Lean 4 syntax.

Problem: {problem}

Please provide:
1. A structured mathematical restatement of the problem
2. The Lean 4 theorem declaration
3. A draft proof in mathematical text form

Example format:
---
Structured Problem: [Your structured version]
Lean 4 Theorem:
```lean
theorem example_theorem (a b : ℕ) (ha : Even a) (hb : Even b) : Even (a + b) := 
```
Draft Proof: [Your draft proof in mathematical language]
---
"""
    
    def _parse_formalization_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format."""
        lines = response.split('\n')
        result = {
            'structured_problem': '',
            'lean_code': '',
            'draft_proof': '',
            'raw_response': response
        }
        
        current_section = None
        lean_code_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Structured Problem:'):
                current_section = 'structured_problem'
                result['structured_problem'] = line.replace('Structured Problem:', '').strip()
            elif line.startswith('Lean 4 Theorem:'):
                current_section = 'lean_code'
            elif line.startswith('Draft Proof:'):
                current_section = 'draft_proof'
                result['draft_proof'] = line.replace('Draft Proof:', '').strip()
            elif line.startswith('```lean') and current_section == 'lean_code':
                continue
            elif line.startswith('```') and current_section == 'lean_code':
                current_section = None
            elif current_section == 'lean_code' and line:
                lean_code_lines.append(line)
            elif current_section == 'structured_problem' and line and not line.startswith('Structured Problem:'):
                result['structured_problem'] += ' ' + line
            elif current_section == 'draft_proof' and line and not line.startswith('Draft Proof:'):
                result['draft_proof'] += ' ' + line
        
        result['lean_code'] = '\n'.join(lean_code_lines)
        return result