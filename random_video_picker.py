import logging
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk, scrolledtext, font
from typing import Optional
from video_scanner import VideoScanner
from video_player import VideoPlayer
from video_preview import VideoPreview

# Set up logging
logger = logging.getLogger(__name__)

# Constants
PICK_DEBOUNCE_MS = 500  # Minimum time between picks



class RandomVideoPicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Random Video Picker")
        self.root.minsize(400, 250)  # Smaller minimum size for basic mode
        
        # Setup custom styling
        self.setup_styles()
        
        # Core components
        self.scanner = VideoScanner()
        self.player = VideoPlayer()
        self.folder_path = None
        self.advanced_visible = False  # Track if advanced features are visible
        self.persistence_enabled = tk.BooleanVar(value=False)
        self.preview_visible = tk.BooleanVar(value=False)
        self.recent_visible = tk.BooleanVar(value=True)
        self.include_subfolders = tk.BooleanVar(value=True)
        self.last_include_subfolders = True  # Cache for subfolder setting
        self._last_recent_count = 0  # Cache for recent videos count
        
        # Status tracking
        self.app_status = "ready"  # ready, scanning, error
        
        # Touchpad/gesture tracking for smooth scrolling
        self.last_scroll_time = 0
        self.scroll_momentum = 0
        
        # Debounce tracking for spacebar to prevent double-triggering
        self._last_pick_time = 0
        
        # Preview tracking - initialize all attributes here
        self.current_preview_video: Optional[Path] = None
        self._preview_lock = threading.Lock()
        self._current_preview_request_id = 0
        
        self.setup_ui()
        
        # Setup keyboard shortcuts
        self.root.bind('<space>', lambda event: self.pick_random_video_and_consume(event))
        
        # Setup global scroll bindings - will be set up after UI creation
        self.root.after(100, self.setup_global_scroll_bindings)
        
        # Initialize status indicator
        self.update_status('ready')
        
        # Try to load saved state if persistence was enabled
        self._try_load_saved_state()
    
    def setup_styles(self):
        """Setup custom ttk styles for modern appearance."""
        style = ttk.Style()
        
        # Configure the root theme
        style.theme_use('clam')
        
        # Color palette
        bg_color = '#f8f9fa'  # Light background
        primary_color = '#4a90e2'  # Blue primary
        success_color = '#28a745'  # Green success
        warning_color = '#ffc107'  # Yellow warning
        error_color = '#dc3545'  # Red error
        text_color = '#2c3e50'  # Dark text
        border_color = '#dee2e6'  # Light border
        
        # Configure overall style
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=text_color, font=('TkDefaultFont', 10, 'bold'))
        
        # Enhanced button styles
        style.configure('TButton', 
                       background='white',
                       foreground=text_color,
                       borderwidth=1,
                       focuscolor='none',
                       font=('TkDefaultFont', 10),
                       relief='flat')
        style.map('TButton',
                 background=[('active', '#e9ecef'), ('pressed', '#dee2e6')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Accent button style for primary actions
        style.configure('Accent.TButton',
                       background=primary_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                        font=('TkDefaultFont', 11, 'bold'),
                       relief='flat')
        style.map('Accent.TButton',
                 background=[('active', '#357abd'), ('pressed', '#2e6aa5')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Success button style
        style.configure('Success.TButton',
                       background=success_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('TkDefaultFont', 10),
                       relief='flat')
        style.map('Success.TButton',
                 background=[('active', '#218838'), ('pressed', '#1e7e34')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Warning button style
        style.configure('Warning.TButton',
                       background=warning_color,
                       foreground=text_color,
                       borderwidth=0,
                       focuscolor='none',
                       font=('TkDefaultFont', 10),
                       relief='flat')
        style.map('Warning.TButton',
                 background=[('active', '#e0a800'), ('pressed', '#d39e00')],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Enhanced label styles
        style.configure('TLabel', 
                       background=bg_color,
                       foreground=text_color,
                        font=('TkDefaultFont', 10))
        
        style.configure('Header.TLabel',
                       background=bg_color,
                       foreground=text_color,
                       font=('TkDefaultFont', 12, 'bold'))
        
        style.configure('Title.TLabel',
                       background=bg_color,
                       foreground=text_color,
                       font=('TkDefaultFont', 14, 'bold'))
        
        # Enhanced progress bar
        style.configure('TProgressbar',
                       background=primary_color,
                       troughcolor=bg_color,
                       bordercolor=border_color,
                       lightcolor=primary_color,
                       darkcolor=primary_color,
                       borderwidth=1,
                       relief='flat')
        
        # Enhanced checkbox
        style.configure('TCheckbutton',
                       background=bg_color,
                       foreground=text_color,
                       font=('TkDefaultFont', 10),
                       focuscolor='none')
        style.map('TCheckbutton',
                 background=[('active', bg_color)],
                 foreground=[('active', primary_color)])
        
        # Enhanced scrollbar styling
        style.configure('TScrollbar',
                       background=bg_color,
                       troughcolor='#e9ecef',  # Light trough
                       bordercolor=border_color,
                       darkcolor=primary_color,
                       lightcolor=primary_color,
                       arrowcolor=text_color,
                       width=12,  # Thicker, more modern
                       relief='flat')
        style.map('TScrollbar',
                 background=[('active', bg_color), ('pressed', primary_color)],
                 troughcolor=[('active', '#dee2e6'), ('pressed', '#e9ecef')],
                 arrowcolor=[('active', primary_color), ('pressed', 'white')])
        
        # Configure listbox colors (for recent videos)
        self.root.option_add('*Listbox.selectBackground', primary_color)
        self.root.option_add('*Listbox.selectForeground', 'white')
        self.root.option_add('*Listbox.background', 'white')
        self.root.option_add('*Listbox.foreground', text_color)
        self.root.option_add('*Listbox.font', 'TkDefaultFont 10')
        
        # Set root background
        self.root.configure(bg=bg_color)
        
        # Add cursor changes for interactive elements
        self.root.option_add('*Button.cursor', 'hand2')
        self.root.option_add('*Checkbutton.cursor', 'hand2')
        self.root.option_add('*Listbox.cursor', 'hand2')
        self.root.option_add('*Scrollbar.cursor', 'hand2')
        
    def setup_ui(self):
        """Create and arrange GUI widgets."""
        # Main container with enhanced padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="wens")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Make advanced section scrollable area expand
        
        # Header with status indicator
        self.create_header_section(main_frame)
        
        # Basic section (always visible)
        self.create_basic_section(main_frame)
        
        # Section divider
        self.create_section_divider(main_frame)
        
        # Create scrollable container for advanced section
        self.create_scrollable_advanced_section(main_frame)
        
        # Initially hide advanced section
        self.toggle_advanced_section(show=False)
    
    def create_header_section(self, parent):
        """Create compact header with title and status indicator."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Status indicator dot
        self.status_indicator = tk.Label(
            header_frame,
            text="●",
            font=('TkDefaultFont', 12),  # Smaller for compact layout
            fg='#28a745',  # Green for ready
            bg='#f8f9fa'
        )
        self.status_indicator.grid(row=0, column=0, padx=(0, 8))
        
        # App title (more compact)
        title_label = ttk.Label(
            header_frame,
            text="🎲 Random Video",
            style='Header.TLabel'  # Use Header instead of Title for smaller
        )
        title_label.grid(row=0, column=1, sticky=tk.W)
        
        # Status text (on the right)
        self.status_text = ttk.Label(
            header_frame,
            text="Ready",
            style='TLabel'
        )
        self.status_text.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
    
    def create_section_divider(self, parent):
        """Create a visual divider between sections."""
        divider_frame = ttk.Frame(parent)
        divider_frame.grid(row=3, column=0, sticky="ew", pady=(10, 10))
        
        # Create a separator line
        separator = ttk.Separator(divider_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=2)
        
    def update_status(self, status, message=None):
        """Update the status indicator and message."""
        self.app_status = status
        
        # Update indicator color
        colors = {
            'ready': '#28a745',      # Green
            'scanning': '#ffc107',   # Yellow
            'error': '#dc3545',      # Red
            'success': '#17a2b8'     # Cyan
        }
        
        messages = {
            'ready': 'Ready',
            'scanning': 'Scanning...',
            'error': 'Error',
            'success': 'Success'
        }
        
        color = colors.get(status, '#6c757d')  # Default gray
        display_message = message or messages.get(status, 'Unknown')
        
        self.status_indicator.config(fg=color)
        self.status_text.config(text=display_message)
        
    def create_basic_section(self, parent):
        """Create basic interface components optimized for small windows."""
        # Folder selection with enhanced styling (responsive layout)
        folder_frame = ttk.Frame(parent)
        folder_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)
        
        self.folder_button = ttk.Button(
            folder_frame, 
            text="📂 Choose", 
            command=self.choose_folder,
            width=10,
            takefocus=0
        )
        self.folder_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.folder_label = ttk.Label(
            folder_frame, 
            text="No folder selected", 
            style='TLabel',
            wraplength=300  # Reduced for small windows
        )
        self.folder_label.grid(row=0, column=1, sticky="ew")
        
        # Primary action section (responsive layout)
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        # Pick Random Video button (primary action) - enhanced
        self.pick_button = ttk.Button(
            action_frame, 
            text="🎲 Pick Video", 
            command=self.pick_random_video,
            state="disabled",
            style='Accent.TButton',
            width=15,
            takefocus=0
        )
        self.pick_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # More Features toggle with enhanced styling
        self.more_features_button = ttk.Button(
            action_frame,
            text="▶ More",
            command=self.toggle_advanced_ui,
            takefocus=0
        )
        self.more_features_button.grid(row=0, column=1, sticky="e")
        
    def create_scrollable_advanced_section(self, parent):
        """Create collapsible advanced section with scrollable content."""
        # Scrollable container
        self.scroll_container = ttk.Frame(parent)
        self.scroll_container.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        self.scroll_container.grid_rowconfigure(0, weight=1)
        self.scroll_container.grid_columnconfigure(0, weight=1)
        
        # Create canvas with enhanced scrollbar
        self.advanced_canvas = tk.Canvas(self.scroll_container, highlightthickness=0, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.advanced_canvas.yview, style='TScrollbar')
        self.advanced_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.advanced_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 2))  # Small gap between content and scrollbar
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Advanced frame inside canvas
        self.advanced_frame = ttk.Frame(self.advanced_canvas)
        self.advanced_frame.bind(
            "<Configure>",
            lambda e: self.advanced_canvas.configure(scrollregion=self.advanced_canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.advanced_canvas.create_window((0, 0), window=self.advanced_frame, anchor="nw")
        
        # Progress section
        self.create_progress_section(self.advanced_frame)
        
        # Advanced buttons
        self.create_advanced_buttons(self.advanced_frame)
        
        # Container for preview and recent sections using grid layout
        self.preview_recent_container = ttk.Frame(self.advanced_frame)
        self.preview_recent_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Recent videos section - will be at row 1 (create first)
        self.create_recent_section(self.preview_recent_container)
        
        # Preview section (collapsible) - will be at row 0 (create second)
        self.create_preview_section(self.preview_recent_container)
        
        # Enhanced touchpad/mousewheel support for canvas - bind to scroll container for better coverage
        self.scroll_container.bind('<MouseWheel>', self._on_global_mousewheel)
        self.scroll_container.bind('<Button-4>', lambda e: self._on_global_mousewheel(e, delta=1))
        self.scroll_container.bind('<Button-5>', lambda e: self._on_global_mousewheel(e, delta=-1))
        self.scroll_container.bind('<Shift-MouseWheel>', lambda e: self._on_global_mousewheel(e, delta=-e.delta//120 if e.delta else 0))  # Horizontal scrolling
        self.scroll_container.bind('<Control-MouseWheel>', lambda e: self._on_smooth_scroll(e, self.advanced_canvas, fine=True))  # Fine scroll with Ctrl
        
        # Also bind to canvas for direct interaction
        self.advanced_canvas.bind('<MouseWheel>', self._on_global_mousewheel)
        self.advanced_canvas.bind('<Button-4>', lambda e: self._on_global_mousewheel(e, delta=1))
        self.advanced_canvas.bind('<Button-5>', lambda e: self._on_global_mousewheel(e, delta=-1))
        
        # Bind to preview_recent_container to capture scroll events when preview is visible
        self.preview_recent_container.bind('<MouseWheel>', self._on_global_mousewheel)
        self.preview_recent_container.bind('<Button-4>', lambda e: self._on_global_mousewheel(e, delta=1))
        self.preview_recent_container.bind('<Button-5>', lambda e: self._on_global_mousewheel(e, delta=-1))
        self.preview_recent_container.bind('<Shift-MouseWheel>', lambda e: self._on_global_mousewheel(e, delta=-e.delta//120 if e.delta else 0))
    
    def _on_global_mousewheel(self, event, delta=None):
        """Handle enhanced mousewheel/touchpad scrolling for canvas with momentum."""
        if delta is None:
            # Windows/Mac: event.delta contains scroll amount
            delta = -1 * (event.delta // 120) if event.delta else 0
        else:
            # Linux: Button-4 (scroll up) and Button-5 (scroll down)
            delta = delta
        
        current_time = time.time()
        time_diff = current_time - self.last_scroll_time
        
        # Detect rapid scrolling (touchpad gesture) vs slow scrolling (mouse wheel)
        if time_diff < 0.1:  # Rapid scrolling indicates touchpad
            scroll_amount = delta * 2  # Faster for touchpad gestures
        else:
            scroll_amount = delta * 3  # Normal speed for mouse wheel
        
        self.last_scroll_time = current_time
        self.advanced_canvas.yview_scroll(scroll_amount, "units")
        return "break"
    
    def _on_mousewheel(self, event, delta=None):
        """Handle enhanced mousewheel/touchpad scrolling for canvas with momentum."""
        if delta is None:
            # Windows/Mac: event.delta contains scroll amount
            delta = -1 * (event.delta // 120) if event.delta else 0
        else:
            # Linux: Button-4 (scroll up) and Button-5 (scroll down)
            delta = delta
        
        current_time = time.time()
        time_diff = current_time - self.last_scroll_time
        
        # Detect rapid scrolling (touchpad gesture) vs slow scrolling (mouse wheel)
        if time_diff < 0.1:  # Rapid scrolling indicates touchpad
            scroll_amount = delta * 2  # Faster for touchpad gestures
        else:
            scroll_amount = delta * 3  # Normal speed for mouse wheel
        
        self.last_scroll_time = current_time
        self.advanced_canvas.yview_scroll(scroll_amount, "units")
        return "break"
    
    def _on_smooth_scroll(self, event, widget, fine=False):
        """Handle smooth scrolling for touchpad gestures."""
        if fine:
            # Fine control with Ctrl key for precise scrolling
            delta = -1 * (event.delta // 480) if event.delta else 0  # Much smaller increments
        else:
            # Regular smooth scrolling
            delta = -1 * (event.delta // 240) if event.delta else 0  # Half normal speed
        
        if hasattr(widget, 'yview_scroll'):
            widget.yview_scroll(delta, "units")
        return "break"
    
    def _on_listbox_mousewheel(self, event, listbox, delta=None):
        """Handle mousewheel scrolling for listbox."""
        if delta is None:
            # Windows/Mac: event.delta contains scroll amount
            delta = -1 * (event.delta // 120) if event.delta else 0
        else:
            # Linux: Button-4 (scroll up) and Button-5 (scroll down)
            delta = delta
        
        # Scroll the listbox
        current = listbox.yview()
        if delta > 0 and current[0] > 0:
            # Scroll up
            listbox.yview_moveto(max(0, current[0] - 0.1))
        elif delta < 0 and current[1] < 1:
            # Scroll down
            listbox.yview_moveto(min(1, current[0] + 0.1))
        return "break"
    
    def _on_listbox_smooth_scroll(self, event, listbox, fine=False):
        """Handle smooth scrolling for listbox with touchpad gestures."""
        if fine:
            # Fine control with Ctrl key for precise scrolling
            delta = -1 * (event.delta // 480) if event.delta else 0  # Much smaller increments
        else:
            # Regular smooth scrolling
            delta = -1 * (event.delta // 240) if event.delta else 0  # Half normal speed
        
        current = listbox.yview()
        if delta > 0 and current[0] > 0:
            # Smooth scroll up
            listbox.yview_moveto(max(0, current[0] - 0.05))  # Smaller increments for smoothness
        elif delta < 0 and current[1] < 1:
            # Smooth scroll down
            listbox.yview_moveto(min(1, current[0] + 0.05))  # Smaller increments for smoothness
        return "break"
    
    def setup_global_scroll_bindings(self):
        """Set up global scroll bindings on the root window for better touchpad support."""
        # Bind scroll events to root window - they'll be routed to appropriate widgets
        self.root.bind('<MouseWheel>', self._route_scroll_event)
        self.root.bind('<Button-4>', lambda e: self._route_scroll_event(e, delta=1))
        self.root.bind('<Button-5>', lambda e: self._route_scroll_event(e, delta=-1))
        self.root.bind('<Shift-MouseWheel>', lambda e: self._route_scroll_event(e, delta=-e.delta//120 if e.delta else 0))
    
    def _route_scroll_event(self, event, delta=None):
        """Route scroll events to the appropriate widget based on mouse position and visibility."""
        if delta is None:
            # Windows/Mac: event.delta contains scroll amount
            delta = -1 * (event.delta // 120) if event.delta else 0
        else:
            # Linux: Button-4 (scroll up) and Button-5 (scroll down)
            delta = delta
        
        # Determine which widget should receive the scroll event
        # Priority: listbox under mouse -> canvas if visible -> no action
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        
        # Check if mouse is over recent listbox
        if widget_under_mouse:
            # Walk up the widget hierarchy to find listbox or its parent
            current = widget_under_mouse
            while current:
                if current == self.recent_listbox or (hasattr(current, 'winfo_children') and self.recent_listbox in current.winfo_children()):
                    # Mouse is over or inside recent listbox frame - scroll listbox
                    return self._on_listbox_mousewheel(event, self.recent_listbox, delta=delta)
                current = current.master if hasattr(current, 'master') else None
        
        # Check if advanced section is visible and scroll canvas
        if self.advanced_visible:
            # Check if mouse is anywhere in the scroll container area
            scroll_container_x = self.scroll_container.winfo_rootx()
            scroll_container_y = self.scroll_container.winfo_rooty()
            scroll_container_width = self.scroll_container.winfo_width()
            scroll_container_height = self.scroll_container.winfo_height()
            
            if (scroll_container_x <= x <= scroll_container_x + scroll_container_width and
                scroll_container_y <= y <= scroll_container_y + scroll_container_height):
                # Mouse is over scroll container area - scroll canvas
                return self._on_global_mousewheel(event, delta=delta)
        
        return "break"
        
    def create_progress_section(self, parent):
        """Create compact progress indicator widgets."""
        # Section header (more compact)
        progress_header = ttk.Label(
            parent,
            text="📊 Progress",
            style='Header.TLabel'
        )
        progress_header.pack(anchor=tk.W, pady=(0, 8))
        
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress container (more compact)
        progress_info_frame = ttk.Frame(progress_frame)
        progress_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Progress label with enhanced styling
        self.progress_label = ttk.Label(
            progress_info_frame, 
            text="0/0 videos",
            style='TLabel',
            font=('TkDefaultFont', 10, 'bold')
        )
        self.progress_label.pack(side=tk.LEFT)
        
        # Percentage label
        self.progress_percentage_label = ttk.Label(
            progress_info_frame,
            text="0%",
            style='TLabel',
            font=('TkDefaultFont', 9)
        )
        self.progress_percentage_label.pack(side=tk.RIGHT)
        
        # Enhanced progress bar (more compact)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='determinate',
            style='TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 2))
        
    def create_advanced_buttons(self, parent):
        """Create compact advanced action buttons."""
        # Section header (more compact)
        buttons_header = ttk.Label(
            parent,
            text="⚙️ Options",
            style='Header.TLabel'
        )
        buttons_header.pack(anchor=tk.W, pady=(0, 8))
        
        # Settings frame (more compact)
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Subfolder checkbox with enhanced styling (shorter text)
        self.subfolder_checkbox = ttk.Checkbutton(
            settings_frame,
            text="📁 Include subfolders",
            variable=self.include_subfolders,
            command=self.rescan_if_folder_selected
        )
        self.subfolder_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        self.persistence_checkbox = ttk.Checkbutton(
            settings_frame,
            text="💾 Save progress between sessions",
            variable=self.persistence_enabled,
            command=self.toggle_persistence
        )
        self.persistence_checkbox.pack(anchor=tk.W)
        
        # Actions section header (more compact)
        actions_header = ttk.Label(
            parent,
            text="🎬 Actions",
            style='Header.TLabel'
        )
        actions_header.pack(anchor=tk.W, pady=(8, 8))
        
        # Enhanced buttons frame (centered)
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=(0, 10), expand=True)
        
        # Reset Session button with styling
        self.reset_button = ttk.Button(
            buttons_frame, 
            text="🔄 Reset Session", 
            command=self.reset_session,
            state="disabled",
            takefocus=0
        )
        self.reset_button.pack(side=tk.LEFT, padx=(0, 3))
        
        # Preview toggle button with styling
        self.preview_toggle_button = ttk.Button(
            buttons_frame, 
            text="👁 Preview", 
            command=self.toggle_preview_section,
            takefocus=0
        )
        self.preview_toggle_button.pack(side=tk.LEFT, padx=3)
        
        # Recent toggle button with styling
        self.recent_toggle_button = ttk.Button(
            buttons_frame, 
            text="📝 Hide Recent", 
            command=self.toggle_recent_section,
            takefocus=0
        )
        self.recent_toggle_button.pack(side=tk.LEFT, padx=(3, 0))
        
    def create_recent_section(self, parent):
        """Create recent videos display section."""
        # Recent section container
        self.recent_frame = ttk.Frame(parent)
        self.recent_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        
        # Configure grid weights so recent section expands
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Recent videos label with enhanced styling
        recent_label = ttk.Label(
            self.recent_frame, 
            text="📝 Recent Videos:",
            style='Header.TLabel'
        )
        recent_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Recent videos list with scrollbar for small windows
        listbox_frame = ttk.Frame(self.recent_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create listbox with scrollbar
        self.recent_listbox = tk.Listbox(
            listbox_frame, 
            height=5,  # Reduced height for small windows
            width=40,  # Reduced width for small windows
            font=('TkDefaultFont', 9),  # Smaller font
            selectbackground='#4a90e2',  # Use primary color
            selectforeground='white',
            activestyle='none',
            relief='flat',
            borderwidth=1,
            highlightthickness=0,
            yscrollcommand=""
        )
        
        # Add enhanced scrollbar
        recent_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.recent_listbox.yview, style='TScrollbar')
        self.recent_listbox.config(yscrollcommand=recent_scrollbar.set)
        
        # Pack listbox and scrollbar with small gap
        self.recent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to play video and add hover effect
        self.recent_listbox.bind('<Double-Button-1>', self.on_recent_double_click)
        self.recent_listbox.bind('<Enter>', lambda e: self.recent_listbox.config(relief='solid'))
        self.recent_listbox.bind('<Leave>', lambda e: self.recent_listbox.config(relief='flat'))
        
        # Enhanced mousewheel support to recent listbox with touchpad gestures - bind to parent frame for better coverage
        listbox_frame.bind('<MouseWheel>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox))
        listbox_frame.bind('<Button-4>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox, delta=1))
        listbox_frame.bind('<Button-5>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox, delta=-1))
        listbox_frame.bind('<Shift-MouseWheel>', lambda e: self._on_listbox_smooth_scroll(e, self.recent_listbox, fine=False))
        listbox_frame.bind('<Control-MouseWheel>', lambda e: self._on_listbox_smooth_scroll(e, self.recent_listbox, fine=True))
        
        # Also bind directly to listbox
        self.recent_listbox.bind('<MouseWheel>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox))
        self.recent_listbox.bind('<Button-4>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox, delta=1))
        self.recent_listbox.bind('<Button-5>', lambda e: self._on_listbox_mousewheel(e, self.recent_listbox, delta=-1))
        self.recent_listbox.bind('<Shift-MouseWheel>', lambda e: self._on_listbox_smooth_scroll(e, self.recent_listbox, fine=False))
        self.recent_listbox.bind('<Control-MouseWheel>', lambda e: self._on_listbox_smooth_scroll(e, self.recent_listbox, fine=True))
        
    def create_preview_section(self, parent):
        """Create the embedded preview section."""
        # Preview section container (more compact)
        self.preview_frame = ttk.Frame(parent)
        self.preview_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))
        
        # Preview title with enhanced styling (more compact)
        self.preview_title_label = ttk.Label(
            self.preview_frame,
            text="👁 Preview",
            style='Header.TLabel',
            wraplength=300  # Reduced for small windows
        )
        self.preview_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Compact preview content
        preview_content = ttk.Frame(self.preview_frame)
        preview_content.pack(fill=tk.X)
        
        # Smaller thumbnail frame
        self.thumbnail_frame = ttk.Frame(preview_content)
        self.thumbnail_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.thumbnail_label: tk.Label = tk.Label(
            self.thumbnail_frame,
            text="📹",
            font=('TkDefaultFont', 32),  # Smaller font
            fg='gray'
        )
        self.thumbnail_label.pack()
        
        # Compact video info (2 columns)
        self.info_frame = ttk.Frame(preview_content)
        self.info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Compact single-column layout for info (better for small windows)
        info_row1 = ttk.Frame(self.info_frame)
        info_row1.pack(fill=tk.X)
        
        self.size_label = ttk.Label(info_row1, text="Size: -", font=('TkDefaultFont', 9))
        self.size_label.pack(side=tk.LEFT)
        
        self.duration_label = ttk.Label(info_row1, text="Duration: -", font=('TkDefaultFont', 9))
        self.duration_label.pack(side=tk.LEFT, padx=(15, 0))
        
        info_row2 = ttk.Frame(self.info_frame)
        info_row2.pack(fill=tk.X, pady=(2, 0))
        
        self.resolution_label = ttk.Label(info_row2, text="Res: -", font=('TkDefaultFont', 9))  # Shortened
        self.resolution_label.pack(side=tk.LEFT)
        
        self.modified_label = ttk.Label(info_row2, text="Mod: -", font=('TkDefaultFont', 9))  # Shortened
        self.modified_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Compact action buttons
        self.preview_action_frame = ttk.Frame(self.preview_frame)
        self.preview_action_frame.pack(pady=(5, 0))
        
        self.play_from_preview_button = ttk.Button(
            self.preview_action_frame,
            text="▶ Play",
            command=self.play_from_preview,
            state="disabled",
            style='Success.TButton',
            width=8,
            takefocus=0
        )
        self.play_from_preview_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.skip_from_preview_button = ttk.Button(
            self.preview_action_frame,
            text="⏭ Skip",
            command=self.skip_from_preview,
            state="disabled",
            style='Warning.TButton',
            width=8,
            takefocus=0
        )
        self.skip_from_preview_button.pack(side=tk.LEFT)
        
        # Initially hide the preview section
        self.preview_frame.grid_forget()
        
    def toggle_advanced_ui(self):
        """Toggle the visibility of advanced features."""
        self.advanced_visible = not self.advanced_visible
        
        if self.advanced_visible:
            self.toggle_advanced_section(show=True)
            self.more_features_button.config(text="▼ Less")
        else:
            self.toggle_advanced_section(show=False)
            self.more_features_button.config(text="▶ More")
    
    def toggle_advanced_section(self, show: bool):
        """Show or hide the advanced section."""
        if show:
            # Show the scroll container
            self.scroll_container.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
            # Update scroll region
            self.advanced_frame.update_idletasks()
            self.advanced_canvas.configure(scrollregion=self.advanced_canvas.bbox("all"))
            # Smaller minimum size for better small window experience
            self.root.minsize(450, 450)
        else:
            # Hide the scroll container
            self.scroll_container.grid_remove()
            # Smaller window for basic mode
            self.root.minsize(350, 180)
            
        # Update window size
        self.root.update_idletasks()
        
    def choose_folder(self):
        """Open folder dialog and scan for videos."""
        folder = filedialog.askdirectory()
        if folder:
            folder_path = Path(folder)
            
            # Validate the selected folder
            try:
                if not folder_path.exists():
                    messagebox.showerror("Error", "Selected folder does not exist.")
                    return
                
                if not folder_path.is_dir():
                    messagebox.showerror("Error", "Selected path is not a directory.")
                    return
                
                # Check if folder is readable
                try:
                    # Try to list the directory to verify read permissions
                    next(folder_path.iterdir(), None)
                except (PermissionError, OSError):
                    messagebox.showerror("Error", "Cannot read the selected folder. Please check permissions.")
                    return
                
                self.folder_path = folder_path
                self.folder_label.config(text=f"Selected: {self.folder_path}")
                self.scan_for_videos()
            except Exception as e:
                logger.error(f"Error validating folder: {e}")
                messagebox.showerror("Error", f"Failed to access folder: {str(e)}")
            
    def scan_for_videos(self):
        """Scan selected folder for video files (optimized with background thread)."""
        if not self.folder_path:
            return
        
        # Show loading indicator and update status
        self.update_status('scanning')
        self.folder_label.config(text=f"Scanning: {self.folder_path}...")
        self.root.update_idletasks()
        
        def scan_in_background():
            try:
                video_count = self.scanner.scan_folder(
                    self.folder_path,  # type: ignore
                    persistent=self.persistence_enabled.get()
                )
                
                # Update UI from main thread
                self.root.after(0, lambda: self._update_scan_result(video_count))
                
            except ValueError as e:
                logger.error(f"Invalid folder error: {e}")
                self.root.after(0, lambda msg=str(e): self._show_scan_error(msg))
            except PermissionError as e:
                logger.error(f"Permission denied scanning folder: {e}")
                self.root.after(0, lambda: self._show_scan_error("Permission denied accessing folder"))
            except OSError as e:
                logger.error(f"OS error scanning folder: {e}")
                self.root.after(0, lambda msg=str(e): self._show_scan_error(f"System error: {msg}"))
            except Exception as e:
                logger.exception("Unexpected error scanning folder")
                self.root.after(0, lambda: self._show_scan_error(f"Unexpected error: {str(e)}"))
        
        threading.Thread(target=scan_in_background, daemon=True).start()
    
    def _update_scan_result(self, video_count: int):
        """Update UI after scan completes (called from main thread)."""
        self.last_include_subfolders = self.include_subfolders.get()
        
        if video_count > 0:
            self.update_status('ready', f'Found {video_count} videos')
            self.folder_label.config(text=f"Selected: {self.folder_path}")
            self.pick_button.config(state="normal")
            self.reset_button.config(state="normal")
            self.preview_toggle_button.config(state="normal")
            messagebox.showinfo("Success", f"Found {video_count} videos!")
            self.update_progress()
            self.update_recent_display()
        else:
            self.update_status('error', 'No videos found')
            self.folder_label.config(text=f"Selected: {self.folder_path}")
            self.pick_button.config(state="disabled")
            self.reset_button.config(state="disabled")
            self.preview_toggle_button.config(state="disabled")
            messagebox.showwarning("No Videos", "No video files found in this folder.")
            self.update_progress()
            self.update_recent_display()
    
    def _show_scan_error(self, error_msg: str):
        """Show scan error (called from main thread)."""
        self.update_status('error', 'Scan failed')
        self.folder_label.config(text=f"Selected: {self.folder_path}")
        messagebox.showerror("Error", f"Failed to scan folder: {error_msg}")
    
    def rescan_if_folder_selected(self):
        """Rescan videos if a folder is selected and subfolder setting changed (optimized with caching)."""
        if self.folder_path and self.include_subfolders.get() != self.last_include_subfolders:
            self.scan_for_videos()
    
    def pick_random_video_and_consume(self, event):
        """Play random video and consume event to prevent button activation."""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Debounce: prevent triggering if called too recently
        if current_time - self._last_pick_time < PICK_DEBOUNCE_MS:
            return 'break'
        
        self._last_pick_time = current_time
        
        # Move focus to root window to prevent any button from being activated by spacebar
        self.root.focus_set()
        
        self.pick_random_video()
        return 'break'  # Prevent event propagation to buttons
            
    def pick_random_video(self):
        """Pick and play a random video."""
        random_video = self.scanner.get_random_video()
        
        if not random_video:
            messagebox.showwarning("No Videos", "Please select a folder with videos first.")
            return
        
        try:
            self.player.play_video(random_video)
            self.scanner.mark_played(random_video)
            if self.persistence_enabled.get():
                self.scanner.save_state()
            self.update_progress()
            self.update_recent_display()
            
        except OSError as e:
            logger.error(f"OS error playing video: {e}")
            messagebox.showerror("Error", f"Failed to play video: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error playing video")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            
    def skip_random_video(self):
        """Skip a random video without playing it."""
        random_video = self.scanner.get_random_video()
        
        if not random_video:
            messagebox.showwarning("No Videos", "Please select a folder with videos first.")
            return
        
        self.scanner.skip_video(random_video)
        if self.persistence_enabled.get():
            self.scanner.save_state()
        self.update_progress()
        self.update_recent_display()
        
        # Show which video was skipped
        messagebox.showinfo("Video Skipped", f"Skipped: {random_video.name}")
        
    def preview_random_video(self):
        """Show preview for a random video in the integrated preview section."""
        random_video = self.scanner.get_random_video()
        
        if not random_video:
            messagebox.showwarning("No Videos", "Please select a folder with videos first.")
            return
        
        # Update preview section if it's visible, otherwise show it
        if not self.preview_visible.get():
            self.toggle_preview_section()
        
        # Update the preview display with the new video
        self.update_preview_display(random_video)
        
    def reset_session(self):
        """Reset the session progress."""
        self.scanner.reset_session()
        if self.persistence_enabled.get():
            self.scanner.save_state()
        self.update_progress()
        self.update_recent_display()
        messagebox.showinfo("Session Reset", "Session has been reset. All videos are now available.")
        
    def update_progress(self):
        """Update the enhanced progress display."""
        played, total = self.scanner.get_progress()
        
        if total > 0:
            percentage = (played / total) * 100
            self.progress_label.config(text=f"{played}/{total} videos played")
            self.progress_percentage_label.config(text=f"{percentage:.1f}%")
            self.progress_bar['value'] = percentage
        else:
            self.progress_label.config(text="0/0 videos played")
            self.progress_percentage_label.config(text="0%")
            self.progress_bar['value'] = 0
            
    def update_recent_display(self):
        """Update recent videos display (optimized with caching)."""
        recent_videos = self.scanner.get_recent_videos()
        
        # Check if update is needed (avoid unnecessary redraws)
        if len(recent_videos) == self._last_recent_count:
            # Check if actual content changed by comparing paths
            current_items = []
            for i in range(self.recent_listbox.size()):
                current_items.append(self.recent_listbox.get(i))
            
            # Build expected items
            expected_items = [f"{i}. {video.name}" for i, video in enumerate(recent_videos, 1)] if recent_videos else ["No videos played yet."]
            
            # If no change, skip update
            if current_items == expected_items:
                return
        
        self._last_recent_count = len(recent_videos)
        
        # Clear existing items
        self.recent_listbox.delete(0, tk.END)
        
        if recent_videos:
            for i, video in enumerate(recent_videos, 1):
                # Add video to listbox (only one entry per video)
                self.recent_listbox.insert(tk.END, f"{i}. {video.name}")
        else:
            self.recent_listbox.insert(tk.END, "No videos played yet.")
    
    def on_recent_double_click(self, event):
        """Handle double-click on recent video to play it."""
        selection = self.recent_listbox.curselection()
        if selection:
            # Get the index of the selected item
            index = selection[0]
            # Calculate the video path index (skip the visible items)
            videos = self.scanner.get_recent_videos()
            if index < len(videos):
                video_path = videos[index]
                self.play_recent_video(video_path)
    
    def play_recent_video(self, video_path):
        """Play a recently watched video without updating progress."""
        try:
            logger.debug(f"Playing recent video: {video_path}")
            self.player.play_video(video_path)
        except OSError as e:
            logger.error(f"OS error playing recent video: {e}")
            messagebox.showerror("Error", f"Failed to play video: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error playing recent video")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def toggle_persistence(self):
        """Handle persistence checkbox toggle."""
        if self.persistence_enabled.get():
            # Enable persistence - save current state
            self.scanner.save_state()
            messagebox.showinfo("Persistence Enabled", "Session progress will be saved and restored across app restarts.")
        else:
            # Disable persistence - clear saved state
            self.scanner.clear_saved_state()
            messagebox.showinfo("Persistence Disabled", "Session will reset when the app is closed.")
    
    def _try_load_saved_state(self):
        """Try to load saved state when persistence was previously enabled."""
        if self.scanner.load_state():
            # Successfully loaded saved state
            self.folder_path = self.scanner.current_folder
            self.folder_label.config(text=f"Selected: {self.folder_path}")
            self.persistence_enabled.set(True)
            
            # Enable buttons since we have loaded state
            if self.scanner.video_files:
                self.pick_button.config(state="normal")
                self.reset_button.config(state="normal")
                self.preview_toggle_button.config(state="normal")
                self.update_progress()
                self.update_recent_display()
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()
    
    def toggle_preview_section(self):
        """Toggle the visibility of the preview section."""
        self.preview_visible.set(not self.preview_visible.get())
        
        if self.preview_visible.get():
            self.preview_frame.grid(row=0, column=0, sticky="ew", pady=(15, 0))
            self.preview_toggle_button.config(text="👁 Hide Preview")
            # Generate a preview if we haven't loaded one yet
            if not hasattr(self, 'current_preview_video') or self.current_preview_video is None:
                self.preview_random_video()
        else:
            self.preview_frame.grid_forget()
            self.preview_toggle_button.config(text="👁 Show Preview")
    
    def toggle_recent_section(self):
        """Toggle the visibility of the recent videos section."""
        self.recent_visible.set(not self.recent_visible.get())
        
        if self.recent_visible.get():
            self.recent_frame.grid(row=1, column=0, sticky="nsew")
            self.recent_toggle_button.config(text="📝 Hide Recent")
        else:
            self.recent_frame.grid_forget()
            self.recent_toggle_button.config(text="📝 Show Recent")
    
    def update_preview_display(self, video_path):
        """Update the preview section with video information (optimized)."""
        # Increment request ID to invalidate old requests
        with self._preview_lock:
            self._current_preview_request_id += 1
            request_id = self._current_preview_request_id
            self.current_preview_video = video_path
        
        # Show immediate feedback
        self.preview_title_label.config(text=video_path.name)
        self.size_label.config(text="Size: Loading...")
        self.duration_label.config(text="Duration: Loading...")
        self.resolution_label.config(text="Resolution: Loading...")
        self.modified_label.config(text="Modified: Loading...")
        
        # Show placeholder immediately
        self.thumbnail_label.config(image="", text="📹", font=('TkDefaultFont', 32), fg='gray')
        
        # Enable action buttons immediately
        self.play_from_preview_button.config(state="normal")
        self.skip_from_preview_button.config(state="normal")
        
        # Load detailed info in background
        def load_details():
            try:
                # Create a new VideoPreview instance for this thread
                preview = VideoPreview()
                info = preview.get_video_info(video_path)
                
                # Update UI in main thread with request ID check
                self.root.after(0, lambda: self._update_preview_details(info, request_id))
                
                # Load thumbnail in background
                thumbnail = preview.create_preview_image(video_path, size=(160, 120))
                if thumbnail:
                    self.root.after(0, lambda: self._update_preview_thumbnail(thumbnail, request_id))
                    
            except Exception as e:
                logger.exception("Error loading preview details")
                # Show error state with request ID check
                self.root.after(0, lambda: self._update_preview_error(str(e), request_id))
        
        # Start background thread
        threading.Thread(target=load_details, daemon=True).start()
    
    def _update_preview_details(self, info, request_id=None):
        """Update preview info labels (called from main thread)."""
        # Check if this request is still valid
        if request_id is not None and request_id != self._current_preview_request_id:
            return
        
        self.size_label.config(text=f"Size: {info.get('size', 'Unknown')}")
        self.duration_label.config(text=f"Duration: {info.get('duration', 'Unknown')}")
        self.resolution_label.config(text=f"Resolution: {info.get('resolution', 'Unknown')}")
        self.modified_label.config(text=f"Modified: {info.get('modified', 'Unknown')}")
    
    def _update_preview_thumbnail(self, thumbnail, request_id=None):
        """Update preview thumbnail (called from main thread)."""
        # Check if this request is still valid
        if request_id is not None and request_id != self._current_preview_request_id:
            return
        
        self.thumbnail_label.configure(image=thumbnail)
        self.thumbnail_label.image = thumbnail  # type: ignore - Keep reference
    
    def _update_preview_error(self, error_msg, request_id=None):
        """Update preview to show error state (called from main thread)."""
        # Check if this request is still valid
        if request_id is not None and request_id != self._current_preview_request_id:
            return
        
        self.thumbnail_label.config(image="", text="❌", font=('TkDefaultFont', 32), fg='red')
    
    def play_from_preview(self):
        """Play the currently previewed video."""
        if self.current_preview_video:
            try:
                self.player.play_video(self.current_preview_video)
                self.scanner.mark_played(self.current_preview_video)
                if self.persistence_enabled.get():
                    self.scanner.save_state()
                self.update_progress()
                self.update_recent_display()
                # Update preview with next random video
                self.preview_random_video()
            except OSError as e:
                logger.error(f"OS error playing video from preview: {e}")
                messagebox.showerror("Error", f"Failed to play video: {str(e)}")
            except Exception as e:
                logger.exception("Unexpected error playing video from preview")
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def skip_from_preview(self):
        """Skip the currently previewed video."""
        if self.current_preview_video:
            self.scanner.skip_video(self.current_preview_video)
            if self.persistence_enabled.get():
                self.scanner.save_state()
            self.update_progress()
            self.update_recent_display()
            # Update preview with next random video
            self.preview_random_video()


def main():
    app = RandomVideoPicker()
    app.run()

if __name__ == "__main__":
    main()