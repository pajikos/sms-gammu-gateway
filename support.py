import sys

import gammu


def load_user_data(filename='credentials.txt'):
    users = {}
    with open(filename) as credentials:
        for line in credentials:
            username, password = line.partition(":")[::2]
            users[username.strip()] = password.strip()
    return users


def init_state_machine(pin, filename='gammu.config'):
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


def retrieveAllSms(machine):
    status = machine.GetSMSStatus()
    allMultiPartSmsCount = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    allMultiPartSms = []
    start = True

    while len(allMultiPartSms) < allMultiPartSmsCount:
        if start:
            currentMultiPartSms = machine.GetNextSMS(Start = True, Folder = 0)
            start = False
        else:
            currentMultiPartSms = machine.GetNextSMS(Location = currentMultiPartSms[0]['Location'], Folder = 0)
        allMultiPartSms.append(currentMultiPartSms)

    allSms = gammu.LinkSMS(allMultiPartSms)

    results = []
    for sms in allSms:
        smsPart = sms[0]

        result = {
            "Date": str(smsPart['DateTime']),
            "Number": smsPart['Number'],
            "State": smsPart['State'],
            "Locations": [smsPart['Location'] for smsPart in sms],
        }

        decodedSms = gammu.DecodeSMS(sms)
        if decodedSms == None:
            result["Text"] = smsPart['Text']
        else:
            text = ""
            for entry in decodedSms['Entries']:
                if entry['Buffer'] != None:
                    text += entry['Buffer']

            result["Text"] = text

        results.append(result)

    return results


def deleteSms(machine, sms):
    list(map(lambda location: machine.DeleteSMS(Folder=0, Location=location), sms["Locations"]))
