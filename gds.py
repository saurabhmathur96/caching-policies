"""lirs.py: Implements the Greedy Dual Size cache eviction policy."""
class GDSCache:
    """A cache that implments the GDS policy and uses an injected backing store
        Members:
            size: int
            H: dict of str->float, cost of eviction of each page
            L: float, lowest value in H
            C: float, parameter of the GDS policy
            cache : Dict or MemCache
    """
    def __init__(self, size, cache):
        self.size = size
        self.cache = cache
        self.H = {}
        self.L = 0
        self.C = 1

    def get(self, key):
        if key not in self.H:
            return None
        else:
            val = self.cache.get(key)
            self.H[key] = self.L + self.C / len(val)
        return val

    
    def put(self, _key, value):
        if _key in self.H:
            self.H[_key] = self.L + self.C / len(value)
        else:
            if len(self.H) == self.size:
                # retrieve min key
                min_key = min(self.H, key=self.H.get)
                # # retrieve min value
                self.L = self.H[min_key]
                # remove min key,value
                self.H.pop(min_key)
                self.cache.remove(min_key)
            # add new key, value
            self.H[_key] = self.L + self.C / len(value)
        self.cache.put(_key, value)
