from uuid import uuid4


def generate_recovery_codes(number_of_tokens):
    for _ in range(number_of_tokens):
        yield uuid4().hex.upper()
