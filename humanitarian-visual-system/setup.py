#!/usr/bin/env python3
"""
Humanitarian Visual System - Setup Script
نظام التوثيق البصري الإنساني - ملف التثبيت

Install with:
    pip install humanitarian-visual
    pip install -e .  (development mode)

التثبيت:
    pip install humanitarian-visual
    pip install -e .  (وضع التطوير)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="humanitarian-visual",
    version="1.0.0",
    author="Humanitarian Visual System Team",
    author_email="hv@humanitarian.org",
    description="Ethical documentation system for humanitarian visual content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/humanitarian/visual-system",
    project_urls={
        "Documentation": "https://github.com/humanitarian/visual-system/docs",
        "Bug Tracker": "https://github.com/humanitarian/visual-system/issues",
    },
    license="Humanitarian Use License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Humanitarian Organizations",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Documentation",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pillow>=9.0.0",
        "opencv-python>=4.5.0",
    ],
    extras_require={
        "full": [
            "streamlit>=1.20.0",
            "piexif>=1.1.3",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hv=hv.cli:main",
            "humanitarian-visual=hv.cli:main",
        ],
    },
    package_data={
        "hv": [
            "config/*.yaml",
            "templates/*.json",
        ],
    },
    keywords=[
        "humanitarian",
        "documentation",
        "visual",
        "ethical",
        "media",
        "photography",
        "gaza",
        "aid",
    ],
)
