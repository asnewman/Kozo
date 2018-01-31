# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import unittest
import sys

from src.api import API

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Must have a file with valid Robinhood credentials
        # Currently the account must not have MFA
        with open('./tests/credentials.txt') as f:
            data = f.readlines()
            self.username = data[0]
            self.password = data[1]
    
    def test_good_login(self):
        r = API().login(self.username, self.password)
        self.assertEqual(r.status_code, 200)
