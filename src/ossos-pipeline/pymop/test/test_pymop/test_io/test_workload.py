__author__ = "David Rusk <drusk@uvic.ca>"

import unittest

from mock import MagicMock

from pymop.io.persistence import ProgressManager


class WorkloadFactoryTest(unittest.TestCase):
    def setUp(self):
        self.progress_manager = MagicMock(spec=ProgressManager)

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
