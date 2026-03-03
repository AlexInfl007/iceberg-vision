class EventBus:

    def __init__(self):
        self.listeners = []

    def register(self, callback):
        self.listeners.append(callback)

    def unregister(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    async def emit(self, event):
        stale = []

        for listener in self.listeners:
            try:
                await listener(event)
            except Exception:
                stale.append(listener)

        for listener in stale:
            self.unregister(listener)
