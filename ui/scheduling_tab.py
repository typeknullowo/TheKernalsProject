from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QScrollArea, QFrame, QGridLayout, QTextEdit, QSlider
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette

from scheduler.engine import SimulationEngine
from tests.sample_scenarios import get_sample_processes
from models.process import Process

class ProcessCard(QFrame):
    def __init__(self, process: Process):
        super().__init__()
        self.setFixedSize(140, 100)
        self.setFrameShape(QFrame.StyledPanel)
        self.process = process
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Header: PID
        self.lbl_pid = QLabel(f"<b>{self.process.pid}</b>")
        self.lbl_pid.setAlignment(Qt.AlignCenter)
        self.lbl_pid.setStyleSheet("font-size: 14px;")
        
        # Details
        details_font = QFont("Arial", 9)
        self.lbl_arrival = QLabel(f"Arr: {self.process.arrival_time}")
        self.lbl_burst = QLabel(f"Burst: {self.process.burst_time}")
        self.lbl_remain = QLabel(f"Rem: {self.process.remaining_time}")
        
        for lbl in [self.lbl_arrival, self.lbl_burst, self.lbl_remain]:
            lbl.setFont(details_font)
            lbl.setAlignment(Qt.AlignCenter)
            
        layout.addWidget(self.lbl_pid)
        layout.addWidget(self.lbl_arrival)
        layout.addWidget(self.lbl_burst)
        layout.addWidget(self.lbl_remain)
        
        if self.process.priority > 0:
            self.lbl_priority = QLabel(f"Pri: {self.process.priority}")
            self.lbl_priority.setFont(details_font)
            self.lbl_priority.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.lbl_priority)
            
        self.setLayout(layout)
        self.update_style()

    def update_style(self):
        state = self.process.state.value
        colors = {
            "New": "#4d4d4d",
            "Ready": "#007acc",
            "Running": "#28a745",
            "Waiting": "#ffc107",
            "Terminated": "#343a40"
        }
        text_color = "white" if state != "Waiting" else "black"
        bg_color = colors.get(state, "#4d4d4d")
        border = "2px solid white" if state == "Running" else "1px solid #555"
        
        self.setStyleSheet(f"""
            ProcessCard {{
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
            }}
        """)

class QueuePanel(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QueuePanel {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 10px;
            }
        """)
        
        main_layout = QVBoxLayout()
        self.title_lbl = QLabel(f"<b>{title.upper()}</b>")
        self.title_lbl.setStyleSheet("color: #888; font-size: 11px; padding-left: 5px;")
        main_layout.addWidget(self.title_lbl)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container_layout = QHBoxLayout()
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        self.container_layout.setAlignment(Qt.AlignLeft)
        self.container.setLayout(self.container_layout)
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)
        self.setLayout(main_layout)

    def clear(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_process(self, process):
        self.container_layout.addWidget(ProcessCard(process))

class MetricsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(250)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            MetricsPanel {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 10px;
            }
            QLabel {
                font-size: 13px;
                padding: 2px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("<b>DASHBOARD METRICS</b>")
        title.setStyleSheet("color: #007acc; font-size: 16px; margin-bottom: 10px;")
        self.layout.addWidget(title)
        
        self.metrics = {}
        fields = [
            ("Time", "0"),
            ("Algorithm", "-"),
            ("Quantum", "-"),
            ("Completed", "0"),
            ("Avg Wait", "0.0"),
            ("Avg Turnaround", "0.0"),
            ("Avg Response", "0.0"),
            ("Context Switches", "0")
        ]
        
        for name, initial in fields:
            row = QHBoxLayout()
            lbl_name = QLabel(f"{name}:")
            lbl_name.setStyleSheet("color: #aaa;")
            lbl_val = QLabel(initial)
            lbl_val.setStyleSheet("color: white; font-weight: bold;")
            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_val)
            self.layout.addLayout(row)
            self.metrics[name] = lbl_val
            
        self.layout.addStretch()
        self.setLayout(self.layout)

    def update_metrics(self, state):
        self.metrics["Time"].setText(str(state["time"]))
        self.metrics["Algorithm"].setText(state["algorithm"])
        self.metrics["Quantum"].setText(str(state["time_quantum"]) if "time_quantum" in state else "-")
        self.metrics["Completed"].setText(str(len(state["terminated"])))
        self.metrics["Avg Wait"].setText(f"{state['avg_wait']:.2f}")
        self.metrics["Avg Turnaround"].setText(f"{state['avg_turnaround']:.2f}")
        self.metrics["Avg Response"].setText(f"{state['avg_response']:.2f}")
        self.metrics["Context Switches"].setText(str(state["context_switches"]))

class GanttBlock(QFrame):
    def __init__(self, pid, start, end, width):
        super().__init__()
        self.setFixedSize(width, 40)
        self.setStyleSheet(f"""
            background-color: #6f42c1;
            color: white;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            font-size: 10px;
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        lbl = QLabel(f"<b>{pid}</b>\n{start}-{end}")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        self.setLayout(layout)

class SchedulingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_simulation)
        self.sim_speed = 500
        
        self.init_ui()
        self.reset_simulation()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # --- 1. TOP CONTROL BAR ---
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #2d2d2d; border-radius: 8px;")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(15, 10, 15, 10)
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["FCFS", "Round Robin", "SJF", "Priority"])
        self.algo_combo.currentTextChanged.connect(self.on_algo_changed)
        top_layout.addWidget(QLabel("Algorithm:"))
        top_layout.addWidget(self.algo_combo)
        
        self.lbl_quantum = QLabel("Quantum:")
        self.spin_quantum = QSpinBox()
        self.spin_quantum.setRange(1, 20)
        self.spin_quantum.setValue(2)
        self.lbl_quantum.hide()
        self.spin_quantum.hide()
        top_layout.addWidget(self.lbl_quantum)
        top_layout.addWidget(self.spin_quantum)
        
        top_layout.addSpacing(20)
        
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setMinimumWidth(80)
        self.btn_play.clicked.connect(self.play_simulation)
        
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.clicked.connect(self.pause_simulation)
        
        self.btn_step = QPushButton("⏯ Step")
        self.btn_step.clicked.connect(self.step_simulation)
        
        self.btn_reset = QPushButton("↺ Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)
        
        for btn in [self.btn_play, self.btn_pause, self.btn_step, self.btn_reset]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3e3e42;
                    color: white;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #505050; border-color: #007acc; }
                QPushButton:pressed { background-color: #007acc; }
            """)
            top_layout.addWidget(btn)
            
        top_layout.addSpacing(30)
        top_layout.addWidget(QLabel("<b>Simulator Speed:</b>"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setFixedWidth(150)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(1000)
        self.speed_slider.setInvertedAppearance(True) # Lower ms = faster
        self.speed_slider.valueChanged.connect(self.update_speed)
        top_layout.addWidget(self.speed_slider)
        
        top_layout.addStretch()
        top_bar.setLayout(top_layout)
        main_layout.addWidget(top_bar)
        
        # --- 2. MIDDLE AREA (Queues + Metrics) ---
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(25)
        
        # Left side: Queues
        left_sim_layout = QVBoxLayout()
        left_sim_layout.setSpacing(15)
        self.panel_incoming = QueuePanel("Incoming Processes")
        self.panel_ready = QueuePanel("Ready Queue (Waiting)")
        
        # CPU Area
        cpu_container = QVBoxLayout()
        cpu_container.setContentsMargins(0, 10, 0, 10)
        cpu_container.setAlignment(Qt.AlignCenter)
        
        self.cpu_frame = QFrame()
        self.cpu_frame.setFixedSize(220, 160)
        self.cpu_frame.setStyleSheet("""
            background-color: #1e1e1e;
            border: 2px dashed #444;
            border-radius: 20px;
        """)
        self.cpu_layout = QVBoxLayout()
        self.cpu_layout.setAlignment(Qt.AlignCenter)
        self.cpu_label = QLabel("CPU IDLE")
        self.cpu_label.setStyleSheet("color: #444; font-size: 20px; font-weight: bold;")
        self.cpu_layout.addWidget(self.cpu_label)
        self.cpu_frame.setLayout(self.cpu_layout)
        
        cpu_container.addWidget(QLabel("<b>PROCESSOR CORE</b>"), 0, Qt.AlignCenter)
        cpu_container.addWidget(self.cpu_frame, 0, Qt.AlignCenter)
        
        self.panel_terminated = QueuePanel("Completed Processes")
        
        left_sim_layout.addWidget(self.panel_incoming)
        left_sim_layout.addWidget(self.panel_ready)
        left_sim_layout.addLayout(cpu_container)
        left_sim_layout.addWidget(self.panel_terminated)
        
        middle_layout.addLayout(left_sim_layout, 7)
        
        # Right side: Metrics
        self.metrics_panel = MetricsPanel()
        middle_layout.addWidget(self.metrics_panel, 3)
        
        main_layout.addLayout(middle_layout)
        
        # --- 3. BOTTOM AREA (Gantt + Log) ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Gantt
        gantt_container = QVBoxLayout()
        gantt_container.addWidget(QLabel("<b>TIMELINE: LIVE GANTT CHART</b>"))
        self.gantt_scroll = QScrollArea()
        self.gantt_scroll.setWidgetResizable(True)
        self.gantt_scroll.setFixedHeight(100)
        self.gantt_scroll.setStyleSheet("background-color: #1a1a1a; border: 1px solid #3e3e42; border-radius: 8px;")
        
        self.gantt_inner = QWidget()
        self.gantt_layout = QHBoxLayout()
        self.gantt_layout.setSpacing(0)
        self.gantt_layout.setAlignment(Qt.AlignLeft)
        self.gantt_inner.setLayout(self.gantt_layout)
        self.gantt_scroll.setWidget(self.gantt_inner)
        gantt_container.addWidget(self.gantt_scroll)
        
        # Log
        log_container = QVBoxLayout()
        log_container.addWidget(QLabel("<b>EVENT LOG</b>"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(80)
        self.log_output.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            border: 1px solid #3e3e42;
            border-radius: 5px;
        """)
        log_container.addWidget(self.log_output)
        
        bottom_layout.addLayout(gantt_container, 6)
        bottom_layout.addLayout(log_container, 4)
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)

    def on_algo_changed(self, algo):
        if algo == "Round Robin":
            self.lbl_quantum.show()
            self.spin_quantum.show()
        else:
            self.lbl_quantum.hide()
            self.spin_quantum.hide()
        self.reset_simulation()

    def update_speed(self, value):
        self.sim_speed = value
        if self.timer.isActive():
            self.timer.start(self.sim_speed)

    def play_simulation(self):
        self.timer.start(self.sim_speed)
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(True)

    def pause_simulation(self):
        self.timer.stop()
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)

    def reset_simulation(self):
        self.timer.stop()
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(False)
        
        algo = self.algo_combo.currentText()
        quantum = self.spin_quantum.value()
        
        processes = get_sample_processes()
        self.engine = SimulationEngine(processes, algo, quantum)
        
        self.log_output.clear()
        self.log_output.append(f"Simulation Reset: {algo}")
        self.update_visuals(self.engine.get_state())

    def step_simulation(self):
        if not self.engine.is_finished():
            state = self.engine.tick()
            self.update_visuals(state)
        else:
            self.pause_simulation()
            self.log_output.append("Simulation Complete.")

    def update_visuals(self, state):
        # Update Panels
        self.panel_incoming.clear()
        for p in state['unarrived']: self.panel_incoming.add_process(p)
        
        self.panel_ready.clear()
        for p in state['ready_queue']: self.panel_ready.add_process(p)
        
        self.panel_terminated.clear()
        for p in state['terminated']: self.panel_terminated.add_process(p)
        
        # Update CPU
        while self.cpu_layout.count():
            item = self.cpu_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if state['running']:
            self.cpu_frame.setStyleSheet("background-color: #1e1e1e; border: 3px solid #28a745; border-radius: 15px;")
            self.cpu_layout.addWidget(ProcessCard(state['running']))
        else:
            self.cpu_frame.setStyleSheet("background-color: #1e1e1e; border: 2px dashed #555; border-radius: 15px;")
            self.cpu_label = QLabel("CPU IDLE")
            self.cpu_label.setStyleSheet("color: #555; font-size: 18px; font-weight: bold;")
            self.cpu_layout.addWidget(self.cpu_label)
            
        # Update Metrics
        self.metrics_panel.update_metrics(state)
        
        # Update Gantt
        while self.gantt_layout.count():
            item = self.gantt_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for block in state['gantt_chart']:
            duration = block['end'] - block['start']
            width = max(50, duration * 25)
            self.gantt_layout.addWidget(GanttBlock(block['pid'], block['start'], block['end'], width))
            
        # Update Log
        current_text = self.log_output.toPlainText()
        new_events = state['event_log'][len(current_text.split('\n'))-1:]
        for event in new_events:
            self.log_output.append(event)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
