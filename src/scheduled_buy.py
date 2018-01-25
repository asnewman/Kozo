import sys
from kozo import Kozo
from resources import Resources

# Fires a buy order with specified options

# Imported args
# 1. username
# 2. password
# 3. symbol
# 4. amount
# 5. price
# 6. directions (above or below)

# Validates that the args are in correct format
def validate_args(args):
    # Make sure amout is a positive int
    if not args[4].isdigit():
        print "Amount is not a positive integer: " + args[3]
        return False
    

    try:
        float(args[5])
    except ValueError:
        print "Price is not a float: " + args[4]
        return False

    # Make sure direction is either 'above' or 'below'
    if args[6] != "above" and args[6] != "below":
        print "Direction must be either above or below: " + args[5]
        return False

    return True

def buy(user, args):
    print 'Attempting to buy ' + args[3]
    quote = user.get_quote(args[3])

    # above case
    if args[6] == "above" and quote > float(args[5]):
        user.buy(args[3], args[4])
    # below case
    elif args[6] == "below" and quote < float(args[5]):
        user.buy(args[3], args[4])
    else:
        print args[6] + ' condition not met for ' + args[3] + ' at ' + \
            args[5] + '.' + ' Current price is ' + str(quote) + '.'

def main():
    # Make sure the args are the correct length
    if len(sys.argv) != 7:
        print "Incorrect amount of arguements"
        exit(0)
    
    validate_args(sys.argv)
    user = Kozo()
    if not Resources.auto_login(user, sys.argv[1], sys.argv[2]):
        print 'Username or password was incorrect'
        exit(0)
    buy(user, sys.argv)

if __name__ == "__main__":
    main()
