"""
AI_Prover - Main orchestration script.

Multi-agent system for converting natural language math problems to formal Lean 4 proofs.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import modules (handle both direct execution and module import)
try:
    from .agents.formalizer import FormalizerAgent
    from .agents.proof_generator import ProofGeneratorAgent
    from .utils.llm_client import LLMClient
    from .utils.lean_validator import LeanValidator
    from .utils.logger import AIProverLogger
except ImportError:
    # Fallback for direct execution - use absolute imports
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Add project root to path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Import with absolute paths
    from src.agents.formalizer import FormalizerAgent
    from src.agents.proof_generator import ProofGeneratorAgent
    from src.utils.llm_client import LLMClient
    from src.utils.lean_validator import LeanValidator
    from src.utils.logger import AIProverLogger

class AIProver:
    """Main AI_Prover orchestrator."""
    
    def __init__(self, lean_path: Optional[str] = None, log_dir: str = "logs"):
        """
        Initialize AI_Prover system.
        
        Args:
            lean_path: Path to Lean 4 executable
            log_dir: Directory for logs and outputs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.logger = AIProverLogger(log_dir)
        self.lean_validator = LeanValidator(lean_path)
        self.formalizer_client = LLMClient.create_formalizer_client()
        self.proof_generator_client = LLMClient.create_proof_generator_client()
        
        # Initialize agents
        self.formalizer = FormalizerAgent(self.formalizer_client, self.lean_validator)
        self.proof_generator = ProofGeneratorAgent(self.proof_generator_client, self.lean_validator)
        
        self.logger.log_info("AI_Prover initialized successfully")
    
    def solve_problem(self, problem_text: str, problem_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Solve a math problem by converting to Lean 4 and generating proof.
        
        Args:
            problem_text: Natural language math problem
            problem_id: Optional problem identifier
            
        Returns:
            Dict containing complete solution with metrics
        """
        if not problem_id:
            problem_id = f"problem_{int(time.time())}"
        
        # Start logging session
        self.logger.start_problem_session(problem_id, problem_text)
        
        # Phase 1: Formalization
        self.logger.start_formalization()
        formalization_result = self.formalizer.formalize_problem(problem_text)
        
        # Check formalization success
        formalization_success = formalization_result.get('syntax_valid', False)
        formalization_errors = formalization_result.get('syntax_errors', [])
        
        self.logger.end_formalization(
            success=formalization_success,
            lean_code=formalization_result.get('lean_code', ''),
            errors=formalization_errors
        )
        
        if not formalization_success:
            self.logger.log_error("Formalization failed, cannot proceed to proof generation")
            self.logger.end_problem_session()
            return {
                'problem_id': problem_id,
                'success': False,
                'phase': 'formalization',
                'error': 'Formalization failed',
                'errors': formalization_errors,
                'formalization': formalization_result
            }
        
        # Phase 2: Proof Generation
        self.logger.start_proof_generation()
        lean_theorem = formalization_result.get('lean_code', '')
        structured_problem = formalization_result.get('structured_problem', '')
        
        proof_result = self.proof_generator.generate_proof(lean_theorem, structured_problem)
        
        # Check proof generation success
        proof_success = proof_result.get('proof_valid', False)
        proof_errors = proof_result.get('proof_errors', [])
        
        self.logger.end_proof_generation(
            success=proof_success,
            lean_proof=proof_result.get('lean_proof', ''),
            errors=proof_errors
        )
        
        # Phase 3: Lean Compilation
        lean_proof = proof_result.get('lean_proof', '')
        if lean_proof:
            lean_compilation_result = self.lean_validator.validate_proof(lean_proof)
            lean_compilation_success = lean_compilation_result['valid']
            lean_compilation_errors = lean_compilation_result.get('errors', [])
        else:
            lean_compilation_success = False
            lean_compilation_errors = ['No proof generated']
        
        self.logger.log_lean_compilation(lean_compilation_success, lean_compilation_errors)
        
        # End session and save results
        self.logger.end_problem_session()
        
        # Save complete solution
        solution = {
            'problem_id': problem_id,
            'problem_text': problem_text,
            'success': formalization_success and proof_success and lean_compilation_success,
            'formalization': formalization_result,
            'proof': proof_result,
            'lean_compilation': {
                'success': lean_compilation_success,
                'errors': lean_compilation_errors
            },
            'metrics': {
                'formalization_success': formalization_success,
                'proof_success': proof_success,
                'lean_compilation_success': lean_compilation_success,
                'total_errors': len(formalization_errors) + len(proof_errors) + len(lean_compilation_errors)
            }
        }
        
        # Save solution to file
        self._save_solution(problem_id, solution)
        
        return solution
    
    def _save_solution(self, problem_id: str, solution: Dict[str, Any]):
        """Save complete solution to file."""
        solution_file = self.log_dir / f"solution_{problem_id}.json"
        
        with open(solution_file, 'w', encoding='utf-8') as f:
            json.dump(solution, f, indent=2, ensure_ascii=False)
        
        # Also save Lean files if successful
        if solution['success']:
            lean_file = self.log_dir / f"{problem_id}.lean"
            lean_code = solution['formalization'].get('lean_code', '')
            lean_proof = solution['proof'].get('lean_proof', '')
            
            with open(lean_file, 'w', encoding='utf-8') as f:
                f.write(f"-- AI_Prover Solution: {problem_id}\n")
                f.write(f"-- Problem: {solution['problem_text']}\n\n")
                f.write("import Mathlib\n\n")
                f.write(f"-- Formalized theorem:\n{lean_code}\n\n")
                f.write(f"-- Generated proof:\n{lean_proof}\n")
    
    def batch_solve(self, problems: Dict[str, str]) -> Dict[str, Any]:
        """
        Solve multiple problems in batch.
        
        Args:
            problems: Dict mapping problem IDs to problem texts
            
        Returns:
            Dict containing results for all problems
        """
        results = {}
        total_start_time = time.time()
        
        for problem_id, problem_text in problems.items():
            self.logger.log_info(f"Solving problem {problem_id}")
            try:
                result = self.solve_problem(problem_text, problem_id)
                results[problem_id] = result
            except Exception as e:
                self.logger.log_error(f"Error solving problem {problem_id}: {str(e)}")
                results[problem_id] = {
                    'problem_id': problem_id,
                    'success': False,
                    'error': str(e),
                    'phase': 'unknown'
                }
        
        total_time = time.time() - total_start_time
        
        # Calculate summary statistics
        total_problems = len(results)
        successful_problems = sum(1 for r in results.values() if r.get('success', False))
        
        summary = {
            'total_problems': total_problems,
            'successful_problems': successful_problems,
            'success_rate': successful_problems / total_problems if total_problems > 0 else 0,
            'total_time': total_time,
            'average_time_per_problem': total_time / total_problems if total_problems > 0 else 0,
            'results': results
        }
        
        # Save batch results
        batch_file = self.log_dir / f"batch_results_{int(time.time())}.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.log_info(f"Batch processing completed:")
        self.logger.log_info(f"  Total problems: {total_problems}")
        self.logger.log_info(f"  Successful: {successful_problems}")
        self.logger.log_info(f"  Success rate: {summary['success_rate']:.2%}")
        self.logger.log_info(f"  Total time: {total_time:.2f}s")
        
        return summary

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='AI_Prover - Automated Mathematical Formalization and Proof Generator')
    parser.add_argument('--problem', '-p', type=str, help='Single problem to solve')
    parser.add_argument('--batch', '-b', type=str, help='JSON file with batch problems')
    parser.add_argument('--lean-path', type=str, help='Path to Lean 4 executable')
    parser.add_argument('--log-dir', type=str, default='logs', help='Log directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize AI_Prover
        prover = AIProver(lean_path=args.lean_path, log_dir=args.log_dir)
        
        if args.problem:
            # Solve single problem
            result = prover.solve_problem(args.problem)
            print(f"\nSolution for problem:")
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Lean file saved to: {args.log_dir}/{result['problem_id']}.lean")
            else:
                print(f"Errors: {result.get('errors', [])}")
        
        elif args.batch:
            # Solve batch of problems
            with open(args.batch, 'r', encoding='utf-8') as f:
                problems = json.load(f)
            
            summary = prover.batch_solve(problems)
            print(f"\nBatch processing summary:")
            print(f"Total problems: {summary['total_problems']}")
            print(f"Successful: {summary['successful_problems']}")
            print(f"Success rate: {summary['success_rate']:.2%}")
            print(f"Results saved to: {args.log_dir}")
        
        else:
            print("Please provide either --problem or --batch argument")
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.exception("Unexpected error in main")
        sys.exit(1)

if __name__ == "__main__":
    import time
    main()