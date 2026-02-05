import glob
import logging
import os
import subprocess
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict
import tkinter as tk

# Set up logging
logger = logging.getLogger(__name__)

# Constants
MAX_CACHE_SIZE = 50
CACHE_EVICTION_COUNT = 25
THUMBNAIL_MAX_AGE_SECONDS = 86400  # 24 hours
FFMPEG_TIMEOUT_SECONDS = 1
FFPROBE_TIMEOUT_SECONDS = 2
THUMBNAIL_TIMEOUT_SECONDS = 3
DEFAULT_THUMBNAIL_SIZE = (160, 120)
PREVIEW_THUMBNAIL_SIZE = (320, 240)


class VideoPreview:
    """Handles video thumbnail generation and information extraction."""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.pil_available = self._check_pil()
        self.ffmpeg_cache = {}  # Cache for video info to avoid repeated calls
        self.cache_lock = threading.Lock()  # Thread safety for cache
        self._cleanup_old_thumbnails()  # Clean up old thumbnails on init
        
    def _check_pil(self) -> bool:
        """Check if PIL is available for image handling."""
        try:
            from PIL import Image, ImageTk
            return True
        except ImportError:
            return False
    
    def _cleanup_old_thumbnails(self):
        """Clean up old thumbnail files from temp directory."""
        try:
            current_time = time.time()
            
            # Find all thumbnail files created by this app
            pattern = str(Path(self.temp_dir) / "thumb_*.jpg")
            for thumb_path in glob.glob(pattern):
                try:
                    thumb_file = Path(thumb_path)
                    # Delete files older than 24 hours
                    if thumb_file.exists() and (current_time - thumb_file.stat().st_mtime) > THUMBNAIL_MAX_AGE_SECONDS:
                        thumb_file.unlink()
                        logger.debug(f"Cleaned up old thumbnail: {thumb_path}")
                except (OSError, PermissionError) as e:
                    logger.warning(f"Failed to clean up thumbnail {thumb_path}: {e}")
        except Exception as e:
            logger.warning(f"Thumbnail cleanup failed: {e}")
        
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available for thumbnail generation (cached for speed)."""
        cache_key = "ffmpeg_available"
        with self.cache_lock:
            if cache_key in self.ffmpeg_cache:
                return self.ffmpeg_cache[cache_key]
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=FFMPEG_TIMEOUT_SECONDS)
            with self.cache_lock:
                self.ffmpeg_cache[cache_key] = True
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"ffmpeg not available: {e}")
            with self.cache_lock:
                self.ffmpeg_cache[cache_key] = False
            return False
    
    def generate_thumbnail(self, video_path: Path, size: Tuple[int, int] = DEFAULT_THUMBNAIL_SIZE) -> Optional[Path]:
        """
        Generate thumbnail from video using ffmpeg (optimized for speed).
        
        Args:
            video_path: Path to video file
            size: Thumbnail size (width, height) - smaller by default for speed
            
        Returns:
            Path to generated thumbnail or None if failed
        """
        if not self.check_ffmpeg():
            return None
            
        # Check cache first
        thumb_cache_key = f"thumb_{video_path.stem}_{size[0]}x{size[1]}.jpg"
        thumb_path = Path(self.temp_dir) / thumb_cache_key
        
        # Return cached thumbnail if it exists
        if thumb_path.exists():
            return thumb_path
            
        try:
            # Use fixed 20-second seek for speed - avoids intros without needing duration
            seek_time = '00:00:20'
            
            # Optimized ffmpeg command for speed
            cmd = [
                'ffmpeg', '-ss', seek_time, '-i', str(video_path),  # Seek before input (faster)
                '-vframes', '1',
                '-q:v', '2',  # Low quality for speed
                '-vf', f'scale={size[0]}:{size[1]}',
                '-y',  # Overwrite existing
                str(thumb_path)
            ]
            
            # Much shorter timeout for responsiveness
            result = subprocess.run(cmd, capture_output=True, check=True, timeout=THUMBNAIL_TIMEOUT_SECONDS)
            
            if thumb_path.exists() and thumb_path.stat().st_size > 0:
                return thumb_path
            else:
                logger.warning(f"Thumbnail file not created or empty for {video_path}")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Thumbnail generation timed out for {video_path}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Thumbnail generation failed for {video_path}: {e}")
        except OSError as e:
            logger.error(f"OS error during thumbnail generation for {video_path}: {e}")
        finally:
            # Clean up partial files on any error
            try:
                if thumb_path.exists() and thumb_path.stat().st_size == 0:
                    thumb_path.unlink()
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to clean up partial thumbnail: {e}")
            
        return None
    
    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds using ffprobe (cached for speed)."""
        # Check cache first
        cache_key = f"duration_{video_path}"
        with self.cache_lock:
            if cache_key in self.ffmpeg_cache:
                return self.ffmpeg_cache[cache_key]
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=FFPROBE_TIMEOUT_SECONDS)
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                # Cache the result
                with self.cache_lock:
                    self.ffmpeg_cache[cache_key] = duration
                return duration
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, ValueError) as e:
            logger.debug(f"Failed to get duration for {video_path}: {e}")
            
        # Cache the failure
        with self.cache_lock:
            self.ffmpeg_cache[cache_key] = 0.0
        return 0.0
    
    def get_video_info(self, video_path: Path) -> Dict[str, str]:
        """
        Extract basic video information with caching.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        # Check cache first
        video_key = str(video_path)
        with self.cache_lock:
            if video_key in self.ffmpeg_cache:
                return self.ffmpeg_cache[video_key]
        
        info = {}
        
        # Basic file info (fast)
        try:
            stat = video_path.stat()
            info['size'] = self._format_file_size(stat.st_size)
            info['modified'] = self._format_timestamp(stat.st_mtime)
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to get file stats for {video_path}: {e}")
        
        # Fast ffmpeg info extraction with shorter timeout
        if self.check_ffmpeg():
            try:
                # Use a single ffprobe call to get all info at once
                cmd = [
                    'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                    '-show_entries', 'stream=width,height:format=duration',
                    '-of', 'csv=p=0',
                    str(video_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=FFPROBE_TIMEOUT_SECONDS)
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split(',')
                    if len(parts) >= 3 and parts[0] and parts[1]:
                        info['resolution'] = f"{parts[0]}x{parts[1]}"
                        try:
                            duration = float(parts[2])
                            info['duration'] = self._format_duration(duration)
                        except (ValueError, IndexError):
                            info['duration'] = "Unknown"
                        
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
                logger.debug(f"Failed to get video info for {video_path}: {e}")
        
        # Fallback info
        info['name'] = video_path.name
        info['path'] = str(video_path)
        
        # Cache the result
        with self.cache_lock:
            self.ffmpeg_cache[video_key] = info
            # Limit cache size to prevent memory issues - do this inside the lock
            if len(self.ffmpeg_cache) > MAX_CACHE_SIZE:
                # Remove oldest entries (keep only last CACHE_EVICTION_COUNT entries)
                keys_to_remove = list(self.ffmpeg_cache.keys())[:-CACHE_EVICTION_COUNT]
                for key in keys_to_remove:
                    del self.ffmpeg_cache[key]
        
        return info
    
    def create_preview_image(self, video_path: Path, size: Tuple[int, int] = PREVIEW_THUMBNAIL_SIZE):
        """
        Create a PhotoImage for display in Tkinter.
        
        Args:
            video_path: Path to video file
            size: Image size
            
        Returns:
            PhotoImage object or None
        """
        if not self.pil_available:
            return None
            
        try:
            from PIL import Image, ImageTk
        except ImportError:
            return None
            
        thumb_path = self.generate_thumbnail(video_path, size)
        
        if thumb_path and thumb_path.exists():
            try:
                image = Image.open(thumb_path)
                photo = ImageTk.PhotoImage(image)
                return photo
            except (OSError, IOError) as e:
                logger.warning(f"Failed to open thumbnail image: {e}")
        
        # Return a placeholder image
        return self._create_placeholder(size)
    
    def _create_placeholder(self, size: Tuple[int, int]):
        """Create a placeholder image when thumbnail fails."""
        if not self.pil_available:
            return None
            
        try:
            from PIL import Image, ImageTk, ImageDraw, ImageFont
            
            # Create a simple gray placeholder
            image = Image.new('RGB', size, color='gray')
            
            # Add text
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except (OSError, IOError):
                font = ImageFont.load_default()
            
            text = "No Preview"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            return ImageTk.PhotoImage(image)
            
        except Exception as e:
            logger.warning(f"Failed to create placeholder image: {e}")
            # Fallback: create a simple solid color image
            try:
                from PIL import Image, ImageTk
                image = Image.new('RGB', size, color='darkgray')
                return ImageTk.PhotoImage(image)
            except Exception as e2:
                logger.error(f"Failed to create fallback placeholder: {e2}")
                return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp as readable date."""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    
    def _format_duration(self, duration_seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        if duration_seconds <= 0:
            return "Unknown"
        
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class PreviewDialog:
    """Dialog for showing video preview with details."""
    
    def __init__(self, parent, video_path: Path):
        self.parent = parent
        self.video_path = video_path
        self.preview = VideoPreview()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Video Preview")
        self.dialog.minsize(400, 300)
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create preview dialog UI."""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack()
        
        # Video info
        info = self.preview.get_video_info(self.video_path)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text=info['name'],
            font=('Arial', 12, 'bold'),
            wraplength=350
        )
        title_label.pack(pady=(0, 10))
        
        # Thumbnail
        thumbnail = self.preview.create_preview_image(self.video_path)
        if thumbnail:
            thumbnail_label = tk.Label(main_frame, image=thumbnail)
            # Keep reference to prevent garbage collection
            thumbnail_label.image = thumbnail  # type: ignore
            thumbnail_label.pack(pady=10)
        else:
            # Show placeholder text when no image available
            placeholder_label = tk.Label(
                main_frame, 
                text="📹 No Preview Available\n(Install Pillow for thumbnails)",
                height=8,
                width=30,
                bg='lightgray',
                fg='black'
            )
            placeholder_label.pack(pady=10)
        
        # Video details
        details_frame = tk.Frame(main_frame)
        details_frame.pack(pady=10, fill='x')
        
        details = [
            ("File Size:", info.get('size', 'Unknown')),
            ("Duration:", info.get('duration', 'Unknown')),
            ("Resolution:", info.get('resolution', 'Unknown')),
            ("Modified:", info.get('modified', 'Unknown')),
        ]
        
        for label, value in details:
            row_frame = tk.Frame(details_frame)
            row_frame.pack(fill='x', pady=2)
            
            tk.Label(row_frame, text=label, width=12, anchor='w').pack(side='left')
            tk.Label(row_frame, text=value, anchor='w').pack(side='left')
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))
        
        play_button = tk.Button(
            button_frame, 
            text="Play Video", 
            command=self.play_video,
            width=15
        )
        play_button.pack(side='left', padx=(0, 10))
        
        skip_button = tk.Button(
            button_frame, 
            text="Skip", 
            command=self.skip_video,
            width=15
        )
        skip_button.pack(side='left')
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def play_video(self):
        """Play the video and close dialog."""
        from video_player import VideoPlayer
        try:
            player = VideoPlayer()
            player.play_video(self.video_path)
            self.dialog.destroy()
        except (OSError, subprocess.CalledProcessError) as e:
            import tkinter.messagebox as messagebox
            logger.error(f"Failed to play video: {e}")
            messagebox.showerror("Error", f"Failed to play video: {str(e)}")
    
    def skip_video(self):
        """Skip the video and close dialog."""
        self.dialog.destroy()
    
    def show(self) -> bool:
        """Show the dialog and return whether to play the video."""
        self.dialog.wait_window()
        return False  # Will be handled by the button callbacks
