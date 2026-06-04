"""
Pytest configuration for the Aegis backend test suite.

This conftest adds the backend directory to sys.path so that
`import app.*` resolves correctly regardless of the working directory.
"""

import os
import sys

# Ensure the backend root is on the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
