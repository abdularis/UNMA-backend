# decorator.py
# Created by abdularis on 21/10/17

import functools


def decorate_function(f, **add_kwargs):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        kwargs.update(add_kwargs)
        return f(*args, **kwargs)
    return wrapper
