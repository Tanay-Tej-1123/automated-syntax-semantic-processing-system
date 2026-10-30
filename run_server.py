"""
Runner script for Automated Syntax and Semantic Analysis System
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Automated Syntax and Semantic Analysis System on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
