import random

class SyncEngine:
    def __init__(self, buffer_size: int = 5):
        self.buffer_size = buffer_size
        self.buffer = []
        
        self.mutex = True  # True = Unlocked, False = Locked
        self.mutex_owner = None
        
        self.empty_sem = buffer_size
        self.full_sem = 0
        
        self.producer_state = "IDLE" # IDLE -> WAITING_EMPTY -> WAITING_MUTEX -> IN_CS -> IDLE
        self.consumer_state = "IDLE" # IDLE -> WAITING_FULL -> WAITING_MUTEX -> IN_CS -> IDLE
        
        self.item_counter = 1
        self.event_log = []

    def log(self, msg: str):
        self.event_log.append(msg)

    def tick(self) -> dict:
        """
        Advances the simulation by 1 step. Randomly chooses to advance Producer or Consumer.
        """
        # Choose randomly who gets CPU time to simulate race/interleaving,
        # but favor the one that actually CAN make progress.
        choices = []
        if self.producer_state != "WAITING_EMPTY" or self.empty_sem > 0:
            choices.append("PRODUCER")
        if self.consumer_state != "WAITING_FULL" or self.full_sem > 0:
            choices.append("CONSUMER")
            
        if not choices:
            self.log("DEADLOCK OR COMPLETE STALL!")
            return self.get_state()
            
        turn = random.choice(choices)
        
        if turn == "PRODUCER":
            self._step_producer()
        else:
            self._step_consumer()
            
        return self.get_state()

    def _step_producer(self):
        if self.producer_state == "IDLE":
            self.producer_state = "WAITING_EMPTY"
            self.log("[Producer] Wants to produce. Checking empty slots...")
            
        elif self.producer_state == "WAITING_EMPTY":
            if self.empty_sem > 0:
                self.empty_sem -= 1
                self.producer_state = "WAITING_MUTEX"
                self.log("[Producer] Acquired empty slot. Waiting for Mutex...")
            else:
                self.log("[Producer] Blocked. No empty slots.")
                
        elif self.producer_state == "WAITING_MUTEX":
            if self.mutex:
                self.mutex = False
                self.mutex_owner = "Producer"
                self.producer_state = "IN_CS"
                self.log("[Producer] Acquired Mutex. Entering Critical Section.")
            else:
                self.log("[Producer] Blocked. Mutex is locked by Consumer.")
                
        elif self.producer_state == "IN_CS":
            # Produce
            item = f"Data_{self.item_counter}"
            self.item_counter += 1
            self.buffer.append(item)
            self.log(f"[Producer] Produced {item}.")
            
            # Release Mutex
            self.mutex = True
            self.mutex_owner = None
            self.log("[Producer] Released Mutex.")
            
            # Release Full
            self.full_sem += 1
            self.producer_state = "IDLE"
            self.log("[Producer] Signaled Full Semaphore. Returned to IDLE.")

    def _step_consumer(self):
        if self.consumer_state == "IDLE":
            self.consumer_state = "WAITING_FULL"
            self.log("[Consumer] Wants to consume. Checking full slots...")
            
        elif self.consumer_state == "WAITING_FULL":
            if self.full_sem > 0:
                self.full_sem -= 1
                self.consumer_state = "WAITING_MUTEX"
                self.log("[Consumer] Acquired full slot. Waiting for Mutex...")
            else:
                self.log("[Consumer] Blocked. No full slots available.")
                
        elif self.consumer_state == "WAITING_MUTEX":
            if self.mutex:
                self.mutex = False
                self.mutex_owner = "Consumer"
                self.consumer_state = "IN_CS"
                self.log("[Consumer] Acquired Mutex. Entering Critical Section.")
            else:
                self.log("[Consumer] Blocked. Mutex is locked by Producer.")
                
        elif self.consumer_state == "IN_CS":
            # Consume
            item = self.buffer.pop(0)
            self.log(f"[Consumer] Consumed {item}.")
            
            # Release Mutex
            self.mutex = True
            self.mutex_owner = None
            self.log("[Consumer] Released Mutex.")
            
            # Release Empty
            self.empty_sem += 1
            self.consumer_state = "IDLE"
            self.log("[Consumer] Signaled Empty Semaphore. Returned to IDLE.")

    def get_state(self) -> dict:
        return {
            "buffer": list(self.buffer),
            "buffer_size": self.buffer_size,
            "mutex": self.mutex,
            "mutex_owner": self.mutex_owner,
            "empty_sem": self.empty_sem,
            "full_sem": self.full_sem,
            "producer_state": self.producer_state,
            "consumer_state": self.consumer_state,
            "event_log": list(self.event_log)
        }
