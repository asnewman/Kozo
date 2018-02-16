# =============================================================================
# Created by asnewman (Ashley Newman)
# tsl.py is to be run as a trailing stoploss by crontab.
# It will get information from a file label 'tsl.data' which is generated
# by the main program.
#
# Imported args
# 1. orders path
# 2. username
# 3. password
# =============================================================================
import sys
import requests
import time as timesleep
from kozo import Kozo
from resources import Resources
from api import API
from datetime import datetime, time

def tsl(path, user):
    orders = get_orders(path)

    # Make sure that there are still orders to process and the market is open
    while len(orders) and check_market_open():
        new_orders = []
        for order in orders:
            curr_price = user.get_quote(order["ticker"])

            print datetime.now().time()
            print order["ticker"]
            print "curr price: " + str(curr_price)
            print "trail price: " + str(order["trailPrice"])

            # Check if need to sell
            if curr_price <= order["trailPrice"]:
                user.sell(order["ticker"].upper, order["amount"])
                #print "tsl for " + order["ticker"] + " has sold"
            else:
                if curr_price > order["trailPrice"] + order["trailDiff"]:
                    order["trailPrice"] = curr_price - order["trailDiff"]

                # Save the order for the next run
                new_orders.append(order)
        orders = new_orders
        timesleep.sleep(5)

    # Save the current orders
    f = open(path, 'w')
    for order in orders:
        f.write(str(order["ticker"]) +  " " +\
                str(order["amount"]) +  " " +\
                str(order["trailDiff"]) +  " " +\
                str(order["trailPrice"]) + "\n")

    exit()

# Check to see if the market is open
def check_market_open():
    api = API()
    links = api.market_hours()
    
    for link in links:
        req = requests.get(link)
        if req.json()["is_open"] == False:
            return False

    # Currently in PST
    now_time = datetime.now().time()

    if time(6,30) <= now_time <= time(13,00):
        return True

    return False

# Validates data of an order
# 0. Ticker (string)
# 1. Amount of stock (int)
# 2. Trail difference (float)
# 3. Current trail price (float)
def validate_order(order):
    ORDER_LENGTH = 4
    TICKER = 0
    AMOUNT = 1
    TRAIL_DIFF = 2
    CURR_TRAIL = 3

    # Assume ticker is correct for now

    # Check for valid length
    if len(order) != ORDER_LENGTH:
        print "Invalid order length"
        return False

    # Amount check
    if not order[AMOUNT].isdigit():
        print "Amount is not a positive integer"
        return False

    # Trail difference check
    if not check_string_positive_float(order[TRAIL_DIFF]):
        print "Trail difference is not a positive float"
        return False

    # Current trail price check
    if not check_string_positive_float(order[CURR_TRAIL]):
        print "Current trail price is not a positive float"
        return False
    
    return True

def check_string_positive_float(s):
    try:
        if float(s) <= 0:
            return False
        return True
    except:
        return False

# Gets the orders from a file given
def get_orders(path):
    TICKER = 0
    AMOUNT = 1
    TRAIL_DIFF = 2
    CURR_TRAIL = 3

    orders = []

    with open(path) as f:
        data = f.readlines()
        for order in data:
            order = order.split()
            if validate_order(order):
                # Create json object of the order
                orders.append({"ticker": order[TICKER], 
                               "amount": int(order[AMOUNT]), \
                               "trailDiff": float(order[TRAIL_DIFF]),\
                               "trailPrice": float(order[CURR_TRAIL])})

    return orders

def main():
    # Make sure there is two args for the username and password
    if len(sys.argv) != 4:
        print "Incorrect amount of args. Need just order path, username and "+\
               "password"
        exit()

    user = Kozo()
    if not Resources.auto_login(user, sys.argv[2], sys.argv[3]):
        print 'Username or password was incorrect'
        exit()

    tsl(sys.argv[1], user) 

if __name__ == "__main__":
    main()
