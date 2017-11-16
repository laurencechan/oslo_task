from functools import wraps
def wrap(f):
    @wraps(f)
    def t(self):
        try:
            return f(self)
        finally:
            print self.id
    return t

class b(object):
    def __init__(self,id):
        self.id=id
    @wrap
    def update(self,):
        self.id=5


def test():
    b1=b(3)
    b1.update()

test()
