"""
Setup script for Pakistan Freight Intelligence Platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pak-freight-intelligence",
    version="1.0.0",
    author="Pakistan Freight Intelligence Team",
    author_email="info@freight-intelligence.pk",
    description="Pakistan's first real-time freight rate intelligence platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pak-freight-intelligence",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Transportation Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Transportation",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "freight-backend=backend.main:main",
            "freight-frontend=frontend.app:main",
            "freight-test=test_platform:main",
        ],
    },
)