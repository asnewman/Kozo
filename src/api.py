# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import requests

# Class for executing API calls to Robinhood or to the test API
class API:
    baseUrl = 'https://api.robinhood.com'
    urls = {
        'login': baseUrl + '/api-token-auth/username',
        'quotes': baseUrl + '/quotes/',
        'accounts': baseUrl + '/accounts/',
        'orders': baseUrl + '/orders/',
        'instruments': baseUrl + '/instruments/',
        'markets': baseUrl + '/markets/'
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
            })

    # Return the list of markets that include links to hours
    def market_hours(self):
        req = requests.get(self.urls['markets'])
        links = []

        # Only checking for NSYE and NASDAQ for now
        for market in req.json()["results"]:
            if market["mic"] == "XNAS" or market["mic"] == "XNYS":
                links.append(market["todays_hours"])

        return links
