class ContextBuilder:
    def __init__(self, info_text, memory_manager):
        self.info_text = info_text
        self.memory_manager = memory_manager

    def build_system_prompt(self):
        return """You are an AI agent that has full control over a computer.
You can interact with the system using various actions.
Your goal is to assist the user by performing tasks on their machine.

Available Actions:
- move_to(x, y): Move the mouse to absolute coordinates (x, y).
- left_click(x=None, y=None): Left click at current position or at (x, y).
- right_click(x=None, y=None): Right click at current position or at (x, y).
- drag(start_x, start_y, end_x, end_y, button='left'): Drag from start to end coordinates.
- type_text(text): Type the provided text.
- press_key(key): Press a specific key (e.g., 'enter', 'tab', 'esc').
- hotkey(*keys): Press a combination of keys (e.g., 'ctrl', 'c').
- screenshot(): Take a screenshot of the current screen.
- add_to_high_memory(content): Save important information to persistent memory (max 10 items).

Response Format:
You MUST respond with a valid JSON object containing the next action to take.
Example: {{"action": "left_click", "params": {{"x": 100, "y": 200}}}}
If you need to wait or have finished, you can use a "wait" or "finish" action (though not explicitly implemented in control, you can suggest it).
Actually, stick to the implemented actions.

Current Machine Information:
{info_text}

{memory_context}
"""

    def get_full_prompt(self, current_observation=None):
        memory_context = self.memory_manager.get_full_context_string()
        system_prompt = self.build_system_prompt().format(
            info_text=self.info_text,
            memory_context=memory_context
        )

        prompt = f"{system_prompt}\n\nCurrent Observation: {current_observation or 'No observation available.'}\n\nNext Action (JSON):"
        return prompt
