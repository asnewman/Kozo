# =============================================================================
# Created by asnewman (Ashley Newman)
# =============================================================================

import requests
import datetime
import time
import os
from crontab import CronTab
from prettytable import PrettyTable


class Kozo:
    account_url = None
    username = None
    password = None
    token = None

    urls = {
        'login': 'https://api.robinhood.com/api-token-auth/username',
        'quote': 'https://api.robinhood.com/quotes/',
        'account': 'https://api.robinhood.com/accounts/',
        'order': 'https://api.robinhood.com/orders/',
        'instrument': 'https://api.robinhood.com/instruments/'
    }

    # Setter for the username
    def set_username(self, new_username):
        self.username = new_username

    # Setter for the password
    def set_password(self, new_password):
        self.password = new_password

    # Logs in user and sets the user's token
    # Returns True if the login is successful, otherwise false
    def login(self):
        r = requests.post(self.urls['login'], data={'username': self.username,
                                                    'password': self.password})

        # Check for successful login
        if r.status_code == 200:
            self.token = r.json()['token']

            r = requests.get(self.urls['account'], headers={
                             'Authorization': 'Token ' + self.token})
            self.account_url = r.json()['results'][0]['url']

            print 'Log in successful'
            return True
        else:
            print 'Log in unsuccessful'
            return False

    # Prints the users profile (stocks held in the account)
    def profile(self):
        r = requests.get(
            self.account_url + 'positions/',
            headers={'Authorization': 'Token ' + self.token})

        # Gather all of the items with quantity over 0
        holding = []
        for res in r.json()['results']:
            if float(res['quantity']) > 0:
                holding.append(res)

        table = PrettyTable(['stock', 'quantity', 'average price',
                             'current price', 'total price', 'gain'])
        for h in holding:
            symbol = requests.get(h['instrument']).json()['symbol']
            quantity = float(h['quantity'])
            avgPrice = float(h['average_buy_price'])
            currPrice = float(requests.get(
                self.urls['quote'] + symbol + '/').json()['last_trade_price'])
            gain = currPrice * quantity - avgPrice * quantity
            table.add_row([symbol, quantity, avgPrice, currPrice,
                           quantity * currPrice, gain])
        print table

    # Prints the given tickers current stock price
    def quote(self, ticker):
        # Create output table
        table = PrettyTable(['stock', 'price'])
        table.add_row([ticker, self.get_quote(ticker)])
        print table

    # Returns the price of the given ticker
    def get_quote(self, ticker):
        ticker = ticker.upper()
        r = requests.get(self.urls['quote'] + ticker + '/')
        price = float(r.json()['last_trade_price'])

        # Round the price of the stock to two decimals if 1.00 or over
        if price < 1:
            return price
        else:
            return round(price, 2)

    # Returns the price of the given ticker 
    # (used for testing while the market is closed)
    def get_test_quote(self, ticker):
        url = "http://localhost:3000/prices"
        r = requests.get(url)
        price = float(r.json()[ticker])
        if price < 1:
            return price
        else:
            return round(price, 2)

    # Buys a specified stock at market price
    def buy(self, symbol, amount):
        instrument = self.get_instrument(symbol)

        # Don't do anything if the instrument isn't found
        if instrument == None:
            return

        r = requests.post(self.urls['order'], 
                          headers={'Authorization': 'Token ' + self.token},
                          data={'symbol': symbol, 
                                'type': 'market', 
                                'trigger': 'immediate',
                                'time_in_force': 'gtc', 
                                'quantity': amount, 
                                'side': 'buy', 
                                'price': round(self.get_quote(symbol) * 1.05, 2),
                                'instrument': instrument, 
                                'account': self.account_url})

        if r.status_code == 201:
            print amount + ' ' + symbol + ' shares bought'
        else:
            print "error"

    # Sells a specified stock at market price
    def sell(self, symbol, amount):
        instrument = self.get_instrument(symbol)

        # Don't do anything if the instrument isn't found
        if instrument == None:
            return

        r = requests.post(self.urls['order'], 
                          headers={'Authorization': 'Token ' + self.token},
                          data={'symbol': symbol, 
                                'type': 'market', 
                                'trigger': 'immediate',
                                'time_in_force': 'gtc', 
                                'quantity': amount, 
                                'side': 'sell', 
                                'price': round(self.get_quote(symbol) * .95, 2),
                                'instrument': instrument, 
                                'account': self.account_url})

        if r.status_code == 201:
            print str(amount) + ' ' + symbol + ' shares sold'
        else:
            print "error"

    # Returns the symbols instrument url
    def get_instrument(self, symbol):
        r = requests.get(self.urls['instrument'], params={'symbol': symbol})

        # Make sure symbol exists in Robinhood
        if len(r.json()['results']) == 0:
            print symbol + ' not valid or available'
            return None
        else:
            return r.json()['results'][0]['url']

    # Schdules trailing stoplosses by writing to orders.data
    def trailing_stoploss(self):
        path = "orders.data"
        tsls = []
        

        ticker = raw_input("Ticker: ").upper()
        amount = raw_input("Amount: ")
        trail_amount = raw_input("Trail Amount: ")
        curr_trail = self.get_quote(ticker) - float(trail_amount)

        with open(path, "a") as orders_file:
            orders_file.write(ticker + " " +\
                              amount + " " +\
                              trail_amount + " " +\
                              str(curr_trail) + "\n")

        print "Trailing " + ticker + " of amount " + amount +\
              " at a trail of " + trail_amount + "."

    # Schedules a buy order with a price constraint
    def scheduled_buy(self):
        symbol = raw_input("Symbol: ").upper()
        amount = raw_input("Amount: ")
        price = raw_input("Price: ")
        direction = raw_input("Direction (above/below): ")
        date = raw_input("Date (mm/dd): ").split("/")

        month = int(date[0])
        day = int(date[1])

        cron = CronTab(user=True)
        # only working for my directory
        # please change the directory path to be relevant for your system
        command = "python " + os.path.dirname(os.path.realpath(__file__)) + \
            "/scheduled_buy.py " + str(self.username) + " " + \
            str(self.password) + " " + str(symbol) + " " + str(amount) + \
            " " + str(price) + " " + str(direction) # \
        job = cron.new(command=command)

        job.minute.on(59)
        job.hour.on(12)
        job.day.on(day)
        job.month.on(month)

        cron.write()
        print "Buy scheduled for " + amount + " shares of " + symbol + \
              " " + direction + " " + price + " at 12:59PM PST on " +\
              str(month) + "/" + str(day)
