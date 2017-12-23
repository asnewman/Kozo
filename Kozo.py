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
      self.username = raw_input('Username: ')
      self.password = getpass.getpass('Password: ')
      self.login()
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
         elif command[0] == "buy" or command[0] =="b":
            if len(command) == 3:
               self.buy(command[1].upper(), command[2])
            else:
               print 'buy command must include and only include the ' 
               + 'symbol and amount'
         elif command[0] == "sell" or command[0] =="s":
            if len(command) == 3:
               self.sell(command[1].upper(), command[2])
            else:
               print 'sell command must include and only include the ' 
               + 'symbol and amount'
         elif command[0] == "tsl":
            if len(command) == 4:
               self.trailing_stoploss(command[1].upper(), command[2], float(command[3]))
            else:
               print 'tsl command must include and only include the ' 
               + 'symbol, amount, and price difference'
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
      print 'tsl [symbol] [amount] [price difference] - start trailing stoploss for a stock'
      print ''

   # Logs in user and sets the user's token
   # Returns True if the login is successful, otherwise false
   def login(self):
      r = requests.post(self.urls['login'], data={'username':self.username, 
         'password':self.password})

      # Check for successful login
      if r.status_code == 200:
         self.token = r.json()['token']

         r = requests.get(self.urls['account'], headers={'Authorization':'Token '+self.token})
         self.account_url = r.json()['results'][0]['url']

         print 'Log in successful'
         return True
      else:
         print 'Log in unsuccessful'
         return False

   # Prints the users profile (stocks held in the account)
   def profile(self):
      r = requests.get(
         self.account_url+'positions/', 
         headers={'Authorization':'Token '+self.token})
       
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
            self.urls['quote']+symbol+'/').json()['last_trade_price'])
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
      r = requests.get(self.urls['quote']+ticker+'/')
      price = float(r.json()['last_trade_price'])

      # Round the price of the stock to two decimals if 1.00 or over
      if price < 1:
         return price
      else:
         return round(price, 2)

   # Returns the price of the given ticker (used for testing while the market is closed)
   def get_test_quote(self, ticker):
      url = "http://localhost:3000/prices"
      r = requests.get(url)
      price = float(r.json()['current'])
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

      r = requests.post(self.urls['order'], headers={'Authorization':'Token '+self.token}, 
         data={'symbol':symbol, 'type':'market', 'trigger':'immediate', 
         'time_in_force':'gtc', 'quantity':amount, 'side':'buy', 'price':self.get_quote(symbol),
         'instrument':instrument, 'account':'https://api.robinhood.com/accounts/5SF74735/'})
      
      print amount + ' ' + symbol + ' shares bought'

   # Sells a specified stock at market price
   def sell(self, symbol, amount):
      instrument = self.get_instrument(symbol)

      # Don't do anything if the instrument isn't found
      if instrument == None:
         return

      r = requests.post(self.urls['order'], headers={'Authorization':'Token '+self.token}, 
         data={'symbol':symbol, 'type':'market', 'trigger':'immediate', 
         'time_in_force':'gtc', 'quantity':amount, 'side':'sell', 'price':self.get_quote(symbol),
         'instrument':instrument, 'account':'https://api.robinhood.com/accounts/5SF74735/'})

      print amount + ' ' + symbol + ' shares sold'

   # Returns the symbols instrument url
   def get_instrument(self, symbol):
      r = requests.get(self.urls['instrument'], params={'symbol':symbol})

      # Make sure symbol exists in Robinhood
      if len(r.json()['results']) == 0:
         print symbol + ' not valid or available'
         return None
      else:
         return r.json()['results'][0]['url']

   # Manually implements a trailing stop loss
   def trailing_stoploss(self, symbol, amount, price_diff):
      print 'Starting trailing stop loss for ' + symbol + ' will price difference of ' + str(price_diff)
   
      init_price = self.get_quote(symbol)
      # init_price = self.get_test_quote(symbol)
   
      trail_price = init_price - price_diff
    
      curr_price = self.get_quote(symbol)
      # curr_price = self.get_test_quote(symbol)


      while curr_price > trail_price:
         time.sleep(5)
         curr_price = self.get_quote(symbol)
         # curr_price = self.get_test_quote(symbol)

         table = PrettyTable(['Stock', 'Initial Price', 
         'Current Price', 'Trail Price'])

         table.add_row([symbol, init_price, curr_price, trail_price])
         print table

         if round(curr_price - trail_price, 2) > round(price_diff, 2):
            trail_price = curr_price - price_diff
            print 'Updating trail price'

      self.sell(symbol, amount)
      # print 'Selling ' + symbol






user = Kozo()
user.start()


















