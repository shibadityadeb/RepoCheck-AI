# AI Project Auto-Evaluator

A production-quality modular system for automated GitHub repository evaluation. Analyzes code quality, architecture, maintainability, test coverage, and ML/AI readiness to generate comprehensive engineering-style evaluation reports.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

- **Automated Repository Analysis**: Clone and analyze any public GitHub repository
- **Multi-Metric Evaluation**: 
  - Code Quality Score (0-100)
  - Architecture Rating
  - Maintainability Score
  - Test Coverage Estimation
  - ML/AI Readiness Score
- **Beautiful Terminal Reports**: Rich, colorful terminal output using Rich library
- **JSON Export**: Machine-readable reports for integration
- **Smart Caching**: Reuse cloned repositories to save time
- **Actionable Recommendations**: Prioritized improvement roadmap
- **Production-Ready**: Clean architecture, SOLID principles, comprehensive error handling

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Git installed on your system

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/project-evaluator.git
cd project-evaluator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Basic Usage

```bash
# Analyze a GitHub repository (terminal output)
python main.py --repo https://github.com/user/repo

# Generate JSON report
python main.py --repo https://github.com/user/repo --format json

# Save JSON to file
python main.py --repo https://github.com/user/repo --format json --output report.json

# Force fresh clone (ignore cache)
python main.py --repo https://github.com/user/repo --force-refresh

# Verbose output for debugging
python main.py --repo https://github.com/user/repo --verbose
```

### Advanced Options

```bash
# Use custom configuration
python main.py --repo https://github.com/user/repo --config custom_config.yaml

# Specify custom cache directory
python main.py --repo https://github.com/user/repo --cache-dir /path/to/cache

# Show version
python main.py --version

# Show help
python main.py --help
```

## 📊 Output Example

### Terminal Report

```
╔══════════════════════════════════════════════════════════════╗
║                    🔍 AI PROJECT AUTO-EVALUATOR              ║
║  Repository: https://github.com/user/awesome-project         ║
║  Generated: 2026-02-18 14:30:00                             ║
╚══════════════════════════════════════════════════════════════╝

──────────────────── 📊 Project Overview ─────────────────────

Total Files                 142
Total Lines of Code         12,450
Code Lines                  9,230
Languages                   Python, JavaScript
Files Analyzed              98

────────────────────── ⭐ Evaluation Scores ──────────────────

╔══════════════════════════════════════════════════════════════╗
║                       Overall Score                          ║
║                    78.5/100 (Grade: C)                       ║
╚══════════════════════════════════════════════════════════════╝

Category                    Score        Rating
─────────────────────────────────────────────────────
Code Quality                82.3/100     ████████░░
Architecture                75.0/100     ███████░░░
Maintainability            70.5/100     ███████░░░
Test Coverage              65.0/100     ██████░░░░
ML/AI Readiness            45.0/100     ████░░░░░░
```

### JSON Report

```json
{
  "metadata": {
    "repository": "https://github.com/user/repo",
    "generated_at": "2026-02-18T14:30:00",
    "evaluator_version": "1.0.0"
  },
  "scores": {
    "overall": 78.5,
    "grade": "C",
    "code_quality": 82.3,
    "architecture": 75.0,
    "maintainability": 70.5,
    "test_coverage": 65.0,
    "ml_ai_readiness": 45.0
  },
  "recommendations": [
    {
      "title": "Improve Test Coverage",
      "priority": "High",
      "category": "Testing",
      "action_steps": ["..."]
    }
  ]
}
```

## 🏗️ Architecture

The system follows clean, modular architecture with clear separation of concerns:

```
project_evaluator/
│
├── main.py                # CLI entry point (Facade Pattern)
├── config.yaml            # Scoring configuration
├── requirements.txt       # Dependencies
│
├── fetcher/               # Repository fetching (Single Responsibility)
│   ├── __init__.py
│   └── github.py          # GitHub cloning and caching
│
├── scanner/               # Project structure analysis
│   ├── __init__.py
│   └── stats.py           # File counting, LOC, language detection
│
├── analyzer/              # Code quality analysis
│   ├── __init__.py
│   └── quality.py         # Complexity, maintainability metrics
│
├── scorer/                # Scoring engine (Strategy Pattern)
│   ├── __init__.py
│   └── score.py           # Weighted metric calculation
│
├── recommender/           # Improvement suggestions (Builder Pattern)
│   ├── __init__.py
│   └── suggest.py         # Actionable recommendations
│
├── reporter/              # Report generation (Factory Pattern)
│   ├── __init__.py
│   └── report.py          # Terminal and JSON output
│
└── utils/                 # Shared utilities
    ├── __init__.py
    └── logger.py          # Centralized logging (Singleton Pattern)
```

### Design Principles

- **SOLID Principles**: Each module has a single responsibility
- **Separation of Concerns**: Clear boundaries between modules
- **Dependency Injection**: Configuration-driven behavior
- **Design Patterns**: Facade, Strategy, Factory, Singleton, Builder
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Docstrings**: Every class and function documented

## 📝 Configuration

Edit `config.yaml` to customize scoring weights and thresholds:

```yaml
scoring:
  weights:
    code_quality: 0.30        # 30% weight
    architecture: 0.25        # 25% weight
    maintainability: 0.20     # 20% weight
    test_coverage: 0.15       # 15% weight
    ml_ai_readiness: 0.10     # 10% weight
  
  thresholds:
    complexity:
      excellent: 5
      good: 10
      moderate: 15
      poor: 20
    
    maintainability:
      excellent: 80
      good: 65
      moderate: 50
      poor: 25
```

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### Code Quality Checks

```bash
# Run mypy for type checking
mypy project_evaluator/

# Check complexity
radon cc project_evaluator/ -a

# Check maintainability
radon mi project_evaluator/ -s
```

## 📚 Dependencies

- **GitPython**: Repository cloning
- **Radon**: Cyclomatic complexity and maintainability index
- **Lizard**: Multi-language code analysis
- **Rich**: Beautiful terminal output
- **PyYAML**: Configuration management
- **pathspec**: .gitignore-style pattern matching

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python 3.10+
- Uses industry-standard tools (Radon, Lizard)
- Inspired by best practices in software engineering

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ by a Senior Python Software Architect**
