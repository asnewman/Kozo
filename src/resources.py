import getpass

class Resources:
    # Login user to Robinhood account using passed in arguements
    @staticmethod
    def auto_login(user, username, password):
        user.set_username(username)
        user.set_password(password)
        return user.login()

    # Login user to Robinhood account
    @staticmethod
    def login(user):
        # Loop until successful
        loggedin = False
        while loggedin == False:
            user.set_username(raw_input('Username: '))
            user.set_password(getpass.getpass('Password: '))
            loggedin = user.login()
        
    # Prints all of the available commands
    @staticmethod
    def print_help():
        print ''
        print 'profile, p - get information about currently held stocks'
        print 'quote, q [symbol] - get information about a stock'
        print 'buy, b [symbol] [amount] - purchase a stock at market price'
        print 'sell, s [symbol] [amount] - purchase a stock at market price'
        print 'tsl - start trailing stoploss for stocks'
        print 'sb - schedules a buy at 12:59pm PST the next day with price condition'
        print '     [symbol] [amount] [price] [direction - above|below]'
        print ''
        
    # Gets commands from the user
    @staticmethod
    def get_commands(user):
        print("Enter 'help' for a list of commands")
        command = raw_input("Command: ")
        command = command.split()
    
        while True:
            if command[0] == "help":
                Resources.print_help()
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
            elif command[0] == "sb":
                if len(command) == 5:
                    user.scheduled_buy(command[1].upper(), command[2], \
                            command[3], command[4])
                else:
                    print "sb must have only 5 arguements"
            elif command[0] == "quit":
                exit(0)
            command = raw_input("Command: ")
            command = command.split()
