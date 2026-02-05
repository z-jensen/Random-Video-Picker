import logging
import os
import subprocess
import sys
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Constants
SUBPROCESS_TIMEOUT_SECONDS = 30  # Timeout for launching video player


class VideoPlayer:
    """Handles cross-platform video playback."""
    
    @staticmethod
    def play_video(video_path: Path) -> bool:
        """
        Play video using system default player.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OSError: If unable to play video
        """
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(video_path))
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(
                    ['open', str(video_path)], 
                    check=True, 
                    timeout=SUBPROCESS_TIMEOUT_SECONDS
                )
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(
                    ['xdg-open', str(video_path)], 
                    check=True, 
                    timeout=SUBPROCESS_TIMEOUT_SECONDS
                )
            else:
                raise OSError(f"Unsupported operating system: {sys.platform}")
            return True
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout launching video player for: {video_path}")
            raise OSError(f"Timeout launching video player (took longer than {SUBPROCESS_TIMEOUT_SECONDS}s)")
        except subprocess.CalledProcessError as e:
            logger.error(f"Video player process failed: {e}")
            raise OSError(f"Failed to play video: {e}")
        except (OSError, PermissionError) as e:
            logger.error(f"OS error playing video: {e}")
            raise OSError(f"Failed to play video: {e}")
        except Exception as e:
            logger.error(f"Unexpected error playing video: {e}")
            raise OSError(f"Failed to play video: {str(e)}")
