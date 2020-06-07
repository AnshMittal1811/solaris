from multiprocessing import Pool
def _parallel_compute_function(x):
    return (x[0])(*(x[1]))()
verbose = 0


class PipeSegment:
    def __init__(self):
        self.feeder = None
        self.procout = None
        self.procstart = False
        self.procfinish = False
    def __call__(self):
        if self.procstart and not self.procfinish:
            raise Exception('(!) Circular dependency in workflow.')
        if not self.procfinish:
            self.procstart = True
            if 
            self.procout = self.process()
            self.procfinish = True
        return self.procout
    def process(self):
        pin = self.feeder()
        self.printout(pin)
        return self.transform(pin)
    def transform(self, pin):
        return pin
    def reset(self):
        self.procout = None
        self.procstart = False
        self.procfinish = False
        self.feeder.reset()
    def printout(*args):
        if verbose >= 1:
            print(type(self))
        if verbose >= 2:
            print(vars(self))
        if verbose >= 3:
            for x in args:
                print(x)
        if verbose >= 2:
            print()
    def selfstring(self, offset=0):
        return ' '*2*offset + type(self).__name__ + '\n'
    def __str__(self, offset=0):
        return self.selfstring(offset) + self.feeder.__str__(offset+1)
    def attach_check(self, ps):
        if not self.attach(ps):
            raise Exception('(!) ' + type(self).__name__
                            + ' has no free input at which to attach '
                            + type(ps).__name__ + '.')
    def attach(self, ps):
        if self.feeder is None:
            self.feeder = ps
            return True
        else:
            return self.feeder.attach(ps) or ps is self
    def __mul__(self, other):
        other.attach_check(self)
        return other
    def __or__(self, other):
        other.attach_check(self)
        return other
    def __add__(self, other):
        return MergeSegment(self, other)
    def __rmul__(self, other):
        return LoadSegment(other) * self
    def __ror__(self, other):
        return LoadSegment(other) * self
    @classmethod
    def parallel(cls, inputargs, processes=None):
        allinputs = list(zip([cls]*len(inputargs),inputargs))
        with Pool(processes) as pool:
            return pool.map(_parallel_compute_function, allinputs)


class LoadSegment(PipeSegment):
    def __init__(self, source=None):
        super().__init__()
        self.source = source
    def process(self):
        self.printout()
        self.load()
    def load(self):
        return self.source
    def reset(self):
        self.procout = None
        self.procstart = False
        self.procfinish = False
    def __str__(self, offset=0):
        return self.selfstring(offset)
    def attach(self, ps):
        return ps is self


class MergeSegment(PipeSegment):
    def __init__(self, feeder1, feeder2):
        super().__init__()
        self.feeder1 = feeder1
        self.feeder2 = feeder2
    def process(self):
        p1 = self.feeder1()
        p2 = self.feeder2()
        self.printout(p1, p2)
        if not isinstance(p1, tuple):
            p1 = (p1,)
        if not isinstance(p2, tuple):
            p2 = (p2,)
        return p1 + p2
    def reset(self):
        self.procout = None
        self.procstart = False
        self.procfinish = False
        self.feeder1.reset()
        self.feeder2.reset()
    def __str__(self, offset=0):
        return self.selfstring(offset) \
            + self.feeder1.__str__(offset+1) \
            + self.feeder2.__str__(offset+1)
    def attach(self, ps):
        if self.feeder1 is None:
            self.feeder1 = ps
            flag1 = True
        else:
            flag1 = self.feeder1.attach(ps)
        if self.feeder2 is None:
            self.feeder2 = ps
            flag2 = True
        else:
            flag2 = self.feeder2.attach(ps)
        return flag1 or flag2 or ps is self


class Identity(PipeSegment):
    """
    This class is an alias for the PipeSegment base class to emphasize
    its role as the identity element (i.e., output = input).
    """
    pass


class SelectItem(PipeSegment):
    """
    Given an iterable, return one of its items.  This can be used to select
    a single output from a class that returns a tuple of outputs.
    """
    def __init__(self, index=0):
        super().__init__()
        self.index = index
    def transform(self, pin):
        return pin[self.index]


class ReturnEmpty(PipeSegment):
    """
    Regardless of input, returns an empty tuple.
    Used in Map and Conditional classes.
    """
    def transform(self, pin):
        return ()


class PipeArgs(PipeSegment):
    """
    Wrapper for any PipeSegment subclass which enables it to accept
    initialization arguments from piped input.
    """
    def __init__(self, inner_class, *args, **kwargs):
        super().__init__()
        self.inner_class = inner_class
        self.args = args
        self.kwargs = kwargs
    def transform(self, pin):
        if issubclass(self.inner_class, LoadSegment):
            isloadsegment = True
            argstart = 0
        else:
            isloadsegment = False
            argstart = 1
            inner_pin = pin[0]
        # Gather all initialization arguments
        args = self.args
        kwargs = self.kwargs.copy()
        pargs = (pin if isinstance(pin, tuple) else (pin,))[argstart:]
        for p in pargs:
            if isinstance(p, dict):
                kwargs.update(p)
            else:
                args = args + (p,)
        #Initialize and call object
        obj = self.inner_class(*args, **kwargs)
        if isloadsegment:
            return obj()
        else:
            return (inner_pin * obj)()


class FunctionPipe(PipeSegment):
    """
    Turns a user-supplied function into a PipeSegment
    """
    def __init__(self, function):
        super().__init()
        self.function = function
    def transform(self, pin):
        return self.function(pin)


def PipeFunction(inner_class=PipeSegment, pin=(), *args, **kwargs):
    """
    Turns a PipeSegment into a standalone function.
    inner_class is the PipeSegment class, pin is the input to pipe into it,
    and *args and **kwargs are sent to the PipeSegment's constructor.
    """
    psobject = inner_class(*args, **kwargs)
    if issubclass(self.inner_class, LoadSegment):
        return psobject()
    else:
        return (pin * psobject)()
