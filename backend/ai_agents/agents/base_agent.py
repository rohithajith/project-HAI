class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    async def process_message(self, message: str, state: dict) -> str:
        raise NotImplementedError("Subclasses must implement this method")