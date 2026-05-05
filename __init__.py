"""
YTDL-PRO — Downloader profissional de vídeos e playlists do YouTube
"""

__version__ = "1.0.0"
__author__ = "ytdl-pro"
__description__ = "Downloader profissional de vídeos e playlists do YouTube com interface TUI incrível"

from .main import cli
from .config import ConfigManager, HistoricoManager
from .downloader import YTDLPro

__all__ = ["cli", "ConfigManager", "HistoricoManager", "YTDLPro"]
