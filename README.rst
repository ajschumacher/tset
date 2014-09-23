====
tset
====

time set: all the states of a Python ``set`` data structure over time,
without storing every complete version, and with nice 'as-of' (``at``)
access.

Usage
-----

  from tset import Tset
  from datetime import datetime
  
  beginning = datetime.now()
  t = Tset(range(1,5))
  middle = datetime.now()
  t.value(range(3,8))
  
  t.value()
  {3, 4, 5, 6, 7}
  
  t.value(at=middle)
  {1, 2, 3, 4}
  
  t.value(at=beginning)
  {}

tests
-----

Run the tests with ``nosetests`` or ``python -m test``.
