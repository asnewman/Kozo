# =============================================================================
# Created by asnewman (Ashley Newman)
# tsl.py is to be run as a trailing stoploss by crontab.
# It will get information from a file label 'tsl.data' which is generated
# by the main program.
#
# Imported args
# 1. username
# 2. password
# =============================================================================

from kozo import Kozo
from resources import Resources

# Validates data of an order
# 1. Ticker (string)
# 2. Amout of stock (int)
# 3. Trailing price (float)
def validate_order(order):
    # Assume ticker is correct for now

    # Check for valid length
    if len(order) != 3:
        print "Invalid order length"
        return False

    if not order[1].isdigit():
        print "Amount is not a positive integer"
        return False

    try:
        if float(order[2]) <= 0:
            print "Price different cannot be negative"
            return False
    except ValueError:
        print "Price difference is not a float"
        return False

    return True

# Gets the orders from a file given
def get_orders(path):
    TICKER = 0
    AMOUNT = 1
    DIFF = 2

    orders = []

    with open(path) as f:
        data = f.readlines()
        for order in data:
            order = order.split()
            if validate_order(order):
                orders.append([order[TICKER], int(order[AMOUNT]), \
                    float(order[DIFF])])

    return orders

def main():
    # Make sure there is two args for the username and password
    if len(sys.argv) != 3:
        print "Incorrect amount of args. Need just username and password"

    user = Kozo()
    if not Resources.auto_login(user, sys.argv[1], sys.argv[2]):
        print 'Username or password was incorrect'
        exit(0)
