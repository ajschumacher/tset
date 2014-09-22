from tset import Tset
from datetime import datetime, timedelta
import sys
import unittest

class TestCreation(unittest.TestCase):

    def test_creating_blank(self):
        tset = Tset()
        self.assertEqual(tset.value(), set())
        self.assertEqual(tset.value(just_value=False)[1], datetime.min)

    def test_creating_empty(self):
        tset = Tset(set())
        self.assertEqual(tset.value(), set())
        self.assertNotEqual(tset.value(just_value=False)[1], datetime.min)

    def test_creating_with_set(self):
        tset = Tset(set([1, 2, 3]))
        self.assertEqual(tset.value(), set([1, 2, 3]))
        self.assertNotEqual(tset.value(just_value=False)[1], datetime.min)

    def test_creating_with_list(self):
        tset = Tset([1, 2, 3])
        self.assertEqual(tset.value(), set([1, 2, 3]))

    def test_creating_empty_at_time(self):
        time = datetime.now()
        tset = Tset(at=time)
        self.assertEqual(tset.value(), set())
        self.assertEqual(tset.value(just_value=False), (set(), time))

class TestEdges(unittest.TestCase):

    def test_early_access(self):
        before = datetime.now()
        tset = Tset([1])
        self.assertEqual(tset.value(at=before), set())
        self.assertEqual(tset.value(at=before, just_value=False)[1], datetime.min)

    def test_time_must_be_time(self):
        tset = Tset()
        with self.assertRaises(TypeError):
            tset.value(set(), 'now')

class TestReturns(unittest.TestCase):

    def test_returns_set(self):
        tset = Tset()
        self.assertIs(type(tset.value()), set)

    def test_returns_set_and_datetime(self):
        tset = Tset()
        response = tset.value(just_value=False)
        self.assertEqual(len(response), 2)
        self.assertIs(type(response[0]), set)
        self.assertIs(type(response[1]), datetime)

class TestUpdates(unittest.TestCase):

    def test_single_growing_update(self):
        tset = Tset([1])
        between = datetime.now()
        tset.value([1, 2, 3])
        self.assertEqual(tset.value(at=between), set([1]))
        self.assertEqual(tset.value(), set([1, 2, 3]))

    def test_single_shrinking_update(self):
        tset = Tset([1, 2, 3])
        between = datetime.now()
        tset.value([1])
        self.assertEqual(tset.value(at=between), set([1, 2, 3]))
        self.assertEqual(tset.value(), set([1]))

    def test_single_complex_update(self):
        tset = Tset([1, 2])
        between = datetime.now()
        tset.value([1, 3])
        self.assertEqual(tset.value(at=between), set([1, 2]))
        self.assertEqual(tset.value(), set([1, 3]))

    def test_future_update(self):
        week = timedelta(days=7)
        tset = Tset()
        tset.value([1, 2, 3], datetime.now() + week)
        self.assertEqual(tset.value(), set())
        self.assertEqual(tset.value(at=datetime.now() + 2*week), set([1, 2, 3]))

    def test_past_update(self):
        one = datetime.now()
        two = datetime.now()
        three = datetime.now()
        tset = Tset([1, 2, 3])
        tset.value([3, 4], two)
        # didn't change the present
        self.assertEqual(tset.value(), set([1, 2, 3]))
        # didn't change beginning of time
        self.assertEqual(tset.value(at=one), set())
        # change in place at time
        self.assertEqual(tset.value(at=two), set([3, 4]))
        # and chronologically
        self.assertEqual(tset.value(at=three), set([3, 4]))

    def test_intermediate_change_works_correctly(self):
        one = datetime.now()
        tset = Tset([1, 2, 3])
        two = datetime.now()
        three = datetime.now()
        four = datetime.now()
        tset.value([3, 4, 5])
        five = datetime.now()
        tset.value([2, 3, 4, 6], three)
        # final value still in place at time five
        self.assertEqual(tset.value(at=five), set([3, 4, 5]))
        # and now
        self.assertEqual(tset.value(), set([3, 4, 5]))
        # land before time still fine
        self.assertEqual(tset.value(at=one), set())
        # initial value not messed with
        self.assertEqual(tset.value(at=two), set([1, 2, 3]))
        # value we put in is there
        self.assertEqual(tset.value(at=three), set([2, 3, 4, 6]))
        # value we put in is kept there until later change
        self.assertEqual(tset.value(at=four), set([2, 3, 4, 6]))

class TestSameTimeUpdates(unittest.TestCase):

    def test_single_same_time_update(self):
        one = datetime.now()
        tset = Tset([1, 2, 3], one)
        tset.value(['a'], one)
        self.assertEqual(tset.value(), set(['a']))

    def test_initial_same_time_update(self):
        one = datetime.now()
        tset = Tset([1, 2, 3], one)
        tset.value([2, 3, 4])
        tset.value(['a'], one)
        self.assertEqual(tset.value(), set([2, 3, 4]))

    def test_last_same_time_update(self):
        one = datetime.now()
        two = datetime.now()
        tset = Tset([1, 2, 3], two)
        three = datetime.now()
        four = datetime.now()
        tset.value([2, 3, 4], four)
        tset.value(['a'], four)
        self.assertEqual(tset.value(), set(['a']))
        self.assertEqual(tset.value(at=three), set([1, 2, 3]))

    def test_interposed_same_time_update(self):
        one = datetime.now()
        two = datetime.now()
        three = datetime.now()
        four = datetime.now()
        five = datetime.now()
        six = datetime.now()
        tset = Tset([1, 2, 3], two)
        tset.value([2, 3, 4], four)
        tset.value([3, 4, 5], six)
        tset.value(['a', 'b', 3], four)
        self.assertEqual(tset.value(at=one), set())
        self.assertEqual(tset.value(at=two), set([1, 2, 3]))
        self.assertEqual(tset.value(at=three), set([1, 2, 3]))
        self.assertEqual(tset.value(at=four), set(['a', 'b', 3]))
        self.assertEqual(tset.value(at=five), set(['a', 'b', 3]))
        self.assertEqual(tset.value(), set([3, 4, 5]))

class TestPerformance(unittest.TestCase):

    def test_not_limited_by_recursion_limit(self):
        n = sys.getrecursionlimit()
        one = datetime.now()
        two = datetime.now()
        tset = Tset([0], two)
        for i in range(1, n+11):
            tset.value([i])
        self.assertEqual(tset.value(at=one), set())
        self.assertEqual(tset.value(at=two), set([0]))
        self.assertEqual(tset.value(), set([n+10]))


if __name__ == '__main__':
    unittest.main()
