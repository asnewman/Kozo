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

    # Manually implements a trailing stop loss
    def trailing_stoploss(self, symbols, amounts, price_diffs):
        print 'Starting trailing stop losses'

        init_prices = []
        trail_prices = []
        curr_prices = []

        print symbols

        # Getting initial prices for symbols
        for symbol in symbols:
            init_prices.append(self.get_quote(symbol))
            # init_prices.append(self.get_test_quote(symbol))

        # Getting trailing prices for symbols
        cnt = 0
        for symbol in symbols:
            trail_prices.append(init_prices[cnt] - price_diffs[cnt])
            cnt += 1

        # Getting current prices for symbols
        cnt = 0
        for symbol in symbols:
            curr_prices.append(self.get_quote(symbols[cnt]))
            # curr_prices.append(self.get_test_quote(symbols[cnt]))
            cnt += 1

        # While there are symbols in the list
        while len(symbols) != 0:
            time.sleep(5)
            table = PrettyTable(['Symbol', 'Initial Price',
                                 'Current Price', 'Trail Price'])

            # Get current prices for symbols
            cnt = 0
            for symbol in symbols:
                curr_prices[cnt] = self.get_quote(symbol)
                # curr_prices[cnt] = self.get_test_quote(symbol)

                table.add_row([symbol, init_prices[cnt], curr_prices[cnt],
                               trail_prices[cnt]])

                if round(curr_prices[cnt] - trail_prices[cnt], 2) \
                > round(price_diffs[cnt], 2):
                    trail_prices[cnt] = curr_prices[cnt] - price_diffs[cnt]
                    print 'Updating ' + symbol + ' trail price'

                if round(curr_prices[cnt], 2) <= round(trail_prices[cnt], 2):
                    print time.ctime()
                    print table
                    self.sell(symbol, amounts[cnt])
                    # print 'Selling ' + symbol
                    symbols.pop(cnt)
                    init_prices.pop(cnt)
                    curr_prices.pop(cnt)
                    trail_prices.pop(cnt)
                    amounts.pop(cnt)
                    price_diffs.pop(cnt)
                    break

                cnt += 1

    # Gets a lists of symbols, amounts, and price differences for
    # trailing stoploss
    def multi_tsl(self):
        symbols = []
        amounts = []
        price_diffs = []

        while True:
            symbols.append((raw_input('Symbol: ')).upper())
            amounts.append(float(raw_input('Amount: ')))
            price_diffs.append(float(raw_input('Price Difference: ')))

            if raw_input('Add more? [yes/no] ') != 'yes':
                break

        self.trailing_stoploss(symbols, amounts, price_diffs)

    # Schedules a buy order with a price constraint
    def scheduled_buy(self, symbol, amount, price, direction):
        cron = CronTab(user=True)
        # only working for my directory
        # please change the directory path to be relevant for your system
        command = "python " + os.path.dirname(os.path.realpath(__file__)) + \
            "/scheduled_buy.py " + str(self.username) + " " + \
            str(self.password) + " " + str(symbol) + " " + str(amount) + \
            " " + str(price) + " " + str(direction) # \
            # Going to send output to email for now, make sure sendmail is configured
            # + " >> " + os.path.dirname(os.path.realpath(__file__)) + "/scheduled_buy.log"
        job = cron.new(command=command)

        # getting tomorrow's date
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        job.minute.on(59)
        job.hour.on(15)
        job.day.on(tomorrow.day)
        job.month.on(tomorrow.month)

        cron.write()
        print "Buy scheduled for " + amount + " shares of " + symbol + \
              " " + direction + " " + price + " at 12:59PM PST"
