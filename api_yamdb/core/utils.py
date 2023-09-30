from random import choice
from string import ascii_letters


def get_confirmation_code():
    return ''.join(choice(ascii_letters) for i in range(12))
