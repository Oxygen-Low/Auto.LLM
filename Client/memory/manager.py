from .short_term import ShortTermMemory
from .high_memory import HighMemory
import time

class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.high_memory = HighMemory()

    def add_event(self, event_type, content, metadata=None):
        self.short_term.add_event(event_type, content, metadata)

    def add_to_high_memory(self, content, tags=None):
        return self.high_memory.add_memory(content, tags)

    def format_short_term_for_llm(self, n=10):
        events = self.short_term.get_recent(n)
        if not events:
            return "No recent events."

        formatted = "Recent Events:\n"
        for e in events:
            timestamp = time.strftime('%H:%M:%S', time.localtime(e['timestamp']))
            formatted += f"[{timestamp}] {e['event_type'].upper()}: {e['content']}\n"
        return formatted

    def format_high_memory_for_llm(self):
        memories = self.high_memory.get_all()
        if not memories:
            return "No persistent memories."

        formatted = "Persistent Memories:\n"
        for m in memories:
            m_id = m.get('id', 'unknown')
            content = m.get('content', 'no content')
            tags = m.get('tags') or []
            tags_str = ", ".join(map(str, tags))
            formatted += f"- [ID: {m_id}] {content} (Tags: {tags_str})\n"
        return formatted

    def get_full_context_string(self):
        return f"{self.format_high_memory_for_llm()}\n\n{self.format_short_term_for_llm()}"
