class EventBus:

    def __init__(self):
        self.listeners = []

    def register(self, callback):
        self.listeners.append(callback)

    async def emit(self, event):
        for listener in self.listeners:
            await listener(event)