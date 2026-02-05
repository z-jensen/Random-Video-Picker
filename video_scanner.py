import json
import logging
import random
from pathlib import Path
from typing import List, Set, Optional

# Set up logging
logger = logging.getLogger(__name__)


class VideoScanner:
    """Handles video scanning and random selection logic."""
    
    def __init__(self):
        self.video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
        self.video_files: List[Path] = []
        self.played_videos: Set[Path] = set()
        self.recent_videos: List[Path] = []
        self.max_recent = 10
        self.current_folder: Optional[Path] = None
        
        # Portable mode: Check for .portable file in app directory
        self._app_dir = Path(__file__).parent.resolve()
        self._portable_file = self._app_dir / '.portable'
        
        if self._portable_file.exists():
            # Use app directory for config (portable mode)
            self.config_dir = self._app_dir / '.random_video_picker'
            self.config_dir.mkdir(exist_ok=True)
            self.config_file = self.config_dir / 'state.json'
        else:
            # Use home directory for config (standard mode)
            self.config_file = Path.home() / '.random_video_picker.json'
        
    def scan_folder(self, folder: Path, persistent: bool = False) -> int:
        """
        Scan folder recursively for video files.
        
        Args:
            folder: Path to folder to scan
            persistent: Whether to load previous session data
            
        Returns:
            Number of videos found
            
        Raises:
            ValueError: If folder doesn't exist
        """
        if not folder or not folder.exists():
            raise ValueError("Invalid folder path")
            
        self.current_folder = folder
        self.video_files.clear()
        
        if not persistent:
            self.played_videos.clear()
            self.recent_videos.clear()
        
        for file_path in folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.video_extensions:
                self.video_files.append(file_path)
                
        return len(self.video_files)
    
    def get_random_video(self, include_skipped: bool = True) -> Optional[Path]:
        """
        Get a random unplayed video.
        
        Args:
            include_skipped: Whether to include videos already marked as skipped
            
        Returns:
            Random video path or None if no videos available
        """
        if not self.video_files:
            return None
            
        unplayed_videos = [
            video for video in self.video_files 
            if video not in self.played_videos
        ]
        
        if not unplayed_videos:
            # All videos have been played, reset session
            self.reset_session()
            unplayed_videos = self.video_files.copy()
            
        return random.choice(unplayed_videos)
    
    def mark_played(self, video: Path) -> None:
        """Mark a video as played and add to recent list."""
        self.played_videos.add(video)
        
        # Update recent videos list
        if video in self.recent_videos:
            self.recent_videos.remove(video)
        self.recent_videos.insert(0, video)
        
        # Keep only the most recent videos
        if len(self.recent_videos) > self.max_recent:
            self.recent_videos = self.recent_videos[:self.max_recent]
    
    def skip_video(self, video: Path) -> None:
        """Mark a video as played without actually playing it or adding to recent."""
        self.played_videos.add(video)
        # Don't add to recent_videos - that's for actually watched videos only
    
    def reset_session(self) -> None:
        """Reset the played videos tracking for a fresh session."""
        self.played_videos.clear()
        self.recent_videos.clear()
    
    def get_progress(self) -> tuple[int, int]:
        """
        Get current session progress.
        
        Returns:
            Tuple of (played_count, total_count)
        """
        played_count = len(self.played_videos)
        total_count = len(self.video_files)
        return played_count, total_count
    
    def get_recent_videos(self, limit: Optional[int] = None) -> List[Path]:
        """Get list of recently played videos."""
        if limit:
            return self.recent_videos[:limit]
        return self.recent_videos.copy()
    
    def _validate_path(self, path_str: str, base_folder: Optional[Path] = None) -> Optional[Path]:
        """
        Validate a path to prevent path traversal attacks.
        
        Args:
            path_str: String representation of the path
            base_folder: Optional base folder that the path must be within
            
        Returns:
            Path object if valid, None if invalid
        """
        try:
            path = Path(path_str)
            resolved_path = path.resolve()
            
            # Check for path traversal attempts
            if '..' in path_str:
                logger.warning(f"Path traversal attempt detected: {path_str}")
                return None
            
            # If base folder is specified, ensure path is within it
            if base_folder:
                resolved_base = base_folder.resolve()
                try:
                    resolved_path.relative_to(resolved_base)
                except ValueError:
                    logger.warning(f"Path outside base folder: {path_str}")
                    return None
            
            return path
        except (ValueError, OSError) as e:
            logger.warning(f"Invalid path: {path_str} - {e}")
            return None
    
    def save_state(self) -> None:
        """Save current session state to config file."""
        if not self.current_folder:
            return
            
        state = {
            'current_folder': str(self.current_folder),
            'played_videos': [str(video) for video in self.played_videos],
            'recent_videos': [str(video) for video in self.recent_videos],
            'video_files': [str(video) for video in self.video_files]
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(state, f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Failed to save state: {e}")
    
    def load_state(self) -> bool:
        """
        Load previous session state from config file.
        
        Returns:
            True if state was loaded successfully, False otherwise
        """
        if not self.config_file.exists():
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                state = json.load(f)
            
            # Validate and convert string paths back to Path objects
            current_folder = self._validate_path(state.get('current_folder', ''))
            if not current_folder:
                logger.error("Invalid current_folder in state file")
                return False
            
            self.current_folder = current_folder
            
            # Validate all paths are within the current folder
            self.played_videos = set()
            for video_str in state.get('played_videos', []):
                video_path = self._validate_path(video_str, current_folder)
                if video_path:
                    self.played_videos.add(video_path)
                else:
                    logger.warning(f"Skipping invalid played video path: {video_str}")
            
            self.recent_videos = []
            for video_str in state.get('recent_videos', []):
                video_path = self._validate_path(video_str, current_folder)
                if video_path:
                    self.recent_videos.append(video_path)
                else:
                    logger.warning(f"Skipping invalid recent video path: {video_str}")
            
            self.video_files = []
            for video_str in state.get('video_files', []):
                video_path = self._validate_path(video_str, current_folder)
                if video_path:
                    self.video_files.append(video_path)
                else:
                    logger.warning(f"Skipping invalid video file path: {video_str}")
            
            return True
        except (json.JSONDecodeError, KeyError, IOError, OSError) as e:
            logger.error(f"Failed to load state: {e}")
            return False
    
    def clear_saved_state(self) -> None:
        """Remove saved state file."""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Failed to clear saved state: {e}")
