"""lirs.py: Implements the Least Inter-Reference Recency Set cache eviction policy."""
class Stack:
    """A FIFO Stack (As described in paper)"""
    
    def __init__(self):
        self.data = []
    
    def push(self, item):
        self.data.append(item)
    
    def pop(self):
        if len(self.data) == 0:
            return None
        
        value, *rest = self.data
        self.data = rest
        return value
    
    def peek(self):
        if len(self.data) == 0:
            return None
        value, *_ = self.data
        return value

    def remove(self, value, key):
        # key = function item -> typeof(value)

        matches = [(i, item) for i, item in enumerate(self.data) if key(item) == value]
        if len(matches) == 0:
            # print ("Not found")
            return None
        index, item = matches[0]

        del self.data[index]
        return item
    
    def is_empty(self):
        return len(self.data) == 0


NR = 0
HIRS = 1
LIRS = 2

status = ["NR", "HIRS", "LIRS"]

class Item:
    """Items to to saved in Stack.

        Members:
            value : str
            status : int 
        
        0 = Non-Resident
        1 = High Inter-Reference Recency Set
        2 = Low Inter-Reference Recency Set
        """
    def __init__(self, value, status):
        self.value = value
        self.status = status




class LIRSCache:
    """A cache that implements the LIRS policy and uses an injected backing store
        Members:
            S : Stack
            Q : Stack
            size: int
            max_hirs : int
            max_lirs : int
            cache : Dict or MemCache
    """
    def __init__(self, size, cache):
        self.S = Stack()
        self.Q = Stack()
        self.size = size
        
        self.max_hirs = max(1, 0.1 * self.size)
        self.max_lirs = self.size - self.max_hirs

        self.cache = cache
    
    
    def put(self, key, value):
        item = self.S.remove(key,  key=lambda x: x.value)
        if item is not None:
            # Found in S

            if item.status == HIRS:
                # Remove from Q
                self.Q.remove(key,  key=lambda x: x.value)

                self.evict()
                item.status = LIRS
                self.migrate()
                
        
            elif item.status == NR:
                # Miss
                
                item.status = LIRS
                self.evict()
                self.migrate()
                
            
            self.prune_S()
            self.S.push(item)
            # insert into cache
            self.cache.put(key, value)
            return

        item = self.Q.remove(key,  key=lambda x: x.value)
        if item is not None:
            # found in Q
            self.Q.push(item)

            self.prune_S()
            # insert into cache
            self.cache.put(key, value)
            return
        
        # Not found anywhere
        lirs_count = len([item for item in self.S.data if item.status == LIRS])
        
        if lirs_count < self.max_lirs:
            item = Item(key, LIRS)
        else:
            item = Item(key, HIRS)
            self.evict()
            self.Q.push(item)
        self.S.push(item)

        self.prune_S()
        # insert into cache
        self.cache.put(key, value)

    def get(self, key):
        
        item = self.S.remove(key,  key=lambda x: x.value)
        if item is not None:
            if item.status == NR:
                # Miss
                return None
            else:
                # Found in S
                if item.status == LIRS:
                    self.S.push(item)
                
                else:
                    # status=HIRS
                    self.Q.remove(key,  key=lambda x: x.value)
                    item.status = LIRS
                    self.S.push(item)
                    self.migrate()
                
                self.prune_S()
                return self.cache.get(key)
        

        item = self.Q.remove(key,  key=lambda x: x.value)
        if item is not None:
            # found in Q
            self.Q.push(item)

            self.prune_S()
            # insert into cache
            
            return self.cache.get(key)
        
        return None
    def prune_S(self):
        while not self.S.is_empty():
            if self.S.peek().status == LIRS:
                break
            else:
                item = self.S.pop()
                
                self.Q.remove(item.value, key=lambda x: x.value)
                if item.status == HIRS: 
                    
                    self.cache.remove(item.value)

    def evict(self):
        
       
        count = len(set([item.value for item in self.S.data if item.status == HIRS] + [item.value for item in self.Q.data]))
        
        
        if count < self.max_hirs:
            
            return
        
        victim = self.Q.pop()
        
        
        self.S.remove(victim.value, key=lambda x: x.value)
        # remove from cache
        key = victim.value
        self.cache.remove(key)
        
        victim.status = NR
        self.S.push(victim)
        
    def migrate(self):
        bottom = self.S.pop()
        bottom.status = HIRS
        # self.evict()
        self.Q.push(bottom)



def print_stack(stack):
    print (",".join(["%s %s" % (item.value, status[item.status]) for item in stack.data]))
        
