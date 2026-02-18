# Design Documentation

## Architecture Overview

The AI Project Auto-Evaluator follows a **modular, layered architecture** with clear separation of concerns. Each module has a single responsibility and communicates through well-defined interfaces.

## Design Principles Applied

### 1. SOLID Principles

#### Single Responsibility Principle (SRP)
- **GitHubFetcher**: Only handles repository cloning and caching
- **ProjectScanner**: Only scans project structure and counts files
- **QualityAnalyzer**: Only analyzes code quality metrics
- **ScoringEngine**: Only calculates scores from metrics
- **RecommendationEngine**: Only generates recommendations
- **ReportGenerator**: Only formats and outputs reports

#### Open/Closed Principle (OCP)
- New quality metrics can be added without modifying existing analyzer code
- New report formats can be added by extending ReportGenerator
- Scoring rules are externalized in `config.yaml` for easy modification

#### Liskov Substitution Principle (LSP)
- All analyzers follow consistent interfaces
- Dataclasses provide predictable data structures

#### Interface Segregation Principle (ISP)
- Each module exposes only necessary public methods
- Private methods (_method_name) for internal implementation

#### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions (dataclasses, protocols)
- Configuration-driven behavior reduces hard dependencies

### 2. Design Patterns

#### Facade Pattern (main.py)
The `ProjectEvaluator` class provides a simple interface to the complex evaluation pipeline:

```python
evaluator = ProjectEvaluator()
evaluator.evaluate(repo_url)  # Simple interface, complex operations
```

#### Singleton Pattern (utils/logger.py)
Logger ensures single instance across all modules:

```python
class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### Strategy Pattern (scorer/score.py)
Scoring strategies can be swapped via configuration:

```yaml
scoring:
  weights:
    code_quality: 0.30
    architecture: 0.25
```

#### Factory Pattern (reporter/report.py)
Report generation creates different formats from same data:

```python
if format == 'terminal':
    generate_terminal_report()
elif format == 'json':
    generate_json_report()
```

#### Builder Pattern (recommender/suggest.py)
Recommendations are built incrementally based on analysis:

```python
recommendations = []
recommendations.extend(quality_recommendations)
recommendations.extend(architecture_recommendations)
return sorted(recommendations)
```

### 3. Separation of Concerns

Each layer has distinct responsibilities:

```
┌─────────────────────────────────────┐
│  Presentation Layer (CLI/Reports)   │  ← main.py, reporter/
├─────────────────────────────────────┤
│  Business Logic (Scoring/Recs)      │  ← scorer/, recommender/
├─────────────────────────────────────┤
│  Analysis Layer (Quality/Stats)     │  ← analyzer/, scanner/
├─────────────────────────────────────┤
│  Data Access Layer (Fetching)       │  ← fetcher/
├─────────────────────────────────────┤
│  Infrastructure (Logging/Utils)     │  ← utils/
└─────────────────────────────────────┘
```

## Module Design Decisions

### fetcher/github.py

**Why GitPython?**
- Industry standard for Git operations
- Reliable and well-maintained
- Supports shallow clones for performance

**Caching Strategy:**
- Uses file modification time to track cache age
- Configurable expiry (default: 7 days)
- Validates cache integrity before reuse

**Design Choice:**
```python
def fetch(self, url: str, force_refresh: bool = False) -> Optional[Path]:
    """Main public interface - simple and clear"""
```

### scanner/stats.py

**Why pathspec?**
- Supports .gitignore-style patterns
- Efficient file filtering
- Cross-platform compatibility

**Data Structure:**
```python
@dataclass
class ProjectStats:
    """Immutable data class for project statistics"""
    total_files: int = 0
    total_lines: int = 0
    # ... more fields
```

**Why dataclasses?**
- Clean, readable data structures
- Automatic __init__, __repr__, __eq__
- Type hints for better IDE support

### analyzer/quality.py

**Why Radon + Lizard?**
- **Radon**: Excellent for Python (cyclomatic complexity, maintainability index)
- **Lizard**: Multi-language support (C++, Java, Go, etc.)
- Complementary strengths

**Quality Metrics:**
- Cyclomatic Complexity: Measures code complexity
- Maintainability Index: Combined metric of complexity, volume, comments
- Function-level analysis: Identifies problematic functions

### scorer/score.py

**Configuration-Driven:**
```yaml
scoring:
  weights:
    code_quality: 0.30    # 30% of overall score
    architecture: 0.25
```

**Why config-driven?**
- Easy to adjust scoring without code changes
- Different scoring profiles for different needs
- Testable scoring logic

**Weighted Scoring:**
```python
overall_score = (
    code_quality * 0.30 +
    architecture * 0.25 +
    maintainability * 0.20 +
    test_coverage * 0.15 +
    ml_ai_readiness * 0.10
)
```

### recommender/suggest.py

**Priority-Based:**
```python
class Priority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
```

**Actionable Recommendations:**
Each recommendation includes:
- Title & description
- Priority & category
- Impact & effort estimation
- Concrete action steps

### reporter/report.py

**Why Rich?**
- Beautiful terminal output
- Cross-platform color support
- Tables, panels, progress bars
- Enhanced developer experience

**Multiple Output Formats:**
- Terminal: Human-readable, colorful
- JSON: Machine-readable, for integration

### utils/logger.py

**Centralized Logging:**
- Consistent log format across modules
- Rich formatting for terminal
- Optional file logging
- Singleton pattern prevents duplicate loggers

## Error Handling Strategy

### Fail Gracefully
```python
try:
    repo_path = fetcher.fetch(url)
except GitCommandError as e:
    logger.error(f"Git error: {e}")
    return None  # Return None instead of crashing
```

### Informative Errors
- Log context with errors
- Use appropriate log levels
- Provide recovery suggestions

### Defensive Programming
```python
if quality_metrics.files_analyzed == 0:
    return 50.0  # Neutral score if no data
```

## Performance Considerations

### 1. Shallow Clones
```python
git.Repo.clone_from(url, path, depth=1, single_branch=True)
```
- Only fetch latest commit
- Significantly faster than full clone

### 2. Caching
- Reuse cloned repositories
- Configurable cache expiry
- Reduces network usage

### 3. File Limits
```python
def analyze_repository(self, repo_path: Path, max_files: int = 1000):
```
- Safety limits to prevent excessive processing
- Configurable per use case

### 4. Lazy Analysis
- Only analyze source files
- Skip tests, docs, generated files
- Pattern-based filtering

## Extensibility

### Adding New Metrics

1. **Add to analyzer/quality.py:**
```python
def analyze_new_metric(self, file_path: Path) -> float:
    # Implement new metric
    pass
```

2. **Update QualityMetrics dataclass:**
```python
@dataclass
class QualityMetrics:
    new_metric: float = 0.0
```

3. **Add to scorer/score.py:**
```python
def calculate_new_score(self, metrics: QualityMetrics) -> float:
    return metrics.new_metric * weight
```

### Adding New Report Formats

```python
def generate_pdf_report(self, ...):
    """Generate PDF report"""
    pass
```

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external dependencies
- Test edge cases

### Integration Tests
- Test complete pipeline
- Use sample repositories
- Verify output formats

### Example:
```python
def test_scoring_engine():
    engine = ScoringEngine()
    scores = engine.calculate_scores(mock_stats, mock_quality)
    assert 0 <= scores.overall_score <= 100
    assert scores.grade in ['A', 'B', 'C', 'D', 'F']
```

## Future Enhancements

### Potential Improvements
1. **Parallel Processing**: Analyze multiple files concurrently
2. **Incremental Analysis**: Only analyze changed files
3. **Web Interface**: Browser-based reports
4. **Database Storage**: Track metrics over time
5. **CI/CD Integration**: GitHub Actions plugin
6. **Custom Analyzers**: Plugin system for custom metrics

### Scalability
- Current design handles repos up to ~10,000 files
- For larger repos, consider:
  - Sampling strategy
  - Distributed analysis
  - Cloud-based processing

## Code Quality Standards

### Type Hints
```python
def fetch(self, url: str, force_refresh: bool = False) -> Optional[Path]:
```

### Docstrings
```python
"""
Fetch a GitHub repository.

Args:
    url: GitHub repository URL
    force_refresh: Force fresh clone

Returns:
    Optional[Path]: Path to repository or None

Example:
    >>> fetcher.fetch("https://github.com/user/repo")
"""
```

### Naming Conventions
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_CASE`
- Private: `_leading_underscore`

## Conclusion

This system demonstrates **production-quality Python architecture**:
- ✅ Clean, modular design
- ✅ SOLID principles
- ✅ Design patterns
- ✅ Comprehensive error handling
- ✅ Type hints and documentation
- ✅ Extensible and maintainable
- ✅ Performance optimizations
- ✅ Beautiful user experience

The architecture supports long-term maintenance and easy extension while maintaining code quality and testability.
