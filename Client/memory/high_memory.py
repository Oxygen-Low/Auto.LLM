import json
import os
import uuid
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class HighMemory:
    def __init__(self, storage_path="Client/memory/high_memory.json", limit=10):
        self.storage_path = Path(storage_path)
        self.limit = limit
        self.memories = self._load_memories()

    def _load_memories(self):
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.exception("Error loading high memory: %s", e)
            return []

    def _save_memories(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(self.memories, f, indent=4)
        except Exception as e:
            logger.exception("Error saving high memory: %s", e)

    def add_memory(self, content, tags=None):
        if len(self.memories) >= self.limit:
            raise ValueError(f"High memory limit reached ({self.limit} items). Please remove an item before adding a new one.")

        entry = {
            "id": str(uuid.uuid4()),
            "content": content,
            "created_timestamp": time.time(),
            "tags": tags or []
        }
        self.memories.append(entry)
        self._save_memories()
        return entry["id"]

    def remove_memory(self, memory_id):
        self.memories = [m for m in self.memories if str(m["id"]) != str(memory_id)]
        self._save_memories()

    def get_all(self):
        return self.memories.copy()

    def get_count(self):
        return len(self.memories)
