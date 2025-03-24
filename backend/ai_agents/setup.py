"""
Setup script for the Hotel AI system.
"""

from setuptools import setup, find_packages

setup(
    name="hotel_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "faiss-cpu",
        "pydantic",
        "numpy",
        "langchain",
        "langchain-core",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock",
        ],
    },
)