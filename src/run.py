from Kozo import Kozo
import getpass

# Login user to Robinhood account
def login(user):
    # Loop until successful
    loggedin = False
    while loggedin == False:
        user.set_username(raw_input('Username: '))
        user.set_password(getpass.getpass('Password: '))
        loggedin = user.login()
    
# Prints all of the available commands
def print_help():
    print ''
    print 'profile, p - get information about currently held stocks'
    print 'quote, q [symbol] - get information about a stock'
    print 'buy, b [symbol] [amount] - purchase a stock at market price'
    print 'sell, s [symbol] [amount] - purchase a stock at market price'
    print 'tsl - start trailing stoploss for stocks'
    print ''
    
# Gets commands from the user
def get_commands(user):
    print("Enter 'help' for a list of commands")
    command = raw_input("Command: ")
    command = command.split()

    while True:
        if command[0] == "help":
            print_help()
        elif command[0] == "profile" or command[0] == "p":
            user.profile()
        elif command[0] == "quote" or command[0] == "q":
            if len(command) == 2:
                user.quote(command[1].upper())
            else:
                print 'ticker not given'
        elif command[0] == "buy" or command[0] == "b":
            if len(command) == 3:
                user.buy(command[1].upper(), command[2])
            else:
                print 'buy command must include and only include the '
                + 'symbol and amount'
        elif command[0] == "sell" or command[0] == "s":
            if len(command) == 3:
                user.sell(command[1].upper(), command[2])
            else:
                print 'sell command must include and only include the '
                + 'symbol and amount'
        elif command[0] == "tsl":
            user.multi_tsl()
        elif command[0] == "quit":
            exit(0)
        command = raw_input("Command: ")
        command = command.split()

def main():
    user = Kozo()
    login(user)    
    get_commands(user)

if __name__ == "__main__":
    main()
