from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pandas_mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个基于MCP架构的pandas扩展框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pandas_mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Data Science",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "scikit-learn>=0.24.0",
        "scipy>=1.6.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=20.8b1",
            "isort>=5.0",
            "flake8>=3.9.0",
            "mypy>=0.800"
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx-rtd-theme>=0.5.0",
            "nbsphinx>=0.8.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "pandas_mcp_example=pandas_mcp.examples.basic_example:run_example"
        ]
    },
    include_package_data=True,
    zip_safe=False
)
