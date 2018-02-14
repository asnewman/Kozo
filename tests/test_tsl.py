# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import unittest
import os
import src.tsl as tsl

class TestTSL(unittest.TestCase):
    # validate_order tests
    # =========================================================================
    def test_validate_good_order(self):
        order = ["AMD", "5", "0.31", "21.32"]
        self.assertTrue(tsl.validate_order(order))

    def test_validate_bad_order_incorrect_item_amount(self):
        order = ["AMD", "5" ".21"]
        self.assertFalse(tsl.validate_order(order))

    def test_validate_bad_order_amount(self):
        order = ["AMD", "five", "0.20", "321.21"]
        self.assertFalse(tsl.validate_order(order))

    def test_validate_bad_order_price(self):
        order = ["AMD", "5", "twenty", "32.21"]
        self.assertFalse(tsl.validate_order(order))

    def test_validate_bad_order_negative_amount(self):
        order = ["AMD", "-5", ".2", "23.1"]
        self.assertFalse(tsl.validate_order(order))

    def test_validate_bad_order_negative_price(self):
        order = ["AMD", "5", "2.14", "-201.32"]
        self.assertFalse(tsl.validate_order(order))

    def test_validate_bad_order_negative_price(self):
        order = ["AMD", "5", "2.14", "-201.32"]
        self.assertFalse(tsl.validate_order(order))
    
    # get_orders test
    # =========================================================================
    TEST_FILE = "test_tsl_orders.data"

    def create_test_file(self):
        # Delete if the test file already exists
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)
        
    def delete_test_file(self):
        os.remove(self.TEST_FILE)

    def test_get_orders_good(self):
        self.create_test_file()
        
        with open(self.TEST_FILE, "w") as tsl_file:
            tsl_file.write("amd 5 .20 11.30\n")
            tsl_file.write("nvda 2 .49 140.23")

        expected = [["amd", 5, .20, 11.30], ["nvda", 2, .49, 140.23]]

        self.assertEqual(tsl.get_orders(self.TEST_FILE), expected)
        
        self.delete_test_file()

    def test_get_orders_one_good_one_bad(self):
        self.create_test_file()
        
        with open(self.TEST_FILE, "w") as tsl_file:
            tsl_file.write("amd 5 .20 11.30\n")
            tsl_file.write("nvda two .49, 12.30")

        expected = [["amd", 5, .20, 11.30]]

        self.assertEqual(tsl.get_orders(self.TEST_FILE), expected)

    def test_get_orders_bad(self):
        self.create_test_file()
        
        with open(self.TEST_FILE, "w") as tsl_file:
            tsl_file.write("amd five .20, 13.20\n")
            tsl_file.write("nvda 5 -.20, 120.30\n")
            
        self.assertEqual(tsl.get_orders(self.TEST_FILE), [])

    def test_get_orders_bad2(self):
        self.create_test_file()
        
        with open(self.TEST_FILE, "w") as tsl_file:
            tsl_file.write("amd 5 .20, thirty\n")
            tsl_file.write("nvda 5 .20, five\n")
            
        self.assertEqual(tsl.get_orders(self.TEST_FILE), [])

if __name__ == '__main__':
    unittest.main()


























