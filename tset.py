from datetime import datetime, timedelta
microsec = timedelta(microseconds=1)

class Tset(object):
    """
    Time sets maintain the states of a set data structure over time.
    """

    def __init__(self, value=None, at=None, data=None):
        if data is not None:
            if value is not None or at is not None:
                raise ValueError("`data` must be only argument")
            self.data = data # no checking!
            return
        self.data = dict()
        self.value(set(), at=datetime.min) # everything starts from nothing
        if value is None and at is None:
            return # no information in the Tset
        if value is None:
            value = set() # specfied `at` but not value; starts empty here
        self.value(value, at=at) # `at` will get defaulted to now if need be

    def _assign(self, value, at=None):
        """
        Declare a known value of the set as of a specified time, or now.

        No return value (returns None).

        Parameters
        ----------
        value : set or iterable
        at : datetime (defaults to datetime.now() if None)
        """
        if at is None:
            at = datetime.now()
        if type(at) != datetime:
            raise TypeError("must be a datetime")
        if value is None:
            value = set()
        else:
            value = set(value)
        if 0 == len(self.data): # single checkpoint at origin
            content = {'value': value}
            self.data[at] = content
        else:
            later = min(filter(lambda then: at < then, self.data.keys()) or [None])
            if later is not None:
                next = self.value(at=later)
                adds = next - value
                dels = value - next
                content = {'adds': adds,
                           'dels': dels}
                self.data[later] = content
            base = self.value(at=at)
            adds = value - base
            dels = base - value
            content = {'adds': adds,
                       'dels': dels}
            self.data[at] = content

    def _access(self, at=None, just_value=True):
        """
        Get the set's value as of a specified time, or now.
        Optionally also get the datetime of the returned update.

        Returns a set, or a (set, datetime) tuple with just_value=False.

        Parameters
        ----------
        at : datetime (defaults to datetime.now() if None)
        just_value : if False, return only the set value;
                     if True, also return the as-of time of
                     the update returned
        """
        if at is None:
            at = datetime.now()
        best = max(filter(lambda then: then <= at, self.data.keys()))
        content = self.data[best]
        if 'value' in content:
            if just_value:
                return content['value']
            else:
                return content['value'], best
        else:
            value = ((self.value(at=best - microsec)
                      | content['adds'])
                      - content['dels'])
            if just_value:
                return value
            else:
                return value, best
            return value, best

    def value(self, value=None, at=None, just_value=True):
        """
        Assign or access the value of the tset, as of a specified time, or now.

        Parameters
        ----------
        value : set or iterable
        at : datetime (defaults to datetime.now() if None)
        just_value : if False, return only the set value;
                     if True, also return the as-of time of
                     the update returned
        """
        if value is None:
            return self._access(at, just_value)
        else:
            return self._assign(value, at)

    def __repr__(self):
        return self.value().__repr__()
