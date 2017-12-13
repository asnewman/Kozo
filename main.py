import requests
import getpass
import sys
from prettytable import PrettyTable

def login(username, password):
    url = 'https://api.robinhood.com/api-token-auth/username'
    r = requests.post(url, data={'username':username, 'password':password})
    if r.status_code == 200:
        print 'log in successful!'
        return r.json()['token']
    else:
        print 'log in unsuccessful'
        exit(1)

def printHelp():
    print "profile, p - get information about currently held stocks"
    print "quote, q [ticker] - get ticket information about a stock"

def profile(token):
    url = 'https://api.robinhood.com/accounts/'
    r = requests.get('https://api.robinhood.com/accounts/5SF74735/positions/', headers={'Authorization':'Token '+token})
    
    # Gather all of the items with quantity over 0
    holding = []
    for res in r.json()['results']:
        if float(res['quantity']) > 0:
            holding.append(res)

    table = PrettyTable(['stock', 'quantity', 'average price', 'current price', 'total price', 'gain'])
    for h in holding:
        symbol = requests.get(h['instrument']).json()['symbol']
        quantity = float(h['quantity'])
        avgPrice = float(h['average_buy_price'])
        currPrice = float(requests.get('https://api.robinhood.com/quotes/'+symbol+'/').json()['last_trade_price'])
        gain = currPrice * quantity - avgPrice * quantity
        table.add_row([symbol, quantity, avgPrice, currPrice, quantity * currPrice, gain])

    print table

def quote(ticker):
    print "looking up " + ticker
    url = "https://api.robinhood.com/quotes/"
    r = requests.get(url+ticker+'/')
    table = PrettyTable(['stock', 'price'])
    table.add_row([ticker, r.json()['last_trade_price']])
    print table

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
        elif command[0] == "quit":
            exit(0)
        command = raw_input("command: ")
        command = command.split()
main()
