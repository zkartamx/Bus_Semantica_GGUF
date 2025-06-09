"""
Setup script for ChromaDB Gradio Demo
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chroma-gradio-demo",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A semantic search demo using ChromaDB and Gradio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chroma_gradio_demo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "chroma-gradio-demo=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.json", "*.md", "*.txt"],
    },
)
