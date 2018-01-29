# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import unittest
import sys

sys.path.insert(0, '../src/')

from api import API

class TestAPI(unittest.TestCase):
    def __init__(self):
        with open('../credentials.txt', r) as f:
            self.username = f[0]
            self.password = f[1]
    
    def test_good_login(self):
        r = API().login(self.username, self.password)
        self.assertEqual(r.status_code, 200)
