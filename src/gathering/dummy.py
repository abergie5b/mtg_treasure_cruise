
class AsyncIter:
    def __init__(self, items):
        self._items = items

    async def __aiter__(self):
        for item in self._items:
            yield item

# Dummy Models
class _Price(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class _Card(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

