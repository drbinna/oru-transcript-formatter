from setuptools import setup, find_packages

setup(
    name="transcript-formatter",
    version="0.1.0",
    description="Convert raw transcript text files into beautifully formatted Word and PDF documents",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "python-docx>=0.8.11",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "transcript-format=transcript_formatter.cli:cli",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)