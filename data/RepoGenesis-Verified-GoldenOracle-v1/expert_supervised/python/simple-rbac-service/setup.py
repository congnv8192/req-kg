#!/usr/bin/env python3
"""
Setup configuration for Simple RBAC Service
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-rbac-service",
    version="1.0.0",
    author="Development Team",
    description="A lightweight Role-Based Access Control (RBAC) service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/simple-rbac-service",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.0.0",
        "requests>=2.25.0",
        "Werkzeug>=2.0.0",
    ],
)

