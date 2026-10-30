"""
CivicAI - Vercel Serverless Function Entry Point
Imports and exposes the Flask WSGI application instance.
"""
import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

