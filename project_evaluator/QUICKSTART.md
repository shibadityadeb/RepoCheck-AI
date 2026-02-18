# 🚀 Quick Start Guide

Get up and running with AI Project Auto-Evaluator in 5 minutes!

## Step 1: Installation (2 minutes)

```bash
# Navigate to the project directory
cd project_evaluator

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Test the Installation (1 minute)

```bash
# Verify it works
python main.py --help
```

You should see:
```
usage: main.py [-h] --repo REPO [--format {terminal,json}] ...
```

## Step 3: Run Your First Evaluation (2 minutes)

```bash
# Analyze a popular Python project
python main.py --repo https://github.com/psf/requests
```

This will:
1. ✅ Clone the repository
2. ✅ Analyze code structure
3. ✅ Calculate quality metrics
4. ✅ Generate scores
5. ✅ Create recommendations
6. ✅ Display a beautiful report

## Common Usage Patterns

### 📊 Terminal Report (Default)
```bash
python main.py --repo https://github.com/user/repo
```

### 💾 JSON Export
```bash
python main.py --repo https://github.com/user/repo --format json --output report.json
```

### 🔄 Force Refresh
```bash
python main.py --repo https://github.com/user/repo --force-refresh
```

### 🐛 Debug Mode
```bash
python main.py --repo https://github.com/user/repo --verbose
```

## Programmatic Usage

Create a Python script:

```python
from fetcher import fetch_github_repo
from scanner import scan_project
from analyzer import analyze_code_quality
from scorer import calculate_project_scores

# Quick evaluation
repo_path = fetch_github_repo("https://github.com/pallets/flask")
stats = scan_project(repo_path)
quality = analyze_code_quality(repo_path)
scores = calculate_project_scores(stats, quality)

print(f"Overall Score: {scores.overall_score}/100")
print(f"Grade: {scores.grade}")
```

## Customize Scoring Weights

Edit `config.yaml`:

```yaml
scoring:
  weights:
    code_quality: 0.35      # Increase code quality weight
    architecture: 0.25
    maintainability: 0.20
    test_coverage: 0.15
    ml_ai_readiness: 0.05   # Decrease ML/AI weight
```

## Troubleshooting

### Issue: `command not found: python`
**Solution:** Use `python3` instead:
```bash
python3 main.py --repo https://github.com/user/repo
```

### Issue: `ModuleNotFoundError: No module named 'git'`
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Repository clone fails
**Solution:** Check internet connection and repository URL:
```bash
# Test with a known public repo
python main.py --repo https://github.com/pallets/flask
```

### Issue: Permission denied
**Solution:** Make sure main.py is executable:
```bash
chmod +x main.py
./main.py --repo https://github.com/user/repo
```

## Example Repositories to Try

```bash
# Small project
python main.py --repo https://github.com/pallets/click

# Medium project
python main.py --repo https://github.com/psf/requests

# Large project (may take a few minutes)
python main.py --repo https://github.com/django/django

# ML project
python main.py --repo https://github.com/ageron/handson-ml2
```

## Next Steps

1. ✅ Read [README.md](README.md) for detailed documentation
2. ✅ Check [DESIGN.md](DESIGN.md) for architecture details
3. ✅ Explore [example_usage.py](example_usage.py) for advanced usage
4. ✅ Customize `config.yaml` for your needs

## Getting Help

- Check the `--help` flag: `python main.py --help`
- Review error messages with `--verbose` flag
- Read the docstrings in the code
- Consult the documentation files

## Pro Tips 💡

1. **Use caching**: Second run is much faster due to caching
2. **JSON output**: Great for automation and CI/CD integration
3. **Verbose mode**: Use when debugging or learning the system
4. **Custom config**: Create multiple config files for different evaluation profiles

## Congratulations! 🎉

You're now ready to evaluate any GitHub repository!

Try it on your own projects:
```bash
python main.py --repo https://github.com/YOUR_USERNAME/YOUR_PROJECT
```

Happy evaluating! 🚀
