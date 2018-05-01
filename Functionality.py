class Container(object):

    def __init__(self, wrapped_list):

        self._wl = wrapped_list

    def __repr__(self):
        return self._wl[0].__class__.__bases__[0].__name__ + 'Container'

    def __call__(self):
        return self._wl

    # allow no filtering
    # remove keys where entire value list is nans
    def to_dict(self,  attributes='all', filts='all'):

        filt_dict = {d: [] for x in self._wl for d in (x.__dict__.keys())}
        if (attributes != 'all') and (filts != 'all'):
            types = {e[attributes] for e in self._wl}

        for x in self._wl:
            if (filts != 'all') and (str(filts) in types or
                                     set(filts).issubset(set(types))):
                if (x[attributes] != filts and x[attributes] not in filts):
                    pass
                else:
                    for k in filt_dict.keys():
                        try:
                            filt_dict[k].append(x.__dict__[k])
                        except KeyError:
                            filt_dict[k].append(float('nan'))
            elif (filts == 'all') and (attributes == 'all'):
                for k in filt_dict.keys():
                        try:
                            filt_dict[k].append(x.__dict__[k])
                        except KeyError:
                            filt_dict[k].append(float('nan'))

        return filt_dict
