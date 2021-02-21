import os

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import load_user_data, init_state_machine, retrieveAllSms, deleteSms
from gammu import GSMNetworks

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
    def get(self):
        allSms = retrieveAllSms(machine)
        list(map(lambda sms: sms.pop("Locations"), allSms))
        return allSms

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        if args['text'] is None or args['number'] is None:
            abort(404, message="Parameters 'text' and 'number' are required.")
        result = [machine.SendSMS({
          'Text': args.get("text"),
          'SMSC': {'Number': args.get("smsc")} if args.get("smsc") else {'Location': 1},
          'Number': number,
        }) for number in args.get("number").split(',')]
        return {"status": 200, "message": str(result)}, 200


class Signal(Resource):
    def __init__(self, sm):
        self.machine = sm

    def get(self):
        return machine.GetSignalQuality()


class Reset(Resource):
    def __init__(self, sm):
        self.machine = sm

    def get(self):
        machine.Reset(False)
        return {"status":200, "message": "Reset done"}, 200


class Network(Resource):
    def __init__(self, sm):
        self.machine = sm

    def get(self):
        network = machine.GetNetworkInfo()
        network["NetworkName"] = GSMNetworks.get(network["NetworkCode"], 'Unknown')
        return network


class GetSms(Resource):
    def __init__(self, sm):
        self.machine = sm

    @auth.login_required
    def get(self):
        allSms = retrieveAllSms(machine)
        sms = {"Date": "", "Number": "", "State": "", "Text": ""}
        if len(allSms) > 0:
            sms = allSms[0]
            deleteSms(machine, sms)
            sms.pop("Locations")

        return sms


class SmsById(Resource):
    def __init__(self, sm):
        self.machine = sm

    @auth.login_required
    def get(self, id):
        allSms = retrieveAllSms(machine)
        self.abort_if_id_doesnt_exist(id, allSms)
        sms = allSms[id]
        sms.pop("Locations")
        return sms

    def delete(self, id):
        allSms = retrieveAllSms(machine)
        self.abort_if_id_doesnt_exist(id, allSms)
        deleteSms(machine, allSms[id])
        return '', 204

    def abort_if_id_doesnt_exist(self, id, allSms):
        if id < 0 or id >= len(allSms):
            abort(404, message = "Sms with id '{}' not found".format(id))


api.add_resource(Sms, '/sms', resource_class_args=[machine])
api.add_resource(SmsById, '/sms/<int:id>', resource_class_args=[machine])
api.add_resource(Signal, '/signal', resource_class_args=[machine])
api.add_resource(Network, '/network', resource_class_args=[machine])
api.add_resource(GetSms, '/getsms', resource_class_args=[machine])
api.add_resource(Reset, '/reset', resource_class_args=[machine])

if __name__ == '__main__':
    if ssl:
        app.run(port='5000', host="0.0.0.0", ssl_context=('/ssl/cert.pem', '/ssl/key.pem'))
    else:
        app.run(port='5000', host="0.0.0.0")
