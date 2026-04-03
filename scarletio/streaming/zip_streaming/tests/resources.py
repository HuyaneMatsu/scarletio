__all__ = ()


class AsyncGenerator:
    __slots__ = ('data_chunks',)
    
    def __new__(cls, data_chunks):
        self = object.__new__(cls)
        self.data_chunks = data_chunks
        return self
    
    
    async def __aiter__(self):
        for data_chunk in self.data_chunks:
            yield data_chunk
    
    
    def get_data_size(self):
        return sum(len(data_chunk) for data_chunk in self.data_chunks)
