from collections import deque
import time

class ShortTermMemory:
    def __init__(self, maxlen=20):
        self.memory = deque(maxlen=maxlen)

    def add_event(self, event_type, content, metadata=None):
        entry = {
            "timestamp": time.time(),
            "event_type": event_type, # e.g., "action", "observation"
            "content": content,
            "metadata": metadata or {}
        }
        self.memory.append(entry)

    def get_recent(self, n):
        if n <= 0:
            return []
        items = list(self.memory)
        return items[-n:] if n < len(items) else items

    def get_all(self):
        return list(self.memory)

    def clear(self):
        self.memory.clear()
