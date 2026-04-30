from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HomeTab(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # Title Section
        title = QLabel("OS ARENA")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setStyleSheet("color: #007acc; margin-bottom: 0px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("A Real-Time Operating System Simulator and Visualizer")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #888; margin-top: 0px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        # Modules Grid
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)
        
        modules = [
            ("Scheduling", "CPU priority, Round Robin, SJF, and FCFS visualization.", 1),
            ("Memory", "Page replacement (FIFO, LRU, Optimal) and Allocation logic.", 2),
            ("Deadlock", "Banker's Algorithm safety check and resource matrices.", 3),
            ("Sync", "Producer-Consumer problem with Mutex and Semaphores.", 4)
        ]
        
        for name, desc, idx in modules:
            card = QFrame()
            card.setFixedSize(220, 280)
            card.setStyleSheet("""
                QFrame {
                    background-color: #252526;
                    border: 1px solid #3e3e42;
                    border-radius: 15px;
                }
                QFrame:hover {
                    border: 1px solid #007acc;
                    background-color: #2d2d30;
                }
            """)
            card_v = QVBoxLayout()
            card_v.setContentsMargins(20, 20, 20, 20)
            
            m_title = QLabel(name.upper())
            m_title.setFont(QFont("Arial", 14, QFont.Bold))
            m_title.setStyleSheet("color: #007acc; border: none;")
            
            m_desc = QLabel(desc)
            m_desc.setWordWrap(True)
            m_desc.setStyleSheet("color: #ccc; border: none;")
            
            btn = QPushButton("Launch Module")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3e3e42;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover { background-color: #007acc; }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.switch_callback(i))
            
            card_v.addWidget(m_title)
            card_v.addWidget(m_desc)
            card_v.addStretch()
            card_v.addWidget(btn)
            card.setLayout(card_v)
            grid_layout.addWidget(card)
            
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        footer = QLabel("Developed as an Interactive Educational Tool for OS Fundamentals")
        footer.setStyleSheet("color: #555; font-size: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        self.setLayout(layout)
