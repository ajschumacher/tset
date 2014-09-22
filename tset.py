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
            self._data = data # no checking!
            return
        self._data = dict() # initialize empty
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
        times = self._data.keys()
        if len(times) == 0:
            self._data[at] = {'value': value}
            return
        if at in times:
            raise ValueError('same-time updates not yet supported')
        times.sort()
        last_time = times[-1]
        if last_time < at:
            last_value = self._data[last_time].pop('value')
            self._data[at] = {'value': value}
            self._data[last_time]['adds'] = last_value - value
            self._data[last_time]['dels'] = value - last_value
            return
        first_time = times[0]
        if at < first_time:
            first_value = self.value(at=first_time)
            self._data[at] = {'adds': value - first_value,
                              'dels': first_value - value}
            return

    def __value_time(self, value, time, just_value):
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
            value = (value | self._data[time]['adds']) - self._data[time]['dels']
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
        return self.value().__repr__()
