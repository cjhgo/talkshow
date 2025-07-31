#!/usr/bin/env python3
"""
TalkShow Web Server Launcher

Launch the TalkShow web application with FastAPI and uvicorn.
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the TalkShow web server."""
    print("🎭 Starting TalkShow Web Server...")
    print("=" * 50)
    
    # Check if data file exists
    data_file = project_root / "data" / "web_sessions.json"
    if not data_file.exists():
        print("⚠️  Warning: No data file found at", data_file)
        print("   Please run the following command first:")
        print("   python scripts/simple_cli.py parse history --summarize -o data/web_sessions.json")
        print()
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Exiting...")
            return
    
    print("📁 Data file:", data_file)
    print("🌐 Starting server at: http://localhost:8000")
    print("📱 API docs at: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run the FastAPI app
        from talkshow.web.app import app
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()