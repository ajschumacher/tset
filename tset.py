from datetime import datetime


class Tset(object):
    """
    Time sets maintain the states of a set data structure over time.
    """

    def __init__(self, value=None, at=None):
        """
        Create Tset, optionally with value at a time (datetime).
        """
        self._data = dict()  # initialize empty
        if value is None and at is None:
            return  # no information in the Tset
        if value is None:
            value = set()  # specfied `at` but not value; starts empty here
        self.value(value, at)  # `at` will get defaulted to now if need be

    @classmethod
    def from_lists(cls, lists):
        """
        Create a Tset from data in plain list format.

        See `to_lists` for format details.
        """
        result = cls()
        for record in lists:
            if len(record) == 3:
                result._data[record[2]] = {'adds': set(record[0]),
                                           'dels': set(record[1])}
            else:
                result._data[record[1]] = {'value': set(record[0])}
        return result

    def to_lists(self):
        """
        Export the current internal data in plain lists.

        The return format is a list of lists. All but the last have
        three elements: a list of `adds`, a list of `dels`, and the
        `at` time. The last has two elements: a list of elements in
        the latest version of the set, and the `at` time for that
        state.

        Suitable for storage in systems with limited data structures.
        """
        times = sorted(self._data.keys())
        for time in times:
            if len(self._data[time]) == 2:
                yield [list(self._data[time]['adds']),
                       list(self._data[time]['dels']),
                       time]
            else:
                yield [list(self._data[time]['value']), time]

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
        times = self._data.keys()
        befores = filter(lambda time: time < at, times)
        if 1 <= len(befores):
            before = max(befores)
            before_value = self.value(at=before)
            self._data[before] = {'adds': before_value - value,
                                  'dels': value - before_value}
        afters = filter(lambda time: at < time, times)
        if 1 <= len(afters):
            after = min(afters)
            after_value = self.value(at=after)
            self._data[at] = {'adds': value - after_value,
                              'dels': after_value - value}
        else:
            self._data[at] = {'value': value}

    def __value_time(self, value, time, just_value):
        """
        Return either a value or a value and time.
        """
        if just_value:
            return value
        else:
            return value, time

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
        times = sorted(self._data.keys(), reverse=True)
        if len(times) == 0:
            return self.__value_time(set(), datetime.min, just_value)
        time = times.pop(0)
        value = self._data[time]['value']
        if time <= at:
            return self.__value_time(value, time, just_value)
        for time in times:
            value = ((value | self._data[time]['adds']) -
                     self._data[time]['dels'])
            if time <= at:
                return self.__value_time(value, time, just_value)
        return self.__value_time(set(), datetime.min, just_value)

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
        """
        Print current version to screen.
        """
        return self.value().__repr__()
