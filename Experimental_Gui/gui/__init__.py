"""GUI components for NN-Downloader"""

# Import conditionally to avoid webview dependency
try:
    from .main_window import MainWindow
    __all__ = ["MainWindow"]
except ImportError:
    __all__ = []