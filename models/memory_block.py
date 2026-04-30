from dataclasses import dataclass
from typing import Optional

@dataclass
class MemoryBlock:
    id: int
    size: int
    allocated_to: Optional[str] = None
    allocated_size: int = 0
    
    @property
    def is_free(self) -> bool:
        return self.allocated_to is None

    @property
    def fragmentation(self) -> int:
        """Internal fragmentation for this block"""
        if self.is_free:
            return 0
        return self.size - self.allocated_size
