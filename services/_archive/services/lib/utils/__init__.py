import secrets
import os
from pusher import Pusher


RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'


def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.
    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)
    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return ''.join(secrets.choice(allowed_chars) for i in range(length))


def get_pusher_client():
    # configure pusher object
    return Pusher(
      app_id=os.environ['PUSHER_APP_ID'],
      key=os.environ['PUSHER_API_KEY'],
      secret=os.environ['PUSHER_API_SECRET'],
      cluster=os.environ['PUSHER_CLUSTER'],
      ssl=os.getenv('PUSHER_SSL', True)
    ) 