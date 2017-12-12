import requests
import getpass
import sys
from prettytable import PrettyTable

def login(username, password):
    url = 'https://api.robinhood.com/api-token-auth/username'
    r = requests.post(url, data={'username':username, 'password':password})
    print r.text
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
#    r = requests.get(url, headers={'Authorization':'Token '+token})
 #   print r.text
    r = requests.get('https://api.robinhood.com/accounts/5SF74735/positions/', headers={'Authorization':'Token '+token})
    print r.text

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
    
    print("token entered: " + token)

    print("enter help for a list of commands")
    command = raw_input("command: ")
    command = command.split()
    while True:
        if command[0] == "help":
            printHelp()
        elif command[0] == "profile" or command[0] == "p":
            profile(token)
        elif command[0] == "quote" or command[0] == "q":
            quote(command[1].upper())
        elif command[0] == "quit":
            exit(0)
        command = raw_input("command: ")
        command = command.split()
main()
