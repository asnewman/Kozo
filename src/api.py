# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import requests

# Class for executing API calls to Robinhood or to the test API
class API:
    baseUrl = 'https://api.robinhood.com'
    urls = {
        'login': baseUrl + '/api-token-auth/username',
        'quote': baseUrl + '/quotes/',
        'account': baseUrl + '/accounts/',
        'order': baseUrl + '/orders/',
        'instrument': baseUrl + '/instruments/'
    }

    # Constructor that takes in whether the API class will be setup for testing
    # or not.
    def __init__(self, test=False):
        if test == True:
            self.baseUrl = 'http://localhost:5005/'

    # Logs in user
    def login(self, username, password):
        return requests.post(self.urls['login'], data = {
                'username': username,
                'password': password
            }
