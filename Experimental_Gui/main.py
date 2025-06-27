"""NN-Downloader v2.0 - Simple Main Entry Point"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point - just launch the GUI"""
    try:
        # Try to import and run the GUI
        from gui.tkinter_app import run_tkinter_app
        print("🚀 Starting NN-Downloader v2.0...")
        run_tkinter_app()
    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
        print("\n💡 If you see import errors, try installing dependencies:")
        print("   pip install aiohttp aiofiles")
        print("\n📦 Or run with basic Python dependencies only:")
        print("   python -c \"import tkinter; print('GUI should work')\"")
        return 1
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return 1

if __name__ == "__main__":
    main()