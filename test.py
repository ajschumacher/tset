from tset import tset
from datetime import datetime, timedelta
import unittest

class TestCreation(unittest.TestCase):

    def test_creating_empty(self):
        t = tset()
        self.assertEqual(t.get(), set())

    def test_creating_with_set(self):
        t = tset(set([1, 2, 3]))
        self.assertEqual(t.get(), set([1, 2, 3]))

    def test_creating_with_list(self):
        t = tset([1, 2, 3])
        self.assertEqual(t.get(), set([1, 2, 3]))

    def test_creating_empty_at_time(self):
        time = datetime.now()
        t = tset(when=time)
        self.assertEqual(t.get(), set())
        self.assertEqual(t.get(just_value=False), (set(), time))

class TestEdges(unittest.TestCase):

    def test_early_access(self):
        before = datetime.now()
        t = tset([1])
        self.assertEqual(t.get(before), set())

class TestReturns(unittest.TestCase):

    def test_returns_set(self):
        t = tset()
        self.assertIs(type(t.get()), set)

    def test_returns_set_and_datetime(self):
        t = tset()
        response = t.get(just_value=False)
        self.assertEqual(len(response), 2)
        self.assertIs(type(response[0]), set)
        self.assertIs(type(response[1]), datetime)

class TestSetting(unittest.TestCase):

    def test_time_must_be_time(self):
        t = tset()
        with self.assertRaises(TypeError):
            t.set(set(), 'now')

    def test_single_growing_update(self):
        t = tset([1])
        between = datetime.now()
        t.set([1, 2, 3])
        self.assertEqual(t.get(between), set([1]))
        self.assertEqual(t.get(), set([1, 2, 3]))

    def test_single_shrinking_update(self):
        t = tset([1, 2, 3])
        between = datetime.now()
        t.set([1])
        self.assertEqual(t.get(between), set([1, 2, 3]))
        self.assertEqual(t.get(), set([1]))

    def test_single_complex_update(self):
        t = tset([1, 2])
        between = datetime.now()
        t.set([1, 3])
        self.assertEqual(t.get(between), set([1, 2]))
        self.assertEqual(t.get(), set([1, 3]))

    def test_future_update(self):
        week = timedelta(days=7)
        t = tset()
        t.set([1, 2, 3], datetime.now() + week)
        self.assertEqual(t.get(), set())
        self.assertEqual(t.get(datetime.now() + 2*week), set([1, 2, 3]))


if __name__ == '__main__':
    unittest.main()
