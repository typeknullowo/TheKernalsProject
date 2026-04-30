from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ScenariosTab(QWidget):
    def __init__(self, load_scenario_callback):
        super().__init__()
        self.load_scenario_callback = load_scenario_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("GUIDED SIMULATION SCENARIOS")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #007acc;")
        layout.addWidget(title)
        
        subtitle = QLabel("Select a preset scenario to observe specific Operating System behaviors.")
        subtitle.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(15)
        container.setLayout(self.container_layout)
        
        scenarios = [
            ("CPU-Intensive Mixed Load", "Scheduling", "A mix of short and long CPU bursts to demonstrate the effectiveness of Round Robin vs SJF.", 1),
            ("The Page Fault Storm", "Memory", "A reference string designed to trigger high thrashing in FIFO while showing LRU's temporal efficiency.", 2),
            ("Deadlock-Prone Resource Request", "Deadlock", "A system state that is currently SAFE but will enter an UNSAFE state if a specific large request is granted.", 3),
            ("High Concurrency Interleaving", "Sync", "Multiple producer-consumer actions happening in rapid succession to test lock stability.", 4)
        ]
        
        for s_title, module, desc, midx in scenarios:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #252526;
                    border: 1px solid #3e3e42;
                    border-radius: 10px;
                }
                QFrame:hover { border: 1px solid #007acc; }
            """)
            card_h = QHBoxLayout()
            card_h.setContentsMargins(20, 20, 20, 20)
            
            info_v = QVBoxLayout()
            t_lbl = QLabel(f"<b>{s_title}</b>")
            t_lbl.setStyleSheet("font-size: 16px; color: white; border: none;")
            m_lbl = QLabel(f"Module: {module}")
            m_lbl.setStyleSheet("color: #007acc; font-size: 11px; border: none;")
            d_lbl = QLabel(desc)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet("color: #aaa; border: none;")
            
            info_v.addWidget(t_lbl)
            info_v.addWidget(m_lbl)
            info_v.addWidget(d_lbl)
            
            btn = QPushButton("Load Scenario")
            btn.setFixedSize(140, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #005a9e; }
            """)
            btn.clicked.connect(lambda checked, m=midx: self.load_scenario_callback(m))
            
            card_h.addLayout(info_v, 8)
            card_h.addWidget(btn, 2)
            card.setLayout(card_h)
            self.container_layout.addWidget(card)
            
        self.container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
