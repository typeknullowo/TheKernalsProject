import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

# Import all modules
from ui.home_tab import HomeTab
from ui.scheduling_tab import SchedulingTab
from ui.memory_tab import MemoryTab
from ui.deadlock_tab import DeadlockTab
from ui.sync_tab import SyncTab
from ui.scenarios_tab import ScenariosTab

class OSArenaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OS Arena - Professional Visual Simulator")
        self.resize(1300, 850)
        
        # --- GLOBAL STYLESHEET ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { color: #d4d4d4; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #ffffff; }
            
            /* Sidebar Styling */
            QListWidget {
                background-color: #252526;
                border: none;
                border-right: 1px solid #3e3e42;
                outline: none;
                padding-top: 20px;
            }
            QListWidget::item {
                height: 55px;
                padding-left: 20px;
                margin: 6px 12px;
                border-radius: 8px;
                color: #aaa;
                font-weight: bold;
                font-size: 13px;
            }
            QListWidget::item:hover { background-color: #2d2d30; color: white; }
            QListWidget::item:selected { background-color: #007acc; color: white; }
            
            /* Dropdown (QComboBox) Styling */
            QComboBox {
                background-color: #3e3e42;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px;
                color: white;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: white;
                selection-background-color: #007acc;
                border: 1px solid #3e3e42;
                outline: none;
            }
            
            /* Generic Button Styling */
            QPushButton {
                background-color: #3e3e42;
                border: 1px solid #4d4d4d;
                border-radius: 6px;
                padding: 10px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #505050; border-color: #007acc; }
            QPushButton:pressed { background-color: #007acc; }
            
            /* Scrollbars */
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px 0 0px 0;
            }
            QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- 1. SIDEBAR NAVIGATION ---
        sidebar_container = QFrame()
        sidebar_container.setFixedWidth(260)
        sidebar_v = QVBoxLayout()
        sidebar_v.setContentsMargins(0, 0, 0, 0)
        sidebar_v.setSpacing(0)
        
        logo_area = QFrame()
        logo_area.setFixedHeight(120)
        logo_v = QVBoxLayout()
        logo_v.setAlignment(Qt.AlignCenter)
        logo_lbl = QLabel("OS ARENA")
        logo_lbl.setFont(QFont("Arial", 26, QFont.Bold))
        logo_lbl.setStyleSheet("color: #007acc; margin-top: 20px;")
        sub_lbl = QLabel("VISUAL SIMULATOR")
        sub_lbl.setStyleSheet("color: #666; font-size: 10px; letter-spacing: 2px;")
        logo_v.addWidget(logo_lbl)
        logo_v.addWidget(sub_lbl)
        logo_area.setLayout(logo_v)
        sidebar_v.addWidget(logo_area)
        
        self.nav_list = QListWidget()
        items = [
            ("Home", 0),
            ("CPU Scheduling", 1),
            ("Memory / Paging", 2),
            ("Deadlock Avoidance", 3),
            ("Synchronization", 4),
            ("Guided Scenarios", 5)
        ]
        for name, idx in items:
            item = QListWidgetItem(name)
            self.nav_list.addItem(item)
            
        self.nav_list.currentRowChanged.connect(self.switch_tab)
        sidebar_v.addWidget(self.nav_list)
        
        sidebar_v.addStretch()
        
        version_lbl = QLabel("v2.0 Presentation Ready")
        version_lbl.setStyleSheet("color: #444; font-size: 9px; padding: 10px;")
        version_lbl.setAlignment(Qt.AlignCenter)
        sidebar_v.addWidget(version_lbl)
        
        sidebar_container.setLayout(sidebar_v)
        main_layout.addWidget(sidebar_container)
        
        # --- 2. CONTENT AREA (STOCKED WIDGET) ---
        self.stack = QStackedWidget()
        
        # Instantiate Tabs
        self.home_tab = HomeTab(self.switch_tab)
        self.scheduling_tab = SchedulingTab()
        self.memory_tab = MemoryTab()
        self.deadlock_tab = DeadlockTab()
        self.sync_tab = SyncTab()
        self.scenarios_tab = ScenariosTab(self.switch_tab)
        
        # Add to stack
        self.stack.addWidget(self.home_tab)      # 0
        self.stack.addWidget(self.scheduling_tab) # 1
        self.stack.addWidget(self.memory_tab)     # 2
        self.stack.addWidget(self.deadlock_tab)   # 3
        self.stack.addWidget(self.sync_tab)       # 4
        self.stack.addWidget(self.scenarios_tab)  # 5
        
        main_layout.addWidget(self.stack)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Start at Home
        self.nav_list.setCurrentRow(0)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.nav_list.setCurrentRow(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OSArenaGUI()
    window.show()
    sys.exit(app.exec_())
