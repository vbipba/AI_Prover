# AI_Prover - Automated Mathematical Formalization and Proof Generator

AI_Prover is a multi-agent AI system that automatically converts natural language math problems into formal Lean 4 code and generates corresponding proofs. The system bridges the gap between informal mathematics and formal theorem proving.

## 🎯 Project Overview

AI_Prover takes a math problem written in natural language and:

1. **Formalizes** it into Lean 4 syntax
2. **Generates** a mathematically correct proof
3. **Presents** both human-readable and machine-verifiable outputs

## 🏗️ System Architecture

### Multi-Agent Pipeline

- **Agent A1 - Formalizer**: Converts natural language to Lean 4 syntax
- **Agent A2 - Proof Generator**: Generates formal Lean 4 proofs

### Output Format

```
(1) Problem Section
    - Original problem (text form)
    - Lean 4 formalization

(2) Solution Section  
    - Mathematical proof (text form)
    - Lean 4 proof
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Lean 4 installed and accessible in PATH
- OpenAI API key (or local LLM setup)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Prover
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### Single Problem
```bash
python src/main.py --problem "Prove that the sum of two even numbers is even."
```

#### Batch Processing
```bash
python src/main.py --batch data/sample_problems.json
```

#### With Custom Lean Path
```bash
python src/main.py --problem "Your problem here" --lean-path /path/to/lean
```

## 📁 Project Structure

```
AI_Prover/
├── src/
│   ├── main.py              # Main orchestration script
│   ├── agents/
│   │   ├── formalizer.py    # Agent A1 - Formalizer
│   │   └── proof_generator.py # Agent A2 - Proof Generator
│   └── utils/
│       ├── llm_client.py    # LLM API client
│       ├── lean_validator.py # Lean 4 validation
│       └── logger.py        # Enhanced logging
├── data/
│   └── sample_problems.json # Test problems
├── logs/                    # Generated logs and solutions
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### LLM Providers

The system supports multiple LLM providers:

- **OpenAI**: GPT-3.5-turbo (formalizer), GPT-4 (proof generator)
- **Local**: Ollama, LM Studio, or other local LLMs

### Environment Variables

```bash
OPENAI_API_KEY=your_api_key_here
LEAN_PATH=/path/to/lean/executable
LOG_DIR=custom/log/directory
```

## 📊 Metrics and Logging

AI_Prover tracks comprehensive metrics:

- **Formalization success rate**
- **Proof generation success rate** 
- **Lean compilation success rate**
- **Token usage**
- **Processing time**
- **Error patterns**

All metrics are logged to the `logs/` directory with rich formatting.

## 🧪 Testing

### Sample Problems

The `data/sample_problems.json` file contains various test problems:

- Basic arithmetic
- Algebra
- Number theory
- Set theory
- Calculus
- Geometry
- Logic
- Induction
- Inequalities
- Combinatorics

### Running Tests

```bash
# Test with sample problems
python src/main.py --batch data/sample_problems.json --verbose
```

## 🎓 Educational Use

AI_Prover is designed for:

- **Students**: Learning formal theorem proving
- **Educators**: Creating automated proof assistants
- **Researchers**: Exploring AI-assisted mathematics
- **Developers**: Building formal verification tools

## 🔬 Research Value

This project explores:

- Natural language → formal logic translation
- AI-assisted theorem proving
- Multi-agent reasoning systems
- Formal verification with LLMs
- Automated proof generation

## 🚧 Development Roadmap

### Phase 1 - Prototype ✅
- [x] Multi-agent architecture
- [x] Lean 4 integration
- [x] Basic formalization and proof generation
- [x] Metrics tracking

### Phase 2 - Evaluation
- [ ] Comprehensive benchmarking
- [ ] Performance optimization
- [ ] Error analysis and improvement

### Phase 3 - Enhancement
- [ ] Fine-tuning on Lean datasets
- [ ] Error-repair agent (A3)
- [ ] Web interface
- [ ] Advanced feedback loops

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Lean 4 community for the theorem prover
- OpenAI for powerful LLM APIs
- Mathlib contributors for formal mathematics libraries

## 📞 Contact

For questions, suggestions, or collaboration opportunities:

- Create an issue on GitHub
- Email: [your-email@example.com]
- Project website: [your-project-website.com]

---

**AI_Prover** - Making formal mathematics accessible through AI