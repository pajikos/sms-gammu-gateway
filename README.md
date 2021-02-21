# REST API SMS Gateway using gammu

Simple SMS REST API gateway for sending and receiving SMS from gammu supported devices. Gammu supports standard AT commands, which are using most of USB GSM modems.

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/pajikos/sms-gammu-gateway.svg)
![Docker Automated build](https://img.shields.io/docker/automated/pajikos/sms-gammu-gateway.svg)
![GitHub](https://img.shields.io/github/license/pajikos/sms-gammu-gateway.svg)


#### Available REST API endpoints:

- ##### Send a SMS :lock:
  ```
  POST http://xxx.xxx.xxx.xxx:5000/sms
  Content-Type: application/json
  Authorization: Basic admin password
  {
    "text": "Hello, how are you?",
    "number": "+420xxxxxxxxx"
  }
  ```
  Example:
  ```bash
  AUTH=$(echo -ne "admin:password" | base64 --wrap 0)
  curl -H 'Content-Type: application/json' -H "Authorization: Basic $AUTH" -X POST --data '{"text":"Hello, how   are you?", "number":"+420xxxxxxxxx"}' http://localhost:5000/sms
  1
  ```
  If you need to customize the smsc number:
  ```bash
  curl -H 'Content-Type: application/json' -H "Authorization: Basic $AUTH" -X POST --data '{"text":"Hello, how are you?", "number":"+420xxxxxxxxx","smsc": "+33695000695"}' http://localhost:5000/sms
  ```
- ##### Retrieve all the SMS stored on the modem/SIM Card :lock:
  ```
  GET http://xxx.xxx.xxx.xxx:5000/sms
  ```
  ```json
  [
    {
      "Date": "2021-02-17 15:20:20",
      "Number": "+xxxxxxxxxxx",
      "State": "UnRead",
      "Text": "Hello"
    },
    ...
  ]
  ```

- ##### Retrieve {n}th message stored on the modem/SIM Card :lock:
  ```
  GET http://xxx.xxx.xxx.xxx:5000/sms/{n}
  ```
  ```json
  {
    "Date": "2021-02-17 15:20:20",
    "Number": "+xxxxxxxxxxx",
    "State": "UnRead",
    "Text": "Hello"
  }
  ```

- ##### Delete {n}th message stored on the modem/SIM Card :lock:
  ```
  DELETE http://xxx.xxx.xxx.xxx:5000/sms/{n}
  ```

- ##### Retrieve 1st message stored on the modem/SIM Card and delete it :lock:
  ```
  GET http://xxx.xxx.xxx.xxx:5000/getsms
  ```
  ```json
  {
    "Date": "2021-02-17 15:20:20",
    "Number": "+xxxxxxxxxxx",
    "State": "UnRead",
    "Text": "Hello"
  }
  ```

- ##### Get the current signal strength :unlock: 
  ```
  GET http://xxx.xxx.xxx.xxx:5000/signal
  ```
  ```json
  {
    "SignalStrength": -83, 
    "SignalPercent": 45, 
    "BitErrorRate": -1
  }
  ```

- ##### Get the current network details :unlock: 
  ```
  GET http://xxx.xxx.xxx.xxx:5000/network
  ```
  ```json
  {
    "NetworkName": "DiGi",
    "State": "RoamingNetwork",
    "PacketState": "RoamingNetwork",
    "NetworkCode": "502 16",
    "CID": "00A18B30",
    "PacketCID": "00A18B30",
    "GPRS": "Attached",
    "PacketLAC": "7987",
    "LAC": "7987"
  }
  ```

- ##### Reset the modem (see FAQ for more info) :unlock:
  ```
  GET http://xxx.xxx.xxx.xxx:5000/reset
  ```
  ```json
  {
    "Status": 200,
    "Message": "Reset done"
  }


# Usage

There are two options how to run this REST API SMS Gateway:
* Standalone installation
* Running in Docker

## Prerequisites
Either you are using Docker or standalone installation, your GSM modem must be visible in the system. 
When you put a USB stick to your system, you have to see a new USB device:
```
dmesg | grep ttyUSB
```
or typing command:
```
lsusb
```
```
...
Bus 001 Device 009: ID 12d1:1406 Huawei Technologies Co., Ltd. E1750
...
```
If only cdrom device appeared, install [usb-modeswitch](http://www.draisberghof.de/usb_modeswitch) to see a modem as well:
```
apt-get install usb-modeswitch
```

## Standalone installation
This guide does not cover Python 3.x installation process (including pip), but it is required as well.
#### Install system dependencies (using apt):
```
apt-get update && apt-get install -y pkg-config gammu libgammu-dev libffi-dev
```
#### Clone repository
```
git clone https://github.com/pajikos/sms-gammu-gateway
cd sms-gammu-gateway
```
#### Install python dependencies
```
pip install -r requirements.txt
```
#### Edit gammu configuration 
You usually need to edit device property in file [gammu.config](https://wammu.eu/docs/manual/config/index.html) only, e.g.:
```
[gammu]
device = /dev/ttyUSB1
connection = at
```
#### Run application (it will start to listen on port 5000):
```
python run.py
``` 

## Running in Docker
In a case of using any GSM supporting AT commands, you can simply run the container:
```
docker run -d -p 5000:5000 --device=/dev/ttyUSB0:/dev/mobile pajikos/sms-gammu-gateway
```
#### Docker compose:
```
version: '3'
services:
  sms-gammu-gateway:
    container_name: sms-gammu-gateway
    restart: always
    image: pajikos/sms-gammu-gateway
    environment:
      - PIN="1234"
    ports:
      - "5000:5000"
    devices:
      - /dev/ttyUSB1:/dev/mobile
```

## FAQ
#### PIN configuration
Pin to unblock SIM card could be set using environment variable PIN, e.g. PIN=1234.
#### Authentication
Out of the box, there is needed an HTTP Basic authentication to send any SMS, username and password can be configured in `credentials.txt`
#### How to use HTTPS?
Using environment variable SSL=True, the program expects RSA private key and certificate to provide content via HTTPS.
Expected file paths (you can edit it in run.py or mount your own key/cert in Docker):

```
/ssl/key.pem
/ssl/cert.pem
```
#### No more modem response ?
If you have some regular problem with your modem and you don't want to disconnect and reconnect it physically to reset it, you can try to regularly use the reset function.
(For example with my Huawei modem the reset function is used every 24 hours to maintain the stability of the system)

#### It does not work...
Try to check [gammu configuration file site](https://wammu.eu/docs/manual/config/index.html)

## Integration with Home Assistant
#### Signal Strength sensor
```yaml
- platform: rest
  resource: http://xxx.xxx.xxx.xxx:5000/signal
  name: GSM Signal
  scan_interval: 30
  value_template: '{{ value_json.SignalPercent }}'
  unit_of_measurement: '%'
```

#### SMS notification
```yaml
notify:
  - name: SMS GW
    platform: rest
    resource: http://xxx.xxx.xxx.xxx:5000/sms
    method: POST_JSON
    authentication: basic
    username: !secret sms_gateway_username
    password: !secret sms_gateway_password
    target_param_name: number
    message_param_name: text
```

#### Using in Automation
```yaml
- alias: Alarm Entry Alert - Garage Door
  trigger:
    platform: state
    entity_id: binary_sensor.garage_door
    state: 'on'
  condition:
    - platform: state
      entity_id: alarm_control_panel.alarm
      state: 'armed_home'
  action:
    service: notify.sms_gw
    data:
      message: 'alert, entry detected at garage door'
      target: '+xxxxxxxxxxxx'
```

#### Receiving SMS and sending notification

```yaml
sensor:
  - platform: rest
    resource: http://127.0.0.1:5000/getsms
    name: sms
    scan_interval: 20
    username: !secret sms_gateway_username
    password: !secret sms_gateway_password
    json_attributes:
      - Date
      - Number
      - Text
      - State

automation sms_automations:
  - alias: Notify on received SMS
    trigger:
      - platform: template
        value_template: "{{state_attr('sensor.sms', 'Text') != ''}}"
    action:
      - service: notify.mobile_app_[DEVICE]
        data:
          title: SMS from {{ state_attr('sensor.sms', 'Number') }}
          message: "{{ state_attr('sensor.sms', 'Text') }}"
          data:
            sticky: "true"
      - service: persistent_notification.create
        data:
          title: SMS from {{ state_attr('sensor.sms', 'Number') }}
          message: "{{ state_attr('sensor.sms', 'Text') }}"
```
