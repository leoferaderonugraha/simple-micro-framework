# Define a decorator function
def custom_route(url, **opts):
    def decorator(func):
        return func
    return decorator  # Return the decorator function


# Applying the decorator to a function
@custom_route('/example', methods=['GET', 'POST'])
def my_function(arg1, arg2, optional_arg=None):
    print(f"Arguments received: {arg1}, {arg2}, {optional_arg}")


# Test the decorated function
my_function('Hello', 'World', optional_arg='Optional')
