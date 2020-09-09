import os

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import load_user_data, init_state_machine

pin = os.getenv('PIN', None)
ssl = os.getenv('SSL', False)
user_data = load_user_data()
machine = init_state_machine(pin)
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return user_data.get(username) == password


class Sms(Resource):

    def __init__(self, sm):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('text')
        self.parser.add_argument('number')
        self.parser.add_argument('smsc')
        self.machine = sm

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        if args['text'] is None or args['number'] is None:
            abort(404, message="Parameters 'text' and 'number' are required.")
        message = {
            'Text': args.get("text"),
            'SMSC': args.get("smsc") or {'Location': 1},
            'Number': args.get("number"),
        }
        return machine.SendSMS(message), 200


class Signal(Resource):
    def __init__(self, sm):
        self.machine = sm

    def get(self):
        return machine.GetSignalQuality()

class Getsms(Resource):
    def __init__(self, sm):
        self.machine = sm

    @auth.login_required
    def get(self):
        status = machine.GetSMSStatus()
        remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

        sms_dict = {"Date": "", "Number": "", "State": "", "Text": ""}

        try:

           sms = machine.GetNextSMS(Start=True, Folder=0)

        except:
           return sms_dict

        if len(sms) > 0:

          sms_dict["Date"] = str(sms[0]['DateTime'])
          sms_dict["Number"] = str(sms[0]['Number'])
          sms_dict["State"] = str(sms[0]['State'])
          sms_dict["Text"] = str(sms[0]['Text'])

          machine.DeleteSMS(Folder=0, Location=sms[0]['Location'])

        return sms_dict

api.add_resource(Sms, '/sms', resource_class_args=[machine])
api.add_resource(Signal, '/signal', resource_class_args=[machine])
api.add_resource(Getsms, '/getsms', resource_class_args=[machine])

if __name__ == '__main__':
    if ssl:
        app.run(port='5000', host="0.0.0.0", ssl_context=('/ssl/cert.pem', '/ssl/key.pem'))
    else:
        app.run(port='5000', host="0.0.0.0")
