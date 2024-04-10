import random


def generateRandomPhoneNumber():
    return random.choice(['+62', '+39', '+86', '+44']) + str(random.randint(1000000000, 9999999999))