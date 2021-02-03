class VSConstResolver:
    def __init__(self):
        self.rev_lookup = {}
        self.const_lookup = {}

    def clearAll(self):
        self.rev_lookup = {}
        self.const_lookup = {}

    def addModule(self, mod):
        for name in dir(mod):
            val = getattr(mod, name)
            if type(val) is not int:
                continue

            # First lets add the "reverse" lookup
            revs = self.rev_lookup.get(val)
            if revs is None:
                revs = []
                self.rev_lookup[val] = revs
            revs.append(name)

            # Now the forward....
            self.const_lookup[name] = val

    def constLookup(self, name):
        return self.const_lookup.get(name)

    def revLookup(self, const):
        '''
        Lookup the possible names of a constant based on
        modules added with constAddModule()
        '''
        return self.rev_lookup.get(const)
