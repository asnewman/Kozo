import requests
import getpass
import sys
import time
from prettytable import PrettyTable

# logs in user and returns the user's token
def login(username, password):
    url = 'https://api.robinhood.com/api-token-auth/username'
    r = requests.post(url, data={'username':username, 
        'password':password})
    if r.status_code == 200:
        print 'log in successful!'
        return r.json()['token']
    else:
        print 'log in unsuccessful'
        exit(1)

# prints all of the available commands
def printHelp():
    print "profile, p - get information about currently held stocks"
    print "quote, q [symbol] - get information about a stock"
    print "buy, b [symbol] [amount] - purchase a stock at market price"
    print "sell, s [symbol] [amount] - purchase a stock at market price"
    print "tsl [symbol] [amount] [price difference] - start trailing stoploss for a stock"


# buys a specified stock at market price
def buy(token, symbol, amount):
    instrument = get_instrument(symbol)

    if instrument == None:
        return

    url = 'https://api.robinhood.com/orders/'
    r = requests.post(url, headers={'Authorization':'Token '+token}, 
        data={'symbol':symbol, 'type':'market', 'trigger':'immediate', 
        'time_in_force':'gtc', 'quantity':amount, 'side':'buy', 'price':get_quote(symbol),
        'instrument':instrument, 'account':'https://api.robinhood.com/accounts/5SF74735/'})
    print r.text
    print amount + ' ' + symbol + ' shares bought'

# returns the symbols instrument url
def get_instrument(symbol):
    url = 'https://api.robinhood.com/instruments/'
    r = requests.get(url, params={'symbol':symbol})

    # make sure symbol exists in Robinhood
    if len(r.json()['results']) == 0:
        print symbol + ' not valid or available'
        return None
    else:
        return r.json()['results'][0]['url']

# sells a specified stock at market price
def sell(token, symbol, amount):
    instrument = get_instrument(symbol)

    if instrument == None:
        return

    url = 'https://api.robinhood.com/orders/'
    r = requests.post(url, headers={'Authorization':'Token '+token}, 
        data={'symbol':symbol, 'type':'market', 'trigger':'immediate', 
        'time_in_force':'gtc', 'quantity':amount, 'side':'sell', 'price':get_quote(symbol),
        'instrument':instrument, 'account':'https://api.robinhood.com/accounts/5SF74735/'})
    print r.text
    print amount + ' ' + symbol + ' shares sold'

# manually implements a trailing stop loss
def trailing_stoploss(token, symbol, amount, price_diff):    
    print 'Starting trailing stop loss for ' + symbol + ' will price difference of ' + str(price_diff)
   
    init_price = get_quote(symbol)
    #init_price = get_test_quote(symbol)
   
    trail_price = init_price - price_diff
    
    curr_price = get_quote(symbol)
    #curr_price = get_test_quote(symbol)


    while curr_price > trail_price:
        #curr_price = get_quote(symbol)
        curr_price = get_test_quote(symbol)

        print 'Initial price: ' + str(init_price)
        print 'Current price: ' + str(curr_price)
        print 'Trail price ' + str(trail_price)

        if round(curr_price - trail_price, 2) > round(price_diff, 2):
            trail_price = curr_price - price_diff
            print 'Updating trail price'
        print '----------------------'
        time.sleep(5)

    sell(token, symbol, amount)
    #print 'Selling ' + symbol


# prints the users profile (stocks held in the account)
def profile(token):
    url = 'https://api.robinhood.com/accounts/'
    r = requests.get(
            'https://api.robinhood.com/accounts/5SF74735/positions/', 
            headers={'Authorization':'Token '+token})
    
    # Gather all of the items with quantity over 0
    holding = []
    for res in r.json()['results']:
        if float(res['quantity']) > 0:
            holding.append(res)

    table = PrettyTable(['stock', 'quantity', 
        'average price', 'current price', 'total price', 'gain'])
    for h in holding:
        symbol = requests.get(h['instrument']).json()['symbol']
        quantity = float(h['quantity'])
        avgPrice = float(h['average_buy_price'])
        currPrice = float(requests.get(
            'https://api.robinhood.com/quotes/'+symbol+'/').json()\
                    ['last_trade_price'])
        gain = currPrice * quantity - avgPrice * quantity
        table.add_row([symbol, quantity, avgPrice, currPrice, 
            quantity * currPrice, gain])

    print table

# prints the given tickers current stock price
def quote(ticker):
    print "looking up " + ticker
    url = "https://api.robinhood.com/quotes/"
    r = requests.get(url+ticker+'/')
    table = PrettyTable(['stock', 'price'])
    table.add_row([ticker, get_quote(ticker)])
    print table

# returns the price of the given ticker
def get_quote(ticker):
    url = "https://api.robinhood.com/quotes/"
    r = requests.get(url+ticker+'/')
    price = float(r.json()['last_trade_price'])
    if price < 1:
        return price
    else:
        return round(price, 2)

# returns the price of the given ticker (used for testing while the market is closed)
def get_test_quote(ticker):
    url = "http://localhost:3000/prices"
    r = requests.get(url)
    price = float(r.json()['current'])
    if price < 1:
        return price
    else:
        return round(price, 2)


def main():
    username = raw_input("username: ")
    # password = getpass.getpass("password: ")
    password = raw_input("password: ")
    token = login(username, password)

    print("enter help for a list of commands")
    command = raw_input("command: ")
    command = command.split()
    while True:
        if command[0] == "help":
            printHelp()
        elif command[0] == "profile" or command[0] == "p":
            profile(token)
        elif command[0] == "quote" or command[0] == "q":
            if len(command) == 2:
                quote(command[1].upper())
            else:
                print 'ticker not given'
        elif command[0] == "buy" or command[0] =="b":
            if len(command) == 3:
                buy(token, command[1].upper(), command[2])
            else:
                print 'buy command must include and only include the ' 
                + 'symbol and amount'
        elif command[0] == "sell" or command[0] =="s":
            if len(command) == 3:
                sell(token, command[1].upper(), command[2])
            else:
                print 'sell command must include and only include the ' 
                + 'symbol and amount'
        elif command[0] == "tsl":
            if len(command) == 4:
                trailing_stoploss(token, command[1].upper(), command[2], float(command[3]))
            else:
                print 'tsl command must include and only include the ' 
                + 'symbol, amount, and price difference'
        elif command[0] == "quit":
            exit(0)
        command = raw_input("command: ")
        command = command.split()
main()
