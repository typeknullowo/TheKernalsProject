from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QFrame, QScrollArea, QTextEdit, QLineEdit, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from memory.paging import run_fifo, run_lru, run_optimal
from memory.allocation import first_fit, best_fit
from models.memory_block import MemoryBlock

class PageCard(QFrame):
    def __init__(self, val, is_current=False, action=None):
        super().__init__()
        self.setFixedSize(45, 45)
        self.val = val
        self.is_current = is_current
        self.action = action
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(str(self.val))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(lbl)
        self.setLayout(layout)
        
        # Styling
        bg = "#3e3e42"
        border = "1px solid #555"
        text = "#ccc"
        
        if self.is_current:
            bg = "#28a745" if self.action == "Hit" else "#dc3545"
            text = "white"
            border = "2px solid white"
            
        self.setStyleSheet(f"""
            PageCard {{
                background-color: {bg};
                color: {text};
                border: {border};
                border-radius: 5px;
            }}
            QLabel {{ color: {text}; }}
        """)

class FrameCard(QFrame):
    def __init__(self, val, highlighted=False, action=None):
        super().__init__()
        self.setFixedSize(70, 70)
        self.val = val
        self.highlighted = highlighted
        self.action = action
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        lbl = QLabel(str(self.val) if self.val is not None else "-")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(lbl)
        self.setLayout(layout)
        
        bg = "#1e1e1e"
        border = "2px solid #3e3e42"
        if self.highlighted:
            bg = "#155724" if self.action == "Hit" else "#721c24"
            border = "2px solid #28a745" if self.action == "Hit" else "2px solid #dc3545"
            
        self.setStyleSheet(f"""
            FrameCard {{
                background-color: {bg};
                color: white;
                border: {border};
                border-radius: 8px;
            }}
            QLabel {{ color: white; }}
        """)

class AllocationBar(QFrame):
    def __init__(self, title, blocks):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #252526; border: 1px solid #3e3e42; border-radius: 10px;")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{title.upper()}</b>"))
        
        bar_layout = QHBoxLayout()
        bar_layout.setSpacing(2)
        
        total_size = sum(b.size for b in blocks)
        for b in blocks:
            width = max(40, int((b.size / total_size) * 600))
            block_frame = QFrame()
            block_frame.setFixedSize(width, 50)
            
            color = "#28a745" if b.is_free else "#007acc"
            block_frame.setStyleSheet(f"background-color: {color}; border: 1px solid #1e1e1e; border-radius: 3px;")
            
            b_layout = QVBoxLayout()
            b_layout.setContentsMargins(2, 2, 2, 2)
            txt = f"{b.size}" if b.is_free else f"{b.allocated_to}\n{b.allocated_size}"
            lbl = QLabel(txt)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 9px; color: white; font-weight: bold;")
            b_layout.addWidget(lbl)
            block_frame.setLayout(b_layout)
            
            # Show internal fragmentation if allocated
            if not b.is_free and b.fragmentation > 0:
                frag_width = max(5, int((b.fragmentation / b.size) * width))
                # Note: Visualizing frag inside the same block is hard with simple layout, 
                # we'll just use a tooltip or label.
                block_frame.setToolTip(f"Internal Frag: {b.fragmentation}")
                
            bar_layout.addWidget(block_frame)
            
        layout.addLayout(bar_layout)
        self.setLayout(layout)

class MemoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_simulation)
        self.history = []
        self.current_step = 0
        
        self.init_ui()
        self.reset_simulation()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # --- 1. TOP BAR (CONTROLS) ---
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #2d2d2d; border-radius: 10px;")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(15, 12, 15, 12)
        top_layout.setSpacing(15)
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["FIFO", "LRU", "Optimal"])
        top_layout.addWidget(QLabel("<b>Algorithm:</b>"))
        top_layout.addWidget(self.algo_combo)
        
        top_layout.addWidget(QLabel("<b>Frames:</b>"))
        self.spin_frames = QSpinBox()
        self.spin_frames.setRange(1, 8)
        self.spin_frames.setValue(3)
        top_layout.addWidget(self.spin_frames)
        
        top_layout.addWidget(QLabel("<b>Reference String:</b>"))
        self.line_ref = QLineEdit("7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2")
        self.line_ref.setMinimumWidth(250)
        self.line_ref.setStyleSheet("padding: 5px; background: #1e1e1e; border: 1px solid #3e3e42; border-radius: 4px;")
        top_layout.addWidget(self.line_ref)
        
        top_layout.addStretch()
        
        self.btn_play = QPushButton("▶ Play")
        self.btn_step = QPushButton("⏯ Step")
        self.btn_reset = QPushButton("↺ Load / Reset")
        
        for btn in [self.btn_play, self.btn_step, self.btn_reset]:
            btn.setStyleSheet("background-color: #3e3e42; color: white; padding: 10px 15px; border-radius: 6px; font-weight: bold;")
            top_layout.addWidget(btn)
        
        self.btn_play.clicked.connect(self.play_simulation)
        self.btn_step.clicked.connect(self.step_simulation)
        self.btn_reset.clicked.connect(self.reset_simulation)
        
        top_bar.setLayout(top_layout)
        main_layout.addWidget(top_bar)
        
        # --- 2. MIDDLE AREA (Paging Simulator) ---
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(25)
        
        # Left: Visualizer
        paging_viz = QVBoxLayout()
        paging_viz.setSpacing(10)
        
        paging_viz.addWidget(QLabel("<b>PROCESS REFERENCE STREAM</b>"))
        self.scroll_ref = QScrollArea()
        self.scroll_ref.setWidgetResizable(True)
        self.scroll_ref.setFixedHeight(90)
        self.scroll_ref.setStyleSheet("background-color: #1a1a1a; border: 1px solid #3e3e42; border-radius: 10px;")
        self.ref_container = QWidget()
        self.ref_layout = QHBoxLayout()
        self.ref_layout.setAlignment(Qt.AlignLeft)
        self.ref_container.setLayout(self.ref_layout)
        self.scroll_ref.setWidget(self.ref_container)
        paging_viz.addWidget(self.scroll_ref)
        
        paging_viz.addSpacing(15)
        paging_viz.addWidget(QLabel("<b>PHYSICAL MEMORY FRAMES (RAM)</b>"))
        self.frames_layout = QHBoxLayout()
        self.frames_layout.setAlignment(Qt.AlignCenter)
        self.frames_layout.setSpacing(20)
        paging_viz.addLayout(self.frames_layout)
        
        mid_layout.addLayout(paging_viz, 7)
        
        # Right: Metrics
        self.metrics_frame = QFrame()
        self.metrics_frame.setFixedWidth(240)
        self.metrics_frame.setStyleSheet("background-color: #252526; border: 1px solid #3e3e42; border-radius: 12px;")
        metrics_v = QVBoxLayout()
        metrics_v.setContentsMargins(20, 20, 20, 20)
        metrics_v.addWidget(QLabel("<b>ANALYTICS</b>"))
        metrics_v.addSpacing(10)
        
        self.lbl_hits = QLabel("Hits: 0")
        self.lbl_hits.setStyleSheet("color: #28a745; font-size: 22px; font-weight: bold;")
        self.lbl_faults = QLabel("Faults: 0")
        self.lbl_faults.setStyleSheet("color: #dc3545; font-size: 22px; font-weight: bold;")
        self.lbl_ratio = QLabel("Ratio: 0%")
        self.lbl_ratio.setStyleSheet("font-size: 16px; color: #aaa; margin-top: 5px;")
        
        metrics_v.addWidget(self.lbl_hits)
        metrics_v.addWidget(self.lbl_faults)
        metrics_v.addWidget(self.lbl_ratio)
        metrics_v.addStretch()
        self.metrics_frame.setLayout(metrics_v)
        mid_layout.addWidget(self.metrics_frame)
        
        main_layout.addLayout(mid_layout)
        
        # --- 3. ALLOCATION AREA ---
        main_layout.addWidget(QLabel("<b>MAIN MEMORY ALLOCATION (FIRST FIT VS BEST FIT)</b>"))
        self.alloc_layout = QVBoxLayout()
        main_layout.addLayout(self.alloc_layout)
        
        # --- 4. BOTTOM AREA (LOG) ---
        main_layout.addWidget(QLabel("<b>SIMULATION LOG</b>"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(100)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace; border-radius: 5px;")
        main_layout.addWidget(self.log_output)
        
        self.setLayout(main_layout)

    def play_simulation(self):
        self.timer.start(800)
        self.btn_play.setEnabled(False)

    def reset_simulation(self):
        self.timer.stop()
        self.btn_play.setEnabled(True)
        self.current_step = 0
        
        # Parse ref string
        try:
            ref = [int(x.strip()) for x in self.line_ref.text().split(",")]
        except:
            self.log_output.append("Error: Invalid reference string.")
            return
            
        num_frames = self.spin_frames.value()
        algo = self.algo_combo.currentText()
        
        if algo == "FIFO": res = run_fifo(ref, num_frames)
        elif algo == "LRU": res = run_lru(ref, num_frames)
        else: res = run_optimal(ref, num_frames)
        
        self.history = res["history"]
        self.reference_string = ref
        self.log_output.clear()
        self.log_output.append(f"Simulation Reset: {algo}")
        
        self.update_visuals()
        self.update_allocation_view()

    def step_simulation(self):
        if self.current_step < len(self.history):
            self.update_visuals()
            self.current_step += 1
        else:
            self.timer.stop()
            self.btn_play.setEnabled(True)
            self.log_output.append("Paging Simulation Complete.")

    def update_visuals(self):
        # 1. Update Reference String
        while self.ref_layout.count():
            item = self.ref_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for i, val in enumerate(self.reference_string):
            is_current = (i == self.current_step)
            action = self.history[self.current_step][1] if is_current else None
            self.ref_layout.addWidget(PageCard(val, is_current, action))
            
        # 2. Update Frames
        while self.frames_layout.count():
            item = self.frames_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if self.current_step < len(self.history):
            page, action, frames = self.history[self.current_step]
            num_frames = self.spin_frames.value()
            for i in range(num_frames):
                val = frames[i] if i < len(frames) else None
                highlighted = (val == page)
                self.frames_layout.addWidget(FrameCard(val, highlighted, action))
                
            # 3. Update Metrics
            hits = sum(1 for i in range(self.current_step + 1) if self.history[i][1] == "Hit")
            faults = (self.current_step + 1) - hits
            self.lbl_hits.setText(f"Hits: {hits}")
            self.lbl_faults.setText(f"Faults: {faults}")
            ratio = (hits / (hits + faults)) * 100
            self.lbl_ratio.setText(f"Hit Ratio: {ratio:.1f}%")
            
            # 4. Update Log
            self.log_output.append(f"T={self.current_step}: Page {page} -> {action}")
            self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def update_allocation_view(self):
        while self.alloc_layout.count():
            item = self.alloc_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # Run allocation demos
        def get_blocks(): return [MemoryBlock(1, 100), MemoryBlock(2, 500), MemoryBlock(3, 200), MemoryBlock(4, 300), MemoryBlock(5, 600)]
        reqs = [("P1", 212), ("P2", 417), ("P3", 112), ("P4", 426)]
        
        blocks_ff = get_blocks()
        for p, s in reqs: first_fit(blocks_ff, p, s)
        
        blocks_bf = get_blocks()
        for p, s in reqs: best_fit(blocks_bf, p, s)
        
        self.alloc_layout.addWidget(AllocationBar("First Fit Allocation", blocks_ff))
        self.alloc_layout.addWidget(AllocationBar("Best Fit Allocation", blocks_bf))
