from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRect
from PyQt5.QtGui import QFont, QColor

from sync.banker import BankersAlgorithm

class MatrixCard(QFrame):
    def __init__(self, title, rows, cols, data, headers):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #252526; border: 1px solid #3e3e42; border-radius: 10px;")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{title.upper()}</b>"))
        
        self.table = QTableWidget(rows, cols)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("background: transparent; color: white; gridline-color: #3e3e42; border: none;")
        self.table.setFixedHeight(150)
        
        for r in range(rows):
            for c in range(cols):
                item = QTableWidgetItem(str(data[r][c]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)
                
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_data(self, data):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                self.table.item(r, c).setText(str(data[r][c]))

class StatusBanner(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.layout = QHBoxLayout()
        self.lbl = QLabel("SYSTEM STATE: UNKNOWN")
        self.lbl.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl)
        self.setLayout(self.layout)
        self.set_safe(True, [])

    def set_safe(self, is_safe, sequence=None):
        if is_safe:
            self.lbl.setText(f"SAFE STATE DETECTED ✅ (Seq: {' → '.join(sequence) if sequence else 'None'})")
            self.setStyleSheet("background-color: #28a745; color: white; border-radius: 10px;")
        else:
            self.lbl.setText("UNSAFE STATE: DEADLOCK RISK ⚠️")
            self.setStyleSheet("background-color: #dc3545; color: white; border-radius: 10px;")

class ResourceBlock(QFrame):
    def __init__(self, label, value):
        super().__init__()
        self.setFixedSize(60, 60)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        l_lbl = QLabel(label)
        l_lbl.setAlignment(Qt.AlignCenter)
        l_lbl.setStyleSheet("font-size: 10px; color: #aaa;")
        
        self.v_lbl = QLabel(str(value))
        self.v_lbl.setAlignment(Qt.AlignCenter)
        self.v_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        
        layout.addWidget(l_lbl)
        layout.addWidget(self.v_lbl)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #3e3e42; border: 1px solid #555; border-radius: 5px;")

class DeadlockTab(QWidget):
    def __init__(self):
        super().__init__()
        self.banker = None
        self.init_ui()
        self.reset_banker()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # --- 1. TOP BANNER ---
        self.banner = StatusBanner()
        main_layout.addWidget(self.banner)
        
        # --- 2. AVAILABLE RESOURCES ---
        avail_container = QFrame()
        avail_container.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 10px;")
        avail_layout = QHBoxLayout()
        avail_layout.addWidget(QLabel("<b>AVAILABLE RESOURCES:</b>"))
        self.avail_blocks_layout = QHBoxLayout()
        avail_layout.addLayout(self.avail_blocks_layout)
        avail_layout.addStretch()
        
        self.btn_reset = QPushButton("↺ Reset System")
        self.btn_reset.clicked.connect(self.reset_banker)
        self.btn_reset.setStyleSheet("background-color: #3e3e42; color: white; padding: 8px; font-weight: bold;")
        avail_layout.addWidget(self.btn_reset)
        
        avail_container.setLayout(avail_layout)
        main_layout.addWidget(avail_container)
        
        # --- 3. MATRICES GRID ---
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)
        
        # --- 4. REQUEST TESTER ---
        test_container = QFrame()
        test_container.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 15px;")
        test_layout = QHBoxLayout()
        test_layout.setSpacing(20) # Added clear spacing
        test_layout.addWidget(QLabel("<b>TEST RESOURCE REQUEST:</b>"))
        
        proc_layout = QHBoxLayout()
        proc_layout.setSpacing(10)
        self.combo_proc = QComboBox()
        proc_layout.addWidget(QLabel("Process:"))
        proc_layout.addWidget(self.combo_proc)
        test_layout.addLayout(proc_layout)
        
        vec_layout = QHBoxLayout()
        vec_layout.setSpacing(10)
        self.line_req = QLineEdit()
        self.line_req.setPlaceholderText("e.g. 1, 0, 2")
        self.line_req.setFixedWidth(120)
        vec_layout.addWidget(QLabel("Vector:"))
        vec_layout.addWidget(self.line_req)
        test_layout.addLayout(vec_layout)
        
        test_layout.addStretch()
        
        self.btn_test = QPushButton("Submit Request")
        self.btn_test.clicked.connect(self.submit_request)
        self.btn_test.setStyleSheet("background-color: #007acc; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        test_layout.addWidget(self.btn_test)
        
        test_container.setLayout(test_layout)
        main_layout.addWidget(test_container)
        
        # --- 5. LOG / EXPLANATION ---
        main_layout.addWidget(QLabel("<b>BANKER'S ALGORITHM LOG & ANALYSIS</b>"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(120)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace; border-radius: 5px;")
        main_layout.addWidget(self.log_output)
        
        self.setLayout(main_layout)

    def reset_banker(self):
        # Default scenario
        processes = ["P0", "P1", "P2", "P3", "P4"]
        available = [3, 3, 2]
        max_claim = [[7,5,3], [3,2,2], [9,0,2], [2,2,2], [4,3,3]]
        allocation = [[0,1,0], [2,0,0], [3,0,2], [2,1,1], [0,0,2]]
        
        self.banker = BankersAlgorithm(processes, available, max_claim, allocation)
        self.combo_proc.clear()
        self.combo_proc.addItems(processes)
        
        # Clear/Rebuild Grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        res_headers = ["A", "B", "C"]
        self.card_alloc = MatrixCard("Allocation", 5, 3, allocation, res_headers)
        self.card_max = MatrixCard("Max Claim", 5, 3, max_claim, res_headers)
        self.card_need = MatrixCard("Need (Max - Alloc)", 5, 3, self.banker.need, res_headers)
        
        self.grid_layout.addWidget(self.card_alloc, 0, 0)
        self.grid_layout.addWidget(self.card_max, 0, 1)
        self.grid_layout.addWidget(self.card_need, 0, 2)
        
        self.log_output.clear()
        self.log_output.append("System initialized to default state.")
        self.update_visuals()

    def update_visuals(self):
        # Update Banner
        is_safe, seq = self.banker.is_safe_state()
        self.banner.set_safe(is_safe, seq)
        
        # Update Available Blocks
        while self.avail_blocks_layout.count():
            item = self.avail_blocks_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        labels = ["A", "B", "C"]
        for i, val in enumerate(self.banker.available):
            self.avail_blocks_layout.addWidget(ResourceBlock(labels[i], val))
            
        # Update Matrices
        self.card_alloc.update_data(self.banker.allocation)
        self.card_need.update_data(self.banker.need)

    def submit_request(self):
        idx = self.combo_proc.currentIndex()
        p_name = self.combo_proc.currentText()
        try:
            req = [int(x.strip()) for x in self.line_req.text().split(",")]
            if len(req) != 3: raise ValueError()
        except:
            self.log_output.append("Error: Invalid request vector. Format: x, y, z")
            return
            
        self.log_output.append(f"\n> Request from {p_name}: {req}")
        success, msg = self.banker.request_resources(idx, req)
        self.log_output.append(msg)
        
        self.update_visuals()
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
