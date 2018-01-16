import requests
import getpass
import time
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

    # Starts and sets up the program
    def start(self):
        # Loop until successful login
        loggedin = False
        while loggedin == False:
            self.username = raw_input('Username: ')
            self.password = getpass.getpass('Password: ')
            loggedin = self.login()
        self.get_commands()

    # Gets commands from the user
    def get_commands(self):
        print("Enter 'help' for a list of commands")
        command = raw_input("Command: ")
        command = command.split()

        while True:
            if command[0] == "help":
                self.print_help()
            elif command[0] == "profile" or command[0] == "p":
                self.profile()
            elif command[0] == "quote" or command[0] == "q":
                if len(command) == 2:
                    self.quote(command[1].upper())
                else:
                    print 'ticker not given'
            elif command[0] == "buy" or command[0] == "b":
                if len(command) == 3:
                    self.buy(command[1].upper(), command[2])
                else:
                    print 'buy command must include and only include the '
                    + 'symbol and amount'
            elif command[0] == "sell" or command[0] == "s":
                if len(command) == 3:
                    self.sell(command[1].upper(), command[2])
                else:
                    print 'sell command must include and only include the '
                    + 'symbol and amount'
            elif command[0] == "tsl":
                self.multi_tsl()
            elif command[0] == "quit":
                exit(0)
            command = raw_input("Command: ")
            command = command.split()

    # Prints all of the available commands
    def print_help(self):
        print ''
        print 'profile, p - get information about currently held stocks'
        print 'quote, q [symbol] - get information about a stock'
        print 'buy, b [symbol] [amount] - purchase a stock at market price'
        print 'sell, s [symbol] [amount] - purchase a stock at market price'
        print 'tsl - start trailing stoploss for stocks'
        print ''

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
                                'price': self.get_quote(symbol),
                                'instrument': instrument, 
                                'account': self.account_url})

        print amount + ' ' + symbol + ' shares bought'

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
                                'price': self.get_quote(symbol),
                                'instrument': instrument, 
                                'account': self.account_url})

        print str(amount) + ' ' + symbol + ' shares sold'

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

                if round(curr_prices[cnt] - trail_prices[cnt], 2) 
                > round(price_diffs[cnt], 2):
                    trail_prices[cnt] = curr_prices[cnt] - price_diffs[cnt]
                    print 'Updating ' + symbol + ' trail price'

                if round(curr_prices[cnt], 2) <= round(trail_prices[cnt], 2):
                    # print 'SELLING'
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

            print table

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


user = Kozo()
user.start()
