import unittest
import sys

sys.path.insert(0, '../src/')

import scheduled_buy as sb

class TestScheduledBuy(unittest.TestCase):
    def test_good_args(self):
        args = ["", "user", "password", "amd", "10", "12.42", "above"]
        self.assertTrue(sb.validate_args(args))
    
    def test_bad_amount_number(self):
        args = ["", "user", "password", "amd", "12.41", "12.42", "above"]
        self.assertFalse(sb.validate_args(args))

    def test_bad_amount_string(self):
        args = ["", "user", "password", "amd", "bob", "13.23", "above"]
        self.assertFalse(sb.validate_args(args))

    def test_bad_price(self):
        args = ["", "user", "password", "amd", "10", "bob", "above"]
        self.assertFalse(sb.validate_args(args))

    def test_good_args_below(self):
        args = ["", "user", "password", "amd", "13", "12.14", "below"]
        self.assertTrue(sb.validate_args(args))

    def test_bad_direction(self):
        args = ["", "user", "password", "amd", "13", "12.14", "bob"]
        self.assertFalse(sb.validate_args(args))

if __name__ == '__main__':
    unittest.main()
