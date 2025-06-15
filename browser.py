import sys
import json
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from downloader import Downloader
from settings import SettingsDialog
from browser_tab import BrowserTab

BOOKMARKS_FILE = "bookmarks.json"
HISTORY_FILE = "history.json"

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.is_dark_mode = False  # Default theme is light
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        # Add navigation buttons (back, forward, reload, etc.)
        self.add_nav_buttons()

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Add new buttons for Bookmarks
        self.add_bookmark_btn = QAction("★ Add Bookmark", self)
        self.add_bookmark_btn.triggered.connect(self.add_to_bookmarks)
        self.navbar.addAction(self.add_bookmark_btn)

        self.bookmark_btn = QAction("📚 Bookmarks", self)
        self.bookmark_btn.triggered.connect(self.show_bookmarks)
        self.navbar.addAction(self.bookmark_btn)

        # History menu button
        history_btn = QAction("History", self)
        history_btn.triggered.connect(self.show_history)
        self.navbar.addAction(history_btn)

        # Settings button (for dark mode)
        settings_btn = QAction("⚙️ Settings", self)
        settings_btn.triggered.connect(self.open_settings)
        self.navbar.addAction(settings_btn)

        # Add New Tab
        new_tab_btn = QAction("🗂 New Tab", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        # Start with one tab
        self.add_new_tab()

        # Load bookmarks and history
        self.load_bookmarks()
        self.load_history()

    def set_dark_mode(self, enable):
        """Update browser UI theme based on dark mode status."""
        self.is_dark_mode = enable
        # Propagate changes to the rest of the UI
        palette = QPalette()
        if enable:
            palette.setColor(QPalette.Background, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.Background, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))

        self.setPalette(palette)  # Apply palette to the entire browser window

    def add_nav_buttons(self):
        """Add navigation buttons to the toolbar (back, forward, reload, etc.)."""
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        self.navbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.navbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        download_btn = QAction("⬇️ Download", self)
        download_btn.triggered.connect(self.download_file)
        self.navbar.addAction(download_btn)

    def current_browser(self):
        """Get the current tab's browser (QWebEngineView)."""
        current_tab = self.tabs.currentWidget()
        return current_tab.browser

    def add_new_tab(self, url="https://www.google.com"):
        """Add a new tab and load the given URL."""
        # Ensure URL is a valid string
        if not isinstance(url, str):
            url = "https://www.google.com"  # default URL if invalid input
        new_tab = BrowserTab()
        new_tab.browser.urlChanged.connect(self.update_url)
        new_tab.browser.loadFinished.connect(self.save_history)
        i = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(i)
        new_tab.browser.setUrl(QUrl(url))

    def close_current_tab(self, index):
        """Close the current tab."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_home(self):
        """Navigate to the home page."""
        self.current_browser().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """Navigate to the URL entered in the address bar."""
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        """Update the URL in the address bar when the page changes."""
        self.url_bar.setText(q.toString())
        self.tabs.setTabText(self.tabs.currentIndex(), q.host())

    def download_file(self):
        """Download the current page URL using the Downloader."""
        url = self.current_browser().url().toString()
        self.downloader.download(url)

    def open_settings(self):
        """Open the settings dialog to toggle dark mode."""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def save_bookmarks(self):
        """Save bookmarks to a file."""
        with open(BOOKMARKS_FILE, 'w') as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        """Load bookmarks from a file."""
        if os.path.exists(BOOKMARKS_FILE) and os.path.getsize(BOOKMARKS_FILE) > 0:
            with open(BOOKMARKS_FILE, 'r') as f:
                try:
                    self.bookmarks = json.load(f)
                except json.JSONDecodeError:
                    self.bookmarks = {}  # In case of a bad or empty file
        else:
            self.bookmarks = {}

    def add_to_bookmarks(self):
        """Add the current page to bookmarks."""
        url = self.current_browser().url().toString()
        title = self.current_browser().title()

        if url not in self.bookmarks:
            self.bookmarks[url] = title
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", f"'{title}' has been added to your bookmarks.")
        else:
            QMessageBox.warning(self, "Bookmark Exists", f"'{title}' is already in your bookmarks.")

    def show_bookmarks(self):
        """Show the bookmarks in a menu."""
        bookmark_menu = QMenu(self)
        if not self.bookmarks:
            bookmark_menu.addAction("No bookmarks added yet.")
        else:
            for url, title in self.bookmarks.items():
                action = QAction(title, self)
                action.triggered.connect(lambda _, url=url: self.navigate_to_bookmark(url))
                bookmark_menu.addAction(action)
        bookmark_menu.exec_(self.navbar.mapToGlobal(QPoint(0, 0)))

    def navigate_to_bookmark(self, url):
        """Navigate to a selected bookmark."""
        self.current_browser().setUrl(QUrl(url))

    def save_history(self):
        """Save the browsing history to a file."""
        url = self.current_browser().url().toString()
        title = self.current_browser().title()
        self.history.append({"title": title, "url": url})
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f)

    def load_history(self):
        """Load the browsing history from a file."""
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            with open(HISTORY_FILE, 'r') as f:
                try:
                    self.history = json.load(f)
                except json.JSONDecodeError:
                    self.history = []  # In case of a bad or empty file
        else:
            self.history = []

    def show_history(self):
        """Show the browser history in a menu."""
        history_menu = QMenu(self)
        for entry in self.history:
            action = QAction(entry["title"], self)
            action.triggered.connect(lambda _, url=entry["url"]: self.navigate_to_history(url))
            history_menu.addAction(action)
        history_menu.exec_(self.navbar.mapToGlobal(QPoint(0, 0)))

    def navigate_to_history(self, url):
        """Navigate to a URL selected from the history menu."""
        self.current_browser().setUrl(QUrl(url))
