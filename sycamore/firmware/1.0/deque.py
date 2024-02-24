# This is a modified version of deque from the Micropython stdlib
# https://github.com/micropython/micropython-lib/blob/7128d423c2e7c0309ac17a1e6ba873b909b24fcc/python-stdlib/collections-deque/collections/deque.py#L4
# Usage:
# Create a new deque, populated with zeros, max length 64:
#   newdeque = deque.deque(64, [0] * 64)
# Start to push values:
#   newdeque.push(42)
# Get the most recent value:
#   newdeque.get(0)
# Get the oldest value:
#   newdeque.get(63)
class deque:
    def __init__(self, maxLength: int, iterable=None):
        self.maxLen = maxLength
        if iterable is None:
            self.q = []
        else:
            self.q = list(iterable)

    # Filling from right to left, for external callers
    # we want to calculate the index of the newest (right-most)
    # to the oldest (left-most)
    def get(self, index):
        return self.q[self.maxLen - 1 - index]

    def popleft(self):
        return self.q.pop(0)

#    def popright(self):
#        return self.q.pop()

#    def pop(self):
#        return self.q.pop()

    # Combined popleft + append
    def push(self, a):
        self.popleft()
        self.append(a)

    def append(self, a):
        self.q.append(a)

#    def appendleft(self, a):
#        self.q.insert(0, a)

#    def extend(self, a):
#        self.q.extend(a)

    def __len__(self):
        return len(self.q)

    def __bool__(self):
        return bool(self.q)

    def __iter__(self):
        yield from self.q

    def __str__(self):
        return "deque({})".format(self.q)
