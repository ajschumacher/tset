# tset

time sets; some kind of persistent set data structure
with litle regard for access performance

### example

```
> from tset import tset
> from datetime import datetime

> beginning = datetime.now()
> t = tset(range(1,5))
> middle = datetime.now()
> t.set(range(3,8))

> t.get()
# {3, 4, 5, 6, 7}

> t.get(middle)
# {1, 2, 3, 4}

> t.get(beginning)
# {}
```
