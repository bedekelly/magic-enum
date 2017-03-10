from collections import namedtuple
params = namedtuple("params", "args kwargs")


class Mock:
    def __init__(self, spec=None):
        self.spec = spec
        self.return_value = None
        self.attributes = {}
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append(params(args, kwargs))
        return self.return_value
    
    @property
    def called(self):
        return bool(len(self.calls))

    def called_with(self, *args, **kwargs):
        return params(args, kwargs) in self.calls

    def __getattr__(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            attr_spec = None
            if self.spec is not None:
                attr_spec = getattr(self.spec, name)
            self.attributes[name] = Mock(attr_spec)
        return self.attributes[name]
