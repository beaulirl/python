from functools import wraps


def decor_maker(test_message):
    def new_year_sale_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if args:
                return function(args[0]) * 0.5
            if kwargs:
                print test_message
                return function(kwargs) * 0.95
        return wrapper
    return new_year_sale_decorator


@decor_maker(None)
def set_price(product):
    """Set price for oranges, apples ans pears."""
    if product == 'Orange':
        return 50
    elif product == 'Apple':
        return 40
    elif product == 'Pear':
        return 30


@decor_maker('Discount for A')
def set_general_sum(busket):
    general_sum = 0
    for product, amount in busket.iteritems():
        general_sum += set_price(product) * amount
    return general_sum

print set_price('Apple')

print set_price.__name__

print set_price.__doc__

print set_general_sum(Apple=2, Orange=3, Pear=4)
