from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QTextEdit
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from sync.engine import SyncEngine

class SyncTab(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = SyncEngine(buffer_size=5)
        self.timer = QTimer()
        self.timer.timeout.connect(self.step_simulation)
        
        self.init_ui()
        self.update_visuals(self.engine.get_state())

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- 1. CONTROLS BAR ---
        controls_layout = QHBoxLayout()
        
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_simulation)
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_simulation)
        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.step_simulation)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_simulation)
        
        for btn in [self.btn_play, self.btn_pause, self.btn_step, self.btn_reset]:
            controls_layout.addWidget(btn)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # --- 2. ENTITIES (Producer & Consumer) ---
        entities_layout = QHBoxLayout()
        
        # Producer Card
        self.gb_producer = QFrame()
        self.gb_producer.setFrameShape(QFrame.Box)
        prod_layout = QVBoxLayout()
        self.lbl_prod_title = QLabel("<b>PRODUCER</b>")
        self.lbl_prod_title.setAlignment(Qt.AlignCenter)
        self.lbl_prod_state = QLabel("IDLE")
        self.lbl_prod_state.setAlignment(Qt.AlignCenter)
        self.lbl_prod_state.setStyleSheet("color: #17a2b8; font-size: 16px; font-weight: bold;")
        prod_layout.addWidget(self.lbl_prod_title)
        prod_layout.addWidget(self.lbl_prod_state)
        self.gb_producer.setLayout(prod_layout)
        entities_layout.addWidget(self.gb_producer)
        
        # Consumer Card
        self.gb_consumer = QFrame()
        self.gb_consumer.setFrameShape(QFrame.Box)
        cons_layout = QVBoxLayout()
        self.lbl_cons_title = QLabel("<b>CONSUMER</b>")
        self.lbl_cons_title.setAlignment(Qt.AlignCenter)
        self.lbl_cons_state = QLabel("IDLE")
        self.lbl_cons_state.setAlignment(Qt.AlignCenter)
        self.lbl_cons_state.setStyleSheet("color: #fd7e14; font-size: 16px; font-weight: bold;")
        cons_layout.addWidget(self.lbl_cons_title)
        cons_layout.addWidget(self.lbl_cons_state)
        self.gb_consumer.setLayout(cons_layout)
        entities_layout.addWidget(self.gb_consumer)
        
        main_layout.addLayout(entities_layout)
        
        # --- 3. LOCKS & SEMAPHORES ---
        locks_layout = QHBoxLayout()
        
        self.lbl_empty = QLabel("Empty Slots: 5")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.setStyleSheet("background-color: #3e3e42; padding: 10px; border-radius: 5px;")
        
        self.lbl_mutex = QLabel("MUTEX: UNLOCKED")
        self.lbl_mutex.setAlignment(Qt.AlignCenter)
        self.lbl_mutex.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        
        self.lbl_full = QLabel("Full Slots: 0")
        self.lbl_full.setAlignment(Qt.AlignCenter)
        self.lbl_full.setStyleSheet("background-color: #3e3e42; padding: 10px; border-radius: 5px;")
        
        locks_layout.addWidget(self.lbl_empty)
        locks_layout.addWidget(self.lbl_mutex)
        locks_layout.addWidget(self.lbl_full)
        
        main_layout.addLayout(locks_layout)
        
        # --- 4. SHARED BUFFER ---
        main_layout.addWidget(QLabel("<b>Shared Memory Buffer</b>"))
        self.layout_buffer = QHBoxLayout()
        self.layout_buffer.setAlignment(Qt.AlignLeft)
        gb_buffer = QFrame()
        gb_buffer.setLayout(self.layout_buffer)
        gb_buffer.setFixedHeight(100)
        main_layout.addWidget(gb_buffer)
        
        # --- 5. EVENT LOG ---
        main_layout.addWidget(QLabel("<b>Event Log</b>"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)
        
        self.setLayout(main_layout)

    def play_simulation(self):
        self.timer.start(800)

    def pause_simulation(self):
        self.timer.stop()

    def reset_simulation(self):
        self.timer.stop()
        self.engine = SyncEngine(buffer_size=5)
        self.log_output.clear()
        self.log_output.append("--- Simulation Reset ---")
        self.update_visuals(self.engine.get_state())

    def step_simulation(self):
        state = self.engine.tick()
        self.update_visuals(state)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_visuals(self, state):
        # Update Entity States
        self.lbl_prod_state.setText(state['producer_state'].replace('_', ' '))
        if state['producer_state'] == "IN_CS":
            self.gb_producer.setStyleSheet("background-color: #17a2b8; color: white; border: 2px solid white;")
        else:
            self.gb_producer.setStyleSheet("background-color: transparent;")
            
        self.lbl_cons_state.setText(state['consumer_state'].replace('_', ' '))
        if state['consumer_state'] == "IN_CS":
            self.gb_consumer.setStyleSheet("background-color: #fd7e14; color: white; border: 2px solid white;")
        else:
            self.gb_consumer.setStyleSheet("background-color: transparent;")
            
        # Update Locks
        self.lbl_empty.setText(f"Empty Sem: {state['empty_sem']}")
        self.lbl_full.setText(f"Full Sem: {state['full_sem']}")
        
        if state['mutex']:
            self.lbl_mutex.setText("MUTEX: UNLOCKED")
            self.lbl_mutex.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        else:
            self.lbl_mutex.setText(f"MUTEX: LOCKED ({state['mutex_owner']})")
            self.lbl_mutex.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
            
        # Update Buffer
        self._clear_layout(self.layout_buffer)
        for i in range(state['buffer_size']):
            val = state['buffer'][i] if i < len(state['buffer']) else "Empty"
            lbl = QLabel(val)
            lbl.setFixedSize(80, 60)
            lbl.setAlignment(Qt.AlignCenter)
            if val == "Empty":
                lbl.setStyleSheet("background-color: #2d2d2d; border: 2px dashed gray; border-radius: 5px;")
            else:
                lbl.setStyleSheet("background-color: #007acc; color: white; border-radius: 5px; font-weight: bold;")
            self.layout_buffer.addWidget(lbl)
            
        # Update Log
        current_log_count = len(self.log_output.toPlainText().split('\n')) - 1
        if len(state['event_log']) > current_log_count - 1:
            self.log_output.clear()
            self.log_output.append("--- Synchronization Event Log ---")
            for msg in state['event_log']:
                self.log_output.append(msg)
            self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
