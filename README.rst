====
tset
====

time set: all the states of a Python ``set`` data structure over time,
without storing every complete version, and with nice 'as-of' (``at``)
access.

Implementation: Currently stores the most recent version completely,
so accessing the most recent version is not too slow. Accessing older
versions is slower because it walks through the history. The whole
thing will eventually slow down when there are tons of versions
because it goes through all the version times fairly naively.


Usage
-----

::

  > from tset import Tset
  > from datetime import datetime

  > beginning = datetime.now()
  > t = Tset(range(1,5))
  > middle = datetime.now()
  > t.value(range(3,8))

  > t.value()
  # {3, 4, 5, 6, 7}

  > t.value(at=middle)
  # {1, 2, 3, 4}

  > t.value(at=beginning)
  # {}


Tests
-----

Run the tests with ``nosetests`` or ``python -m test``.


Context
-------

The idea of preserving data history is not unique. There is a
considerable work on `persistent data structures`_ (which is quite
distinct from the idea of persisting data to disk). Interesting
related (and more comprehensive) implementations include `ZODB`_'s
`Generational Sets`_, `dat`_, and `Datomic`_.

.. _persistent data structures: http://en.wikipedia.org/wiki/Persistent_data_structure
.. _ZODB: http://www.zodb.org/
.. _Generational Sets: https://github.com/zc/generationalset
.. _dat: http://dat-data.com/
.. _Datomic: http://www.datomic.com/
