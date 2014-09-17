from tset import tset
from datetime import datetime, timedelta
import unittest

class TestCreation(unittest.TestCase):

    def test_creating_blank(self):
        t = tset()
        self.assertEqual(t.value(), set())
        self.assertEqual(t.value(just_value=False)[1], datetime.min)

    def test_creating_empty(self):
        t = tset(set())
        self.assertEqual(t.value(), set())
        self.assertNotEqual(t.value(just_value=False)[1], datetime.min)

    def test_creating_with_set(self):
        t = tset(set([1, 2, 3]))
        self.assertEqual(t.value(), set([1, 2, 3]))
        self.assertNotEqual(t.value(just_value=False)[1], datetime.min)

    def test_creating_with_list(self):
        t = tset([1, 2, 3])
        self.assertEqual(t.value(), set([1, 2, 3]))

    def test_creating_empty_at_time(self):
        time = datetime.now()
        t = tset(when=time)
        self.assertEqual(t.value(), set())
        self.assertEqual(t.value(just_value=False), (set(), time))

class TestEdges(unittest.TestCase):

    def test_early_access(self):
        before = datetime.now()
        t = tset([1])
        self.assertEqual(t.value(at=before), set())
        self.assertEqual(t.value(at=before, just_value=False)[1], datetime.min)

    def test_time_must_be_time(self):
        t = tset()
        with self.assertRaises(TypeError):
            t.value(set(), 'now')

class TestReturns(unittest.TestCase):

    def test_returns_set(self):
        t = tset()
        self.assertIs(type(t.value()), set)

    def test_returns_set_and_datetime(self):
        t = tset()
        response = t.value(just_value=False)
        self.assertEqual(len(response), 2)
        self.assertIs(type(response[0]), set)
        self.assertIs(type(response[1]), datetime)

class TestUpdates(unittest.TestCase):

    def test_single_growing_update(self):
        t = tset([1])
        between = datetime.now()
        t.value([1, 2, 3])
        self.assertEqual(t.value(at=between), set([1]))
        self.assertEqual(t.value(), set([1, 2, 3]))

    def test_single_shrinking_update(self):
        t = tset([1, 2, 3])
        between = datetime.now()
        t.value([1])
        self.assertEqual(t.value(at=between), set([1, 2, 3]))
        self.assertEqual(t.value(), set([1]))

    def test_single_complex_update(self):
        t = tset([1, 2])
        between = datetime.now()
        t.value([1, 3])
        self.assertEqual(t.value(at=between), set([1, 2]))
        self.assertEqual(t.value(), set([1, 3]))

    def test_future_update(self):
        week = timedelta(days=7)
        t = tset()
        t.value([1, 2, 3], datetime.now() + week)
        self.assertEqual(t.value(), set())
        self.assertEqual(t.value(at=datetime.now() + 2*week), set([1, 2, 3]))

    def test_past_update(self):
        one = datetime.now()
        two = datetime.now()
        three = datetime.now()
        t = tset([1, 2, 3])
        t.value([3, 4], two)
        # didn't change the present
        self.assertEqual(t.value(), set([1, 2, 3]))
        # didn't change beginning of time
        self.assertEqual(t.value(at=one), set())
        # change in place at time
        self.assertEqual(t.value(at=two), set([3, 4]))
        # and chronologically
        self.assertEqual(t.value(at=three), set([3, 4]))

    def test_intermediate_change_works_correctly(self):
        one = datetime.now()
        t = tset([1, 2, 3])
        two = datetime.now()
        three = datetime.now()
        four = datetime.now()
        t.value([3, 4, 5])
        five = datetime.now()
        t.value([2, 3, 4], three)
        # final value still in place at time five
        self.assertEqual(t.value(at=five), set([3, 4, 5]))
        # and now
        self.assertEqual(t.value(), set([3, 4, 5]))
        # land before time still fine
        self.assertEqual(t.value(at=one), set())
        # initial value not messed with
        self.assertEqual(t.value(at=two), set([1, 2, 3]))
        # value we put in is there
        self.assertEqual(t.value(at=three), set([2, 3, 4]))
        # value we put in is kept there until later change
        self.assertEqual(t.value(at=four), set([2, 3, 4]))


if __name__ == '__main__':
    unittest.main()
