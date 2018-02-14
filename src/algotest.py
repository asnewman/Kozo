def tsl_test(prices):
    order = {"trailDiff": .05,
             "trailPrice": 10.95}

    for price in prices:
        curr_price = price

        # Current price has hit trail price so sell
        if curr_price <= order["trailPrice"]:
            print "sold"
        # Current price raises trail price
        elif curr_price > order["trailPrice"] + order["trailDiff"]:
            order["trailPrice"] = curr_price - order["trailDiff"]

        print "trail price " + str(order["trailPrice"])


prices = [11, 11.02, 10.99, 10.98, 11.07, 11.05, 11.09]
tsl_test(prices)
