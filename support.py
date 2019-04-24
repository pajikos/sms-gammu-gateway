import sys

import gammu


def load_user_data(filename='/credentials.txt'):
    users = {}
    with open(filename) as credentials:
        for line in credentials:
            username, password = line.partition(":")[::2]
            users[username.strip()] = password.strip()
    return users


def init_state_machine(pin, filename='/gammu.config'):
    sm = gammu.StateMachine()
    sm.ReadConfig(Filename=filename)
    sm.Init()

    if sm.GetSecurityStatus() == 'PIN':
        if pin is None or pin == '':
            print("PIN is required.")
            sys.exit(1)
        else:
            sm.EnterSecurityCode('PIN', pin)
    return sm
