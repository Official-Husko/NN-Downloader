"""Tkinter-based GUI for NN-Downloader"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import queue


@dataclass
class DownloadTask:
    """Represents a download task in the queue"""
    task_id: str
    site: str
    task_type: str  # 'url' or 'tags'
    url: Optional[str] = None
    tags: Optional[str] = None
    max_pages: Optional[int] = None
    status: str = 'pending'  # pending, downloading, completed, failed
    
    def __str__(self):
        if self.task_type == 'url':
            return f"{self.site}: {self.url}"
        else:
            return f"{self.site}: {self.tags} ({self.max_pages or 'unlimited'} pages)"
    
    def get_unique_key(self) -> str:
        """Get a unique key for duplicate detection"""
        if self.task_type == 'url':
            # Normalize URL for comparison (remove trailing slash, convert to lowercase)
            normalized_url = self.url.lower().rstrip('/')
            return f"{self.site}|url|{normalized_url}"
        else:
            # For tags, include site, tags, and max_pages
            tags_normalized = self.tags.lower().strip() if self.tags else ""
            return f"{self.site}|tags|{tags_normalized}|{self.max_pages or 'unlimited'}"
    
    def __eq__(self, other):
        """Check equality based on unique key"""
        if not isinstance(other, DownloadTask):
            return False
        return self.get_unique_key() == other.get_unique_key()
    
    def __hash__(self):
        """Hash based on unique key"""
        return hash(self.get_unique_key())

# Check for basic async dependencies first
HAS_ASYNC_DEPS = False
try:
    import aiohttp
    import aiofiles
    # If basic deps are available, try to import our async components
    from downloaders import (
        download_multporn_comic, download_luscious_album, download_yiffer_comic,
        download_rule34_tags, download_e621_tags, download_furbooru_tags
    )
    from utils.config_manager_async import AsyncConfigManager
    from utils.directory_manager_async import AsyncDirectoryManager
    HAS_ASYNC_DEPS = True
    print("✅ Async dependencies loaded successfully")
except ImportError as e:
    print(f"⚠️  Async dependencies not available: {e}")
    print("   GUI will work in demo mode.")


class TkinterApp:
    """Tkinter-based application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NN-Downloader v2.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1e1e1e')
        self.root.minsize(900, 600)
        
        # Modern color scheme
        self.colors = {
            'bg_primary': '#1e1e1e',      # Dark background
            'bg_secondary': '#2d2d2d',    # Lighter dark for panels
            'bg_tertiary': '#3c3c3c',     # Even lighter for inputs
            'accent': '#0078d4',          # Modern blue accent
            'accent_hover': '#106ebe',    # Darker blue for hover
            'success': '#107c10',         # Green for success
            'warning': '#ff8c00',         # Orange for warnings
            'error': '#d13438',           # Red for errors
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#cccccc',  # Light gray text
            'text_muted': '#999999',      # Muted gray text
            'border': '#484848'           # Border color
        }
        
        # Initialize components
        self.config_manager = None
        self.config = {
            "proxies": False,
            "blacklisted_tags": [],
            "oneTimeDownload": True,
            "user_credentials": {}
        }
        self.directory_manager = None
        
        # Active sessions
        self.sessions: Dict[str, Any] = {}
        
        # Download queue system
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.current_download_info = None
        
        # Event loop for async operations
        self.loop = None
        self.loop_thread = None
        
        # GUI variables
        self.site_var = tk.StringVar(value="e621")
        self.tags_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.max_pages_var = tk.StringVar()
        self.api_site_var = tk.StringVar(value="e621")
        self.api_user_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        
        # Track which input method to show
        self.input_frame = None
        self.queue_frame = None
        
        self.current_session = None
        self.progress_var = tk.DoubleVar()
        self.status_text = tk.StringVar(value="Ready")
        
        # Setup GUI
        self.setup_gui()
        
        # Initialize async components
        self._start_async_loop()
    
    def _start_async_loop(self):
        """Start async event loop in separate thread"""
        if not HAS_ASYNC_DEPS:
            self.add_log("⚠️  Running in demo mode - install dependencies for full functionality")
            self.add_log("   pip install aiohttp aiofiles")
            return
            
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Initialize async components
            async def init_components():
                try:
                    self.config_manager = AsyncConfigManager()
                    self.config = await self.config_manager.load_config()
                    self.directory_manager = AsyncDirectoryManager()
                    
                    # Update status on main thread
                    self.root.after(0, lambda: self.status_text.set("Ready - All components loaded"))
                    self.root.after(0, lambda: self.add_log("✅ Async components loaded"))
                except Exception as e:
                    self.root.after(0, lambda: self.add_log(f"⚠️  Config error: {e}"))
            
            self.loop.run_until_complete(init_components())
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
    
    def setup_gui(self):
        """Setup the tkinter GUI"""
        # Configure modern dark theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme styles
        style.configure('TFrame', background=self.colors['bg_primary'])
        style.configure('TLabel', background=self.colors['bg_primary'], foreground=self.colors['text_primary'])
        style.configure('TLabelframe', background=self.colors['bg_primary'], borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=self.colors['bg_primary'], foreground=self.colors['text_primary'], font=('Segoe UI', 10, 'bold'))
        
        # Modern button styling
        style.configure('Accent.TButton', 
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover']),
                            ('pressed', self.colors['accent_hover'])])
        
        # Entry styling
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.colors['text_primary'])
        
        # Combobox styling
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid',
                       arrowcolor=self.colors['text_primary'])
        
        # Progress bar styling
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with gradient effect simulation
        title_label = tk.Label(header_frame, text="NN-Downloader v2.0", 
                              font=('Segoe UI', 24, 'bold'), 
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['accent'])
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Status indicator with improved styling
        status_text = "🟢 Full Mode - Ready to Download" if HAS_ASYNC_DEPS else "🟡 Demo Mode - Install Dependencies"
        status_color = self.colors['success'] if HAS_ASYNC_DEPS else self.colors['warning']
        status_label = tk.Label(header_frame, text=status_text,
                               font=('Segoe UI', 11, 'bold'), 
                               bg=self.colors['bg_primary'], 
                               fg=status_color)
        status_label.grid(row=1, column=0, pady=(0, 10))
        
        # Improved description
        explanation = tk.Label(header_frame, 
                              text="Professional media downloader for art communities\n" +
                                   "🏷️ Tag-based: e621, e6ai, e926, rule34, furbooru  |  🔗 URL-based: luscious, multporn, yiffer",
                              font=('Segoe UI', 10), 
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_secondary'], 
                              justify='center')
        explanation.grid(row=2, column=0, pady=(0, 5))
        
        # Separator line
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Download section with modern styling
        download_frame = ttk.LabelFrame(main_frame, text="📥 Download Content", padding="15")
        download_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        download_frame.columnconfigure(1, weight=1)
        
        # Site selection with improved styling
        site_label = ttk.Label(download_frame, text="🌐 Select Site:", font=('Segoe UI', 10, 'bold'))
        site_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
        site_combo = ttk.Combobox(download_frame, textvariable=self.site_var, 
                                 values=["e621", "e6ai", "e926", "rule34", "furbooru", "luscious", "multporn", "yiffer"],
                                 state="readonly", style="Modern.TCombobox", font=('Segoe UI', 10))
        site_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(5, 5))
        site_combo.bind('<<ComboboxSelected>>', self.on_site_change)
        
        # Dynamic input frame that changes based on site
        self.input_frame = ttk.Frame(download_frame)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 15))
        self.input_frame.columnconfigure(1, weight=1)
        
        # Download buttons with modern styling
        button_frame = ttk.Frame(download_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        download_btn = ttk.Button(button_frame, text="🚀 Start Download", 
                                 command=self.start_download, style="Accent.TButton")
        download_btn.grid(row=0, column=0, padx=(0, 5), ipadx=15, ipady=5, sticky=(tk.W, tk.E))
        
        queue_btn = ttk.Button(button_frame, text="➕ Add to Queue", 
                              command=self.add_to_queue, style="Accent.TButton")
        queue_btn.grid(row=0, column=1, padx=(5, 0), ipadx=15, ipady=5, sticky=(tk.W, tk.E))
        
        # Setup initial input fields
        self.setup_input_fields()
        
        # Progress section with modern styling
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress", padding="15")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar with modern styling
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, style="Modern.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 10), ipady=3)
        
        # Status label with better typography
        status_label = ttk.Label(progress_frame, textvariable=self.status_text, 
                                font=('Segoe UI', 10))
        status_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Credentials section with modern styling
        cred_frame = ttk.LabelFrame(main_frame, text="🔑 API Credentials", padding="15")
        cred_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        cred_frame.columnconfigure(1, weight=1)
        
        # API Site selection
        ttk.Label(cred_frame, text="Site:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
        api_site_combo = ttk.Combobox(cred_frame, textvariable=self.api_site_var,
                                     values=["e621", "e6ai", "e926", "furbooru"],
                                     state="readonly", style="Modern.TCombobox", font=('Segoe UI', 10))
        api_site_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(5, 5))
        
        # API help text with better styling
        api_help = tk.Label(cred_frame, text="💡 Only required for e621/e6ai/e926/furbooru sites", 
                           font=('Segoe UI', 9), fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
        api_help.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # API Username
        ttk.Label(cred_frame, text="Username:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
        api_user_entry = ttk.Entry(cred_frame, textvariable=self.api_user_var, style="Modern.TEntry", font=('Segoe UI', 10))
        api_user_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 5), ipady=3)
        
        # API Key
        ttk.Label(cred_frame, text="API Key:", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
        api_key_entry = ttk.Entry(cred_frame, textvariable=self.api_key_var, show="*", style="Modern.TEntry", font=('Segoe UI', 10))
        api_key_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(5, 5), ipady=3)
        
        # Save credentials button
        save_cred_btn = ttk.Button(cred_frame, text="💾 Save Credentials", 
                                  command=self.save_credentials, style="Accent.TButton")
        save_cred_btn.grid(row=4, column=0, columnspan=2, pady=(15, 5), ipadx=15, ipady=3)
        
        # Queue section with modern styling
        self.queue_frame = ttk.LabelFrame(main_frame, text="📋 Download Queue", padding="15")
        self.queue_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.queue_frame.columnconfigure(0, weight=1)
        
        # Queue listbox with scrollbar
        queue_container = ttk.Frame(self.queue_frame)
        queue_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        queue_container.columnconfigure(0, weight=1)
        
        self.queue_listbox = tk.Listbox(queue_container, height=4,
                                       bg=self.colors['bg_tertiary'],
                                       fg=self.colors['text_primary'],
                                       selectbackground=self.colors['accent'],
                                       selectforeground='white',
                                       font=('Segoe UI', 9),
                                       relief='flat',
                                       borderwidth=1)
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        queue_scrollbar = ttk.Scrollbar(queue_container, orient="vertical", command=self.queue_listbox.yview)
        queue_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_listbox.config(yscrollcommand=queue_scrollbar.set)
        
        # Queue control buttons
        queue_btn_frame = ttk.Frame(self.queue_frame)
        queue_btn_frame.grid(row=1, column=0, pady=(0, 5))
        
        clear_queue_btn = ttk.Button(queue_btn_frame, text="🗑️ Clear Queue", 
                                    command=self.clear_queue)
        clear_queue_btn.grid(row=0, column=0, padx=(0, 10))
        
        remove_selected_btn = ttk.Button(queue_btn_frame, text="✖️ Remove Selected", 
                                        command=self.remove_selected_from_queue)
        remove_selected_btn.grid(row=0, column=1)
        
        # Log section with modern styling
        log_frame = ttk.LabelFrame(main_frame, text="📝 Activity Log", padding="15")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Log text area with dark theme
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                                 bg=self.colors['bg_tertiary'], 
                                                 fg=self.colors['text_primary'],
                                                 insertbackground=self.colors['text_primary'],
                                                 selectbackground=self.colors['accent'],
                                                 selectforeground='white',
                                                 font=('Consolas', 9),
                                                 relief='flat',
                                                 borderwidth=1)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add initial log message
        self.add_log("NN-Downloader v2.0 initialized")
        if HAS_ASYNC_DEPS:
            self.add_log("✅ Async dependencies available - Full functionality enabled")
            self.add_log("Initializing async components...")
        else:
            self.add_log("⚠️  Running in demo mode - Downloads disabled")
            self.add_log("Install dependencies for full functionality:")
            self.add_log("   pip install aiohttp aiofiles")
            self.add_log("If you have dependencies installed, check console for import errors")
        
        # Initialize queue display
        self.update_queue_display()
    
    def on_site_change(self, event=None):
        """Handle site selection change"""
        self.setup_input_fields()
    
    def setup_input_fields(self):
        """Setup input fields based on selected site"""
        # Clear existing widgets
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        site = self.site_var.get()
        
        if site in ["luscious", "multporn", "yiffer"]:
            # URL-based sites
            ttk.Label(self.input_frame, text="🔗 URL:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
            url_entry = ttk.Entry(self.input_frame, textvariable=self.url_var, style="Modern.TEntry", font=('Segoe UI', 10))
            url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(5, 5), ipady=3)
            
            # URL help text
            if site == "luscious":
                example = "https://www.luscious.net/albums/album-name_123456"
            elif site == "multporn":
                example = "https://multporn.net/comics/comic-name"
            else:  # yiffer
                example = "https://yiffer.xyz/Comic Name"
            
            help_text = tk.Label(self.input_frame, text=f"💡 Example: {example}", 
                               font=('Segoe UI', 9), fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
            help_text.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
            
        else:
            # Tag-based sites
            ttk.Label(self.input_frame, text="🏷️ Search Tags:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
            tags_entry = ttk.Entry(self.input_frame, textvariable=self.tags_var, style="Modern.TEntry", font=('Segoe UI', 10))
            tags_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(5, 5), ipady=3)
            
            # Tags help text
            help_text = tk.Label(self.input_frame, text="💡 Examples: 'fox rating:safe', 'cat dog', 'anthro -human'", 
                               font=('Segoe UI', 9), fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
            help_text.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
            
            # Max pages for tag-based sites
            ttk.Label(self.input_frame, text="📊 Max Pages:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 5))
            pages_entry = ttk.Entry(self.input_frame, textvariable=self.max_pages_var, style="Modern.TEntry", font=('Segoe UI', 10), width=10)
            pages_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 5), ipady=3)
            
            # Pages help text
            if site in ["e621", "e6ai", "e926"]:
                pages_help_text = "⚠️ Leave empty for max (API limit: 750 pages)"
            else:
                pages_help_text = "⚠️ Leave empty for unlimited (be careful!)"
            
            pages_help = tk.Label(self.input_frame, text=pages_help_text, 
                                font=('Segoe UI', 9), fg=self.colors['warning'], bg=self.colors['bg_primary'])
            pages_help.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
    
    def add_log(self, message: str):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def add_to_queue(self):
        """Add current input to download queue"""
        task = self._create_download_task()
        if task:
            # Check for duplicates
            if self._is_duplicate_task(task):
                messagebox.showwarning("Duplicate Download", 
                    f"This download is already in the queue or currently downloading:\n\n{task}")
                self.add_log(f"⚠️ Duplicate detected, not adding: {task}")
                return
            
            self.download_queue.put(task)
            self.add_log(f"➕ Added to queue: {task}")
            self.update_queue_display()
            
            # Start processing queue if not already downloading
            if not self.is_downloading:
                self._process_next_in_queue()
    
    def start_download(self):
        """Start immediate download (skip queue)"""
        if not HAS_ASYNC_DEPS:
            self.add_log("❌ Cannot download - async dependencies not installed")
            messagebox.showwarning("Demo Mode", 
                "This is demo mode. To enable downloads, install dependencies:\n\n"
                "pip install aiohttp aiofiles\n\n"
                "Then restart the application.")
            return
        
        if self.is_downloading:
            # If already downloading, add to queue instead
            self.add_to_queue()
            return
        
        task = self._create_download_task()
        if task:
            # Check for duplicates even for immediate downloads
            if self._is_duplicate_task(task):
                messagebox.showwarning("Duplicate Download", 
                    f"This download is already in the queue or currently downloading:\n\n{task}")
                self.add_log(f"⚠️ Duplicate detected, not starting: {task}")
                return
            
            self._start_download_task(task)
    
    def _create_download_task(self) -> Optional[DownloadTask]:
        """Create a download task from current UI inputs"""
        if not HAS_ASYNC_DEPS:
            return None
        
        site = self.site_var.get()
        
        if not site:
            messagebox.showerror("Error", "Please select a site")
            return None
        
        if site in ["luscious", "multporn", "yiffer"]:
            # URL-based download
            url = self.url_var.get()
            if not url.strip():
                messagebox.showerror("Error", "Please enter a URL")
                return None
            
            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://")):
                messagebox.showerror("Error", "Please enter a valid URL (must start with http:// or https://)")
                return None
            
            # Check if URL matches the site
            site_urls = {
                "luscious": "luscious.net",
                "multporn": "multporn.net", 
                "yiffer": "yiffer.xyz"
            }
            
            if site_urls[site] not in url.lower():
                result = messagebox.askyesno("Warning", 
                    f"URL doesn't seem to be from {site} ({site_urls[site]}). Continue anyway?")
                if not result:
                    return None
            
            return DownloadTask(
                task_id=str(uuid.uuid4()),
                site=site,
                task_type='url',
                url=url
            )
            
        else:
            # Tag-based download
            tags = self.tags_var.get()
            max_pages = self.max_pages_var.get()
            
            if not tags.strip():
                result = messagebox.askyesno("Warning", 
                    "No tags entered. This will download ALL content from the site. Continue?")
                if not result:
                    return None
            
            # Convert max_pages
            try:
                max_pages_int = int(max_pages) if max_pages.strip() else None
            except ValueError:
                messagebox.showerror("Error", "Max pages must be a number")
                return None
            
            # Check tag count for e621 family sites
            if site in ["e621", "e6ai", "e926"] and tags.strip():
                tag_count = len(tags.split())
                if tag_count > 40:
                    messagebox.showerror("Error", 
                        f"{site.upper()} allows maximum 40 tags. You entered {tag_count} tags.")
                    return None
            
            return DownloadTask(
                task_id=str(uuid.uuid4()),
                site=site,
                task_type='tags',
                tags=tags,
                max_pages=max_pages_int
            )
        
    def _start_download_task(self, task: DownloadTask):
        """Start downloading a specific task"""
        # Check if we have the required components
        if HAS_ASYNC_DEPS and self.config_manager is None:
            self.add_log("Error: Core components not initialized. Please wait for startup to complete.")
            messagebox.showerror("Error", "Application is still starting up. Please wait a moment and try again.")
            return
        
        self.is_downloading = True
        self.current_download_info = task
        task.status = 'downloading'
        self.update_queue_display()
        
        self.add_log(f"🚀 Starting download: {task}")
        
        # Start real download
        if self.loop and self.loop.is_running():
            if task.task_type == 'url':
                asyncio.run_coroutine_threadsafe(
                    self._start_url_download(task),
                    self.loop
                )
            else:
                asyncio.run_coroutine_threadsafe(
                    self._start_tag_download(task),
                    self.loop
                )
        else:
            self.add_log("Error: Async loop not available")
            messagebox.showerror("Error", "Download system not ready. Please restart the application.")
            self._download_completed(task, False)
    
    def _process_next_in_queue(self):
        """Process the next item in the download queue"""
        if self.is_downloading or self.download_queue.empty():
            return
        
        try:
            next_task = self.download_queue.get_nowait()
            self._start_download_task(next_task)
        except queue.Empty:
            pass
    
    def _download_completed(self, task: DownloadTask, success: bool):
        """Handle download completion"""
        self.is_downloading = False
        self.current_download_info = None
        task.status = 'completed' if success else 'failed'
        
        if success:
            self.add_log(f"✅ Completed: {task}")
        else:
            self.add_log(f"❌ Failed: {task}")
        
        self.update_queue_display()
        
        # Process next item in queue
        self._process_next_in_queue()
    
    def update_queue_display(self):
        """Update the queue listbox display"""
        self.queue_listbox.delete(0, tk.END)
        
        # Show current download
        if self.current_download_info:
            self.queue_listbox.insert(tk.END, f"🟢 DOWNLOADING: {self.current_download_info}")
        
        # Show queued items
        temp_items = []
        while not self.download_queue.empty():
            try:
                item = self.download_queue.get_nowait()
                temp_items.append(item)
                self.queue_listbox.insert(tk.END, f"⏳ QUEUED: {item}")
            except queue.Empty:
                break
        
        # Put items back in queue
        for item in temp_items:
            self.download_queue.put(item)
    
    def clear_queue(self):
        """Clear all items from the queue"""
        while not self.download_queue.empty():
            try:
                self.download_queue.get_nowait()
            except queue.Empty:
                break
        self.update_queue_display()
        self.add_log("🗑️ Queue cleared")
    
    def remove_selected_from_queue(self):
        """Remove selected item from queue"""
        selection = self.queue_listbox.curselection()
        if not selection:
            return
        
        selected_index = selection[0]
        
        # If it's the current download, we can't remove it
        if self.current_download_info and selected_index == 0:
            messagebox.showwarning("Cannot Remove", "Cannot remove currently downloading item.")
            return
        
        # Adjust index if current download is showing
        queue_index = selected_index
        if self.current_download_info:
            queue_index -= 1
        
        if queue_index >= 0:
            # Remove item from queue
            temp_items = []
            removed_item = None
            item_count = 0
            
            while not self.download_queue.empty():
                try:
                    item = self.download_queue.get_nowait()
                    if item_count == queue_index:
                        removed_item = item
                    else:
                        temp_items.append(item)
                    item_count += 1
                except queue.Empty:
                    break
            
            # Put remaining items back
            for item in temp_items:
                self.download_queue.put(item)
            
            if removed_item:
                self.add_log(f"✖️ Removed from queue: {removed_item}")
    
    def _is_duplicate_task(self, new_task: DownloadTask) -> bool:
        """Check if task is already in queue or currently downloading"""
        # Check current download
        if self.current_download_info and new_task == self.current_download_info:
            return True
        
        # Check queue
        temp_items = []
        is_duplicate = False
        
        while not self.download_queue.empty():
            try:
                item = self.download_queue.get_nowait()
                temp_items.append(item)
                if new_task == item:
                    is_duplicate = True
            except queue.Empty:
                break
        
        # Put items back in queue
        for item in temp_items:
            self.download_queue.put(item)
        
        return is_duplicate
            
        self.update_queue_display()
    
    async def _start_tag_download(self, task: DownloadTask):
        """Start tag-based download process using new async downloaders"""
        site = task.site
        tags = task.tags
        max_pages = task.max_pages
        try:
            self.root.after(0, lambda: self.status_text.set("Initializing download..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Initialize session
            self.sessions[task.task_id] = {
                'site': site,
                'tags': tags,
                'status': 'initializing',
                'progress': 0,
                'active_downloads': []
            }
            
            self.root.after(0, lambda: self.add_log(f"Starting {site} download for tags: '{tags}'"))
            self.root.after(0, lambda: self.status_text.set("Starting download..."))
            
            # Get credentials if needed
            api_user = None
            api_key = None
            if site in ["e621", "e6ai", "e926", "furbooru"]:
                credentials = self.config.get("user_credentials", {}).get(site, {})
                api_user = credentials.get("apiUser", "")
                api_key = credentials.get("apiKey", "")
                
                if not api_key:
                    self.root.after(0, lambda: self.add_log(f"Warning: No API credentials for {site}. Download may be limited."))
            
            # Get blacklist
            blacklist = self.config.get("blacklisted_tags", [])
            
            # Enable oneTimeDownload if configured
            db_file = self.config.get("oneTimeDownload", True)
            
            # Progress callback
            def progress_callback(message: str):
                self.root.after(0, lambda: self.add_log(message))
                self.root.after(0, lambda: self.status_text.set(message))
            
            # Call appropriate async downloader
            result = False
            if site in ["e621", "e6ai", "e926"]:
                result = await download_e621_tags(
                    tags=tags,
                    site=site,
                    blacklist=blacklist,
                    max_pages=max_pages,
                    api_user=api_user,
                    api_key=api_key,
                    db_file=db_file,
                    progress_callback=progress_callback
                )
            elif site == "rule34":
                result = await download_rule34_tags(
                    tags=tags,
                    blacklist=blacklist,
                    max_pages=max_pages,
                    db_file=db_file,
                    progress_callback=progress_callback
                )
            elif site == "furbooru":
                result = await download_furbooru_tags(
                    tags=tags,
                    blacklist=blacklist,
                    max_pages=max_pages,
                    api_key=api_key,
                    db_file=db_file,
                    progress_callback=progress_callback
                )
            
            if result:
                self.root.after(0, lambda: self.status_text.set("Download completed!"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: messagebox.showinfo("Complete", f"Download from {site} completed!"))
            else:
                self.root.after(0, lambda: self.status_text.set("Download failed"))
                self.root.after(0, lambda: messagebox.showwarning("Warning", f"Download from {site} failed or no content found"))
            
            # Mark download as completed
            self.root.after(0, lambda: self._download_completed(task, result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.add_log(f"Download error: {error_msg}"))
            self.root.after(0, lambda: self.status_text.set(f"Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_msg}"))
            self.root.after(0, lambda: self._download_completed(task, False))
    
    async def _start_url_download(self, task: DownloadTask):
        """Start URL-based download process using new async downloaders"""
        site = task.site
        url = task.url
        try:
            self.root.after(0, lambda: self.status_text.set("Initializing download..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            self.root.after(0, lambda: self.add_log(f"Starting {site} download from URL: {url}"))
            
            # Progress callback
            def progress_callback(message: str):
                self.root.after(0, lambda: self.add_log(message))
                self.root.after(0, lambda: self.status_text.set(message))
            
            # Call appropriate async downloader
            result = False
            if site == "luscious":
                result = await download_luscious_album(
                    url=url,
                    progress_callback=progress_callback
                )
            elif site == "multporn":
                result = await download_multporn_comic(
                    url=url,
                    progress_callback=progress_callback
                )
            elif site == "yiffer":
                result = await download_yiffer_comic(
                    url=url,
                    progress_callback=progress_callback
                )
            
            if result:
                self.root.after(0, lambda: self.status_text.set("Download completed!"))
                self.root.after(0, lambda: self.progress_var.set(100))
                media_dir = Path.cwd() / "media"
                self.root.after(0, lambda: self.add_log(f"Files downloaded to: {media_dir}"))
                self.root.after(0, lambda: messagebox.showinfo("Complete", f"Download from {site} completed!\n\nFiles saved to: {media_dir}"))
            else:
                self.root.after(0, lambda: self.status_text.set("Download failed"))
                self.root.after(0, lambda: messagebox.showwarning("Warning", f"Download from {site} failed or no content found"))
            
            # Mark download as completed
            self.root.after(0, lambda: self._download_completed(task, result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.add_log(f"Download error: {error_msg}"))
            self.root.after(0, lambda: self.status_text.set(f"Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_msg}"))
            self.root.after(0, lambda: self._download_completed(task, False))
    
    def save_credentials(self):
        """Save API credentials"""
        site = self.api_site_var.get()
        username = self.api_user_var.get()
        api_key = self.api_key_var.get()
        
        if not site:
            messagebox.showerror("Error", "Please select a site")
            return
        
        if not username or not api_key:
            messagebox.showerror("Error", "Please enter both username and API key")
            return
        
        try:
            # Save credentials via async operation
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._save_credentials_async(site, username, api_key),
                    self.loop
                )
            else:
                messagebox.showerror("Error", "Application not ready")
            
        except Exception as e:
            self.add_log(f"Error saving credentials: {e}")
            messagebox.showerror("Error", f"Failed to save credentials: {e}")
    
    async def _save_credentials_async(self, site: str, username: str, api_key: str):
        """Save credentials asynchronously"""
        try:
            await self.config_manager.update_credentials(site, username, api_key)
            
            # Reload config
            self.config = await self.config_manager.load_config()
            
            # Clear fields on main thread
            self.root.after(0, lambda: self.api_user_var.set(""))
            self.root.after(0, lambda: self.api_key_var.set(""))
            
            self.root.after(0, lambda: self.add_log(f"Credentials saved for {site}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Credentials saved for {site}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f"Error saving credentials: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to save credentials: {e}"))
    
    
    def run(self):
        """Run the application"""
        print("🚀 NN-Downloader started with Tkinter!")
        print("Close the window to exit.")
        
        # Handle window close
        def on_closing():
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        self.root.mainloop()


def run_tkinter_app():
    """Run the Tkinter application"""
    app = TkinterApp()
    app.run()


if __name__ == "__main__":
    run_tkinter_app()