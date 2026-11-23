"""Ship the repository's Lean sources in the wheel alongside the Python package."""
from setuptools import find_namespace_packages, setup

setup(packages=[*find_namespace_packages("src", include=["skillflow", "skillflow.*"],
                                        exclude=["*.__pycache__", "*.__pycache__.*"]),
                "skillflow._lean_sources"])
