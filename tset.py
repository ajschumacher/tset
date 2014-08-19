from datetime import datetime, timedelta
microsec = timedelta(microseconds=1)

class tset:

    def __init__(self, value=None, when=None, data=None):
        if data is not None:
            self.data = data # no checking!
            return
        else:
            self.data = dict()
        self.set(set(), datetime.min) # everything starts from nothing
        if value is not None or when is not None:
            self.set(value, when)

    def set(self, value, when=None):
        """
        Declare a known value of the set as of a specified time, or now.

        No return value (returns None).

        Parameters
        ----------
        value : set or iterable
        when : datetime (set to datetime.now() if None)
        """
        if when is None:
            when = datetime.now()
        if type(when) != datetime:
            raise TypeError("must be a datetime")
        if value is None:
            value = set()
        else:
            value = set(value)
        if 0 == len(self.data): # single checkpoint at origin
            content = {'type': 'checkpoint',
                       'value': value}
            self.data[when] = content
        else:
            later = min(filter(lambda then: when < then, self.data.keys()) or [None])
            if later is not None:
                next = self.get(later)
                adds = next - value
                dels = value - next
                content = {'type': 'changes',
                           'adds': adds,
                           'dels': dels}
                self.data[later] = content
            base = self.get(when)
            adds = value - base
            dels = base - value
            content = {'type': 'changes',
                       'adds': adds,
                       'dels': dels}
            self.data[when] = content

    def get(self, when=None, just_value=True):
        """
        Get the set's value as of a specified time, or now.
        Optionally also get the datetime of the returned update.

        Returns a set, or a (set, datetime) tuple with just_value=False.

        Parameters
        ----------
        when : datetime (set to datetime.now() if None)
        just_value : if False, return only the set value;
                     if True, also return the as-of time of
                     the update returned
        """
        if when is None:
            when = datetime.now()
        best = max(filter(lambda then: then <= when, self.data.keys()))
        content = self.data[best]
        if content['type'] == 'checkpoint':
            if just_value:
                return content['value']
            else:
                return content['value'], best
        else:
            value = ((self.get(best - microsec)
                      | content['adds'])
                      - content['dels'])
            if just_value:
                return value
            else:
                return value, best
            return value, best

    def __repr__(self):
        return self.get().__repr__()
