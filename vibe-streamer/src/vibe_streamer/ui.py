from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLabel,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QDialog,
    QListWidgetItem,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from .config import config
from .scanner import scan_directories
from .player import play_video
from . import db


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Root Directories")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        for path in config.root_dirs:
            self.list_widget.addItem(path)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Directory")
        self.add_btn.clicked.connect(self.add_dir)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_dir)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

    def add_dir(self):
        path, ok = QInputDialog.getText(
            self, "Add Directory", "Enter absolute path to directory:"
        )
        if ok and path:
            from pathlib import Path

            p = Path(path)
            if not p.exists():
                QMessageBox.warning(self, "Error", f"Directory does not exist:\n{path}")
            elif not p.is_dir():
                QMessageBox.warning(self, "Error", f"Path is not a directory:\n{path}")
            else:
                config.add_root_dir(path)
                self.list_widget.addItem(path)
                QMessageBox.information(
                    self, "Success", f"Successfully added {path} to root directories."
                )

    def remove_dir(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            path = current_item.text()
            config.remove_root_dir(path)
            self.list_widget.takeItem(self.list_widget.row(current_item))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe Streamer")
        self.setMinimumSize(900, 600)
        self.library = {}

        self._setup_ui()
        self._setup_menu()
        self.load_library_ui()

    def _setup_menu(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")

        manage_dirs_action = QAction("Manage Root Directories", self)
        manage_dirs_action.triggered.connect(self.open_settings)
        settings_menu.addAction(manage_dirs_action)

        refresh_action = QAction("Refresh Library (Scan Network)", self)
        refresh_action.triggered.connect(self.force_scan_library)
        settings_menu.addAction(refresh_action)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Series Panel
        series_layout = QVBoxLayout()
        series_label = QLabel("Series")
        series_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.series_list = QListWidget()
        self.series_list.itemSelectionChanged.connect(self.on_series_selected)
        series_layout.addWidget(series_label)
        series_layout.addWidget(self.series_list)

        # Season Panel
        season_layout = QVBoxLayout()
        season_label = QLabel("Seasons")
        season_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.season_list = QListWidget()
        self.season_list.itemSelectionChanged.connect(self.on_season_selected)
        season_layout.addWidget(season_label)
        season_layout.addWidget(self.season_list)

        # Episode Panel
        episode_layout = QVBoxLayout()
        episode_label = QLabel("Episodes")
        episode_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.episode_list = QListWidget()
        self.episode_list.itemDoubleClicked.connect(self.on_episode_double_clicked)
        episode_layout.addWidget(episode_label)
        episode_layout.addWidget(self.episode_list)

        main_layout.addLayout(series_layout, 1)
        main_layout.addLayout(season_layout, 1)
        main_layout.addLayout(episode_layout, 2)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        self.force_scan_library()

    def load_library_ui(self):
        self.series_list.clear()
        self.season_list.clear()
        self.episode_list.clear()

        self.library = db.load_library()

        if not self.library and config.root_dirs:
            self.force_scan_library()
            return

        for series in sorted(self.library.keys()):
            self.series_list.addItem(series)

    def force_scan_library(self):
        if not config.root_dirs:
            return

        self.library = scan_directories(config.root_dirs)
        db.save_library(self.library)
        self.load_library_ui()

    def on_series_selected(self):
        self.season_list.clear()
        self.episode_list.clear()

        items = self.series_list.selectedItems()
        if not items:
            return

        series_name = items[0].text()
        seasons = self.library.get(series_name, {})
        for season in sorted(seasons.keys()):
            self.season_list.addItem(season)

    def on_season_selected(self):
        self.episode_list.clear()

        series_items = self.series_list.selectedItems()
        season_items = self.season_list.selectedItems()

        if not series_items or not season_items:
            return

        series_name = series_items[0].text()
        season_name = season_items[0].text()

        episodes = self.library.get(series_name, {}).get(season_name, [])
        for ep in episodes:
            item = QListWidgetItem(ep["name"])
            item.setData(Qt.UserRole, ep["path"])
            self.episode_list.addItem(item)

    def on_episode_double_clicked(self, item):
        path = item.data(Qt.UserRole)
        if path:
            try:
                play_video(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not play video:\n{e}")
