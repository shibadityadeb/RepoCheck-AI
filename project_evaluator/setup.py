"""
Setup configuration for AI Project Auto-Evaluator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="RepoCheck-AI",
    version="1.0.0",
    author="Shibaditya Deb",
    description="Production-quality automated GitHub repository evaluation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shibadityadeb/RepoCheck-AI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "GitPython>=3.1.41",
        "radon>=6.0.1",
        "rich>=13.7.0",
        "PyYAML>=6.0.1",
        "pathspec>=0.12.1",
        "lizard>=1.17.10",
        "pygments>=2.17.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "mypy>=1.8.0",
            "types-PyYAML>=6.0.12.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "project-evaluator=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.yaml"],
    },
)
