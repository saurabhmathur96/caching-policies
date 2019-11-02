class LRUCache:
    """A cache that implments the LRU policy and uses an injected backing store
        Members:
            size: int
            keys: list
            cache : Dict or MemCache
    """
    def __init__(self, size, cache):
        self.size = size
        self.keys = [] 
        self.cache = cache
    
    def get(self, key):
        if key in self.keys:
            i = self.keys.index(key)
            del self.keys[i]
            self.keys.append(key)
            return self.cache.get(key)
        else:
            return None
            
    
    def put(self, key, value):
        if key in self.keys:
            i = self.keys.index(key)
            del self.keys[i]
        else:
            if len(self.keys) == self.size:
                self.cache.remove(self.keys[0])
                del self.keys[0]
                
        self.keys.append(key)
        self.cache.put(key, value)
